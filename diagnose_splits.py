"""
Two-purpose diagnostic:

1. Dumps the FULL raw JSON of every BOOLEAN_BRANCH (conditional-split) action
   in the 3 flows, so we can see exactly what schema Klaviyo stores for the
   data field (including profile_filter / condition_groups structure).

2. Tries additional profile_filter format variants against a minimal test flow
   and prints the FULL 400 error text for each rejected one, so we can read
   Klaviyo's validation message and derive the correct format.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py diagnose_splits.py
"""

import os, sys, json, time, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Current flow IDs
FLOWS = {
    "Seu9Gy": "[Z] Back in Stock",
    "QTNN7U": "[Z] Post-Purchase Series",
    "TGnZPt": "[Z] Replenishment - Reorder Reminders",
    "U6e3uf": "[Z] Flu Season - Winter Wellness",   # no splits — for comparison
    "YdtALs": "[Z] Win-back - Lapsed Customers",    # no splits — for comparison
}

# ── Part 1: Dump existing split action data ────────────────────────────────────

def get_actions(flow_id):
    actions, url = [], f"{BASE_URL}/flows/{flow_id}/flow-actions"
    while url:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        actions.extend(data.get("data", []))
        url = data.get("links", {}).get("next")
        time.sleep(0.1)
    return actions


def dump_split_actions():
    print("=" * 70)
    print("PART 1: Raw BOOLEAN_BRANCH action data from existing flows")
    print("=" * 70)
    for flow_id, name in FLOWS.items():
        print(f"\n--- {name} ({flow_id}) ---")
        try:
            actions = get_actions(flow_id)
            splits = [a for a in actions
                      if a.get("attributes", {}).get("action_type") == "BOOLEAN_BRANCH"]
            if not splits:
                print("  (no BOOLEAN_BRANCH actions)")
                continue
            print(f"  Found {len(splits)} BOOLEAN_BRANCH action(s).")
            # Print first split's full attributes
            a = splits[0]
            print(f"  Action id: {a['id']}")
            print("  Full attributes JSON:")
            print(json.dumps(a.get("attributes", {}), indent=4))
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(0.2)


# ── Part 2: Extended format probes with full error output ─────────────────────

PLACED_ORDER_METRIC = "Sxnb5T"
REPLENISHMENT_METRIC = "UWP7cZ"

_counter = 0

def new_id():
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0


def minimal_split_flow(trigger_metric: str, pf: dict) -> dict:
    reset_ids()
    t1 = new_id()
    t2 = new_id()
    t3 = new_id()
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "__PROBE_DELETE_ME__",
                "definition": {
                    "triggers": [{"type": "metric", "id": trigger_metric}],
                    "profile_filter": None,
                    "entry_action_id": t1,
                    "actions": [
                        {
                            "temporary_id": t1,
                            "type": "conditional-split",
                            "data": {"profile_filter": pf},
                            "links": {"next_if_true": None, "next_if_false": t2},
                        },
                        {
                            "temporary_id": t2,
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "BC",
                                    "reply_to_email": "orders@bargainchemist.co.nz",
                                    "cc_email": None,
                                    "bcc_email": None,
                                    "subject_line": "probe",
                                    "preview_text": "",
                                    "smart_sending_enabled": True,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None,
                                    "name": "_probe",
                                },
                                "status": "draft",
                            },
                            "links": {"next": None},
                        },
                    ],
                },
            },
        }
    }


def probe(label: str, trigger_metric: str, pf: dict):
    payload = minimal_split_flow(trigger_metric, pf)
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        fid = r.json()["data"]["id"]
        print(f"  [ACCEPTED] {label} -> flow {fid}")
        requests.delete(f"{BASE_URL}/flows/{fid}", headers=HEADERS, timeout=15)
    else:
        print(f"  [REJECTED] {label}")
        try:
            errs = r.json().get("errors", [])
            for e in errs:
                print(f"    code:   {e.get('code')}")
                print(f"    title:  {e.get('title')}")
                print(f"    detail: {e.get('detail')}")
                src = e.get("source", {})
                if src:
                    print(f"    source: {src}")
        except Exception:
            print(f"    raw: {r.text[:600]}")
    time.sleep(0.4)


