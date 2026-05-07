"""Deploy Y84ruV v3 — linear flow with in-template 3-tier Liquid conditional.

Architecture (decided by empirical evidence on 2026-05-08):
- Path B: DELETE old Y84ruV + POST new linear flow.
  Reason: probe_flow_action_delete proved single-action DELETE is HTTP 405
  (Method Not Allowed). Cannot surgically remove the trigger-split.
- In-template 3-tier `{% if %}{% elif %}{% else %}` Liquid (verified by
  probe_elif_boundaries.py — 9/9 boundary cases PASS, both bare and defensive).
  Replaces the broken runtime trigger-split with a render-time conditional.
- Defensive `{% with v=event|lookup:'$value'|default:0 %}` wrapping (verified
  by probe_null_value_handling.py — `event|lookup` returns 'None' literal for
  missing keys; defensive default routes safely to Tier A if $value absent).
- Static subjects, fixing the `{{ first_name|default:'Your' }} order's one
  click away` Liquid grammar bug (verified-reproduced by probe_subject_liquid).

Phases:
  A (always)  Build templates by POST + render-test at $value 20/50/120
              + assert expected tier markers + zero Liquid leakage.
  B (--apply) Snapshot existing Y84ruV, POST fresh linear flow with new
              template IDs, DELETE old Y84ruV. Leaves new flow in DRAFT
              for user review + manual flip to LIVE via Klaviyo UI.

Default mode: --dry-run. Nothing destructive runs without --apply.

Run locally:
    python .claude/bargain-chemist/scripts/klaviyo_rebuild_y84ruv_v3.py
    python .claude/bargain-chemist/scripts/klaviyo_rebuild_y84ruv_v3.py --apply

Snapshots to .claude/bargain-chemist/snapshots/<today>/y84ruv-v3/.
"""
import argparse
import json
import re
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
TODAY = date.today().isoformat()
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/y84ruv-v3"
OUT.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = REPO / ".claude/bargain-chemist/templates"

# Klaviyo metrics + flow constants
METRIC_CHECKOUT_STARTED = "VvcTue"  # Shopify Checkout Started
METRIC_PLACED_ORDER = "Sxnb5T"      # Shopify Placed Order
OLD_FLOW_ID = "Y84ruV"
NEW_FLOW_NAME = f"[Z] Abandoned Checkout v3 - tiered (rebuilt {TODAY})"

REVISION_GA = "2025-10-15"
REVISION_BETA = "2024-10-15.pre"

# Subject + preview decisions:
# - Static (no Liquid). probe_subject_liquid confirmed Liquid IS safe in
#   subject_line, but static avoids the 'Sarah order's one click away'
#   class of bugs and adds zero risk.
E1_SUBJECT = "Your cart's saved — pick up when you're ready"
E1_PREVIEW = "Your items are waiting. Free shipping over $79."
E4_SUBJECT = "Your order's one click away"
E4_PREVIEW = "Free shipping over $79 — same Bargain Chemist price."

# Template HTML files (built 2026-05-08 by inline builder, committed alongside
# this script). Each contains the verified 3-tier conditional.
E1_HTML_FILE = TEMPLATES_DIR / "cart-recover-e1-tiered.html"
E4_HTML_FILE = TEMPLATES_DIR / "cart-recover-e4-tiered.html"


# ----------------------------------------------------------------------
# HTTP helpers
# ----------------------------------------------------------------------

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


