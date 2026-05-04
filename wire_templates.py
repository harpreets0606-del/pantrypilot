"""
Wire [Z] email templates to their matching Klaviyo flow messages.

Flow message structure (2024-10-15.pre):
  attributes.name            -- human-readable message name
  attributes.content.*       -- subject, from_email, etc.
  relationships.template.data.id  -- currently assigned template (or null)

Template assignment is done via the JSON:API relationship endpoint:
  PATCH /api/flow-messages/{id}/relationships/template

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py wire_templates.py            # dry run
    py wire_templates.py --apply    # apply changes
"""

import os, sys, time
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

# -- Template mapping: flow message name -> template ID -----------------------
#
# Message names come from the `name` param passed to email_action() in
# klaviyo_flows.py for flows we created, and from Klaviyo's auto-naming
# for pre-existing flows (Browse Abandonment, Welcome Series).

MESSAGE_TEMPLATE_MAP = {
    # Post-Purchase Series (YtmmNC) - names set in klaviyo_flows.py
    "[Z] Post-Purchase Email 1": "RHfcDs",
    "[Z] Post-Purchase Email 2": "Sy929J",
    "[Z] Post-Purchase Email 3": "UNjrA4",
    "[Z] Post-Purchase Email 4": "SQD3nM",

    # Flu Season (U6e3uf) - names set in klaviyo_flows.py
    "[Z] Flu Season Email 1":    "SMDszN",
    "[Z] Flu Season Email 2":    "WALe6F",

    # Win-Back (YdtALs) - names set in klaviyo_flows.py
    "[Z] Win-back Email 1":      "RDNsnL",
    "[Z] Win-back Email 2":      "YuYX38",
    "[Z] Win-back Email 3":      "VEpKb4",
    "[Z] Win-back Email 4":      "VqvY8S",

    # Back in Stock (SKyFTB) - names set in klaviyo_flows.py
    "[Z] Back in Stock Email 1": "UCeqPt",
    "[Z] Back in Stock Email 2": "XXcqNf",

    # Replenishment (XvPhNr) - names set in klaviyo_flows.py
    "[Z] Replenishment Reminder (Regaine)":    "SkCfgY",
    "[Z] Replenishment Reminder (Magnesium)":  "UXVWhK",
    "[Z] Replenishment Reminder (Elevit)":     "UXVWhK",
    "[Z] Replenishment Reminder (Sanderson)":  "UXVWhK",
    "[Z] Replenishment Reminder (GO Healthy)": "UXVWhK",
    "[Z] Replenishment Reminder (Hayfexo)":    "RyVVZV",
    "[Z] Replenishment Reminder (Clinicians)": "UXVWhK",
    "[Z] Replenishment Reminder (Goli)":       "UXVWhK",
    "[Z] Replenishment Reminder (LIVON)":      "UXVWhK",
    "[Z] Replenishment Reminder (Ensure)":     "UXVWhK",
    "[Z] Replenishment Reminder (Oracoat)":    "STBhAz",
    "[Z] Replenishment Reminder (Optifast)":   "RFAcvQ",
    "[Z] Replenishment Reminder (Optislim)":   "RFAcvQ",

    # Browse Abandonment (RtiVC5) - Klaviyo auto-names
    # Email 1 already has its own template; Email 2 is our [Z] one
    "[Z] Browse Abandonment: Email #2":        "QZmDDY",

    # Welcome Series (SehWRt) - Klaviyo auto-names
    # Emails 1-3 are pre-existing; we only have [Z] templates for 4 and 5
    "Welcome Series, Email #4":                "SnDfrv",
    "Welcome Series, Email #5":                "UZWWsg",
}

# Exact flow names to process
Z_FLOW_NAMES = {
    "[Z] Post-Purchase Series",
    "[Z] Flu Season - Winter Wellness",
    "[Z] Win-back - Lapsed Customers",
    "[Z] Back in Stock",
    "[Z] Browse Abandonment",
    "[Z] Welcome Series - Website",
    "[Z] Replenishment - Reorder Reminders",
}


# -- API helpers ---------------------------------------------------------------

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


def get_send_email_actions(flow_id):
    """Returns IDs of all SEND_EMAIL actions in a flow."""
    actions, url = [], f"{BASE_URL}/flows/{flow_id}/flow-actions"
    while url:
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        data = r.json()
        for a in data.get("data", []):
            if a.get("attributes", {}).get("action_type") == "SEND_EMAIL":
                actions.append(a["id"])
        url = data.get("links", {}).get("next")
        time.sleep(0.1)
    return actions


