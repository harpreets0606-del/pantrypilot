"""
Checks which flow email templates already exist in Klaviyo.
Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py klaviyo_match_templates.py
"""
import os, sys, requests

API_KEY = os.environ.get("KLAVIYO_API_KEY", "")
if not API_KEY:
    print("Set KLAVIYO_API_KEY"); sys.exit(1)

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": "2024-10-15",
    "Accept": "application/json",
}

NEEDED = [
    ("Flow 1 — Win-back",       "[Z] Win-back Email 1"),
    ("Flow 1 — Win-back",       "[Z] Win-back Email 2"),
    ("Flow 1 — Win-back",       "[Z] Win-back Email 3"),
    ("Flow 2 — Back in Stock",  "[Z] Back in Stock Email 1"),
    ("Flow 2 — Back in Stock",  "[Z] Back in Stock Email 2"),
    ("Flow 3 — Post-Purchase",  "[Z] Post-Purchase Email 1"),
    ("Flow 3 — Post-Purchase",  "[Z] Post-Purchase Email 2"),
    ("Flow 3 — Post-Purchase",  "[Z] Post-Purchase Email 3"),
    ("Flow 3 — Post-Purchase",  "[Z] Post-Purchase Email 4"),
    ("Flow 4 — Flu Season",     "[Z] Flu Season Email 1"),
    ("Flow 4 — Flu Season",     "[Z] Flu Season Email 2"),
    ("Flow 5 — Replenishment",  "[Z] Replenishment Reminder"),
]

# Fetch only [Z] templates using name filter
print("Fetching [Z] templates...")
catalog: dict[str, str] = {}
url = f"https://a.klaviyo.com/api/templates"
params: dict = {"page[size]": 10, "filter": "contains(name,'[Z]')"}
while url:
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    for t in data.get("data", []):
        catalog[t["attributes"]["name"]] = t["id"]
    url = data.get("links", {}).get("next")
    params = {}

print(f"Found {len(catalog)} [Z] templates.\n")

matched, missing = [], []
for flow, name in NEEDED:
    if name in catalog:
        matched.append((flow, name, catalog[name]))
    else:
        missing.append((flow, name))

print(f"{'='*60}")
print(f"MATCHED ({len(matched)}/{len(NEEDED)})")
print(f"{'='*60}")
for flow, name, tid in matched:
    print(f"  ✓ {name}")
    print(f"    Flow:        {flow}")
    print(f"    Template ID: {tid}")
    print(f"    Edit: https://www.klaviyo.com/email-editor/{tid}/edit")

print(f"\n{'='*60}")
print(f"MISSING ({len(missing)}/{len(NEEDED)}) — need to be created")
print(f"{'='*60}")
for flow, name in missing:
    print(f"  ✗ {name}  ({flow})")
