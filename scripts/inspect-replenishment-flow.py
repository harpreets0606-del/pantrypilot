"""
Inspects the Replenishment flow (V4cZMd) — shows all actions, delays,
email messages, subject lines and templates so we can verify which
products are covered and what's missing (Regaine, Blis, etc.)

Usage:
    py scripts/inspect-replenishment-flow.py
"""

import os, json, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564")
REVISION = "2024-10-15"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Accept": "application/vnd.api+json",
}

FLOW_ID = "V4cZMd"


def kget(path, params=None):
    r = requests.get(f"{BASE_URL}{path}", headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    # 1. Flow overview
    flow = kget(f"/flows/{FLOW_ID}/")
    attrs = flow["data"]["attributes"]
    print(f"Flow: {attrs['name']}")
    print(f"Status: {attrs['status']}")
    print(f"Trigger: {attrs.get('triggerType', '?')}")
    print(f"Created: {attrs['created'][:10]}")
    print()

    # 2. All actions
    actions = kget(f"/flows/{FLOW_ID}/flow-actions/", {"page[size]": 50})
    data = actions.get("data", [])
    print(f"Actions ({len(data)} total):")
    print("-" * 60)

    for a in data:
        atype    = a["attributes"]["action_type"]
        aid      = a["id"]
        settings = a["attributes"].get("settings", {})

        if atype == "TIME_DELAY":
            delay = settings.get("delay", {})
            val   = delay.get("value", "?")
            unit  = delay.get("unit", "?")
            print(f"  [{atype}] {val} {unit}  (id={aid})")

        elif atype == "SEND_EMAIL":
            print(f"  [{atype}] id={aid}")
            msgs = kget(f"/flow-actions/{aid}/flow-messages/").get("data", [])
            for m in msgs:
                mname   = m["attributes"].get("name", "?")
                mstatus = m["attributes"].get("status", "?")
                defn    = m["attributes"].get("definition") or {}
                content = defn.get("content", {})
                subject = content.get("subject", "?")
                preview = content.get("preview_text", "")
                # template relationship
                rels = m.get("relationships", {})
                tpl  = rels.get("template", {}).get("data", {})
                tpl_id = tpl.get("id", "none")
                print(f"    Message: {mname}  [{mstatus}]")
                print(f"    Subject: {subject}")
                if preview:
                    print(f"    Preview: {preview}")
                print(f"    Template ID: {tpl_id}")

        elif atype in ("CONDITIONAL_SPLIT", "BOOLEAN_BRANCH", "TRIGGER_SPLIT"):
            cond = json.dumps(settings, separators=(",", ":"))[:200]
            print(f"  [{atype}] id={aid}")
            print(f"    Condition: {cond}")

        else:
            print(f"  [{atype}] id={aid}")

        print()


if __name__ == "__main__":
    main()
