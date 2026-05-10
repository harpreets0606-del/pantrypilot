"""Discover the flow-action IDs and template-assignment for every email message
in the 5 live flows we need to fix.

Output:
  .claude/bargain-chemist/snapshots/2026-05-07/flow-action-map.json
    [
      {
        "flow_id": "YdejKf",
        "flow_name": "...",
        "action_id": "...",
        "message_id": "...",
        "template_id": "UpdhCT",
        "subject_line": "...",
        "preview_text": "...",
      },
      ...
    ]

Uses revision 2025-10-15 (where /api/flow-actions PATCH is GA).
"""
import json
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / ".claude/bargain-chemist/snapshots/2026-05-07/flow-action-map.json"

LIVE_FLOWS = ["YdejKf", "RPQXaa", "Ua5LdS", "V9XmEm", "Ysj7sg"]

REVISION = "2025-10-15"


def load_key() -> str:
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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY not found")


def gget(url, headers):
    r = requests.get(url, headers=headers, timeout=25)
    r.raise_for_status()
    return r.json()


def main() -> int:
    key = load_key()
    headers = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    out = []
    for fid in LIVE_FLOWS:
        # 1) flow + relationships
        try:
            flow = gget(f"https://a.klaviyo.com/api/flows/{fid}/?include=flow-actions",
                        headers)
        except Exception as e:
            print(f"{fid}: flow GET failed: {e}")
            continue
        flow_name = flow.get("data", {}).get("attributes", {}).get("name", "?")
        actions_rel = flow.get("data", {}).get("relationships", {}).get("flow-actions", {}).get("data", [])
        action_ids = [a["id"] for a in actions_rel if a.get("type") == "flow-action"]
        print(f"\n=== {fid} ({flow_name}) — {len(action_ids)} actions ===")

        for aid in action_ids:
            # 2) flow action
            try:
                act = gget(f"https://a.klaviyo.com/api/flow-actions/{aid}/", headers)
            except Exception as e:
                print(f"  action {aid}: GET failed: {e}")
                continue
            atype = act.get("data", {}).get("attributes", {}).get("action_type", "?")
            if atype != "send-email":
                continue
            # 3) flow message (one-to-one with the action)
            try:
                msg = gget(f"https://a.klaviyo.com/api/flow-actions/{aid}/flow-message/", headers)
            except Exception as e:
                print(f"  action {aid}: flow-message GET failed: {e}")
                continue
            mdata = msg.get("data", {})
            mid = mdata.get("id", "?")
            mattrs = mdata.get("attributes", {}) or {}
            content = mattrs.get("content", {}) or {}
            tmpl_rel = (mdata.get("relationships", {})
                        .get("template", {})
                        .get("data", {}) or {})
            tid = tmpl_rel.get("id")
            entry = {
                "flow_id": fid,
                "flow_name": flow_name,
                "action_id": aid,
                "message_id": mid,
                "template_id": tid,
                "subject_line": content.get("subject"),
                "preview_text": content.get("preview_text"),
                "from_email": content.get("from_email"),
                "from_label": content.get("from_label"),
                "smart_sending_enabled": mattrs.get("smart_sending_enabled"),
            }
            out.append(entry)
            print(f"  action={aid}  msg={mid}  tmpl={tid}  subj={(content.get('subject') or '')[:50]!r}")

    OUT.write_text(json.dumps(out, indent=2))
    print(f"\nWrote {len(out)} send-email mappings -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
