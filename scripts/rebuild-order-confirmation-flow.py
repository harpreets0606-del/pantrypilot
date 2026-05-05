"""
Rebuilds [Z] Order Confirmation flow.

Deletes the auto-generated flow (Smp9WN) whose messages can't be updated
via PATCH (405), then recreates with template QRdbLf which has a proper
6-category CTA grid to fix the 0.76% CTR.

Trigger: Placed Order (Sxnb5T)
Email:   Immediate — "Your order is confirmed" with browse CTA

Usage:
    py scripts/rebuild-order-confirmation-flow.py
"""

import os, sys, time, requests

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

OLD_FLOW_ID      = "Smp9WN"
PLACED_ORDER_ID  = "Sxnb5T"
TEMPLATE_ID      = "QRdbLf"   # [Z] Order Confirmation - v2 (with CTA)

_counter = 0

def new_id():
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0

def email_action(subject, preview, template_id, name):
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
                "preview_text": preview,
                "smart_sending_enabled": False,   # order confirmation = transactional
                "transactional": True,
                "add_tracking_params": True,
                "custom_tracking_params": None,
                "additional_filters": None,
                "name": name,
                "template_id": template_id,
            },
            "status": "draft",
        },
    }

def build_definition(trigger, node_list):
    actions = []

    def process(nodes):
        if not nodes:
            return None
        tids = [new_id() for _ in nodes]
        for i, (node, tid) in enumerate(zip(nodes, tids)):
            ntype  = node["type"]
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

def build_order_confirmation():
    reset_ids()
    nodes = [
        email_action(
            subject="Your Bargain Chemist order #{{ event.OrderId }} is confirmed!",
            preview="We are packing it now - here is everything you need to know.",
            template_id=TEMPLATE_ID,
            name="[Z] Order Confirmation - Email 1",
        ),
    ]
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "[Z] Order Confirmation",
                "definition": build_definition(
                    {"type": "metric", "id": PLACED_ORDER_ID},
                    nodes,
                ),
            },
        }
    }

def delete_flow(flow_id):
    r = requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        print(f"  Warning: delete returned {r.status_code}: {r.text[:200]}")

def create_flow(payload):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:500]}"

def set_flow_live(flow_id):
    body = {"data": {"type": "flow", "id": flow_id, "attributes": {"status": "live"}}}
    r = requests.patch(f"{BASE_URL}/flows/{flow_id}/", headers=HEADERS, json=body, timeout=15)
    return r.ok

def main():
    print("Order Confirmation Flow Rebuild")
    print("-" * 50)
    print(f"Trigger: Placed Order ({PLACED_ORDER_ID})")
    print(f"Template: {TEMPLATE_ID} (6-category CTA grid)")
    print()

    print("Building flow definition...")
    payload = build_order_confirmation()
    action_count = len(payload["data"]["attributes"]["definition"]["actions"])
    print(f"  Definition built: {action_count} action(s)")
    print()

    print(f"Deleting existing flow {OLD_FLOW_ID}...")
    delete_flow(OLD_FLOW_ID)
    print("  Deleted")
    time.sleep(1)

    print("Creating new flow...")
    fid, err = create_flow(payload)
    if err:
        print(f"  FAILED: {err}")
        sys.exit(1)
    print(f"  Created: {fid}")

    print("Setting flow to live...")
    if set_flow_live(fid):
        print("  Flow is live")
    else:
        print("  Could not set live - set manually in Klaviyo UI")

    print()
    print("Flow structure:")
    print("  Trigger: Placed Order (immediate)")
    print("  Email: Order confirmed + 6-category browse CTA")
    print()
    print(f"Edit: https://www.klaviyo.com/flow/{fid}/edit")

if __name__ == "__main__":
    main()
