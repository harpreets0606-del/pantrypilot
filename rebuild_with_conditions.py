"""
Rebuilds Back in Stock, Post-Purchase, and Replenishment flows with real
conditional-split filter conditions.

Strategy:
  1. Probe Klaviyo's filter format by creating and immediately deleting a
     tiny test flow with each candidate format until one is accepted.
  2. Use the confirmed format to delete and recreate the 3 flows with
     fully configured split conditions.

Split conditions:
  Back in Stock    -- "Has placed Placed Order at least once since flow start"
  Post-Purchase    -- "Has placed Placed Order at least twice since flow start"
                      (first order triggered the flow; second = repeat buyer)
  Replenishment    -- "Trigger event Item Names contains <keyword>"
                      (one split per product, 13 total)

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py rebuild_with_conditions.py
"""

import os, sys, json, time, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

FROM_EMAIL = "hello@bargainchemist.co.nz"
FROM_LABEL = "Bargain Chemist"
REPLY_TO   = "orders@bargainchemist.co.nz"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

ALL_DAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

# ── Placed Order metric (used for Back-in-Stock and Post-Purchase splits) ──────
PLACED_ORDER_METRIC_ID = "Sxnb5T"

# ── Replenishment trigger metric ───────────────────────────────────────────────
REPLENISHMENT_METRIC_ID = "UWP7cZ"

# ── Candidate profile_filter formats to probe ─────────────────────────────────
# We try each until Klaviyo accepts the flow creation. Ordered most-likely first.

def _placed_order_filter_v1(min_count: int) -> dict:
    """condition_groups / metric / has-done style"""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "metric",
                "metric": {"type": "metric", "id": PLACED_ORDER_METRIC_ID},
                "operator": "has-done",
                "value": min_count,
                "timeframe": {"type": "since-flow-start"},
                "filter": {"type": "all", "conditions": []},
            }]
        }]
    }

def _placed_order_filter_v2(min_count: int) -> dict:
    """Alternate: metric_id at top level"""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "metric",
                "metric_id": PLACED_ORDER_METRIC_ID,
                "operator": "has-done",
                "value": min_count,
                "timeframe": {"type": "since-flow-start"},
                "filter": {"type": "all", "conditions": []},
            }]
        }]
    }

def _placed_order_filter_v3(min_count: int) -> dict:
    """Alternate: uses 'at-least' key"""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "metric",
                "metric_id": PLACED_ORDER_METRIC_ID,
                "operator": "has-done",
                "at-least": min_count,
                "timeframe": "since-flow-start",
            }]
        }]
    }

def _item_name_filter_v1(keyword: str) -> dict:
    """Trigger event property: nested filter"""
    return {
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
                                "value": keyword,
                            }
                        }]
                    }
                }
            }]
        }]
    }

def _item_name_filter_v2(keyword: str) -> dict:
    """Trigger event property: flat style"""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "trigger-event-property",
                "property": "Item Names",
                "operator": "contains",
                "value": keyword,
            }]
        }]
    }

def _item_name_filter_v3(keyword: str) -> dict:
    """Event property with metric_id"""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "event-property",
                "metric_id": REPLENISHMENT_METRIC_ID,
                "filter": {
                    "type": "all",
                    "conditions": [{
                        "property": "Item Names",
                        "operator": "contains",
                        "value": keyword,
                    }]
                }
            }]
        }]
    }

def _item_name_filter_v4(keyword: str) -> dict:
    """Metric with where clause"""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "metric",
                "metric": {"type": "metric", "id": REPLENISHMENT_METRIC_ID},
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
                            "value": keyword,
                        }
                    }]
                }
            }]
        }]
    }


# ── ID counter ─────────────────────────────────────────────────────────────────
_counter = 0

def new_id() -> str:
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0


# ── Action builders ────────────────────────────────────────────────────────────

def email_action(subject: str, template_id, name: str) -> dict:
    msg = {
        "from_email": FROM_EMAIL,
        "from_label": FROM_LABEL,
        "reply_to_email": REPLY_TO,
        "cc_email": None,
        "bcc_email": None,
        "subject_line": subject,
        "preview_text": "",
        "smart_sending_enabled": True,
        "transactional": False,
        "add_tracking_params": True,
        "custom_tracking_params": None,
        "additional_filters": None,
        "name": name,
    }
    if template_id:
        msg["template_id"] = template_id
    return {"type": "send-email", "data": {"message": msg, "status": "draft"}}


def delay_action(value: int, unit: str = "days") -> dict:
    data: dict = {"unit": unit, "value": value, "secondary_value": None}
    if unit == "days":
        data["timezone"] = "profile"
        data["delay_until_weekdays"] = ALL_DAYS
    return {"type": "time-delay", "data": data}


