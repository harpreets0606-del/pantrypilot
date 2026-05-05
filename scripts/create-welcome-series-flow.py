"""
Creates [Z] Welcome Series - No Coupon flow.

Trigger: Added to List -> SxBenU (Website Form Subscribe)
  Email 1 (immediate) -> 3 day delay -> Email 2 -> 4 day delay -> Email 3

Templates:
  TyrDbC  Welcome
  X7gq45  Price Beat
  VMcivM  Product Discovery

Usage:
    py scripts/create-welcome-series-flow.py
"""

import os, sys, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564")
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

LIST_ID = "SxBenU"  # Website Form Subscribe

TPL_WELCOME   = "TyrDbC"
TPL_PRICEBEST = "X7gq45"
TPL_DISCOVER  = "VMcivM"

_counter = 0

def new_id():
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0

def email_action(subject, template_id, name):
    return {
        "type": "send-email",
        "data": {
            "message": {
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
                "template_id": template_id,
            },
            "status": "draft",
        },
    }

def delay_action(value, unit="days"):
    data = {"unit": unit, "value": value, "secondary_value": None}
    if unit == "days":
        data["timezone"] = "profile"
        data["delay_until_weekdays"] = ALL_DAYS
    return {"type": "time-delay", "data": data}

def build_definition(trigger, node_list):
    actions = []

    def process(nodes):
        if not nodes:
            return None
        tids = [new_id() for _ in nodes]
        for i, (node, tid) in enumerate(zip(nodes, tids)):
            ntype = node["type"]
            action = {"temporary_id": tid, "type": ntype, "data": node["data"]}
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

def build_welcome_series():
    reset_ids()
    nodes = [
        email_action(
            "Welcome to Bargain Chemist, {{ first_name|default:'there' }}!",
            TPL_WELCOME,
            "[Z] Welcome - Email 1 - Welcome",
        ),
        delay_action(3),
        email_action(
            "We'll beat any pharmacy price — guaranteed",
            TPL_PRICEBEST,
            "[Z] Welcome - Email 2 - Price Beat",
        ),
        delay_action(4),
        email_action(
            "Explore everything at Bargain Chemist",
            TPL_DISCOVER,
            "[Z] Welcome - Email 3 - Product Discovery",
        ),
    ]
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "[Z] Welcome Series - No Coupon",
                "definition": build_definition(
                    {"type": "list", "id": LIST_ID},
                    nodes,
                ),
            },
        }
    }

def create_flow(payload):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:500]}"

def set_flow_live(flow_id):
    body = {"data": {"type": "flow", "id": flow_id, "attributes": {"status": "live"}}}
    headers = {**HEADERS, "Content-Type": "application/json"}
    r = requests.patch(f"{BASE_URL}/flows/{flow_id}/", headers=headers, json=body, timeout=15)
    return r.ok

def main():
    print("Welcome Series Flow Builder")
    print("-" * 50)
    print(f"Trigger: Added to List -> {LIST_ID} (Website Form Subscribe)")
    print()

    print("Building flow definition...")
    payload = build_welcome_series()
    action_count = len(payload["data"]["attributes"]["definition"]["actions"])
    print(f"  Definition built: {action_count} actions")
    print()

    print("Creating flow...")
    fid, err = create_flow(payload)
    if err:
        print(f"  FAILED: {err}")
        sys.exit(1)

    print(f"  Created: {fid}")

    print("Setting flow to live...")
    if set_flow_live(fid):
        print("  Flow is live")
    else:
        print("  Could not set live — set manually in Klaviyo UI")

    print()
    print("Flow structure:")
    print("  Email 1: Welcome (immediate)")
    print("  3-day delay")
    print("  Email 2: Price Beat Guarantee")
    print("  4-day delay")
    print("  Email 3: Product Discovery")
    print()
    print(f"Edit: https://www.klaviyo.com/flow/{fid}/edit")

if __name__ == "__main__":
    main()
