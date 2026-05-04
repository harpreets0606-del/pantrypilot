"""
Wire [Z] email templates to their matching flow action steps.

For each [Z] flow, fetches all email send actions, finds their
flow-message IDs, then PATCHes the template_id onto each message.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py wire_templates.py            # dry run — shows what would change
    py wire_templates.py --apply    # applies all template assignments
"""

import os, sys, re, time
import requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

APPLY = "--apply" in sys.argv

# ── Template mapping: flow action name → template ID ─────────────────────────
#
# Action names come from the `name` field in email_action() in klaviyo_flows.py
# Replenishment uses "Vitamins and Supplements" as the generic fallback for
# products without their own dedicated template.

ACTION_TEMPLATE_MAP = {
    # Post-Purchase Series (X3N28f)
    "[Z] Post-Purchase Email 1": "RHfcDs",
    "[Z] Post-Purchase Email 2": "Sy929J",
    "[Z] Post-Purchase Email 3": "UNjrA4",
    "[Z] Post-Purchase Email 4": "SQD3nM",

    # Flu Season (U9Di23)
    "[Z] Flu Season Email 1":    "SMDszN",
    "[Z] Flu Season Email 2":    "WALe6F",

    # Win-Back (YwLCkq)
    "[Z] Win-back Email 1":      "RDNsnL",
    "[Z] Win-back Email 2":      "YuYX38",
    "[Z] Win-back Email 3":      "VEpKb4",
    "[Z] Win-back Email 4":      "VqvY8S",

    # Back in Stock (WvqdR2)
    "[Z] Back in Stock Email 1": "UCeqPt",
    "[Z] Back in Stock Email 2": "XXcqNf",

    # Browse Abandonment (RtiVC5) — Email 2 only (Email 1 has no [Z] template)
    "[Z] Browse Abandonment Email 2": "QZmDDY",

    # Welcome Series (SehWRt) — Emails 4 & 5 only (1–3 have no [Z] templates)
    "[Z] Welcome Series Email 4":     "SnDfrv",
    "[Z] Welcome Series Email 5":     "UZWWsg",

    # Replenishment (V3RBGv) — product-specific
    "[Z] Replenishment Reminder (Regaine)":    "SkCfgY",
    "[Z] Replenishment Reminder (Magnesium)":  "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (Elevit)":     "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (Sanderson)":  "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (GO Healthy)": "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (Hayfexo)":    "RyVVZV",
    "[Z] Replenishment Reminder (Clinicians)": "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (Goli)":       "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (LIVON)":      "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (Ensure)":     "UXVWhK",   # generic vitamins
    "[Z] Replenishment Reminder (Oracoat)":    "STBhAz",
    "[Z] Replenishment Reminder (Optifast)":   "RFAcvQ",
    "[Z] Replenishment Reminder (Optislim)":   "RFAcvQ",   # weight mgmt fallback
}

# Exact flow names to process (excludes Triple Pixel variants)
Z_FLOW_NAMES = {
    "[Z] Post-Purchase Series",
    "[Z] Flu Season - Winter Wellness",
    "[Z] Win-back - Lapsed Customers",
    "[Z] Back in Stock",
    "[Z] Browse Abandonment",
    "[Z] Welcome Series - Website",
    "[Z] Replenishment - Reorder Reminders",
}


# ── API helpers ───────────────────────────────────────────────────────────────

def get_z_flows():
    flows, url = [], f"{BASE_URL}/flows"
    params = {"fields[flow]": "name,status", "page[size]": 50}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        for f in data.get("data", []):
            if f["attributes"]["name"] in Z_FLOW_NAMES:
                flows.append({"id": f["id"], "name": f["attributes"]["name"],
                               "status": f["attributes"]["status"]})
        url, params = data.get("links", {}).get("next"), {}
        time.sleep(0.1)
    return flows


