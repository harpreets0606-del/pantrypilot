"""Pull EVERYTHING needed for a full audit of every live flow.

For each live flow:
  - flow definition (with included flow-actions)
  - For every send-email action: capture subject / preview / template_id / smart_sending / definition
  - For every referenced template: GET /api/templates/{id}/ -> save HTML

Outputs:
  snapshots/2026-05-07/audit/<flowId>.json           — full flow + actions
  snapshots/2026-05-07/audit/<flowId>-emails.json    — flat list of email messages with metadata
  snapshots/2026-05-07/audit/templates/<tid>.json    — full template (incl. HTML)
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

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/audit"
TPL_OUT = OUT / "templates"
OUT.mkdir(parents=True, exist_ok=True)
TPL_OUT.mkdir(parents=True, exist_ok=True)

REVISION = "2025-10-15"
LIVE_FLOWS = ["RPQXaa", "T7pmf6", "Ua5LdS", "V9XmEm", "Y84ruV", "YdejKf", "Ysj7sg"]


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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY not found")


def main():
    key = load_key()
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    all_emails = []
    template_ids = set()

    for fid in LIVE_FLOWS:
        url = f"https://a.klaviyo.com/api/flows/{fid}/?include=flow-actions"
        try:
            r = requests.get(url, headers=h, timeout=30)
        except Exception as e:
            print(f"{fid}: GET failed: {e}")
            continue
        if r.status_code != 200:
            print(f"{fid}: HTTP {r.status_code}: {r.text[:200]}")
            continue
        data = r.json()
        (OUT / f"{fid}.json").write_text(json.dumps(data, indent=2))
        flow_name = data.get("data", {}).get("attributes", {}).get("name", "?")
        flow_status = data.get("data", {}).get("attributes", {}).get("status", "?")

        emails = []
        for inc in data.get("included", []):
            attrs = inc.get("attributes", {}) or {}
            defn = attrs.get("definition", {}) or {}
            if defn.get("type") != "send-email":
                continue
            msg = (defn.get("data", {}) or {}).get("message", {}) or {}
            tid = msg.get("template_id")
            if tid:
                template_ids.add(tid)
            emails.append({
                "flow_id": fid,
                "flow_name": flow_name,
                "flow_status": flow_status,
                "action_id": inc.get("id"),
                "msg_id": msg.get("id"),
                "name": msg.get("name"),
                "template_id": tid,
                "subject_line": msg.get("subject_line"),
                "preview_text": msg.get("preview_text"),
                "from_email": msg.get("from_email"),
                "from_label": msg.get("from_label"),
                "smart_sending": msg.get("smart_sending_enabled"),
                "transactional": msg.get("transactional"),
                "add_tracking_params": msg.get("add_tracking_params"),
                "next_action": (defn.get("links") or {}).get("next"),
                "definition_type": defn.get("type"),
            })
        (OUT / f"{fid}-emails.json").write_text(json.dumps(emails, indent=2))
        all_emails.extend(emails)
        print(f"{fid} ({flow_name}): {len(emails)} email actions")

    # Pull every referenced template
    print(f"\nPulling {len(template_ids)} templates...")
    for tid in sorted(template_ids):
        try:
            r = requests.get(f"https://a.klaviyo.com/api/templates/{tid}/", headers=h, timeout=20)
        except Exception as e:
            print(f"  {tid}: FAIL {e}")
            continue
        if r.status_code != 200:
            print(f"  {tid}: HTTP {r.status_code}")
            continue
        (TPL_OUT / f"{tid}.json").write_text(r.text)
        time.sleep(0.15)

    (OUT / "all-emails.json").write_text(json.dumps(all_emails, indent=2))
    print(f"\nDone. {len(all_emails)} emails across {len(LIVE_FLOWS)} flows. Templates -> {TPL_OUT}")


if __name__ == "__main__":
    main()
