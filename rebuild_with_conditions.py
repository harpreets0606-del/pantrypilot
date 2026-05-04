"""
Rebuilds Back in Stock, Post-Purchase, and Replenishment flows with
fully configured conditional-split filter conditions.

Condition format discovered from existing [Z] Cart Abandonment and
[Z] Welcome Series flows in the account (type: "profile-metric").

Split conditions:
  Back in Stock  -- Has placed Placed Order >= 1 time since flow start
                    YES (bought) -> exit  |  NO (hasn't bought) -> Email 2

  Post-Purchase  -- Has placed Placed Order >= 2 times since flow start
                    (first order triggered the flow; second = repeat buyer)
                    YES (repeat buyer) -> exit  |  NO -> Email 4 (review)

  Replenishment  -- Has placed trigger metric with Item Names containing
                    <keyword> >= 1 time since flow start
                    YES (this product) -> product delay + email
                    NO -> next product split

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

PLACED_ORDER_METRIC_ID  = "Sxnb5T"
REPLENISHMENT_METRIC_ID = "UWP7cZ"


# ── Filter builders (confirmed format from existing account flows) ─────────────

def placed_order_filter(min_count: int) -> dict:
    """Has placed Placed Order >= min_count times since flow start."""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "profile-metric",
                "metric_id": PLACED_ORDER_METRIC_ID,
                "measurement": "count",
                "measurement_filter": {
                    "type": "numeric",
                    "operator": "greater-than",
                    "value": min_count - 1,  # >0 means >=1; >1 means >=2
                },
                "timeframe_filter": {
                    "type": "date",
                    "operator": "flow-start",
                },
                "metric_filters": None,
            }]
        }]
    }


def replenishment_filter(keyword: str) -> dict:
    """Has placed trigger metric with Item Names containing keyword since flow start."""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "profile-metric",
                "metric_id": REPLENISHMENT_METRIC_ID,
                "measurement": "count",
                "measurement_filter": {
                    "type": "numeric",
                    "operator": "greater-than",
                    "value": 0,
                },
                "timeframe_filter": {
                    "type": "date",
                    "operator": "flow-start",
                },
                "metric_filters": [{
                    "property": "Item Names",
                    "filter": {
                        "type": "string",
                        "operator": "contains",
                        "value": keyword,
                    },
                }],
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


# ── Template map ───────────────────────────────────────────────────────────────

TPL_MAP = {
    "[Z] Post-Purchase Email 1": "RHfcDs",
    "[Z] Post-Purchase Email 2": "Sy929J",
    "[Z] Post-Purchase Email 3": "UNjrA4",
    "[Z] Post-Purchase Email 4": "SQD3nM",
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


# ── Flow builders ──────────────────────────────────────────────────────────────

def build_back_in_stock() -> dict:
    reset_ids()
    nodes = [
        email_action(
            "{{ event.ProductName }} is back! \U0001f389",
            TPL_MAP["[Z] Back in Stock Email 1"],
            "[Z] Back in Stock Email 1",
        ),
        delay_action(1),
        split_action(
            # YES: has placed order since notification -> exit (they bought)
            # NO:  hasn't ordered yet -> send Email 2
            profile_filter=placed_order_filter(1),
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


def build_post_purchase() -> dict:
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
        split_action(
            # YES: placed 2+ orders since flow start (repeat buyer) -> exit
            # NO:  only original order -> send Email 4 (review request)
            profile_filter=placed_order_filter(2),
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
        {"type": "metric", "id": PLACED_ORDER_METRIC_ID},
        nodes,
    )


def build_replenishment() -> dict:
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
                # YES: this order contained the keyword -> use product-specific delay
                # NO:  try next product keyword
                profile_filter=replenishment_filter(keyword),
                yes_branch=branch(keyword, days),
                no_branch=no_branch,
            )
        ]

    return flow_payload(
        "[Z] Replenishment - Reorder Reminders",
        {"type": "metric", "id": REPLENISHMENT_METRIC_ID},
        no_branch,
    )


# ── API helpers ────────────────────────────────────────────────────────────────

def create_flow(payload: dict) -> tuple:
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:500]}"


def delete_flow(flow_id: str) -> None:
    r = requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        print(f"    Warning: delete {flow_id} returned {r.status_code}")


def edit_link(flow_id: str) -> str:
    return f"https://www.klaviyo.com/flow/{flow_id}/edit"


# ── Current flow IDs to delete ─────────────────────────────────────────────────
FLOWS_TO_DELETE = {
    "UqpyKS": "[Z] Back in Stock",
    "Vvb9ik": "[Z] Post-Purchase Series",
    "XKmyJE": "[Z] Replenishment - Reorder Reminders",
}


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print("Deleting existing flows")
    print("-" * 50)
    for fid, name in FLOWS_TO_DELETE.items():
        print(f"  Deleting {fid} ({name})...", end=" ")
        delete_flow(fid)
        print("done")
        time.sleep(0.3)

    print()
    print("Recreating flows with conditions")
    print("-" * 50)

    results = []
    for label, builder in [
        ("[Z] Back in Stock",              build_back_in_stock),
        ("[Z] Post-Purchase Series",       build_post_purchase),
        ("[Z] Replenishment",              build_replenishment),
    ]:
        print(f"  Building {label}...")
        payload = builder()
        fid, err = create_flow(payload)
        if fid:
            print(f"    Created: {fid}  {edit_link(fid)}")
            results.append((label, fid, None))
        else:
            print(f"    FAILED: {err}")
            results.append((label, None, err))
        time.sleep(0.5)

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, fid, err in results:
        if fid:
            print(f"  OK  {name}")
            print(f"      {edit_link(fid)}")
        else:
            print(f"  FAIL {name}: {err}")
        print()

    ok_ids = {name: fid for name, fid, err in results if fid}
    if len(ok_ids) == 3:
        print("All 3 flows rebuilt with filter conditions.")
        print()
        print("Update FLOWS_TO_DELETE in this script with the new IDs above")
        print("if you need to run it again.")
    else:
        print("Some flows failed - check the error above.")


if __name__ == "__main__":
    main()