def hdrs(key, revision=REVISION_GA, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": revision,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, payload):
    (OUT / name).write_text(
        payload if isinstance(payload, str) else json.dumps(payload, indent=2),
        encoding="utf-8",
    )


# ----------------------------------------------------------------------
# Phase A: build + render-test templates
# ----------------------------------------------------------------------

def post_template(key, name, html):
    body = {"data": {"type": "template", "attributes": {
        "name": name,
        "editor_type": "CODE",
        "html": html,
    }}}
    r = requests.post("https://a.klaviyo.com/api/templates/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"phaseA-post-{name.replace(' ', '_')}.json",
         {"status": r.status_code, "body": r.text[:5000]})
    if r.status_code not in (200, 201):
        sys.exit(f"❌ POST /api/templates/ failed for {name}: HTTP {r.status_code}\n{r.text[:500]}")
    tid = r.json()["data"]["id"]
    print(f"  POST template '{name}' -> {tid}")
    return tid


def render_template(key, template_id, value, label):
    body = {"data": {"type": "template", "attributes": {
        "id": template_id,
        "context": {
            "first_name": "Sam",
            "organization": {
                "name": "Bargain Chemist",
                "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
                "url": "https://www.bargainchemist.co.nz/",
                "homepage": "https://www.bargainchemist.co.nz/",
            },
            "event": {"$value": value, "extra": {"line_items": []}},
        }
    }}}
    r = requests.post("https://a.klaviyo.com/api/template-render/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"phaseA-render-{label}.json",
         {"status": r.status_code, "value": value, "body": r.text[:6000]})
    return r


def assert_tier_render(rendered_html, value, expected_phrases):
    """Assert one of the expected tier-specific phrases appears AND no Liquid leakage."""
    if "{%" in rendered_html or "{{" in rendered_html:
        # Find first leakage for the error message
        leak = re.search(r'(\{[%{][^}]{0,80})', rendered_html)
        return False, f"Liquid leakage: {leak.group(1) if leak else '?'}"
    for phrase in expected_phrases:
        if phrase in rendered_html:
            return True, f"matched '{phrase}'"
    return False, f"no expected phrase found (looked for: {expected_phrases})"


def run_phase_a(key):
    print("\n=== Phase A: build + render-test templates ===")

    # Validate template files exist
    for f in (E1_HTML_FILE, E4_HTML_FILE):
        if not f.exists():
            sys.exit(f"❌ template file missing: {f}")

    e1_html = E1_HTML_FILE.read_text(encoding="utf-8")
    e4_html = E4_HTML_FILE.read_text(encoding="utf-8")
    print(f"  E1 source: {len(e1_html)} bytes  E4 source: {len(e4_html)} bytes")

    # POST both templates
    e1_tid = post_template(key, f"BC OWNED - Y84ruV-v3 E1 tiered ({TODAY})", e1_html)
    e4_tid = post_template(key, f"BC OWNED - Y84ruV-v3 E4 tiered ({TODAY})", e4_html)
    save("phaseA-template-ids.json", {"e1": e1_tid, "e4": e4_tid})

    # Render-test contexts: $value at each tier
    test_cases = [
        # (value, expected-phrases-for-E1, expected-phrases-for-E4)
        (20,
         ["NZ's lowest pharmacy prices"],
         ["Still here when you're ready"]),
        (50,
         ["Free shipping kicks in at $79"],
         ["one or two items from free shipping"]),
        (120,
         ["free-shipping tier ($79+)"],
         ["Free shipping's already on"]),
    ]

    print("\n  Render-testing E1 + E4 across 3 cart values:")
    failures = []
    for value, e1_expect, e4_expect in test_cases:
        for label, tid, expected in [(f"E1-v{value}", e1_tid, e1_expect),
                                       (f"E4-v{value}", e4_tid, e4_expect)]:
            r = render_template(key, tid, value, label)
            if r.status_code != 200:
                failures.append(f"{label} HTTP {r.status_code}")
                print(f"    {label}: ❌ HTTP {r.status_code}")
                continue
            html = r.json()["data"]["attributes"]["html"]
            ok, why = assert_tier_render(html, value, expected)
            if ok:
                print(f"    {label}: ✅ {why}")
            else:
                failures.append(f"{label}: {why}")
                print(f"    {label}: ❌ {why}")

    if failures:
        print(f"\n❌ Phase A FAILED — {len(failures)} render check(s) failed:")
        for f in failures:
            print(f"   - {f}")
        print(f"\nSnapshots: {OUT}")
        # Don't delete the templates; leave them for inspection
        sys.exit(1)

    print(f"\n✅ Phase A complete: 2 templates posted, 6/6 renders verified.")
    return e1_tid, e4_tid


# ----------------------------------------------------------------------
# Phase B: deploy new flow + delete old
# ----------------------------------------------------------------------

def snapshot_old_flow(key):
    print("\n=== Phase B Step 1: snapshot existing Y84ruV ===")
    r = requests.get(
        f"https://a.klaviyo.com/api/flows/{OLD_FLOW_ID}/",
        headers=hdrs(key),
        params={
            "additional-fields[flow]": "definition",
            "include": "flow-actions",
        },
        timeout=30,
    )
    save("phaseB-old-flow-snapshot.json", {"status": r.status_code, "body": r.text})
    if r.status_code == 404:
        print(f"  Old Y84ruV already gone (HTTP 404). Proceeding.")
        return
    if r.status_code != 200:
        sys.exit(f"❌ snapshot failed HTTP {r.status_code}: {r.text[:300]}")
    flow_status = r.json()["data"]["attributes"].get("status", "?")
    print(f"  Snapshotted Y84ruV (status={flow_status})")
    if flow_status == "live":
        sys.exit(f"❌ refusing to delete a LIVE flow. Pause Y84ruV (PATCH status=manual or draft) first.")


def build_new_flow_definition(e1_tid, e4_tid):
    """Build the linear flow definition.

    Structure: trigger Checkout Started -> 1h delay -> E1 -> 23h delay -> E4 -> end
    Profile filter: hasn't placed an order since flow start AND hasn't started another
    checkout since flow start AND has email marketing consent. (Matches the profile
    filter from the prior y84ruv-rebuild attempt.)
    """
    profile_filter = {
        "condition_groups": [
            {"conditions": [{
                "type": "profile-metric",
                "metric_id": METRIC_PLACED_ORDER,
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "flow-start"},
                "metric_filters": None,
            }]},
            {"conditions": [{
                "type": "profile-metric",
                "metric_id": METRIC_CHECKOUT_STARTED,
                "measurement": "count",
                "measurement_filter": {"type": "numeric", "operator": "equals", "value": 0},
                "timeframe_filter": {"type": "date", "operator": "flow-start"},
                "metric_filters": None,
            }]},
            {"conditions": [{
                "type": "profile-marketing-consent",
                "consent": {
                    "channel": "email",
                    "can_receive_marketing": True,
                    "consent_status": {"subscription": "any", "filters": None},
                },
            }]},
        ]
    }

    def send_email_action(temp_id, message_name, subject, preview, template_id, next_id):
        return {
            "temporary_id": temp_id,
            "type": "send-email",
            "data": {
                "message": {
                    "name": message_name,
                    "from_email": "hello@bargainchemist.co.nz",
                    "from_label": "Bargain Chemist",
                    "reply_to_email": "hello@bargainchemist.co.nz",
                    "cc_email": None,
                    "bcc_email": None,
                    "subject_line": subject,
                    "preview_text": preview,
                    "template_id": template_id,
                    "smart_sending_enabled": True,
                    "transactional": False,
                    "add_tracking_params": True,
                    "custom_tracking_params": None,
                    "additional_filters": None,
                },
                "status": "live",  # send actions live so flow processes once flow.status=live
            },
            "links": {"next": next_id},
        }

    def time_delay_action(temp_id, hours, next_id):
        return {
            "temporary_id": temp_id,
            "type": "time-delay",
            "data": {
                "unit": "hours",
                "value": hours,
                "secondary_value": None,
                "timezone": "profile",
            },
            "links": {"next": next_id},
        }

    return {
        "triggers": [{"type": "metric", "id": METRIC_CHECKOUT_STARTED}],
        "profile_filter": profile_filter,
        "entry_action_id": "delay-1",
        "actions": [
            time_delay_action("delay-1", 1, "send-1"),
            send_email_action(
                "send-1",
                "Email #1 — Abandoned Checkout (1h tiered)",
                E1_SUBJECT, E1_PREVIEW,
                e1_tid, "delay-2",
            ),
            time_delay_action("delay-2", 23, "send-2"),
            send_email_action(
                "send-2",
                "Email #4 — Abandoned Checkout (24h tiered, last touch)",
                E4_SUBJECT, E4_PREVIEW,
                e4_tid, None,
            ),
        ],
    }


