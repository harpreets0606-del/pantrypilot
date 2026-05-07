"""Rebuild Y84ruV (Abandoned Checkout) as a NEW flow with proper structure.

Phases:
  1. Pull existing TuHa4f + TUbBRk templates (live HTML for the rebuilt emails)
  2. Inject Jinja conditional block at top of TuHa4f for cart-value-aware messaging
  3. Create 2 owned global templates from those HTML strings
  4. POST a new flow definition (revision 2024-10-15.pre, beta but stable):
       - Trigger: Checkout Started metric VvcTue
       - Profile filter:
           Group 1: Placed Order count = 0 since flow-start
           Group 2: Checkout Started count = 0 since flow-start
           Group 3: profile-marketing-consent (canReceiveMarketing=true)  <- NEW
       - Actions:
           delay-1 (1 hour) -> email-1 (cart-conditional copy)
           -> delay-2 (23 hours) -> email-2 (one-step-away)
  5. Created in DRAFT status. User reviews + activates in UI.
  6. After verification, archive original Y84ruV.

Run: python klaviyo_rebuild_y84ruv.py [--apply]
  Default: dry-run prints the planned flow definition.
"""
import argparse
import copy
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
SNAP_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/y84ruv-rebuild"
SNAP_DIR.mkdir(parents=True, exist_ok=True)

REVISION_CREATE = "2024-10-15.pre"  # Beta but stable per memory
REVISION_GET = "2025-10-15"


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


def save(name, data):
    p = SNAP_DIR / name
    p.write_text(json.dumps(data, indent=2) if isinstance(data, dict) else str(data))


def get_template(tid, key):
    r = requests.get(
        f"https://a.klaviyo.com/api/templates/{tid}/",
        headers=hdrs(key, REVISION_GET), timeout=30,
    )
    r.raise_for_status()
    return r.json()["data"]["attributes"]["html"]


def inject_jinja_conditional(html):
    """Insert a cart-value-aware Jinja block immediately after <body...> tag."""
    block = """
{% if event.$value|default:0|float < 79 %}
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#FFF7E6;">
  <tr><td style="padding:18px 24px;text-align:center;">
    <p style="font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#7A4F00;margin:0;line-height:1.5;">
      Add <strong>${{ (79 - event.$value|float)|round(2) }}</strong> more for free shipping at NZ's lowest pharmacy prices.
    </p>
  </td></tr>
</table>
{% else %}
<table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#E8F5E9;">
  <tr><td style="padding:18px 24px;text-align:center;">
    <p style="font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#1B5E20;margin:0;line-height:1.5;">
      Free shipping is yours — finish checkout in just a few clicks.
    </p>
  </td></tr>
</table>
{% endif %}
"""
    import re
    m = re.search(r"<body[^>]*>", html, re.IGNORECASE)
    if not m:
        return block + html
    return html[: m.end()] + block + html[m.end():]


def post_template(name, html, key):
    body = {
        "data": {
            "type": "template",
            "attributes": {"name": name, "editor_type": "CODE", "html": html},
        }
    }
    r = requests.post(
        "https://a.klaviyo.com/api/templates/",
        headers=hdrs(key, REVISION_GET, content=True), json=body, timeout=30,
    )
    if r.status_code != 201:
        raise RuntimeError(f"Template POST failed HTTP {r.status_code}: {r.text[:300]}")
    new_id = r.json()["data"]["id"]
    save(f"template-{new_id}-create.json", r.json())
    return new_id