def get_flow_actions(flow_id):
    """Returns all actions in a flow. No query params — the sub-resource
    endpoint rejects fields/page parameters in this API revision."""
    actions, url = [], f"{BASE_URL}/flows/{flow_id}/flow-actions"
    while url:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        for a in data.get("data", []):
            attrs = a.get("attributes", {})
            # DEBUG: print full action on first pass to reveal structure
            if not actions:
                import json as _json
                print("  DEBUG action keys:", list(attrs.keys()))
                print("  DEBUG sample:", _json.dumps(a, indent=2)[:600])
            actions.append({"id": a["id"], "name": attrs.get("name", ""), "_attrs": attrs})
        url = data.get("links", {}).get("next")
        time.sleep(0.1)
    return actions


def get_flow_messages(action_id):
    """Returns list of flow-message dicts with id and current definition."""
    msgs, url = [], f"{BASE_URL}/flow-actions/{action_id}/flow-messages"
    while url:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        for m in data.get("data", []):
            attrs = m.get("attributes", {})
            msgs.append({
                "id": m["id"],
                "channel": attrs.get("channel"),
                "definition": attrs.get("definition", {}),
            })
        url = data.get("links", {}).get("next")
        time.sleep(0.1)
    return msgs


def patch_message_template(msg_id, definition, new_template_id):
    """PATCH a flow-message to update its template_id."""
    updated_def = {**definition, "template_id": new_template_id}
    payload = {
        "data": {
            "type": "flow-message",
            "id": msg_id,
            "attributes": {"definition": updated_def},
        }
    }
    r = requests.patch(f"{BASE_URL}/flow-messages/{msg_id}",
                       headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var."); sys.exit(1)

    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"Template wiring ({mode})\n")

    flows = get_z_flows()
    print(f"Found {len(flows)} [Z] flows.\n")

    updates = []  # [(flow_name, action_name, msg_id, definition, new_tpl_id)]
    skipped = []  # action names not in our map

    for flow in flows:
        print(f"── {flow['name']}  [{flow['id']}]  ({flow['status']})")
        try:
            actions = get_flow_actions(flow["id"])
        except Exception as e:
            print(f"   ✗ Could not fetch actions: {e}\n")
            continue

        for action in actions:
            aname = action["name"]
            tpl_id = ACTION_TEMPLATE_MAP.get(aname)

            if not tpl_id:
                skipped.append(f"{flow['name']} / {aname}")
                print(f"   ? {aname}  (no mapping — skip)")
                continue

            msgs = get_flow_messages(action["id"])
            if not msgs:
                print(f"   ! {aname}  (no flow-messages found)")
                continue

            # There's typically one message per email action
            msg = msgs[0]
            current_tpl = msg["definition"].get("template_id", "(none)")

            if current_tpl == tpl_id:
                print(f"   ✓ {aname}  →  already {tpl_id}")
            else:
                status = "WILL SET" if not APPLY else "SETTING"
                print(f"   → {aname}  [{status}]  {current_tpl} → {tpl_id}")
                updates.append((flow["name"], aname, msg["id"], msg["definition"], tpl_id))

        print()
        time.sleep(0.1)

    print(f"{len(updates)} message(s) to update.")

    if skipped:
        print(f"\nActions with no template mapping ({len(skipped)}):")
        for s in skipped:
            print(f"  • {s}")

    if not APPLY:
        print("\nRun with --apply to apply all changes.")
        return

    print("\nApplying…")
    ok, fail = 0, 0
    for flow_name, action_name, msg_id, definition, tpl_id in updates:
        print(f"  {msg_id}  {action_name}…", end=" ")
        try:
            patch_message_template(msg_id, definition, tpl_id)
            print("✓")
            ok += 1
        except Exception as e:
            print(f"✗ {e}")
            fail += 1
        time.sleep(0.3)

    print(f"\nDone. {ok} updated, {fail} failed.")


if __name__ == "__main__":
    main()
