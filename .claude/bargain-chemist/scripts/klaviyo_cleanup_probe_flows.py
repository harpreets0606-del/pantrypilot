"""Delete all PROBE/test flows and superseded draft flows.

Run this locally (not in the Claude Code sandbox):
    python3 .claude/bargain-chemist/scripts/klaviyo_cleanup_probe_flows.py

What it does:
  1. Sets live PROBE flows (UPj2XH, Vny5bc) to manual (paused) first
  2. DELETEs all 5 PROBE flows (irreversible — they're sandbox tests)
  3. DELETEs VaRyRc (incomplete Y84ruV-v2 rebuild — superseded)
  4. DELETEs TsC8GZ ([Z] Welcome Series - No Coupon draft — superseded by live YdejKf)
  5. Prints final flow list for verification

Why DELETE not archive: Klaviyo's PATCH /api/flows/{id} does NOT support the
`archived` field (returns HTTP 400 "'archived' is not a valid field for the
resource 'flow'"). POST /api/flows/{id}/archive/ also 404s. There is no known
public API to archive a flow; the UI's Archive button is not exposed via REST.
For these 7 disposable flows we use DELETE (documented stable). For flows you
want to KEEP visible-but-archived in future, do it via the Klaviyo UI.

Local artifacts under .claude/bargain-chemist/snapshots/ are preserved — DELETE
only removes the Klaviyo-side flow record, not local rebuild work.
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


def delete_flow(flow_id, key, label=""):
    r = requests.delete(
        f"https://a.klaviyo.com/api/flows/{flow_id}/",
        headers=hdrs(key),
        timeout=20,
    )
    tag = label or flow_id
    # Klaviyo returns 204 No Content on success; 404 if already gone (idempotent re-run)
    if r.status_code in (204, 200):
        print(f"  {tag}  HTTP {r.status_code}  deleted")
    elif r.status_code == 404:
        print(f"  {tag}  HTTP 404  already gone")
    else:
        print(f"  {tag}  HTTP {r.status_code}  {r.text[:200]}")
    return r.status_code in (204, 200, 404)


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

    print("=== Step 1: Pause live PROBE flows (set to manual before delete) ===")
    for fid, status in PROBE_FLOWS.items():
        if status == "live":
            patch_flow(fid, {"status": "manual"}, key, label=f"{fid} → manual")

    print("\n=== Step 2: DELETE all 5 PROBE flows (IRREVERSIBLE) ===")
    for fid in PROBE_FLOWS:
        delete_flow(fid, key, label=f"{fid} → DELETE")

    print("\n=== Step 3: DELETE superseded draft flows (IRREVERSIBLE) ===")
    for fid, reason in EXTRA_ARCHIVE.items():
        print(f"  ({reason})")
        delete_flow(fid, key, label=f"{fid} → DELETE")

    print("\n=== Step 4: Verify — current flow list (deleted flows should be absent) ===")
    flows = get_flows(key)
    deleted_targets = set(PROBE_FLOWS) | set(EXTRA_ARCHIVE)
    survivors = []
    for f in flows:
        a = f["attributes"]
        marker = "  ⚠️ STILL PRESENT" if f["id"] in deleted_targets else ""
        if f["id"] in deleted_targets:
            survivors.append(f["id"])
        print(f"  {f['id']}  [{a['status']:>6}]  {a['name']}{marker}")

    if survivors:
        print(f"\n⚠️  {len(survivors)} target flow(s) still present after delete: {survivors}")
    else:
        print("\n✅ All 7 target flows deleted. Only production [Z] flows + YdejKf remain.")


if __name__ == "__main__":
    main()