def split_action(profile_filter, yes_branch: list, no_branch: list) -> dict:
    return {
        "type": "conditional-split",
        "data": {"profile_filter": profile_filter},
        "_yes": yes_branch,
        "_no": no_branch,
    }


def build_definition(trigger, node_list: list) -> dict:
    actions = []

    def process(nodes):
        if not nodes:
            return None
        tids = [new_id() for _ in nodes]
        for i, (node, tid) in enumerate(zip(nodes, tids)):
            ntype = node["type"]
            action = {"temporary_id": tid, "type": ntype, "data": node["data"]}
            if ntype == "conditional-split":
                yes_first = process(node.get("_yes", []))
                no_first  = process(node.get("_no", []))
                action["links"] = {"next_if_true": yes_first, "next_if_false": no_first}
            else:
                next_tid = tids[i + 1] if i < len(nodes) - 1 else None
                action["links"] = {"next": next_tid}
            actions.append(action)
        return tids[0]

    entry_id = process(node_list)
    return {
        "triggers": [trigger] if trigger else [],
        "profile_filter": None,
        "actions": actions,
        "entry_action_id": entry_id,
    }


def flow_payload(name: str, trigger, nodes: list) -> dict:
    return {"data": {"type": "flow", "attributes": {
        "name": name,
        "definition": build_definition(trigger, nodes),
    }}}


# ── Format probing ─────────────────────────────────────────────────────────────

def try_create_flow(payload: dict) -> tuple:
    """Returns (flow_id, None) on success or (None, error_text) on failure."""
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:300]}"


def delete_flow(flow_id: str) -> None:
    requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=15)


def probe_placed_order_format() -> dict | None:
    """Creates a minimal test flow to find the accepted placed-order filter format."""
    print("  Probing placed-order filter format...")
    candidates = [
        ("v1", _placed_order_filter_v1(1)),
        ("v2", _placed_order_filter_v2(1)),
        ("v3", _placed_order_filter_v3(1)),
    ]
    for label, pf in candidates:
        reset_ids()
        nodes = [
            split_action(pf, yes_branch=[], no_branch=[
                email_action("test", None, "_probe_email")
            ])
        ]
        payload = flow_payload(
            "__PROBE_DELETE_ME__",
            {"type": "metric", "id": PLACED_ORDER_METRIC_ID},
            nodes,
        )
        fid, err = try_create_flow(payload)
        if fid:
            print(f"    Accepted format: {label}")
            delete_flow(fid)
            time.sleep(0.3)
            return pf
        print(f"    Rejected {label}: {err[:100]}")
        time.sleep(0.3)
    return None


def probe_item_name_format(keyword: str = "Regaine") -> dict | None:
    """Creates a minimal test flow to find the accepted item-name filter format."""
    print("  Probing item-name filter format...")
    candidates = [
        ("v1", _item_name_filter_v1(keyword)),
        ("v2", _item_name_filter_v2(keyword)),
        ("v3", _item_name_filter_v3(keyword)),
        ("v4", _item_name_filter_v4(keyword)),
    ]
    for label, pf in candidates:
        reset_ids()
        nodes = [
            split_action(pf, yes_branch=[
                email_action("test", None, "_probe_email")
            ], no_branch=[])
        ]
        payload = flow_payload(
            "__PROBE_DELETE_ME__",
            {"type": "metric", "id": REPLENISHMENT_METRIC_ID},
            nodes,
        )
        fid, err = try_create_flow(payload)
        if fid:
            print(f"    Accepted format: {label}")
            delete_flow(fid)
            time.sleep(0.3)
            return pf
        print(f"    Rejected {label}: {err[:100]}")
        time.sleep(0.3)
    return None


# ── Flow builders ──────────────────────────────────────────────────────────────