def post_new_flow(key, e1_tid, e4_tid):
    print("\n=== Phase B Step 2: POST new linear flow ===")
    body = {
        "data": {
            "type": "flow",
            "attributes": {
                "name": NEW_FLOW_NAME,
                "definition": build_new_flow_definition(e1_tid, e4_tid),
            },
        },
    }
    save("phaseB-new-flow-request.json", body)
    r = requests.post("https://a.klaviyo.com/api/flows/",
                      headers=hdrs(key, REVISION_BETA, content=True),
                      json=body, timeout=60)
    save("phaseB-new-flow-response.json",
         {"status": r.status_code, "body": r.text[:8000]})
    if r.status_code not in (200, 201):
        sys.exit(f"❌ POST /api/flows/ failed HTTP {r.status_code}:\n{r.text[:800]}")
    new_flow_id = r.json()["data"]["id"]
    print(f"  New flow created: {new_flow_id} (status=draft)")
    return new_flow_id


def delete_old_flow(key):
    print(f"\n=== Phase B Step 3: DELETE old {OLD_FLOW_ID} ===")
    r = requests.delete(f"https://a.klaviyo.com/api/flows/{OLD_FLOW_ID}/",
                        headers=hdrs(key), timeout=30)
    save("phaseB-delete-old.json", {"status": r.status_code, "body": r.text[:500]})
    if r.status_code in (200, 204):
        print(f"  HTTP {r.status_code}  old Y84ruV deleted")
    elif r.status_code == 404:
        print(f"  HTTP 404  already gone (idempotent rerun)")
    else:
        print(f"  ⚠️  HTTP {r.status_code}  {r.text[:200]}")


