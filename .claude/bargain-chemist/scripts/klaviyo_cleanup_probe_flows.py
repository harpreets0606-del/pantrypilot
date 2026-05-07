"""Archive all PROBE/test flows and superseded draft flows.

Run this locally (not in the Claude Code sandbox):
    python3 .claude/bargain-chemist/scripts/klaviyo_cleanup_probe_flows.py

What it does:
  1. Sets live PROBE flows (UPj2XH, Vny5bc) to manual (paused) first
  2. Archives all 5 PROBE flows
  3. Archives VaRyRc (incomplete Y84ruV-v2 rebuild — superseded)
  4. Archives TsC8GZ ([Z] Welcome Series - No Coupon draft — superseded by live YdejKf)
  5. Prints final live flow list for verification
"""
import json
import requests
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"


def load_key():
    text = ENV_FILE.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[7:].strip()
        if line.startswith("KLAVIYO_PRIVATE_KEY"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing in .env.local")


def hdrs(key, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": "2024-10-15",
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def patch_flow(flow_id, attrs, key, label=""):
    body = {"data": {"type": "flow", "id": flow_id, "attributes": attrs}}
    r = requests.patch(
        f"https://a.klaviyo.com/api/flows/{flow_id}/",
        headers=hdrs(key, content=True),
        json=body,
        timeout=20,
    )
    tag = label or flow_id
    if r.status_code == 200:
        data_attrs = r.json().get("data", {}).get("attributes", {})
        print(f"  {tag}  HTTP {r.status_code}  status={data_attrs.get('status')}  archived={data_attrs.get('archived')}")
    else:
        print(f"  {tag}  HTTP {r.status_code}  {r.text[:200]}")
    return r.status_code == 200


def get_flows(key):
    r = requests.get(
        "https://a.klaviyo.com/api/flows/",
        headers=hdrs(key),
        params={"fields[flow]": "name,status,archived", "page[size]": 50},
        timeout=20,
    )
    if r.status_code != 200:
        print(f"  GET flows failed: {r.status_code} {r.text[:200]}")
        return []
    return r.json().get("data", [])


def main():
    key = load_key()

    # PROBE flows created during conditional-split sandbox testing
    PROBE_FLOWS = {
        "WCMUGZ": "draft",
        "WFhERT": "draft",
        "UPj2XH": "live",    # wrong-trigger probe
        "XG3YXL": "draft",
        "Vny5bc": "live",    # live probe that fired emails
    }
    EXTRA_ARCHIVE = {
        "VaRyRc": "Y84ruV-v2 rebuild (incomplete, superseded)",
        "TsC8GZ": "[Z] Welcome Series - No Coupon draft (superseded by live YdejKf)",
    }

    print("=== Step 1: Pause live PROBE flows (set to manual) ===")
    for fid, status in PROBE_FLOWS.items():
        if status == "live":
            patch_flow(fid, {"status": "manual"}, key, label=f"{fid} → manual")

    print("\n=== Step 2: Archive all 5 PROBE flows ===")
    for fid in PROBE_FLOWS:
        patch_flow(fid, {"archived": True}, key, label=f"{fid} → archived")

    print("\n=== Step 3: Archive superseded draft flows ===")
    for fid, reason in EXTRA_ARCHIVE.items():
        print(f"  ({reason})")
        patch_flow(fid, {"archived": True}, key, label=f"{fid} → archived")

    print("\n=== Step 4: Verify — current non-archived flows ===")
    flows = get_flows(key)
    visible = [f for f in flows if not f.get("attributes", {}).get("archived")]
    for f in visible:
        a = f["attributes"]
        print(f"  {f['id']}  [{a['status']:>6}]  {a['name']}")

    print("\nDone. Review the list above — only production [Z] flows and YdejKf should remain.")


if __name__ == "__main__":
    main()