def get_flow_message(action_id):
    """Returns the flow-message for a SEND_EMAIL action."""
    r = requests.get(f"{BASE_URL}/flow-actions/{action_id}/flow-messages",
                     headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json().get("data", [])
    if not data:
        return None
    m = data[0]
    attrs = m.get("attributes", {})
    template_rel = m.get("relationships", {}).get("template", {}).get("data")
    return {
        "id": m["id"],
        "name": attrs.get("name", ""),
        "current_template_id": template_rel["id"] if template_rel else None,
    }


def assign_template(msg_id, template_id):
    """Assigns a template to a flow-message.
    Klaviyo uses a dedicated action endpoint (same pattern as campaign-message-assign-template).
    Falls back to PATCH on main resource with relationships if action endpoint fails.
    """
    # Strategy 1: POST to flow-message-assign-template action endpoint
    payload = {
        "data": {
            "type": "flow-message-assign-template",
            "relationships": {
                "flow-message": {"data": {"type": "flow-message", "id": msg_id}},
                "template":     {"data": {"type": "template",      "id": template_id}},
            },
        }
    }
    r = requests.post(f"{BASE_URL}/flow-message-assign-template/",
                      headers=HEADERS, json=payload, timeout=30)
    if r.ok or r.status_code == 204:
        return

    # Strategy 2: PATCH main resource with relationships
    payload2 = {
        "data": {
            "type": "flow-message",
            "id": msg_id,
            "relationships": {
                "template": {"data": {"type": "template", "id": template_id}}
            },
        }
    }
    r2 = requests.patch(f"{BASE_URL}/flow-messages/{msg_id}",
                        headers=HEADERS, json=payload2, timeout=30)
    if r2.ok or r2.status_code == 204:
        return

    # Strategy 3: PUT on relationship endpoint
    payload3 = {"data": {"type": "template", "id": template_id}}
    r3 = requests.put(f"{BASE_URL}/flow-messages/{msg_id}/relationships/template",
                      headers=HEADERS, json=payload3, timeout=30)
    if r3.ok or r3.status_code == 204:
        return

    raise RuntimeError(
        f"All strategies failed.\n"
        f"  S1 ({r.status_code}): {r.text[:200]}\n"
        f"  S2 ({r2.status_code}): {r2.text[:200]}\n"
        f"  S3 ({r3.status_code}): {r3.text[:200]}"
    )


# -- Main ----------------------------------------------------------------------

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var."); sys.exit(1)

    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"Template wiring ({mode})\n")

    flows = get_z_flows()
    print(f"Found {len(flows)} [Z] flows.\n")

    updates   = []  # (flow_name, msg_name, msg_id, new_tpl_id)
    no_map    = []  # message names with no mapping
    already   = []  # already correct

    for flow in flows:
        print(f"-- {flow['name']}  [{flow['id']}]  ({flow['status']})")
        try:
            action_ids = get_send_email_actions(flow["id"])
        except Exception as e:
            print(f"   FAILED to fetch actions: {e}\n")
            continue

        if not action_ids:
            print(f"   (no SEND_EMAIL actions)\n")
            continue

        for action_id in action_ids:
            msg = get_flow_message(action_id)
            if not msg:
                print(f"   ! action {action_id} has no flow-message")
                continue

            mname    = msg["name"]
            cur_tpl  = msg["current_template_id"]
            new_tpl  = MESSAGE_TEMPLATE_MAP.get(mname)

            if not new_tpl:
                no_map.append(f"{flow['name']} / {mname!r}")
                print(f"   ? {mname!r}")
                continue

            if cur_tpl == new_tpl:
                already.append(mname)
                print(f"   OK {mname!r}  (already {new_tpl})")
            else:
                tag = "WILL SET" if not APPLY else "SETTING"
                print(f"   -> {mname!r}  [{tag}]  {cur_tpl} -> {new_tpl}")
                updates.append((flow["name"], mname, msg["id"], new_tpl))

            time.sleep(0.1)

        print()

    print(f"{len(updates)} to update, {len(already)} already correct, {len(no_map)} unmapped.\n")

    if no_map:
        print(f"Unmapped messages ({len(no_map)}) -- add to MESSAGE_TEMPLATE_MAP if needed:")
        for s in no_map:
            print(f"  {s}")
        print()

    if not APPLY:
        print("Run with --apply to apply changes.")
        return

    print("Applying...")
    ok = fail = 0
    for flow_name, mname, msg_id, tpl_id in updates:
        print(f"  {mname!r}  ({msg_id})...", end=" ")
        try:
            assign_template(msg_id, tpl_id)
            print("OK")
            ok += 1
        except Exception as e:
            print(f"FAIL  {e}")
            fail += 1
        time.sleep(0.3)

    print(f"\nDone. {ok} updated, {fail} failed.")


if __name__ == "__main__":
    main()