def run_probes():
    print("\n")
    print("=" * 70)
    print("PART 2: Extended profile_filter format probes (full error output)")
    print("=" * 70)

    print("\n-- Placed-order filter candidates (trigger=Placed Order) --\n")

    probe("null/None (baseline — should always succeed)",
          PLACED_ORDER_METRIC,
          None)

    probe("empty dict {}",
          PLACED_ORDER_METRIC,
          {})

    probe("condition_groups empty list",
          PLACED_ORDER_METRIC,
          {"condition_groups": []})

    probe("condition_groups with metric/has-done (metric nested)",
          PLACED_ORDER_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "metric",
                      "metric": {"type": "metric", "id": PLACED_ORDER_METRIC},
                      "operator": "has-done",
                      "value": 1,
                      "timeframe": {"type": "since-flow-start"},
                      "filter": {"type": "all", "conditions": []},
                  }]
              }]
          })

    probe("condition_groups with metric/has-done (metric_id flat)",
          PLACED_ORDER_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "metric",
                      "metric_id": PLACED_ORDER_METRIC,
                      "operator": "has-done",
                      "value": 1,
                      "timeframe": {"type": "since-flow-start"},
                      "filter": {"type": "all", "conditions": []},
                  }]
              }]
          })

    probe("conditions[] at top level (no condition_groups wrapper)",
          PLACED_ORDER_METRIC,
          {
              "conditions": [{
                  "type": "metric",
                  "metric_id": PLACED_ORDER_METRIC,
                  "operator": "has-done",
                  "value": 1,
              }]
          })

    probe("and[] at top level",
          PLACED_ORDER_METRIC,
          {
              "and": [{
                  "metric_id": PLACED_ORDER_METRIC,
                  "operator": "has-done",
                  "value": 1,
              }]
          })

    probe("type+metric_id flat (no condition_groups)",
          PLACED_ORDER_METRIC,
          {
              "type": "metric",
              "metric_id": PLACED_ORDER_METRIC,
              "operator": "has-done",
              "value": 1,
          })

    probe("Klaviyo profile-filter style (HAS_DONE_METRIC uppercase)",
          PLACED_ORDER_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "operand_type": "HAS_DONE_METRIC",
                      "operator": "HAS_DONE",
                      "value": 1,
                      "data": {
                          "metric_id": PLACED_ORDER_METRIC,
                          "timeframe": "SINCE_FLOW_START",
                      }
                  }]
              }]
          })

    print("\n-- Item-name filter candidates (trigger=Placed Order) --\n")

    probe("trigger nested filter (v1 variant)",
          REPLENISHMENT_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "trigger",
                      "definition": {
                          "filter": {
                              "type": "all",
                              "conditions": [{
                                  "type": "property",
                                  "definition": {
                                      "property": "Item Names",
                                      "operator": "contains",
                                      "value": "Regaine"
                                  }
                              }]
                          }
                      }
                  }]
              }]
          })

    probe("trigger-event-property flat (v2 variant)",
          REPLENISHMENT_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "trigger-event-property",
                      "property": "Item Names",
                      "operator": "contains",
                      "value": "Regaine",
                  }]
              }]
          })

    probe("event-property with metric_id (v3 variant)",
          REPLENISHMENT_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "event-property",
                      "metric_id": REPLENISHMENT_METRIC,
                      "filter": {
                          "type": "all",
                          "conditions": [{
                              "property": "Item Names",
                              "operator": "contains",
                              "value": "Regaine",
                          }]
                      }
                  }]
              }]
          })

    probe("metric with where/event-property (v4 variant)",
          REPLENISHMENT_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "metric",
                      "metric": {"type": "metric", "id": REPLENISHMENT_METRIC},
                      "operator": "has-done",
                      "value": 1,
                      "timeframe": {"type": "since-flow-start"},
                      "filter": {
                          "type": "all",
                          "conditions": [{
                              "type": "event-property",
                              "definition": {
                                  "property": "Item Names",
                                  "operator": "contains",
                                  "value": "Regaine",
                              }
                          }]
                      }
                  }]
              }]
          })

    probe("profile_filter with boolean type (Klaviyo legacy format)",
          REPLENISHMENT_METRIC,
          {
              "bool_expr": {
                  "type": "all",
                  "operands": [{
                      "type": "event",
                      "metric_id": REPLENISHMENT_METRIC,
                      "where": {
                          "type": "all",
                          "operands": [{
                              "type": "prop_contains",
                              "property": "Item Names",
                              "value": "Regaine",
                          }]
                      }
                  }]
              }
          })

    probe("item_names via $items property path",
          REPLENISHMENT_METRIC,
          {
              "condition_groups": [{
                  "conditions": [{
                      "type": "metric",
                      "metric_id": REPLENISHMENT_METRIC,
                      "operator": "has-done",
                      "value": 1,
                      "timeframe": {"type": "since-flow-start"},
                      "filter": {
                          "type": "all",
                          "conditions": [{
                              "type": "event-property",
                              "definition": {
                                  "property": "$item_names",
                                  "operator": "contains",
                                  "value": "Regaine",
                              }
                          }]
                      }
                  }]
              }]
          })


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    dump_split_actions()
    run_probes()

    print("\nDone. Paste this full output so the correct format can be identified.")


if __name__ == "__main__":
    main()
