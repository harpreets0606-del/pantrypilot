"""
Account hygiene + fixes script.

Actions:
  1. Delete duplicate Welcome Series flow XGCsx6 (TsC8GZ is the correct one)
  2. Delete 3 unconfigured draft "Essential Flow Recommendation_" flows
  3. Inspect [Z] Post-Purchase Series (RDJQYM) and [Z] Back in Stock (Ysj7sg)
     to understand why they have 0 recipients
  4. Fix [Z] Order Confirmation (Smp9WN): swap template to QRdbLf
     which adds a 6-category CTA grid (was 0.76% CTR, needs click targets)

Usage:
    py scripts/fix-account-hygiene.py
"""

import os, sys, time, json, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ── Flows to delete ────────────────────────────────────────────────────────────
FLOWS_TO_DELETE = [
    ("XGCsx6", "[Z] Welcome Series - No Coupon (DUPLICATE — TsC8GZ is correct)"),
    ("QVtRFG", "Essential Flow Recommendation_ (unconfigured draft)"),
    ("RtRDWV", "Essential Flow Recommendation_ (unconfigured draft)"),
    ("RtTfhE", "Essential Flow Recommendation_ (unconfigured draft)"),
]

# ── Flows to inspect ───────────────────────────────────────────────────────────
FLOWS_TO_INSPECT = [
    ("RDJQYM", "[Z] Post-Purchase Series"),
    ("Ysj7sg", "[Z] Back in Stock"),
]

# ── Order Confirmation fix ─────────────────────────────────────────────────────
ORDER_CONF_FLOW_ID = "Smp9WN"
ORDER_CONF_MSG_ID  = "XJENuf"          # "[Z] Post-Purchase Email 1"
NEW_TEMPLATE_ID    = "QRdbLf"          # [Z] Order Confirmation - v2 (with CTA)
ORDER_CONF_SUBJECT = "Your Bargain Chemist order #{{ event.OrderId }} is confirmed!"
ORDER_CONF_PREVIEW = "We're packing it now — here's everything you need to know."


def kget(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=15)
    return r


def kdelete(path):
    r = requests.delete(f"{BASE_URL}{path}", headers=HEADERS, timeout=15)
    return r


def kpatch(path, body):
    r = requests.patch(f"{BASE_URL}{path}", headers=HEADERS, json=body, timeout=15)
    return r


# ── Step 1: Delete flows ───────────────────────────────────────────────────────
def delete_flows():
    print("Step 1: Deleting unwanted flows")
    print("-" * 50)
    for flow_id, label in FLOWS_TO_DELETE:
        print(f"  Deleting {flow_id} — {label}")
        r = kdelete(f"/flows/{flow_id}")
        if r.ok or r.status_code == 404:
            print(f"  ✓ Done ({r.status_code})")
        else:
            print(f"  ✗ Failed: {r.status_code} {r.text[:200]}")
        time.sleep(0.5)
    print()


# ── Step 2: Inspect zero-recipient flows ──────────────────────────────────────
def inspect_flows():
    print("Step 2: Inspecting zero-recipient flows")
    print("-" * 50)
    for flow_id, name in FLOWS_TO_INSPECT:
        print(f"\n  {name} ({flow_id})")
        r = kget(f"/flows/{flow_id}/flow-actions/", {"page[size]": 50})
        if not r.ok:
            print(f"  ✗ Could not fetch actions: {r.status_code} {r.text[:100]}")
            continue
        actions = r.json().get("data", [])
        print(f"  Actions: {len(actions)}")
        for a in actions:
            atype = a["attributes"]["action_type"]
            aid   = a["id"]
            print(f"    [{atype}] id={aid}")
            settings = a["attributes"].get("settings", {})
            if atype in ("TIME_DELAY", "CONDITIONAL_SPLIT", "TRIGGER_SPLIT"):
                print(f"      settings: {json.dumps(settings, separators=(',',':'))[:200]}")
            if atype == "SEND_EMAIL":
                r2 = kget(f"/flow-actions/{aid}/flow-messages/")
                if r2.ok:
                    for m in r2.json().get("data", []):
                        mstatus = m["attributes"].get("status", "?")
                        mname   = m["attributes"].get("name", "?")
                        defn    = m["attributes"].get("definition", {})
                        subject = defn.get("content", {}).get("subject", "?") if defn else "?"
                        print(f"      msg={m['id']} | {mstatus} | {mname}")
                        print(f"      subject: {subject}")
    print()


