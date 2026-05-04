"""
Reads the definitions of all 5 flows and prints the template_id for
every send-email action so we can confirm templates are wired.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py verify_templates.py
"""

import os, sys, requests, time

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Accept": "application/json",
}

FLOWS = {
    "UqpyKS": "[Z] Back in Stock",
    "Vvb9ik": "[Z] Post-Purchase Series",
    "XKmyJE": "[Z] Replenishment - Reorder Reminders",
    "U6e3uf": "[Z] Flu Season - Winter Wellness",
    "YdtALs": "[Z] Win-back - Lapsed Customers",
}


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    all_ok = True

    for flow_id, name in FLOWS.items():
        print(f"\n{'='*60}")
        print(f"{name} ({flow_id})")
        print('='*60)

        r = requests.get(
            f"{BASE_URL}/flows/{flow_id}",
            headers=HEADERS,
            params={"additional-fields[flow]": "definition"},
            timeout=15,
        )
        if not r.ok:
            print(f"  ERROR: {r.status_code} {r.text[:200]}")
            all_ok = False
            continue

        actions = r.json()["data"]["attributes"].get("definition", {}).get("actions", [])
        emails = [a for a in actions if a.get("type") == "send-email"]

        for a in emails:
            msg = a.get("data", {}).get("message", {})
            msg_name = msg.get("name", "?")
            tpl_id   = msg.get("template_id")
            if tpl_id:
                print(f"  OK  {msg_name!r:50s}  template={tpl_id}")
            else:
                print(f"  !!  {msg_name!r:50s}  NO TEMPLATE")
                all_ok = False

        time.sleep(0.2)

    print()
    print("=" * 60)
    if all_ok:
        print("PASS - All email actions have templates assigned.")
    else:
        print("FAIL - Some email actions are missing templates.")
    print("=" * 60)


if __name__ == "__main__":
    main()