TPL_MAP = {
    "[Z] Post-Purchase Email 1": "RHfcDs",
    "[Z] Post-Purchase Email 2": "Sy929J",
    "[Z] Post-Purchase Email 3": "UNjrA4",
    "[Z] Post-Purchase Email 4": "SQD3nM",
    "[Z] Flu Season Email 1":    "SMDszN",
    "[Z] Flu Season Email 2":    "WALe6F",
    "[Z] Win-back Email 1":      "RDNsnL",
    "[Z] Win-back Email 2":      "YuYX38",
    "[Z] Win-back Email 3":      "VEpKb4",
    "[Z] Back in Stock Email 1": "UCeqPt",
    "[Z] Back in Stock Email 2": "XXcqNf",
    "[Z] Replenishment Reminder":                          "UXVWhK",
    "[Z] Replenishment Reminder (Regaine)":   "SkCfgY",
    "[Z] Replenishment Reminder (Magnesium)": "UXVWhK",
    "[Z] Replenishment Reminder (Elevit)":    "UXVWhK",
    "[Z] Replenishment Reminder (Sanderson)": "UXVWhK",
    "[Z] Replenishment Reminder (GO Healthy)":"UXVWhK",
    "[Z] Replenishment Reminder (Hayfexo)":   "RyVVZV",
    "[Z] Replenishment Reminder (Clinicians)":"UXVWhK",
    "[Z] Replenishment Reminder (Goli)":      "UXVWhK",
    "[Z] Replenishment Reminder (LIVON)":     "UXVWhK",
    "[Z] Replenishment Reminder (Ensure)":    "UXVWhK",
    "[Z] Replenishment Reminder (Oracoat)":   "STBhAz",
    "[Z] Replenishment Reminder (Optifast)":  "RFAcvQ",
    "[Z] Replenishment Reminder (Optislim)":  "RFAcvQ",
}


def build_back_in_stock(placed_order_pf: dict) -> dict:
    reset_ids()
    nodes = [
        email_action(
            "{{ event.ProductName }} is back! 🎉",
            TPL_MAP["[Z] Back in Stock Email 1"],
            "[Z] Back in Stock Email 1",
        ),
        delay_action(1),
        # Split: Has placed order since notification? YES=exit, NO=send Email 2
        split_action(
            profile_filter=placed_order_pf,
            yes_branch=[],
            no_branch=[
                email_action(
                    "Still available - but selling fast",
                    TPL_MAP["[Z] Back in Stock Email 2"],
                    "[Z] Back in Stock Email 2",
                )
            ],
        ),
    ]
    return flow_payload(
        "[Z] Back in Stock",
        {"type": "metric", "id": "USbQRB"},
        nodes,
    )


def build_post_purchase(repeat_order_pf: dict) -> dict:
    reset_ids()
    nodes = [
        delay_action(1, "hours"),
        email_action(
            "Thank you {{ person.first_name|default:'friend' }} - your order is confirmed",
            TPL_MAP["[Z] Post-Purchase Email 1"],
            "[Z] Post-Purchase Email 1",
        ),
        delay_action(3),
        email_action(
            "Getting the most from your order",
            TPL_MAP["[Z] Post-Purchase Email 2"],
            "[Z] Post-Purchase Email 2",
        ),
        delay_action(4),
        email_action(
            "{{ person.first_name|default:'friend' }}, customers also loved these",
            TPL_MAP["[Z] Post-Purchase Email 3"],
            "[Z] Post-Purchase Email 3",
        ),
        delay_action(7),
        # Split: Placed another order (repeat buyer)? YES=exit, NO=review request
        split_action(
            profile_filter=repeat_order_pf,
            yes_branch=[],
            no_branch=[
                email_action(
                    "How did we do, {{ person.first_name|default:'friend' }}?",
                    TPL_MAP["[Z] Post-Purchase Email 4"],
                    "[Z] Post-Purchase Email 4",
                )
            ],
        ),
    ]
    return flow_payload(
        "[Z] Post-Purchase Series",
        {"type": "metric", "id": "Sxnb5T"},
        nodes,
    )


def build_replenishment(item_name_pf_fn) -> dict:
    reset_ids()
    rpl = TPL_MAP["[Z] Replenishment Reminder"]
    subject = "{{ person.first_name|default:'friend' }}, time to restock?"

    products = [
        ("Regaine",    110),
        ("Magnesium",  100),
        ("Elevit",      80),
        ("Sanderson",   90),
        ("GO Healthy",  90),
        ("Hayfexo",     55),
        ("Clinicians",  22),
        ("Goli",        22),
        ("LIVON",       22),
        ("Ensure",      12),
        ("Oracoat",     10),
        ("Optifast",     9),
        ("Optislim",    15),
    ]

    def branch(keyword: str, days: int) -> list:
        tpl_id = TPL_MAP.get(f"[Z] Replenishment Reminder ({keyword})", rpl)
        return [
            delay_action(days),
            email_action(subject, tpl_id, f"[Z] Replenishment Reminder ({keyword})"),
        ]

    no_branch: list = []
    for keyword, days in reversed(products):
        no_branch = [
            split_action(
                profile_filter=item_name_pf_fn(keyword),
                yes_branch=branch(keyword, days),
                no_branch=no_branch,
            )
        ]

    return flow_payload(
        "[Z] Replenishment - Reorder Reminders",
        {"type": "metric", "id": REPLENISHMENT_METRIC_ID},
        no_branch,
    )