def run_phase_b(key, e1_tid, e4_tid):
    snapshot_old_flow(key)
    new_id = post_new_flow(key, e1_tid, e4_tid)
    delete_old_flow(key)
    return new_id


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="Run Phase B (deploy + delete old). Default is dry-run.")
    args = ap.parse_args()

    key = load_key()

    print(f"=== Y84ruV v3 deploy ===")
    print(f"Mode: {'APPLY (will mutate Klaviyo state)' if args.apply else 'DRY-RUN (Phase A only)'}")
    print(f"Snapshots: {OUT}")

    # Phase A always runs
    e1_tid, e4_tid = run_phase_a(key)

    if not args.apply:
        print("\n⚠️  Dry-run complete. To deploy:")
        print("    python .claude/bargain-chemist/scripts/klaviyo_rebuild_y84ruv_v3.py --apply")
        print("\nNew templates remain in account (named 'BC OWNED - Y84ruV-v3 E1/E4 tiered ...')")
        print("for review. Re-run with --apply to deploy the flow.")
        return

    new_flow_id = run_phase_b(key, e1_tid, e4_tid)

    print(f"\n=== ✅ Y84ruV v3 deployed ===")
    print(f"New flow ID: {new_flow_id}")
    print(f"Status: DRAFT (intentional — review before flipping live)")
    print(f"\nNext steps for user:")
    print(f"  1. Open Klaviyo: https://www.klaviyo.com/flow/{new_flow_id}/edit")
    print(f"  2. Send test sends from flow editor at cart $20 / $50 / $120")
    print(f"  3. Confirm 3 distinct banner blocks render correctly")
    print(f"  4. Flip flow to LIVE: PATCH /api/flows/{new_flow_id}/ {{status: live}}")
    print(f"     OR via Klaviyo UI 'Set Live' button")
    print(f"\nSnapshots: {OUT}")


if __name__ == "__main__":
    raise SystemExit(main())