def build_flow_definition(email1_tid, email2_tid):
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "Y84ruV-v2 - Abandoned Checkout (rebuilt 2026-05-07)",
                "definition": {
                    "triggers": [
                        {"type": "metric", "id": "VvcTue"}
                    ],
                    "profile_filter": {
                        "condition_groups": [
                            # Group 1: skip if user has placed an order since flow-start
                            {"conditions": [{
                                "type": "profile-metric",
                                "metric_id": "Sxnb5T",
                                "measurement": "count",
                                "measurement_filter": {
                                    "type": "numeric", "operator": "equals", "value": 0
                                },
                                "timeframe_filter": {
                                    "type": "date", "operator": "flow-start"
                                },
                                "metric_filters": None,
                            }]},
                            # Group 2: skip if user has re-started checkout since flow-start
                            {"conditions": [{
                                "type": "profile-metric",
                                "metric_id": "VvcTue",
                                "measurement": "count",
                                "measurement_filter": {
                                    "type": "numeric", "operator": "equals", "value": 0
                                },
                                "timeframe_filter": {
                                    "type": "date", "operator": "flow-start"
                                },
                                "metric_filters": None,
                            }]},
                            # Group 3: NEW — only fire for marketable profiles
                            {"conditions": [{
                                "type": "profile-marketing-consent",
                                "consent": {
                                    "channel": "email",
                                    "can_receive_marketing": True,
                                    "consent_status": {"subscription": "any", "filters": None},
                                },
                            }]},
                        ]
                    },
                    "entry_action_id": "delay-1",
                    "actions": [
                        {
                            "temporary_id": "delay-1",
                            "type": "time-delay",
                            "data": {
                                "unit": "hours", "value": 1,
                                "secondary_value": None, "timezone": "profile",
                            },
                            "links": {"next": "email-1"},
                        },
                        {
                            "temporary_id": "email-1",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "Y84ruV-v2 Email 1 - Cart aware",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "reply_to_email": None,
                                    "cc_email": None,
                                    "bcc_email": None,
                                    "subject_line": "{{ first_name|default:'Hey' }}, you forgot something at Bargain Chemist",
                                    "preview_text": "Pick up where you left off — Price Beat 10% and free shipping over $79.",
                                    "template_id": email1_tid,
                                    "smart_sending_enabled": True,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None,
                                },
                                "status": "draft",
                            },
                            "links": {"next": "delay-2"},
                        },
                        {
                            "temporary_id": "delay-2",
                            "type": "time-delay",
                            "data": {
                                "unit": "hours", "value": 23,
                                "secondary_value": None, "timezone": "profile",
                            },
                            "links": {"next": "email-2"},
                        },
                        {
                            "temporary_id": "email-2",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "Y84ruV-v2 Email 2 - One step away",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "reply_to_email": None,
                                    "cc_email": None,
                                    "bcc_email": None,
                                    "subject_line": "One step away from everyday savings",
                                    "preview_text": "Your items are waiting — no rush.",
                                    "template_id": email2_tid,
                                    "smart_sending_enabled": True,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None,
                                },
                                "status": "draft",
                            },
                            "links": {"next": None},
                        },
                    ],
                },
            }
        }
    }


def post_flow(body, key):
    r = requests.post(
        "https://a.klaviyo.com/api/flows/",
        headers=hdrs(key, REVISION_CREATE, content=True), json=body, timeout=60,
    )
    save("flow-create-response.json", r.json() if r.status_code < 400 else {"raw": r.text, "status": r.status_code})
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Flow POST failed HTTP {r.status_code}: {r.text[:600]}")
    return r.json()["data"]["id"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    key = load_key()

    print("Phase 1: pull source templates")
    tuha4f_html = get_template("TuHa4f", key)
    print(f"  TuHa4f: {len(tuha4f_html)} chars")
    tubbrk_html = get_template("TUbBRk", key)
    print(f"  TUbBRk: {len(tubbrk_html)} chars")

    print("\nPhase 2: inject Jinja cart-conditional block into TuHa4f")
    email1_html = inject_jinja_conditional(tuha4f_html)
    save("email1-with-jinja.html", email1_html)
    print(f"  email1 HTML: {len(email1_html)} chars (delta: +{len(email1_html)-len(tuha4f_html)})")

    if not args.apply:
        print("\nDRY-RUN — would create owned templates and POST flow")
        plan = build_flow_definition("TEMPLATE_1_PLACEHOLDER", "TEMPLATE_2_PLACEHOLDER")
        save("flow-plan.json", plan)
        print(f"  Flow plan saved -> {SNAP_DIR}/flow-plan.json")
        print("\nRun with --apply to actually create.")
        return 0

    print("\nPhase 3: create owned global templates")
    email1_tid = post_template("BC OWNED - Y84ruV-v2 Email1 cart-aware", email1_html, key)
    print(f"  email1 owned template: {email1_tid}")
    time.sleep(0.3)
    email2_tid = post_template("BC OWNED - Y84ruV-v2 Email2 one-step-away", tubbrk_html, key)
    print(f"  email2 owned template: {email2_tid}")

    print("\nPhase 4: POST new flow as DRAFT")
    body = build_flow_definition(email1_tid, email2_tid)
    save("flow-create-request.json", body)
    new_flow_id = post_flow(body, key)
    print(f"  NEW FLOW ID: {new_flow_id}")
    print(f"  URL: https://www.klaviyo.com/flow/{new_flow_id}/edit")
    print(f"\nNext steps:")
    print(f"  1. Open URL above and review in Klaviyo UI")
    print(f"  2. If happy, change status from Draft to Live")
    print(f"  3. Archive the original Y84ruV via UI or PATCH /api/flows/Y84ruV/ status=draft+archived")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