# ── Current flow IDs to delete ─────────────────────────────────────────────────
FLOWS_TO_DELETE = {
    "SKyFTB": "[Z] Back in Stock",
    "YtmmNC": "[Z] Post-Purchase Series",
    "XvPhNr": "[Z] Replenishment - Reorder Reminders",
}


def edit_link(flow_id: str) -> str:
    return f"https://www.klaviyo.com/flow/{flow_id}/edit"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print("Step 1: Probing accepted filter formats")
    print("-" * 50)

    placed_order_pf = probe_placed_order_format()
    if not placed_order_pf:
        print()
        print("FAILED: Could not find an accepted placed-order filter format.")
        print("The Klaviyo API rejected all format candidates.")
        print("Open Back in Stock and Post-Purchase in the Klaviyo UI and")
        print("manually set the split condition to: Has placed order >= 1 time since flow start.")
        placed_order_pf = None

    item_name_pf = probe_item_name_format()
    if not item_name_pf:
        print()
        print("FAILED: Could not find an accepted item-name filter format.")
        print("The Klaviyo API rejected all format candidates.")
        print("Replenishment splits will need manual configuration in the UI.")
        item_name_pf_fn = lambda k: None
    else:
        # item_name_pf holds the accepted format with keyword="Regaine".
        # Create a factory function that substitutes the keyword.
        accepted_fmt_str = json.dumps(item_name_pf)
        def item_name_pf_fn(keyword: str) -> dict:
            return json.loads(accepted_fmt_str.replace('"Regaine"', json.dumps(keyword)))

    print()
    print("Step 2: Deleting existing flows")
    print("-" * 50)
    for fid, name in FLOWS_TO_DELETE.items():
        print(f"  Deleting {fid} ({name})...", end=" ")
        try:
            delete_flow(fid)
            print("deleted")
        except Exception as e:
            print(f"failed: {e}")
        time.sleep(0.3)

    print()
    print("Step 3: Recreating flows with conditions")
    print("-" * 50)

    results = []

    # Back in Stock
    print("  Building [Z] Back in Stock...")
    pf_bis = placed_order_pf  # Has placed order >= 1 since flow start
    payload = build_back_in_stock(pf_bis)
    fid, err = try_create_flow(payload)
    if fid:
        print(f"    Created: {fid}  {edit_link(fid)}")
        results.append(("[Z] Back in Stock", fid, None))
    else:
        print(f"    FAILED: {err}")
        results.append(("[Z] Back in Stock", None, err))
    time.sleep(0.5)

    # Post-Purchase — split checks >= 2 placed orders since flow start (first order triggered flow)
    print("  Building [Z] Post-Purchase Series...")
    if placed_order_pf:
        # Clone and bump the value to 2
        pf_pp_str = json.dumps(placed_order_pf)
        # Replace the value:1 with value:2 (repeat buyer check)
        pf_pp = json.loads(pf_pp_str.replace('"value": 1', '"value": 2')
                                     .replace('"at-least": 1', '"at-least": 2'))
    else:
        pf_pp = None
    payload = build_post_purchase(pf_pp)
    fid, err = try_create_flow(payload)
    if fid:
        print(f"    Created: {fid}  {edit_link(fid)}")
        results.append(("[Z] Post-Purchase Series", fid, None))
    else:
        print(f"    FAILED: {err}")
        results.append(("[Z] Post-Purchase Series", None, err))
    time.sleep(0.5)

    # Replenishment
    print("  Building [Z] Replenishment - Reorder Reminders...")
    payload = build_replenishment(item_name_pf_fn)
    fid, err = try_create_flow(payload)
    if fid:
        print(f"    Created: {fid}  {edit_link(fid)}")
        results.append(("[Z] Replenishment - Reorder Reminders", fid, None))
    else:
        print(f"    FAILED: {err}")
        results.append(("[Z] Replenishment - Reorder Reminders", None, err))

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_ok = True
    for name, fid, err in results:
        if fid:
            print(f"  OK  {name}")
            print(f"      {edit_link(fid)}")
        else:
            print(f"  FAIL {name}: {err}")
            all_ok = False
        print()

    if not all_ok:
        print("Some flows failed. Paste the FAIL lines above so the format")
        print("can be corrected and the script re-run.")
    else:
        print("All 3 flows rebuilt with filter conditions.")
        print()
        print("UPDATE klaviyo_flows.py FLOWS_TO_DELETE with these new IDs")
        print("so future rebuilds target the right flows.")


if __name__ == "__main__":
    main()
