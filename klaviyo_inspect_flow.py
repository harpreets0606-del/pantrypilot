"""
Fetches one existing flow's full definition from Klaviyo and prints it.
This tells us the exact payload structure needed to create new flows.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py klaviyo_inspect_flow.py
"""

import os, json, sys
import requests

API_KEY = os.environ.get("KLAVIYO_API_KEY", "")
if not API_KEY:
    print("Set KLAVIYO_API_KEY first."); sys.exit(1)

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": "2024-10-15.pre",
    "Accept": "application/json",
}

# 1. List flows (get first one)
r = requests.get(
    "https://a.klaviyo.com/api/flows",
    headers=HEADERS,
    params={"page[size]": 1},
    timeout=15,
)
r.raise_for_status()
flows = r.json().get("data", [])
if not flows:
    print("No flows found in account."); sys.exit(1)

flow = flows[0]
flow_id = flow["id"]
print(f"Inspecting flow: {flow['attributes'].get('name')}  (id={flow_id})\n")

# 2. Get full definition of that flow
r2 = requests.get(
    f"https://a.klaviyo.com/api/flows/{flow_id}",
    headers=HEADERS,
    params={"additional-fields[flow]": "definition"},
    timeout=15,
)
r2.raise_for_status()
data = r2.json()

print(json.dumps(data, indent=2))
