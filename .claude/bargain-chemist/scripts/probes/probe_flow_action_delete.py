"""Probe: can a single flow-action be deleted via API?

The Y84ruV redesign requires removing the trigger-split (action 98627485) and
the orphaned "Copy of Email #4" (action 105923487). Two paths:

  Path A: DELETE /api/flow-actions/{id}            (fast — action-level delete)
  Path B: DELETE /api/flows/{id} + recreate fresh  (clean but invasive)

`klaviyo-api-capabilities.md` notes "flow's structure cannot be updated via
API" but doesn't differentiate action-level deletion from definition-level
mutation. This probe answers definitively.

Approach (idempotent + cleans up after itself):
  1. POST a minimal disposable test flow (DRAFT) with a known action.
  2. Try DELETE /api/flow-actions/{action_id}.
  3. Try DELETE /api/flows/{flow_id}/flow-actions/{action_id} as a fallback.
  4. GET the flow to verify if action was removed.
  5. Cleanup: DELETE the test flow regardless of outcome.

Run locally:
    python .claude/bargain-chemist/scripts/probes/probe_flow_action_delete.py

Snapshots to .claude/bargain-chemist/snapshots/<today>/probe-action-delete/.
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[4]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/probe-action-delete"
OUT.mkdir(parents=True, exist_ok=True)
REVISION_BETA = "2024-10-15.pre"  # required for POST /api/flows
REVISION_GA = "2025-10-15"

# Minimal disposable flow: list trigger -> 1m delay -> placeholder send -> end
# Uses a list ID we know exists or fail loudly for the user to pick one.
PLACEHOLDER_TEMPLATE_ID = "UH72Vm"  # owned global from previous probes


def load_key():
    text = ENV_FILE.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if line.startswith("KLAVIYO_PRIVATE_KEY"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing")


def hdrs(key, revision, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": revision,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def find_a_list(key):
    """Pick any list to use as the trigger. Falls back to error if none."""
    r = requests.get("https://a.klaviyo.com/api/lists/",
                     headers=hdrs(key, REVISION_GA),
                     params={"page[size]": 1},
                     timeout=20)
    if r.status_code != 200:
        sys.exit(f"ERROR fetching lists: {r.status_code} {r.text[:200]}")
    lists = r.json().get("data", [])
    if not lists:
        sys.exit("ERROR: account has no lists")
    return lists[0]["id"], lists[0]["attributes"].get("name", "?")


def main():
    key = load_key()
    list_id, list_name = find_a_list(key)
    print(f"Using list {list_id} ({list_name}) as test trigger\n")

    # 1. POST a disposable test flow
    flow_body = {
        "data": {
            "type": "flow",
            "attributes": {
                "name": f"PROBE - flow-action delete test ({date.today()})",
                "definition": {
                    "triggers": [{"type": "list", "id": list_id}],
                    "profile_filter": None,
                    "entry_action_id": "delay-1",
                    "actions": [
                        {
                            "temporary_id": "delay-1",
                            "type": "time-delay",
                            "data": {
                                "unit": "minutes",
                                "value": 5,
                                "secondary_value": None,
                                "timezone": "profile",
                            },
                            "links": {"next": "send-1"}
                        },
                        {
                            "temporary_id": "send-1",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "Probe Send 1",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Probe",
                                    "subject_line": "probe",
                                    "preview_text": "probe",
                                    "template_id": PLACEHOLDER_TEMPLATE_ID,
                                    "smart_sending_enabled": True,
                                    "transactional": False,
                                    "add_tracking_params": False,
                                    "custom_tracking_params": None,
                                    "additional_filters": None,
                                },
                                "status": "draft",
                            },
                            "links": {"next": None}
                        },
                    ],
                },
            },
        }
    }

    print("Step 1: POST /api/flows/ (create disposable test flow)")
    r = requests.post("https://a.klaviyo.com/api/flows/",
                      headers=hdrs(key, REVISION_BETA, content=True),
                      json=flow_body, timeout=30)
    (OUT / "01-create-flow.json").write_text(
        json.dumps({"status": r.status_code, "body": r.text[:5000]}, indent=2), encoding="utf-8")
    if r.status_code not in (200, 201):
        print(f"  HTTP {r.status_code}  cannot proceed:\n  {r.text[:500]}")
        sys.exit(1)
    flow = r.json().get("data", {})
    flow_id = flow.get("id")
    print(f"  HTTP {r.status_code}  flow_id={flow_id}")

    # 2. Get flow-actions for this flow
    print("\nStep 2: GET flow-actions to find a target action")
    r = requests.get(f"https://a.klaviyo.com/api/flows/{flow_id}/flow-actions/",
                     headers=hdrs(key, REVISION_GA), timeout=20)
    (OUT / "02-list-actions.json").write_text(
        json.dumps({"status": r.status_code, "body": r.text[:5000]}, indent=2), encoding="utf-8")
    actions = r.json().get("data", []) if r.status_code == 200 else []
    if not actions:
        print("  No actions found — cleanup and exit")
        requests.delete(f"https://a.klaviyo.com/api/flows/{flow_id}/",
                        headers=hdrs(key, REVISION_GA), timeout=20)
        sys.exit(1)
    # Pick the time-delay action (first in chain)
    target_action_id = None
    for a in actions:
        if a["attributes"].get("definition", {}).get("type") == "time-delay":
            target_action_id = a["id"]
            break
    if not target_action_id:
        target_action_id = actions[0]["id"]
    print(f"  Target action: {target_action_id} (will try to delete)")

    # 3a. Try DELETE /api/flow-actions/{id}
    print(f"\nStep 3a: DELETE /api/flow-actions/{target_action_id}")
    r = requests.delete(f"https://a.klaviyo.com/api/flow-actions/{target_action_id}/",
                        headers=hdrs(key, REVISION_GA), timeout=20)
    delete_a_status = r.status_code
    delete_a_body = r.text[:500]
    (OUT / "03a-delete-flow-action.json").write_text(
        json.dumps({"status": delete_a_status, "body": delete_a_body}, indent=2), encoding="utf-8")
    print(f"  HTTP {delete_a_status}  {delete_a_body[:120]}")

    # 3b. If 3a failed, try the nested URL form
    delete_b_status = None
    delete_b_body = ""
    if delete_a_status not in (200, 204):
        print(f"\nStep 3b: DELETE /api/flows/{flow_id}/flow-actions/{target_action_id}")
        r = requests.delete(f"https://a.klaviyo.com/api/flows/{flow_id}/flow-actions/{target_action_id}/",
                            headers=hdrs(key, REVISION_GA), timeout=20)
        delete_b_status = r.status_code
        delete_b_body = r.text[:500]
        (OUT / "03b-delete-nested.json").write_text(
            json.dumps({"status": delete_b_status, "body": delete_b_body}, indent=2), encoding="utf-8")
        print(f"  HTTP {delete_b_status}  {delete_b_body[:120]}")

    # 4. GET to verify
    print(f"\nStep 4: GET flow-actions to verify if {target_action_id} is gone")
    r = requests.get(f"https://a.klaviyo.com/api/flows/{flow_id}/flow-actions/",
                     headers=hdrs(key, REVISION_GA), timeout=20)
    actions_after = r.json().get("data", []) if r.status_code == 200 else []
    survived = any(a["id"] == target_action_id for a in actions_after)
    (OUT / "04-verify-actions.json").write_text(
        json.dumps({"status": r.status_code, "survived": survived, "action_count": len(actions_after), "body": r.text[:5000]}, indent=2), encoding="utf-8")
    print(f"  Action {target_action_id} still present? {survived}")

    # 5. Cleanup
    print(f"\nStep 5: DELETE /api/flows/{flow_id} (cleanup)")
    r = requests.delete(f"https://a.klaviyo.com/api/flows/{flow_id}/",
                        headers=hdrs(key, REVISION_GA), timeout=20)
    print(f"  HTTP {r.status_code}")

    print("\n=== VERDICT ===")
    if delete_a_status in (200, 204) and not survived:
        print("✅ DELETE /api/flow-actions/{id} WORKS. Path A available for Y84ruV cleanup.")
    elif delete_b_status in (200, 204) and not survived:
        print("✅ DELETE /api/flows/{flow_id}/flow-actions/{action_id} WORKS (nested form).")
    else:
        print(f"❌ Neither DELETE form works. Last responses:")
        print(f"   DELETE /api/flow-actions/{{id}}: HTTP {delete_a_status}")
        if delete_b_status is not None:
            print(f"   DELETE /api/flows/{{id}}/flow-actions/{{id}}: HTTP {delete_b_status}")
        print(f"   Path B required: DELETE flow + POST fresh flow with desired structure.")
    print(f"\nSnapshots: {OUT}")


if __name__ == "__main__":
    raise SystemExit(main())