# ── Step 3: Fix Order Confirmation template ────────────────────────────────────
def fix_order_confirmation():
    print("Step 3: Fixing Order Confirmation template")
    print("-" * 50)

    # 3a. Pause the flow so messages become editable
    print("  Pausing flow Smp9WN...")
    r = kpatch(f"/flows/{ORDER_CONF_FLOW_ID}/", {
        "data": {"type": "flow", "id": ORDER_CONF_FLOW_ID,
                 "attributes": {"status": "manual"}}
    })
    if not r.ok:
        print(f"  ✗ Could not pause flow: {r.status_code} {r.text[:200]}")
        return False
    print("  ✓ Flow paused")
    time.sleep(1)

    # 3b. Set message to draft
    print(f"  Setting message {ORDER_CONF_MSG_ID} to draft...")
    r = kpatch(f"/flow-messages/{ORDER_CONF_MSG_ID}/", {
        "data": {"type": "flow-message", "id": ORDER_CONF_MSG_ID,
                 "attributes": {"status": "draft"}}
    })
    if not r.ok:
        print(f"  ✗ Could not set to draft: {r.status_code} {r.text[:200]}")
        # Try to re-enable flow before returning
        kpatch(f"/flows/{ORDER_CONF_FLOW_ID}/", {
            "data": {"type": "flow", "id": ORDER_CONF_FLOW_ID,
                     "attributes": {"status": "live"}}
        })
        return False
    print("  ✓ Message is draft")
    time.sleep(0.5)

    # 3c. Update template + subject + preview
    print(f"  Assigning template {NEW_TEMPLATE_ID} and updating subject...")
    update_body = {
        "data": {
            "type": "flow-message",
            "id": ORDER_CONF_MSG_ID,
            "attributes": {
                "definition": {
                    "channel": "email",
                    "content": {
                        "subject":      ORDER_CONF_SUBJECT,
                        "preview_text": ORDER_CONF_PREVIEW,
                    }
                }
            },
            "relationships": {
                "template": {"data": {"type": "template", "id": NEW_TEMPLATE_ID}}
            }
        }
    }
    r = kpatch(f"/flow-messages/{ORDER_CONF_MSG_ID}/", update_body)
    if not r.ok:
        print(f"  ✗ Template update failed: {r.status_code} {r.text[:300]}")
        kpatch(f"/flows/{ORDER_CONF_FLOW_ID}/", {
            "data": {"type": "flow", "id": ORDER_CONF_FLOW_ID,
                     "attributes": {"status": "live"}}
        })
        return False
    print("  ✓ Template and subject updated")
    time.sleep(0.5)

    # 3d. Set message back to live
    print("  Setting message back to live...")
    r = kpatch(f"/flow-messages/{ORDER_CONF_MSG_ID}/", {
        "data": {"type": "flow-message", "id": ORDER_CONF_MSG_ID,
                 "attributes": {"status": "live"}}
    })
    if not r.ok:
        print(f"  ✗ Could not set live: {r.status_code} {r.text[:200]}")
    else:
        print("  ✓ Message is live")
    time.sleep(0.5)

    # 3e. Resume flow
    print("  Resuming flow...")
    r = kpatch(f"/flows/{ORDER_CONF_FLOW_ID}/", {
        "data": {"type": "flow", "id": ORDER_CONF_FLOW_ID,
                 "attributes": {"status": "live"}}
    })
    if r.ok:
        print("  ✓ Flow is live")
    else:
        print(f"  ✗ Could not resume: {r.status_code} — resume manually in Klaviyo UI")

    return True


def main():
    print("Bargain Chemist — Account Hygiene & Flow Fixes")
    print("=" * 55)
    print()

    delete_flows()
    inspect_flows()
    fix_order_confirmation()

    print()
    print("=" * 55)
    print("Done.")
    print()
    print("After running, check in Klaviyo UI:")
    print("  Flows list: XGCsx6 + 3 Essential drafts should be gone")
    print("  Order Confirmation: new template QRdbLf, 6 CTA categories")
    print("  Post-Purchase (RDJQYM) + Back in Stock (Ysj7sg): review")
    print("  output above to understand their trigger configuration")
    print()
    print("Edit flows:")
    print("  Order Confirmation: https://www.klaviyo.com/flow/Smp9WN/edit")
    print("  Post-Purchase:      https://www.klaviyo.com/flow/RDJQYM/edit")
    print("  Back in Stock:      https://www.klaviyo.com/flow/Ysj7sg/edit")


if __name__ == "__main__":
    main()
