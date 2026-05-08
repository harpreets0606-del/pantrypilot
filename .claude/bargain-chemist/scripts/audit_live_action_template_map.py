"""Walk live /api/flows/{id}/flow-actions/ for every LIVE flow and report
the current cloned template_id per send-email action.

Why: MCP has no flow-actions endpoint, so prior audits relied on yesterday's
snapshot for action->template mappings. This script gives ground truth from
the live API, including:

  - flow_id, flow_name, status
  - per send-email action: action_id, name, message_id, subject_line,
    template_id (the live cloned template currently bound)

Run locally:
    python .claude/bargain-chemist/scripts/audit_live_action_template_map.py

Output: one PASS/FAIL classification per (flow, action). Also writes a
JSON snapshot to snapshots/<today>/live-action-template-map.json so you
have a durable record.
"""
import json
import sys
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
TODAY = date.today().isoformat()
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/live-action-template-map"
OUT.mkdir(parents=True, exist_ok=True)


# All currently LIVE flows + the paused one + the draft duplicates
FLOWS_TO_AUDIT = [
    # LIVE flows
    ("RtiVC5", "Browse Abandonment"),
    ("XbQiKg", "Search Abandonment"),
    ("Sr3hxz", "Abandoned Checkout v3"),
    ("RPQXaa", "Added to Cart Abandonment"),
    ("T7pmf6", "Win-back Lapsed Customers"),
    ("Ua5LdS", "Replenishment Category-Based"),
    ("V9XmEm", "Flu Season Winter Wellness"),
    ("YdejKf", "Welcome Series 2026"),
    # Manual (paused)
    ("Ysj7sg", "Back in Stock (paused)"),
    # Draft duplicates (for completeness)
    ("RSnNak", "Browse Triple Pixel (DRAFT)"),
    ("SnakeG", "Cart Triple Pixel (DRAFT)"),
    ("VMKAyS", "Checkout Triple Pixel (DRAFT)"),
    ("SehWRt", "Welcome Website (DRAFT)"),
]


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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing in .env.local")


def hdrs(key):
    return {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": "2025-10-15",
        "Accept": "application/vnd.api+json",
    }


def walk_flow_actions(key, flow_id, flow_label):
    """Walk every flow-action belonging to a flow, find every send-email
    action, return a list of (action_id, message_id, name, subject, preview,
    template_id)."""
    url = f"https://a.klaviyo.com/api/flows/{flow_id}/flow-actions/"
    out = []
    while url:
        r = requests.get(url, headers=hdrs(key), timeout=30,
                         params={"include": "flow-messages"})
        if r.status_code != 200:
            return None, f"GET {flow_id} flow-actions HTTP {r.status_code}: {r.text[:200]}"
        body = r.json()
        for action in body.get("data", []):
            attrs = action["attributes"]
            action_id = action["id"]
            action_type = attrs.get("action_type") or attrs.get("definition", {}).get("type")
            if action_type != "send-email":
                continue
            defn = attrs.get("definition", {})
            msg = defn.get("data", {}).get("message", {})
            out.append({
                "action_id": action_id,
                "action_type": action_type,
                "message_id": msg.get("id"),
                "name": msg.get("name"),
                "subject_line": msg.get("subject_line"),
                "preview_text": msg.get("preview_text"),
                "template_id": msg.get("template_id"),
                "smart_sending": msg.get("smart_sending_enabled"),
                "transactional": msg.get("transactional"),
                "tracking_enabled": msg.get("add_tracking_params"),
                "additional_filters": msg.get("additional_filters"),
            })
        url = body.get("links", {}).get("next")
    return out, None


def main():
    key = load_key()
    print(f"=== Live action→template mapping audit  ({TODAY}) ===")
    print(f"Snapshots: {OUT}\n")

    full_map = {}
    summary = []

    for flow_id, flow_label in FLOWS_TO_AUDIT:
        print(f"\n--- {flow_id} :: {flow_label} ---")
        actions, err = walk_flow_actions(key, flow_id, flow_label)
        if err:
            print(f"  ❌ {err}")
            full_map[flow_id] = {"error": err, "label": flow_label}
            summary.append((flow_id, flow_label, "ERROR", err[:80]))
            continue

        full_map[flow_id] = {"label": flow_label, "send_email_actions": actions}
        if not actions:
            print(f"  (no send-email actions found)")
            summary.append((flow_id, flow_label, "EMPTY", "no send-email actions"))
            continue

        for a in actions:
            tid = a.get("template_id") or "<NULL>"
            sub = (a.get("subject_line") or "")[:80]
            print(f"  action {a['action_id']} → template={tid}  msg={a.get('message_id')}  subj=\"{sub}\"")
            summary.append((flow_id, flow_label, a["action_id"], tid))

    # Write JSON snapshot
    snapshot_path = OUT / "live-action-template-map.json"
    snapshot_path.write_text(json.dumps(full_map, indent=2), encoding="utf-8")
    print(f"\n=== Snapshot written: {snapshot_path} ===")

    # Compact summary table
    print(f"\n=== Summary ({len(summary)} rows) ===")
    print(f"{'Flow':<8} {'Action':<12} {'Template':<10}  Description")
    print("-" * 80)
    for row in summary:
        flow_id, label, act, tid = row
        print(f"{flow_id:<8} {str(act):<12} {str(tid):<10}  {label}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
