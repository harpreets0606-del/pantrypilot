"""
Fetches a flow that contains a conditional-split and prints its full definition.
This reveals the exact payload structure needed to create flows with splits.

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

# 1. Find a flow that has a conditional-split action
flow_id = None
flow_name = None
url = "https://a.klaviyo.com/api/flows"
params: dict = {"page[size]": 10}

while url and not flow_id:
    r = requests.get(url, headers=HEADERS, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    for f in data.get("data", []):
        fid = f["id"]
        # fetch its definition to check for conditional splits
        r2 = requests.get(
            f"https://a.klaviyo.com/api/flows/{fid}",
            headers=HEADERS,
            params={"additional-fields[flow]": "definition"},
            timeout=15,
        )
        if not r2.ok:
            continue
        defn = r2.json()["data"]["attributes"].get("definition", {})
        actions = defn.get("actions", [])
        if any(a["type"] == "conditional-split" for a in actions):
            flow_id = fid
            flow_name = f["attributes"].get("name")
            break
    url = data.get("links", {}).get("next")
    params = {}

if not flow_id:
    print("No flow with a conditional-split found. Showing first flow instead.")
    r = requests.get("https://a.klaviyo.com/api/flows", headers=HEADERS,
                     params={"page[size]": 1}, timeout=15)
    r.raise_for_status()
    flows = r.json().get("data", [])
    flow_id = flows[0]["id"]
    flow_name = flows[0]["attributes"].get("name")

print(f"Inspecting flow: {flow_name}  (id={flow_id})\n")

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
