"""
Phase 2 diagnostic:

1. Reads BOOLEAN_BRANCH actions from flows that likely have conditions set
   (Browse Abandonment, Welcome Series) to find the correct settings schema.

2. Tries to GET the flow definition with additional-fields to see inline conditions.

3. Probes condition type values that haven't been tried yet.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py diagnose_splits2.py
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

PLACED_ORDER_METRIC = "Sxnb5T"
REPLENISHMENT_METRIC = "UWP7cZ"

# ── Part 1: Find flows with configured conditional splits ──────────────────────

def get_all_flows():
    flows, url = [], f"{BASE_URL}/flows"
    params = {"fields[flow]": "name,status", "page[size]": 50}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        flows.extend(data.get("data", []))
        url = data.get("links", {}).get("next")
        params = {}
        time.sleep(0.1)
    return flows


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


def get_action_detail(action_id):
    """GET a single flow-action with all fields."""
    r = requests.get(
        f"{BASE_URL}/flow-actions/{action_id}",
        headers=HEADERS,
        params={"additional-fields[flow-action]": "settings,data"},
        timeout=15,
    )
    return r.status_code, r.json() if r.ok else r.text[:400]


def scan_for_configured_splits():
    print("=" * 70)
    print("PART 1: Scanning all flows for configured BOOLEAN_BRANCH actions")
    print("=" * 70)
    flows = get_all_flows()
    print(f"Found {len(flows)} flows total.\n")

    found_configured = False
    for flow in flows:
        fid = flow["id"]
        fname = flow["attributes"]["name"]
        try:
            actions = get_actions(fid)
        except Exception as e:
            print(f"  {fname}: error reading actions: {e}")
            continue

        splits = [a for a in actions
                  if a.get("attributes", {}).get("action_type") == "BOOLEAN_BRANCH"]
        if not splits:
            continue

        for split in splits:
            settings = split.get("attributes", {}).get("settings", {})
            # Any settings beyond just is_joined?
            meaningful = {k: v for k, v in settings.items() if k != "is_joined"}
            if meaningful:
                print(f"\nFOUND configured split in '{fname}' ({fid})")
                print(f"  Action id: {split['id']}")
                print(f"  Full settings: {json.dumps(settings, indent=4)}")
                found_configured = True
                # Also try with additional-fields
                status, detail = get_action_detail(split["id"])
                print(f"  With additional-fields (status {status}):")
                print(json.dumps(detail, indent=4)[:1000])
            time.sleep(0.1)

    if not found_configured:
        print("\nNo flows with non-trivial BOOLEAN_BRANCH settings found.")
        print("All splits have only {'is_joined': false} in settings.")
        print("Conditions may be stored in the flow definition, not action settings.")


# ── Part 2: Try getting flow definition via additional-fields ──────────────────

def check_definition_endpoint():
    print("\n\n")
    print("=" * 70)
    print("PART 2: GET flow definition via additional-fields")
    print("=" * 70)

    # Try on our Back in Stock flow which has a split
    flow_id = "Seu9Gy"
    url = f"{BASE_URL}/flows/{flow_id}"
    params = {"additional-fields[flow]": "definition"}
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    print(f"GET {url}?additional-fields[flow]=definition")
    print(f"Status: {r.status_code}")
    if r.ok:
        data = r.json()["data"]
        defn = data.get("attributes", {}).get("definition")
        if defn:
            print("Definition found!")
            print(json.dumps(defn, indent=2)[:3000])
        else:
            print("No 'definition' in attributes.")
            print("Available attributes:", list(data.get("attributes", {}).keys()))
    else:
        print(r.text[:400])


# ── Part 3: New condition type probes ──────────────────────────────────────────

_counter = 0

def new_id():
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0


def minimal_flow(pf):
    reset_ids()
    t1, t2 = new_id(), new_id()
    return {"data": {"type": "flow", "attributes": {"name": "__PROBE_DELETE_ME__",
        "definition": {
            "triggers": [{"type": "metric", "id": PLACED_ORDER_METRIC}],
            "profile_filter": None,
            "entry_action_id": t1,
            "actions": [
                {"temporary_id": t1, "type": "conditional-split",
                 "data": {"profile_filter": pf},
                 "links": {"next_if_true": None, "next_if_false": t2}},
                {"temporary_id": t2, "type": "send-email",
                 "data": {"message": {
                     "from_email": "hello@bargainchemist.co.nz", "from_label": "BC",
                     "reply_to_email": "orders@bargainchemist.co.nz",
                     "cc_email": None, "bcc_email": None, "subject_line": "probe",
                     "preview_text": "", "smart_sending_enabled": True,
                     "transactional": False, "add_tracking_params": True,
                     "custom_tracking_params": None, "additional_filters": None,
                     "name": "_probe"}, "status": "draft"},
                 "links": {"next": None}},
            ],
        },
    }}}


def probe(label, pf):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS,
                      json=minimal_flow(pf), timeout=30)
    if r.ok:
        fid = r.json()["data"]["id"]
        print(f"  [ACCEPTED] {label} -> {fid}")
        requests.delete(f"{BASE_URL}/flows/{fid}", headers=HEADERS, timeout=15)
    else:
        print(f"  [REJECTED] {label}")
        try:
            for e in r.json().get("errors", []):
                print(f"    detail: {e.get('detail')}")
                print(f"    source: {e.get('source')}")
        except Exception:
            print(f"    raw: {r.text[:300]}")
    time.sleep(0.35)


def run_new_probes():
    print("\n\n")
    print("=" * 70)
    print("PART 3: New condition type probes")
    print("=" * 70)
    print()

    # Try uppercase type values
    for t in ["METRIC", "EVENT", "PERSON", "PROFILE", "LIST",
              "HAS_DONE_METRIC", "METRIC_AGGREGATE", "PREDICTIVE",
              "person", "event", "profile-property", "list-member",
              "metric-event", "any-metric", "custom-metric"]:
        probe(f"type={t!r}",
              {"condition_groups": [{"conditions": [{"type": t, "metric_id": PLACED_ORDER_METRIC, "operator": "has-done", "value": 1}]}]})

    print()
    print("-- Probing condition_group structure --")
    # Maybe conditions need boolean_type or operator at group level
    probe("group with boolean_type=AND",
          {"condition_groups": [{"boolean_type": "AND", "conditions": [
              {"type": "metric", "metric_id": PLACED_ORDER_METRIC, "operator": "has-done", "value": 1}
          ]}]})

    probe("group with operator=and",
          {"condition_groups": [{"operator": "and", "conditions": [
              {"type": "metric", "metric_id": PLACED_ORDER_METRIC, "operator": "has-done", "value": 1}
          ]}]})

    # Maybe the condition needs an 'id' field
    probe("condition with id field",
          {"condition_groups": [{"conditions": [
              {"id": "1", "type": "metric", "metric_id": PLACED_ORDER_METRIC, "operator": "has-done", "value": 1}
          ]}]})

    # Maybe conditions are typed differently — no 'type', just properties
    probe("condition without type field (just metric_id + operator)",
          {"condition_groups": [{"conditions": [
              {"metric_id": PLACED_ORDER_METRIC, "operator": "has-done", "value": 1}
          ]}]})

    probe("condition without type (nested metric object)",
          {"condition_groups": [{"conditions": [
              {"metric": {"type": "metric", "id": PLACED_ORDER_METRIC}, "operator": "has-done", "value": 1}
          ]}]})

    # Try the Klaviyo segment Filter condition types from public API docs
    # https://developers.klaviyo.com/en/reference/get_segments
    for t in ["metric", "segment-membership", "location", "properties", "tags",
              "email", "push-token", "sms", "mobile-push", "identifier"]:
        probe(f"segment-style type={t!r}",
              {"condition_groups": [{"conditions": [{"type": t}]}]})


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    scan_for_configured_splits()
    check_definition_endpoint()
    run_new_probes()

    print("\n\nDone.")


if __name__ == "__main__":
    main()
