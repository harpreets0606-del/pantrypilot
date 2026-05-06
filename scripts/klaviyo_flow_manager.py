#!/usr/bin/env python3
"""
Bargain Chemist - Klaviyo Flow Manager
Handles pausing Triple Pixel flows, creating email templates, and building
optimised abandonment flows from scratch via the Klaviyo REST API.

Usage:
    python3 klaviyo_flow_manager.py --pause-triple-pixel
    python3 klaviyo_flow_manager.py --create-templates
    python3 klaviyo_flow_manager.py --create-flows
    python3 klaviyo_flow_manager.py --all
"""

import os
import requests
import json
import argparse
import sys
import time

# Read API key from environment variable (GitHub Actions secret), fall back to local default
API_KEY = os.environ.get("KLAVIYO_API_KEY", "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564")
BASE_URL = "https://a.klaviyo.com/api"
REVISION = "2025-10-15"  # 2025-10-15+ exposes Update Flow Action with message.template_id writes

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ─────────────────────────────────────────────
# Flow IDs
# ─────────────────────────────────────────────
TRIPLE_PIXEL_FLOWS = {
    "RSnNak": "[Z] Browse Abandonment - Triple Pixel",
    "VMKAyS": "[Z] Abandoned Checkout - Triple Pixel",
    "SnakeG": "[Z] Added to Cart Abandonment - Triple Pixel",
}

NATIVE_FLOWS = {
    "Y84ruV": "[Z] Abandoned Checkout",
    "RPQXaa": "[Z] Added to Cart Abandonment",
    "RtiVC5": "[Z] Browse Abandonment",
}


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
REQUEST_TIMEOUT = 30  # seconds — fail fast instead of hanging


def api_get(path, params=None):
    r = requests.get(f"{BASE_URL}/{path}", headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    r.raise_for_status()
    return r.json()


def api_patch(path, payload, quiet=False):
    r = requests.patch(f"{BASE_URL}/{path}", headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    if not quiet:
        print(f"  📡 PATCH {path} → HTTP {r.status_code}")
        if r.content:
            print(f"  📄 Response: {r.text[:500]}")
    if r.status_code not in (200, 204):
        if quiet:
            print(f"  ❌ PATCH {path} → HTTP {r.status_code}: {r.text[:200]}")
        return None
    return r.json() if r.content else {}


def api_post(path, payload):
    r = requests.post(f"{BASE_URL}/{path}", headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    if r.status_code not in (200, 201):
        print(f"  ⚠️  POST {path} → {r.status_code}: {r.text[:300]}")
        return None
    return r.json()


# ─────────────────────────────────────────────
# 1. Pause Triple Pixel Flows
# ─────────────────────────────────────────────
def pause_triple_pixel_flows():
    print("\n🔴 Pausing Triple Pixel Flows...")
    for flow_id, flow_name in TRIPLE_PIXEL_FLOWS.items():
        result = api_patch(f"flows/{flow_id}", {
            "data": {
                "type": "flow",
                "id": flow_id,
                "attributes": {"status": "manual"},
            }
        })
        if result is not None:
            print(f"  ✅ Paused: {flow_name} ({flow_id})")
        time.sleep(0.3)




# ─────────────────────────────────────────────
# 4. Get Metric IDs (needed for flow triggers)
# ─────────────────────────────────────────────
def get_metric_id(name_fragment):
    # Klaviyo 2025-10-15 metrics endpoint rejects page[size] and fields[metric];
    # call with no params and follow next links.
    cursor = None
    while True:
        params = {"page[cursor]": cursor} if cursor else None
        try:
            data = api_get("metrics", params)
        except Exception:
            return None, None
        for m in data.get("data", []):
            name = m.get("attributes", {}).get("name") or ""
            if name_fragment.lower() in name.lower():
                return m["id"], name
        next_link = data.get("links", {}).get("next") or ""
        match = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not match:
            return None, None
        cursor = requests.utils.unquote(match.group(1))


def print_metric_ids():
    print("\n🔍 Fetching key metric IDs...")
    for fragment in ["Started Checkout", "Added to Cart", "Viewed Product"]:
        mid, mname = get_metric_id(fragment)
        if mid:
            print(f"  {mname}: {mid}")
        else:
            print(f"  ⚠️  Not found: {fragment}")


# ─────────────────────────────────────────────
# 5. Create Flow Shells
# NOTE: Klaviyo's public API creates the flow container and trigger.
# Time delays, conditional splits, and message assignments must be
# added in the Klaviyo UI — the API does not expose write endpoints
# for flow actions/messages. Use the template IDs above when adding
# messages in the UI.
# ─────────────────────────────────────────────
def create_flow_shell(name, metric_id, status="draft"):
    payload = {
        "data": {
            "type": "flow",
            "attributes": {
                "name": name,
                "status": status,
            },
            "relationships": {
                "flow-triggers": {
                    "data": [{"type": "metric", "id": metric_id}]
                }
            }
        }
    }
    result = api_post("flows", payload)
    if result:
        fid = result["data"]["id"]
        print(f"  ✅ Created flow shell: {name} → ID: {fid}")
        return fid
    return None


def create_flow_shells():
    print("\n🏗️  Creating Flow Shells (Draft)...")
    print_metric_ids()

    checkout_metric_id, _ = get_metric_id("Started Checkout")
    atc_metric_id, _ = get_metric_id("Added to Cart")
    browse_metric_id, _ = get_metric_id("Viewed Product")

    flows = {}

    if checkout_metric_id:
        flows["checkout"] = create_flow_shell(
            "[Z] Abandoned Checkout v2", checkout_metric_id
        )
    else:
        print("  ⚠️  Could not find 'Started Checkout' metric — skipping checkout flow")

    if atc_metric_id:
        flows["atc"] = create_flow_shell(
            "[Z] Added to Cart Abandonment v2", atc_metric_id
        )
    else:
        print("  ⚠️  Could not find 'Added to Cart' metric — skipping ATC flow")

    if browse_metric_id:
        flows["browse"] = create_flow_shell(
            "[Z] Browse Abandonment v2", browse_metric_id
        )
    else:
        print("  ⚠️  Could not find 'Viewed Product' metric — skipping browse flow")

    print("\n📋 Flow IDs (open these in Klaviyo UI to add delays/splits/messages):")
    for key, fid in flows.items():
        if fid:
            url = f"https://www.klaviyo.com/flow/{fid}/edit"
            print(f"  {key}: {fid}  →  {url}")

    return flows


# ─────────────────────────────────────────────
# 6. Print UI Setup Guide
# ─────────────────────────────────────────────
def print_setup_guide(templates, flows):
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║          KLAVIYO UI SETUP GUIDE — Complete in the Klaviyo Dashboard          ║
╚══════════════════════════════════════════════════════════════════════════════╝

The flow shells and templates have been created. Now open each flow in Klaviyo
and add the structure below.

──────────────────────────────────────────────
[Z] ABANDONED CHECKOUT v2
──────────────────────────────────────────────
Trigger:        Started Checkout metric
Re-entry:       Allow re-entry (no time restriction)
Smart sending:  ON (16hr window) on every email

Structure:
  ① Email 1  "One step away from everyday savings"   ← keep existing template
     ↓  Wait 23 hours
  ② Trigger Split: event.value >= 200
        YES → Email 2a  "High-value cart — no coupon"    ← keep existing
        NO  → Email 2b  "Standard cart — no coupon"      ← keep existing
     ↓  Wait 48 hours
  ③ Email 3  (template: [Z] Abandoned Checkout – Email 3 (72hr Final))
             Subject: "⏰ Last chance – your cart expires today"
             Preview: "We've held your items for 72 hours..."

  FIX to apply: In the Trigger Split, change $value condition from 79 → 200
                to match the email naming convention.

──────────────────────────────────────────────
[Z] BROWSE ABANDONMENT v2
──────────────────────────────────────────────
Trigger:        Viewed Product metric
Re-entry:       Allow re-entry after 7 days
Smart sending:  ON (16hr window)

Structure:
  ① Email 1  ← keep existing template
              Subject: "You were just looking at something great..."
     ↓  Wait 24 hours
  ② Email 2  (template: [Z] Browse Abandonment – Email 2 (24hr Social Proof))
              Subject: "Still thinking it over, {{ first_name }}?"
              Preview: "Here's why 100,000+ Kiwis choose Bargain Chemist"
     ↓  Wait 48 hours
  ③ Email 3  (template: [Z] Browse Abandonment – Email 3 (72hr Bestsellers))
              Subject: "Our customers also love these 👇"
              Preview: "Top sellers to pair with what you were browsing"

──────────────────────────────────────────────
[Z] ADDED TO CART ABANDONMENT v2
──────────────────────────────────────────────
Trigger:        Added to Cart metric
Re-entry:       Allow re-entry (no time restriction)
Smart sending:  ON (16hr window)

Structure:
  ① Email 1  ← keep existing template
              Subject: "You left something in your cart"
     ↓  Wait 1 hour
  ② Email 2  ← keep existing template
              Subject: "Ready when you are — your cart is waiting"
     ↓  Wait 48 hours
  ③ Email 3  (template: [Z] ATC Abandonment – Email 3 (72hr Final))
              Subject: "⚠️ Your cart is about to expire, {{ first_name }}"
              Preview: "Final reminder — limited stock"

──────────────────────────────────────────────
FLOWS TO KEEP PAUSED (already done):
──────────────────────────────────────────────
  ✅ [Z] Browse Abandonment - Triple Pixel  (RSnNak)
  ✅ [Z] Abandoned Checkout - Triple Pixel  (VMKAyS)
  ✅ [Z] Added to Cart Abandonment - Triple Pixel  (SnakeG)
""")


# ─────────────────────────────────────────────
# 7. Audit Flows — traverse every flow → action → message → template
#    and check each template against compliance + brand rules
# ─────────────────────────────────────────────
import re

AUDIT_RULES = [
    # (name, regex, severity, description)
    ("Stale free shipping ($49)", re.compile(r"\$\s?49\b|over\s+\$?49"), "🔴", "References $49 free shipping (current threshold is $79)"),
    ("Stale free shipping ($50)", re.compile(r"\$\s?50\b|over\s+\$?50"), "🔴", "References $50 free shipping (current threshold is $79)"),
    ("Coupon/discount code", re.compile(r"\b(coupon|promo\s*code|discount\s*code|use\s*code|enter\s*code|\d+%\s*off|save\s+\d+%)\b", re.I), "🔴", "Mentions coupon/discount code (we cannot apply codes)"),
    ("Fear language: expires", re.compile(r"\b(expire(s|d)?|expiring)\b", re.I), "🟠", "ASA Code: 'expires today' borders on play-on-fear"),
    ("Fear language: last chance", re.compile(r"last\s*chance", re.I), "🟠", "Aggressive urgency, off-brand for Bargain Chemist"),
    ("Fear language: stock alert", re.compile(r"stock\s*alert|running\s*out\s*fast|don't\s*miss", re.I), "🟠", "Pressure-based scarcity, ASA borderline"),
    ("Fear language: act now", re.compile(r"act\s*now|hurry|grab\s*yours", re.I), "🟠", "High-pressure CTAs"),
    ("Missing 'always read the label'", re.compile(r"always\s*read\s*the\s*label", re.I), "✓check", "ASA mandatory disclaimer for therapeutic products"),
    ("Missing 'symptoms persist' disclaimer", re.compile(r"symptoms\s*persist", re.I), "✓check", "ASA mandatory disclaimer for therapeutic products"),
    ("Missing UEMA business identifier", re.compile(r"bargain\s*chemist\s*limited", re.I), "✓check", "UEMA s9: business legal name in footer"),
    ("Missing physical address", re.compile(r"\b(christchurch|auckland|wellington|new\s*zealand|nz\b)", re.I), "✓check", "UEMA s9: physical address in footer"),
    ("Missing unsubscribe", re.compile(r"\{%\s*unsubscribe", re.I), "✓check", "UEMA s11: functional unsubscribe link"),
]


def safe_get(path, params=None, debug=False):
    """GET that returns None on error and logs failure when debug=True."""
    r = requests.get(f"{BASE_URL}/{path}", headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
    if r.status_code == 200:
        return r.json()
    if debug:
        print(f"  ⚠️  GET {path} → {r.status_code}: {r.text[:300]}")
    return None


def get_flow_actions(flow_id, debug=False):
    # Drop fieldset filter — revision 2025-10-15 renamed/removed some fields
    data = safe_get(f"flows/{flow_id}/flow-actions", debug=debug)
    if not data:
        return []
    return data.get("data", [])


def get_messages_for_action(action_id, debug=False):
    data = safe_get(f"flow-actions/{action_id}/flow-messages", debug=debug)
    if not data:
        return []
    return data.get("data", [])


def get_template_id_for_message(message_id, debug=False):
    data = safe_get(f"flow-messages/{message_id}/relationships/template", debug=debug)
    if not data or not data.get("data"):
        return None
    return data["data"].get("id")


_MESSAGE_DEBUG_DUMPED = False
_FAILURE_DEBUG_DUMPED = False


def get_message_content(message_id, debug=False):
    """Fetch full flow-message and return its content dict (from_email, subject_line, etc.).
    Klaviyo requires these fields when PATCHing a flow-action's email message."""
    global _MESSAGE_DEBUG_DUMPED
    data = safe_get(f"flow-messages/{message_id}", debug=debug)
    if not data:
        return {}
    attrs = data.get("data", {}).get("attributes", {}) or {}
    if not _MESSAGE_DEBUG_DUMPED:
        _MESSAGE_DEBUG_DUMPED = True
        defn = attrs.get("definition") or {}
        print(f"  🔍 DEBUG flow-message {message_id} attribute keys: {list(attrs.keys())}")
        print(f"  🔍 DEBUG definition keys: {list(defn.keys()) if isinstance(defn, dict) else type(defn).__name__}")
    # In revision 2025-10-15+, email content lives under attributes.definition
    # (with from_email, from_label, subject_line, preview_text, template_id, etc.)
    return attrs.get("definition") or attrs.get("content") or {}


def build_flow_email_payload(content, new_template_id):
    """Build a complete FlowEmail object for PATCH /api/flow-actions, preserving
    all existing required fields (from_email, from_label, subject_line, etc.)
    and only swapping the template_id."""
    msg = {"template_id": new_template_id}
    # Preserve message identity so Klaviyo treats this as updating the existing
    # message (allowed) rather than replacing it (blocked as "link change")
    if content.get("id"):
        msg["id"] = content["id"]
    if content.get("name"):
        msg["name"] = content["name"]
    # Pass-through required + optional FlowEmail fields from existing content
    for k in ("from_email", "from_label", "reply_to_email", "cc_email", "bcc_email",
              "subject_line", "preview_text", "smart_sending_enabled",
              "transactional", "add_tracking_params", "custom_tracking_params",
              "additional_filters"):
        if k in content and content[k] is not None:
            msg[k] = content[k]
    # Some Klaviyo responses use `subject` rather than `subject_line` — normalize
    if "subject_line" not in msg and content.get("subject"):
        msg["subject_line"] = content["subject"]
    return msg


def get_template_html(template_id):
    data = safe_get(f"templates/{template_id}")
    if not data:
        return None
    return data.get("data", {}).get("attributes", {}).get("html", "")


def audit_template(html, name=""):
    """Run all audit rules against a template's HTML. Returns list of findings."""
    findings = []
    if not html:
        return [("🔴", "Empty template", "Template HTML is empty or missing")]
    for rule_name, regex, severity, desc in AUDIT_RULES:
        match = regex.search(html)
        if severity == "✓check":
            # These rules check for REQUIRED content — flag if MISSING
            if not match:
                findings.append(("🔴", rule_name, desc))
        else:
            # These rules check for FORBIDDEN content — flag if PRESENT
            if match:
                snippet = match.group(0)
                findings.append((severity, rule_name, f"{desc} (found: '{snippet}')"))
    return findings


def audit_all_flows():
    """Pull all live/draft flows, traverse to messages, audit templates."""
    print("\n🔍 AUDITING ALL FLOWS")
    print("=" * 80)

    # Get all flows (paginated - Klaviyo caps page size at 50)
    flows = []
    cursor = None
    while True:
        params = {"fields[flow]": "name,status,trigger_type,archived",
                  "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params, debug=True)
        if not page:
            print("  ❌ Failed to fetch flows")
            return
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next")
        if not next_link:
            break
        # Extract cursor from next link
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))
    print(f"\nFound {len(flows)} total flows. Auditing email templates...\n")

    summary = {"flows_checked": 0, "templates_checked": 0, "issues_found": 0, "critical": 0}
    flow_reports = []

    for flow in flows:
        flow_id = flow["id"]
        attrs = flow["attributes"]
        flow_name = attrs["name"]
        status = attrs["status"]

        # Skip archived flows
        if attrs.get("archived"):
            continue
        # Only audit flows that could send (live or were live recently)
        if status not in ("live", "draft", "manual"):
            print(f"  ⏭️  Skipping {flow_name} (status: {status})")
            continue

        print(f"  📂 Auditing: {flow_name} ({flow_id}, {status})")
        actions = get_flow_actions(flow_id, debug=True)
        print(f"     → Found {len(actions)} flow actions")
        if not actions:
            continue

        flow_findings = []
        for action in actions:
            action_id = action["id"]
            action_type = action.get("attributes", {}).get("action_type", "?")
            messages = get_messages_for_action(action_id, debug=False)
            if messages:
                print(f"     → Action {action_id} ({action_type}): {len(messages)} message(s)")
            for msg in messages:
                msg_id = msg["id"]
                msg_attrs = msg.get("attributes", {})
                msg_name = msg_attrs.get("name", "Unnamed")
                channel = msg_attrs.get("channel", "")

                # Channel may be capitalised or absent — accept email/EMAIL/empty
                if channel and channel.lower() not in ("email", ""):
                    print(f"        ⏭️  Skipping non-email message (channel: {channel})")
                    continue

                # Subject + preview from message content
                content = msg_attrs.get("content") or {}
                subject = content.get("subject", "") or ""
                preview = content.get("preview_text", "") or ""

                # Get the template HTML
                template_id = get_template_id_for_message(msg_id, debug=True)
                html = get_template_html(template_id) if template_id else ""

                # Audit subject + preview + html together
                combined = f"{subject}\n{preview}\n{html}"
                findings = audit_template(combined, msg_name)

                # Always record every email message — even if no findings
                flow_findings.append({
                    "msg_id": msg_id,
                    "msg_name": msg_name,
                    "subject": subject,
                    "preview": preview,
                    "template_id": template_id,
                    "html_len": len(html),
                    "findings": findings,
                })
                summary["templates_checked"] += 1
                summary["issues_found"] += len(findings)
                summary["critical"] += sum(1 for f in findings if f[0] == "🔴")

                time.sleep(0.15)  # rate limit safety

        if flow_findings:
            summary["flows_checked"] += 1
            flow_reports.append({
                "id": flow_id,
                "name": flow_name,
                "status": status,
                "messages": flow_findings,
            })

    # Print report
    print("\n" + "=" * 80)
    print("DETAILED REPORT")
    print("=" * 80)
    for report in flow_reports:
        print("\n┌" + "─" * 78 + "┐")
        print(f"│ {report['name']}")
        print(f"│ ID: {report['id']}  ·  Status: {report['status']}")
        print("└" + "─" * 78 + "┘")
        for msg in report["messages"]:
            print(f"\n  📧 {msg['msg_name']} ({msg['msg_id']})")
            print(f"     Subject: {msg['subject'] or '(empty)'}")
            print(f"     Preview: {msg['preview'] or '(empty)'}")
            print(f"     Template: {msg['template_id'] or '(none)'}  ·  HTML: {msg['html_len']} bytes")
            if not msg["findings"]:
                print("     ✅ No issues found")
            else:
                for severity, rule, desc in msg["findings"]:
                    print(f"     {severity} {rule}: {desc}")

    print("=" * 80)
    print(f"AUDIT SUMMARY")
    print(f"  Flows audited:     {summary['flows_checked']}")
    print(f"  Email templates:   {summary['templates_checked']}")
    print(f"  Total findings:    {summary['issues_found']}")
    print(f"  Critical (🔴):     {summary['critical']}")
    print("=" * 80)


# ─────────────────────────────────────────────
# 8. Fix Issues Found by Audit
# ─────────────────────────────────────────────

# UEMA s9 + ASA mandatory content block injected at the bottom of every template.
# NOTE: Verify the physical address against Bargain Chemist Limited NZBN records
#       before running this in production.
COMPLIANCE_FOOTER_HTML = """\

<!-- ── UEMA & ASA Mandatory Footer (auto-injected) ── -->
<table width="100%" border="0" cellpadding="0" cellspacing="0" bgcolor="#f4f4f4">
<tr><td align="center" style="padding:16px 24px; font-family:Arial,Helvetica,sans-serif;
  font-size:11px; color:#888888; line-height:1.7;">
  <p style="margin:0 0 6px 0;">
    <strong>Bargain Chemist Limited</strong>&nbsp;&middot;&nbsp;
    192 Moorhouse Avenue, Christchurch 8011, New Zealand
  </p>
  <p style="margin:0 0 6px 0; font-size:10px; color:#aaaaaa;">
    Always read the label and use as directed.
    If symptoms persist, see your healthcare professional.
  </p>
  <p style="margin:0;">
    <a href="{{ organization.homepage }}" style="color:#FF0031; text-decoration:none;">Visit our store</a>
    &nbsp;|&nbsp; {% unsubscribe 'Unsubscribe' %}
  </p>
</td></tr>
</table>"""

# Templates confirmed to have stale $49 / $50 free-shipping copy (audit finding).
# IDs sourced from the --audit-flows run. Verify these still match if flows are rebuilt.
STALE_THRESHOLD_TEMPLATE_IDS = [
    ("TTVgr7", "Flu Season Email 2"),
    ("V7tfwK", "Order Confirmation"),
    ("WALe6F", "Campaign template (main branded)"),
]

# Templates containing coupon/promo-code content that must not be sent.
# These cannot be auto-fixed — they need manual replacement or flow deletion.
COUPON_TEMPLATE_IDS = [
    ("W7iN2X", "Welcome Series – $8 Coupon variant"),
    ("T8ZzzJ", "Welcome Series – $15 Coupon variant"),
    ("UCGbPH", "Welcome Series – coupon variant"),
    ("Ut6eYe", "Abandoned Checkout – coupon branch (high value)"),
    ("Uszq8z", "Abandoned Checkout – coupon branch (standard)"),
]

# Templates with fear language that needs copy rewriting (ASA Code Rule 1b).
FEAR_LANGUAGE_TEMPLATE_IDS = [
    ("W2Sbja", "Back in Stock Email 1 – 'Don't miss' / 'Grab yours'"),
    ("Xch2d2", "Back in Stock Email 2 – 'Don't miss'"),
    ("R8QdnF", "Replenishment – Oracoat – 'don't miss'"),
]


def _fetch_all_templates():
    """
    Return all email templates by traversing every active flow →
    actions → email messages → template relationships.

    We do NOT use GET /api/templates because flow-internal templates
    (the templates auto-created when you add an email node to a flow)
    are not always returned by that endpoint, depending on the API
    key's scope. The flow-message → template relationship is the
    reliable way to discover every template that actually sends.
    """
    print("  📡 Walking flows to discover templates...")

    # 1. Get all flows (paginated)
    flows = []
    cursor = None
    while True:
        params = {"fields[flow]": "name,status,archived", "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params, debug=True)
        if not page:
            break
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next")
        if not next_link:
            break
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    # 2. Walk each non-archived flow → actions → messages → template IDs
    seen = {}  # template_id -> friendly name (first message that uses it)
    for flow in flows:
        attrs = flow.get("attributes", {})
        if attrs.get("archived"):
            continue
        # Skip only clearly inactive states; revision 2025-10-15 may use new enum values
        status = (attrs.get("status") or "").lower()
        if status in ("archived", "deleted"):
            continue

        actions = get_flow_actions(flow["id"])
        for action in actions:
            messages = get_messages_for_action(action["id"])
            for msg in messages:
                channel = (msg.get("attributes", {}).get("channel") or "").lower()
                if channel and channel not in ("email", ""):
                    continue
                tid = get_template_id_for_message(msg["id"])
                if tid and tid not in seen:
                    msg_name = msg.get("attributes", {}).get("name", "(unnamed)")
                    flow_name = attrs.get("name", "?")
                    seen[tid] = f"{flow_name} → {msg_name}"
                time.sleep(0.05)

    # Convert to the same shape as a /api/templates response
    return [{"id": tid, "attributes": {"name": label}} for tid, label in seen.items()]


def _list_existing_compliance_templates():
    """Return {original_msg_name: template_id} for all '[COMPLIANCE] ...' templates.

    Lists all templates (no server-side filter — that endpoint has been flaky
    on this account) and filters client-side. Pages through 50 at a time.
    """
    existing = {}
    cursor = None
    page_count = 0
    total_seen = 0
    while True:
        params = {"fields[template]": "name", "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("templates", params=params, debug=True)
        if not page:
            print(f"  ⚠️  GET /api/templates returned no data on page {page_count + 1}")
            break
        page_count += 1
        page_data = page.get("data", [])
        total_seen += len(page_data)
        for tpl in page_data:
            name = tpl.get("attributes", {}).get("name", "")
            if name.startswith("[COMPLIANCE] "):
                existing[name[len("[COMPLIANCE] "):]] = tpl["id"]
        next_link = page.get("links", {}).get("next")
        if not next_link:
            break
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))
    print(f"  📊 Walked {page_count} page(s), saw {total_seen} total templates, "
          f"{len(existing)} match '[COMPLIANCE] *'")
    return existing


def fix_compliance_footers():
    """
    Inject UEMA + ASA mandatory footer into every email flow message whose
    template is missing 'Bargain Chemist Limited'.

    Klaviyo's API does NOT expose a write endpoint for either:
      • PATCH /api/templates/{id} on flow-embedded templates  (404)
      • PATCH /api/flow-messages/{id} or its relationships     (405)

    So for flow-embedded templates we create a new '[COMPLIANCE] <msg name>'
    standalone template containing the patched HTML, and print a copy/paste
    list of UI swaps the user needs to make in the Klaviyo flow editor.
    Existing [COMPLIANCE] templates are reused on re-runs to avoid duplicates.
    """
    print("\n🔧 Fixing UEMA compliance footers across all flow email messages...")

    # Collect all active flows
    flows = []
    cursor = None
    while True:
        params = {"fields[flow]": "name,status,archived", "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params, debug=True)
        if not page:
            break
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next")
        if not next_link:
            break
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    print(f"  Found {len(flows)} total flows. Walking email messages...")

    # Use local cache only (API listing falls back during --rebind-templates if needed)
    print("  Loading local [COMPLIANCE] cache...")
    existing_compliance = _load_compliance_cache()
    print(f"  Loaded {len(existing_compliance)} existing [COMPLIANCE] templates from cache\n")

    fixed = skipped = failed = direct_patched = rebound = 0
    manual_needed = []

    for flow in flows:
        attrs = flow.get("attributes", {})
        if attrs.get("archived"):
            continue
        # Skip only clearly inactive states; revision 2025-10-15 may use new enum values
        status = (attrs.get("status") or "").lower()
        if status in ("archived", "deleted"):
            continue

        flow_name = attrs.get("name", "?")
        actions = get_flow_actions(flow["id"])
        print(f"  📂 {flow_name} (status={status!r}) — {len(actions)} actions")

        for action in actions:
            messages = get_messages_for_action(action["id"], debug=True)
            if messages:
                print(f"     ↳ action {action['id']}: {len(messages)} message(s)")
            for msg in messages:
                channel = (msg.get("attributes", {}).get("channel") or "").lower()
                if channel and channel not in ("email", ""):
                    print(f"        ⏭️  skipping non-email channel: {channel!r}")
                    continue

                msg_id = msg["id"]
                msg_name = msg.get("attributes", {}).get("name") or f"msg_{msg_id}"
                label = f"{flow_name} → {msg_name}"

                # Get this message's template ID + HTML
                template_id = get_template_id_for_message(msg_id)
                if not template_id:
                    print(f"  ⚠️  No template found for: {label}")
                    time.sleep(0.05)
                    continue

                html = get_template_html(template_id) or ""

                # Skip if already compliant
                if re.search(r"bargain\s*chemist\s*limited", html, re.I):
                    print(f"  ✅ Already compliant: {label}")
                    skipped += 1
                    time.sleep(0.05)
                    continue

                # Build the patched HTML
                tag = "</body>"
                pos = html.lower().rfind(tag)
                if pos != -1:
                    new_html = html[:pos] + COMPLIANCE_FOOTER_HTML + "\n" + html[pos:]
                else:
                    new_html = html + COMPLIANCE_FOOTER_HTML

                # ── Strategy A: try patching the template directly (silent on 404 — expected for embedded) ──
                direct_url = f"{BASE_URL}/templates/{template_id}"
                r = requests.patch(direct_url, headers=HEADERS, json={
                    "data": {
                        "type": "template",
                        "id": template_id,
                        "attributes": {"html": new_html},
                    }
                }, timeout=REQUEST_TIMEOUT)
                if r.status_code in (200, 204):
                    print(f"  ✅ Patched directly (library template): {label}")
                    direct_patched += 1
                    fixed += 1
                    time.sleep(0.3)
                    continue

                # ── Strategy B: create / reuse '[COMPLIANCE]' template, log for UI swap ──
                if msg_name in existing_compliance:
                    new_tid = existing_compliance[msg_name]
                    # Update the existing [COMPLIANCE] template's HTML to the latest patched version
                    upd = api_patch(f"templates/{new_tid}", {
                        "data": {
                            "type": "template",
                            "id": new_tid,
                            "attributes": {"html": new_html},
                        }
                    }, quiet=True)
                    if upd is not None:
                        print(f"  ♻️  Reused existing [COMPLIANCE] template ({new_tid}): {label}")
                    else:
                        print(f"  📋 [COMPLIANCE] template exists ({new_tid}): {label}")
                else:
                    new_tpl = api_post("templates", {
                        "data": {
                            "type": "template",
                            "attributes": {
                                "name": f"[COMPLIANCE] {msg_name[:70]}",
                                "editor_type": "CODE",
                                "html": new_html,
                            }
                        }
                    })
                    if not new_tpl:
                        print(f"  ❌ Could not create [COMPLIANCE] template for: {label}")
                        failed += 1
                        time.sleep(0.2)
                        continue
                    new_tid = new_tpl["data"]["id"]
                    print(f"  📋 Created [COMPLIANCE] template ({new_tid}): {label}")

                # Persist to local cache immediately (survives crashes)
                existing_compliance[msg_name] = new_tid
                _save_compliance_cache(existing_compliance)

                # Try to rebind the flow action right now via 2025-10-15 API
                msg_content = get_message_content(msg_id)
                rebind_payload = {
                    "data": {
                        "type": "flow-action",
                        "id": action["id"],
                        "attributes": {
                            "definition": {
                                "id": action["id"],
                                "type": "send-email",
                                "data": {
                                    "message": build_flow_email_payload(msg_content, new_tid)
                                }
                            }
                        }
                    }
                }
                rebind_result = api_patch(f"flow-actions/{action['id']}",
                                          rebind_payload, quiet=True)
                if rebind_result is not None:
                    print(f"  🔁 Rebound flow action to new template: {label}")
                    rebound += 1
                else:
                    # Diagnostic: dump the failing action's structure once so we can see
                    # if there's a pattern (action_type mismatch, locked relationships, etc.)
                    global _FAILURE_DEBUG_DUMPED
                    if not _FAILURE_DEBUG_DUMPED:
                        _FAILURE_DEBUG_DUMPED = True
                        raw = safe_get(f"flow-actions/{action['id']}")
                        if raw:
                            d = raw.get("data", {})
                            a = d.get("attributes", {}) or {}
                            print(f"  🔍 DEBUG failed action {action['id']} keys: {list(a.keys())}")
                            print(f"  🔍 DEBUG action_type: {a.get('action_type')!r}")
                            defn = a.get("definition") or {}
                            if isinstance(defn, dict):
                                print(f"  🔍 DEBUG definition.type: {defn.get('type')!r}")
                                print(f"  🔍 DEBUG definition keys: {list(defn.keys())}")
                            print(f"  🔍 DEBUG links: {json.dumps(d.get('links'))[:300]}")
                    manual_needed.append({
                        "flow": flow_name,
                        "message": msg_name,
                        "msg_id": msg_id,
                        "action_id": action["id"],
                        "new_template_id": new_tid,
                    })
                fixed += 1

                time.sleep(0.4)

    print("\n" + "=" * 80)
    print(f"FOOTER FIX SUMMARY")
    print(f"  Patched directly (library templates):     {direct_patched}")
    print(f"  Rebound automatically (PATCH flow-action): {rebound}")
    print(f"  [COMPLIANCE] templates ready to swap UI:  {len(manual_needed)}")
    print(f"  Already compliant (skipped):              {skipped}")
    print(f"  Failed:                                   {failed}")
    print("=" * 80)

    if manual_needed:
        # Group by flow for readability
        by_flow = {}
        for item in manual_needed:
            by_flow.setdefault(item["flow"], []).append(item)

        print(f"""
📋 MANUAL UI SWAP — {len(manual_needed)} email message(s) across {len(by_flow)} flow(s)

   The compliance-patched HTML is already saved as new templates in your
   Klaviyo library (named '[COMPLIANCE] <message name>'). To activate them:

   For each row below:
     1. Flows → open the flow listed
     2. Click the email message node
     3. Click 'Edit Email' → 'Change Template'
     4. Search for the [COMPLIANCE] template → select → Save
""")
        for flow_name, items in by_flow.items():
            print(f"   ━━━ {flow_name} ━━━")
            for it in items:
                print(f"     • {it['message']}")
                print(f"       Template ID: {it['new_template_id']}  (search: \"[COMPLIANCE] {it['message'][:40]}\")")
            print()

    if manual_needed or fixed > 0:
        print("\n  Run --audit-flows after completing UI swaps to verify compliance.")


def fix_stale_thresholds():
    """
    Replace stale free-shipping copy ($49/$50) with $79 in the specific
    templates identified by --audit-flows.

    Uses conservative regex targeting shipping/delivery context only, so
    product prices at $49/$50 are NOT accidentally changed.
    """
    print("\n🔧 Fixing stale free-shipping thresholds ($49/$50 → $79)...")

    patterns_and_replacements = [
        # "over $49" / "over $50" — shipping threshold copy
        (re.compile(r"(over\s+)\$?(49|50)\b", re.I), r"\g<1>$79"),
        # "orders over 49" / "orders over 50"
        (re.compile(r"(orders?\s+over\s+)\$?(49|50)\b", re.I), r"\g<1>$79"),
        # "$49 free shipping" / "$50 free delivery"
        (re.compile(r"\$(49|50)(\s+(?:free|to unlock|for free))", re.I), r"$79\g<2>"),
        # "free shipping on $49" etc.
        (re.compile(r"(free\s+(?:shipping|delivery)\s+on\s+(?:orders?\s+)?)\$?(49|50)\b", re.I), r"\g<1>$79"),
    ]

    fixed = 0
    skipped_missing = []
    for tid, tname in STALE_THRESHOLD_TEMPLATE_IDS:
        full = safe_get(f"templates/{tid}")
        if not full:
            print(f"  ⚠️  Template {tid} ({tname}) does not exist as a "
                  f"standalone template — the $49/$50 hit was likely in "
                  f"the message SUBJECT line, not the template HTML. "
                  f"Update the subject in the Klaviyo flow UI.")
            skipped_missing.append((tid, tname))
            continue

        html = full.get("data", {}).get("attributes", {}).get("html", "") or ""
        original = html

        for pattern, replacement in patterns_and_replacements:
            html = pattern.sub(replacement, html)

        if html == original:
            print(f"  ⏭️  No stale threshold found: {tname} ({tid}) — may have been fixed already")
            continue

        result = api_patch(f"templates/{tid}", {
            "data": {
                "type": "template",
                "id": tid,
                "attributes": {"html": html},
            }
        }, quiet=True)

        if result is not None:
            print(f"  ✅ Threshold fixed: {tname} ({tid})")
            fixed += 1
        else:
            print(f"  ❌ Patch failed: {tname} ({tid})")

        time.sleep(0.3)

    print(f"\n  Threshold fix summary → {fixed} template(s) patched")
    if skipped_missing:
        print(f"  Manual UI fix needed for these (subject-line $49/$50):")
        for tid, tname in skipped_missing:
            print(f"    • {tname} (template ref: {tid}) — open the flow, "
                  f"edit the email's subject line, change $49/$50 → $79")


def report_manual_fixes_required():
    """
    Print a clear action list for issues that cannot be auto-patched:
    coupon content, fear language rewrites, empty preview text, and
    structural flow problems.
    """
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              MANUAL FIXES REQUIRED — CANNOT BE AUTO-PATCHED                 ║
╚══════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔴  A. COUPON TEMPLATE REMOVAL (Welcome Series + ATC branches)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  These templates offer discount/promo codes which we cannot apply.
  The Welcome Series flow is already paused — do NOT re-activate until fixed.

  Action for each:
    1. Open template in Klaviyo → rewrite body to remove all coupon references.
    2. Replace incentive with: free shipping reminder ($79), social proof,
       value/wellness messaging, or product spotlight.
    3. OR: delete the email node from the flow entirely.

  Templates:
    • W7iN2X — Welcome Series – "$8 Coupon" variant
    • T8ZzzJ — Welcome Series – "$15 Coupon" variant
    • UCGbPH — Welcome Series – coupon variant
    • Ut6eYe — Abandoned Checkout – high-value coupon branch (A: over $200)
    • Uszq8z — Abandoned Checkout – standard coupon branch

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟠  B. FEAR LANGUAGE REWRITES (ASA Code Rule 1b)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Replace fear/pressure copy with warm, wellness-coded alternatives.
  Brand voice guide: "Discover", "Support", "Meet", "Feel good".

  W2Sbja — Back in Stock Email 1
    ✗ "Don't miss" → ✓ "Back for a reason"
    ✗ "Grab yours" → ✓ "Discover it again" / "It's back — shop now"

  Xch2d2 — Back in Stock Email 2
    ✗ "Don't miss" → ✓ "Still interested?" / "It's back in stock"

  R8QdnF — Replenishment – Oracoat
    ✗ "Don't miss" → ✓ "Time to restock?" / "Your supply may be running low"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡  C. EMPTY PREVIEW TEXT (16 Replenishment + 5 other emails)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Preview text is set at the flow-message level (not template level).
  Must be updated via Klaviyo UI: Flow → Email node → Edit → Preview text.

  Flows affected:
    • [Z] Win-back Email 1 (XRDX9U) — e.g. "We miss you — here's what's new"
    • [Z] Win-back Email 2 (Rekdpd) — e.g. "Your favourite products are waiting"
    • [Z] Welcome Series – No Coupon E1/E2/E3 — add descriptive preview per email
    • All 16 Replenishment flow emails — add product-specific reminder copy

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡  D. STRUCTURAL FLOW ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  1. Win-back trigger: currently Metric-based — should be Date Based
     trigger (last active/purchase date) or a segment-entry trigger.
     Fix in UI: Flows → Win-back → Trigger settings → change to
     "Segment trigger" or "Date property based on last purchase".

  2. Order Confirmation: verify it is not double-sending with the
     Shopify native order confirmation email.
     Check: Shopify Admin → Settings → Notifications — if "Order
     confirmation" is enabled there AND in Klaviyo, customers get two.
     Recommended: disable Shopify's native version once Klaviyo is confirmed working.

  3. Abandoned Checkout coupon split: the $200 split threshold is
     named "over $200 - coupon" but coupons cannot be applied.
     Once coupon emails are rewritten, rename the branch and confirm
     the split logic serves the right value-tiered messaging.

  4. _pharmacist-only (S3) product exclusion: no flow currently
     filters these out. Add a profile/event property filter to all
     promotional flows: "event.ProductType is not _pharmacist-only".
     This requires a custom Shopify→Klaviyo property mapping first.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅  AUTO-FIXED BY --fix-templates
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • UEMA footer (Bargain Chemist Limited + address + disclaimers +
    unsubscribe) injected into all 49 templates
  • Stale $49/$50 free shipping threshold corrected to $79 in:
    TTVgr7 (Flu Season E2), V7tfwK (Order Confirmation), WALe6F (campaign)
""")


COMPLIANCE_CACHE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), ".compliance_templates.json"
)


def _load_compliance_cache():
    """Read msg_name -> template_id mapping from local JSON cache."""
    if not os.path.exists(COMPLIANCE_CACHE_PATH):
        return {}
    try:
        with open(COMPLIANCE_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _save_compliance_cache(mapping):
    """Persist msg_name -> template_id mapping so --rebind-templates always finds them."""
    try:
        with open(COMPLIANCE_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
    except OSError as e:
        print(f"  ⚠️  Could not write {COMPLIANCE_CACHE_PATH}: {e}")


def rebind_compliance_templates():
    """
    Walk every flow's email actions and re-point each one to its matching
    '[COMPLIANCE] <message name>' template via PATCH /api/flow-actions/{id}.

    This uses Klaviyo's Update Flow Action endpoint, which (as of revision
    2025-10-15) accepts message content writes including template_id. It
    fully eliminates the need for manual UI template swaps.

    Prerequisites:
      • You must have already run --fix-footers so the [COMPLIANCE] templates
        exist in the Klaviyo library (one per flow message).

    Source of truth: local JSON cache at scripts/.compliance_templates.json,
    populated automatically by --fix-footers. Falls back to GET /api/templates
    if the cache is empty.
    """
    print("\n🔁 Rebinding flow email actions to their [COMPLIANCE] templates...")
    print(f"  Using API revision: {REVISION}\n")

    # Try local cache first — robust against /api/templates list quirks
    compliance = _load_compliance_cache()
    if compliance:
        print(f"  Loaded {len(compliance)} [COMPLIANCE] templates from local cache")
    else:
        print("  Local cache empty — falling back to GET /api/templates...")
        compliance = _list_existing_compliance_templates()
    if not compliance:
        print("  ⚠️  No [COMPLIANCE] templates found — run --fix-footers first.")
        return

    # Walk all flows
    flows = []
    cursor = None
    while True:
        params = {"fields[flow]": "name,status,archived", "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params)
        if not page:
            break
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next")
        if not next_link:
            break
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    rebound = skipped = failed = no_template = 0

    for flow in flows:
        attrs = flow.get("attributes", {})
        if attrs.get("archived") or attrs.get("status") not in ("live", "draft", "manual"):
            continue
        flow_name = attrs.get("name", "?")

        actions = get_flow_actions(flow["id"])
        for action in actions:
            action_id = action["id"]
            action_type = action.get("attributes", {}).get("action_type", "")
            # Only email-send actions have a template to rebind
            if "EMAIL" not in str(action_type).upper() and "SEND" not in str(action_type).upper():
                continue

            messages = get_messages_for_action(action_id)
            for msg in messages:
                msg_name = msg.get("attributes", {}).get("name") or f"msg_{msg['id']}"
                channel = (msg.get("attributes", {}).get("channel") or "").lower()
                if channel and channel not in ("email", ""):
                    continue

                label = f"{flow_name} → {msg_name}"
                new_tid = compliance.get(msg_name)
                if not new_tid:
                    print(f"  ⏭️  No [COMPLIANCE] template for: {label}")
                    no_template += 1
                    continue

                # Skip if already pointing at this template
                current_tid = get_template_id_for_message(msg["id"])
                if current_tid == new_tid:
                    print(f"  ✅ Already bound: {label}")
                    skipped += 1
                    continue

                # PATCH /api/flow-actions/{id} with the new template_id
                msg_content = get_message_content(msg["id"])
                payload = {
                    "data": {
                        "type": "flow-action",
                        "id": action_id,
                        "attributes": {
                            "definition": {
                                "id": action_id,
                                "type": "send-email",
                                "data": {
                                    "message": build_flow_email_payload(msg_content, new_tid)
                                }
                            }
                        }
                    }
                }
                result = api_patch(f"flow-actions/{action_id}", payload, quiet=True)
                if result is not None:
                    print(f"  🔁 Rebound: {label}  →  {new_tid}")
                    rebound += 1
                else:
                    print(f"  ❌ PATCH failed for: {label} (action {action_id})")
                    failed += 1

                time.sleep(0.4)  # rate limit: 3 req/s burst

    print("\n" + "=" * 80)
    print("REBIND SUMMARY")
    print(f"  Rebound to [COMPLIANCE]:  {rebound}")
    print(f"  Already bound:            {skipped}")
    print(f"  No matching template:     {no_template}")
    print(f"  Failed:                   {failed}")
    print("=" * 80)
    if rebound > 0:
        print("\n  Run --audit-flows to verify UEMA findings have dropped to zero.")


def fix_all_templates():
    """Run all auto-fixable template patches, then print manual fix guide."""
    fix_compliance_footers()
    fix_stale_thresholds()
    rebind_compliance_templates()
    report_manual_fixes_required()


OUR_CREATED_TEMPLATE_NAMES = [
    "[Z] Abandoned Checkout – Email 3 (72hr Final)",
    "[Z] Browse Abandonment – Email 2 (24hr Social Proof)",
    "[Z] Browse Abandonment – Email 3 (72hr Bestsellers)",
    "[Z] ATC Abandonment – Email 3 (72hr Final)",
]


def audit_our_templates():
    """For each of the 4 templates we created in --create-templates, find:
       (a) does it exist in Klaviyo, (b) is it bound to any flow message,
       (c) what is that flow's name + status (live/draft)?
    Answers: are these templates active in production or just sitting in the library?"""
    print("\n🔍 AUDITING OUR 4 CREATED TEMPLATES")
    print("=" * 100)

    # 1. Find each template by name (paginate templates with contains filter)
    name_to_id = {}
    cursor = None
    page_no = 0
    while True:
        params = {"filter": 'contains(name,"[Z]")'}
        if cursor:
            params["page[cursor]"] = cursor
        try:
            data = api_get("templates", params)
        except Exception:
            break
        page_no += 1
        for t in data.get("data", []):
            n = (t.get("attributes", {}).get("name") or "")
            if n in OUR_CREATED_TEMPLATE_NAMES:
                # If duplicates exist (older runs), keep the newest
                created = t.get("attributes", {}).get("created") or ""
                existing = name_to_id.get(n)
                if not existing or created > existing[1]:
                    name_to_id[n] = (t["id"], created)
        next_link = data.get("links", {}).get("next") or ""
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    print(f"\nTemplate library status:")
    for n in OUR_CREATED_TEMPLATE_NAMES:
        if n in name_to_id:
            print(f"  ✅ EXISTS  {name_to_id[n][0]:<10} {n}")
        else:
            print(f"  ❌ MISSING            {n}")

    if not name_to_id:
        print("\n  None of the 4 templates were found in the library.")
        return

    target_ids = {tid: n for n, (tid, _) in name_to_id.items()}

    # 2. Walk every flow → action → message and check if template_id matches any of ours
    print(f"\nSearching all flows for these template IDs...")
    cursor = None
    flows = []
    while True:
        params = {"fields[flow]": "name,status,archived", "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params)
        if not page:
            break
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next") or ""
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    bindings = {tid: [] for tid in target_ids}
    for f in flows:
        if f.get("attributes", {}).get("archived"):
            continue
        flow_name = f.get("attributes", {}).get("name", "?")
        flow_status = (f.get("attributes", {}).get("status") or "?").lower()
        for action in get_flow_actions(f["id"]):
            for msg in get_messages_for_action(action["id"]):
                content = get_message_content(msg["id"])
                tid = content.get("template_id")
                if tid in target_ids:
                    bindings[tid].append({
                        "flow_id": f["id"],
                        "flow_name": flow_name,
                        "flow_status": flow_status,
                        "action_id": action["id"],
                        "msg_id": msg["id"],
                    })

    # 3. Report
    print(f"\n{'TEMPLATE':<60} {'TID':<10} BOUND TO")
    print("-" * 100)
    for tid, name in target_ids.items():
        binds = bindings[tid]
        if not binds:
            print(f"  {name[:58]:<60} {tid:<10} ❌ NOT BOUND TO ANY FLOW")
        else:
            for b in binds:
                status_marker = "🚨 LIVE" if b["flow_status"] == "live" else f"📝 {b['flow_status']}"
                print(f"  {name[:58]:<60} {tid:<10} {status_marker} {b['flow_name']} (msg={b['msg_id']})")
    print("=" * 100)
    print("""
Decision guide:
  ❌ NOT BOUND TO ANY FLOW   → safe to DELETE (just sitting in library, not in production)
  📝 draft                   → safe to DELETE or REWRITE before flow goes live
  🚨 LIVE                    → DO NOT DELETE — currently sending. Must rewrite + reassign.
""")
    """Dump a single template's full HTML to stdout so we can inspect rendering issues."""
    print(f"\n📄 TEMPLATE: {template_id}")
    print("=" * 100)
    data = safe_get(f"templates/{template_id}")
    if not data:
        print("  ❌ Template not found.")
        return
    a = data.get("data", {}).get("attributes", {}) or {}
    print(f"  Name:    {a.get('name')}")
    print(f"  Editor:  {a.get('editor_type')}")
    print(f"  Created: {a.get('created')}")
    print(f"  Updated: {a.get('updated')}")
    print("\n  ─── HTML ───")
    print(a.get("html") or "(empty)")
    print("=" * 100)


def audit_action_statuses():
    """For every non-archived flow, walk each email-send action and print its
    individual status (live/draft/manual) — so we can see which findings in
    FLOWS_AUDIT.md are actually shipping vs already paused at action-level."""
    print("\n🔍 PER-ACTION STATUS AUDIT")
    print("=" * 100)
    print(f"  {'FLOW':<40} {'ACTION':<10} {'STATUS':<8} {'TEMPLATE':<10} SUBJECT")
    print("  " + "-" * 110)

    cursor = None
    flows = []
    while True:
        params = {"fields[flow]": "name,status,archived", "page[size]": 10}
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params)
        if not page:
            break
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next") or ""
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    summary = {"live": 0, "draft": 0, "manual": 0, "other": 0}
    skipped_flows = []
    for f in flows:
        if f.get("attributes", {}).get("archived"):
            continue
        flow_name = (f.get("attributes", {}).get("name") or "?")[:38]
        flow_status = (f.get("attributes", {}).get("status") or "?").lower()
        actions = get_flow_actions(f["id"])
        if not actions:
            skipped_flows.append((f["id"], flow_name, "no actions returned"))
            continue
        printed_for_flow = 0
        for action in actions:
            full = safe_get(f"flow-actions/{action['id']}")
            if not full:
                continue
            defn = (full.get("data", {}).get("attributes", {}) or {}).get("definition") or {}
            if not isinstance(defn, dict):
                continue
            d = defn.get("data") or {}
            msg = d.get("message") or {}
            # Only show actions that have a message (covers send-email + any MJML/legacy variants)
            if not isinstance(msg, dict) or not msg.get("template_id"):
                continue
            action_status = (d.get("status") or "?").lower()
            tid = msg.get("template_id") or ""
            subj = (msg.get("subject_line") or "")[:60]
            summary[action_status] = summary.get(action_status, 0) + 1
            marker = ""
            if flow_status == "live" and action_status == "live":
                marker = "🚨 "
            elif flow_status == "live" and action_status == "draft":
                marker = "⏸️  "
            elif flow_status == "live" and action_status == "manual":
                marker = "⏹  "
            print(f"  {marker}{flow_name:<38} {action['id']:<10} {action_status:<8} {tid:<10} {subj}")
            printed_for_flow += 1
            time.sleep(0.1)
        if printed_for_flow == 0:
            # Diagnostic: flow has actions but none had a template_id message
            action_types = []
            for action in actions:
                full = safe_get(f"flow-actions/{action['id']}")
                if full:
                    d = (full.get("data", {}).get("attributes", {}) or {}).get("definition") or {}
                    action_types.append(d.get("type") if isinstance(d, dict) else "?")
            skipped_flows.append((f["id"], flow_name, f"{len(actions)} actions, types={action_types}, no template_id messages"))

    print("\n  " + "=" * 110)
    if skipped_flows:
        print("  SKIPPED FLOWS (no email actions matched the filter):")
        for fid, fname, reason in skipped_flows:
            print(f"    {fid:<10} {fname:<40} {reason}")
        print()
    print(f"  Status breakdown across all email-send actions: {summary}")
    print(f"  🚨 = LIVE in a LIVE flow (actually shipping)")
    print(f"  ⏸️  = DRAFT in a LIVE flow (not sending)")
    print(f"  ⏹  = MANUAL in a LIVE flow (paused)")


def inspect_flow_config(flow_id_or_all):
    """Pull deep config for a flow (or all non-archived flows).
    Reports send_options (Smart Sending), send_strategy, tracking_options,
    conversion_metric_id at flow level + per-action message-level config
    (smart_sending_enabled, transactional, add_tracking_params,
    additional_filters, custom_tracking_params).

    Klaviyo MCP doesn't expose these fields; raw REST API does."""
    if flow_id_or_all == "all":
        # Get all non-archived flows
        flows = []
        cursor = None
        while True:
            params = {"fields[flow]": "name,status,archived", "page[size]": 10}
            if cursor:
                params["page[cursor]"] = cursor
            page = safe_get("flows", params=params)
            if not page:
                break
            flows.extend(page.get("data", []))
            next_link = page.get("links", {}).get("next") or ""
            m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
            if not m:
                break
            cursor = requests.utils.unquote(m.group(1))
        flow_ids = [f["id"] for f in flows
                    if not f.get("attributes", {}).get("archived")]
    else:
        flow_ids = [flow_id_or_all]

    for flow_id in flow_ids:
        _inspect_one_flow_config(flow_id)
        time.sleep(0.5)


def _inspect_one_flow_config(flow_id):
    print(f"\n🔍 INSPECT FLOW CONFIG: {flow_id}")
    print("=" * 100)

    # Try with all interesting fields. If any is rejected, Klaviyo will
    # return a 400; fall back to default response.
    fields = ("name,status,archived,trigger_type,send_options,send_strategy,"
              "tracking_options,conversion_metric_id")
    try:
        data = api_get(f"flows/{flow_id}", {"fields[flow]": fields})
    except Exception as e:
        msg = str(e)
        if "400" in msg or "Invalid" in msg:
            print(f"  ⚠️  Filtered query rejected; some fields may not be supported by API revision {REVISION}.")
            print(f"      Error: {msg[:200]}")
            print(f"      Falling back to default response.")
            data = safe_get(f"flows/{flow_id}")
        else:
            print(f"  ❌ Fetch failed: {e}")
            return
    if not data:
        return

    attrs = data.get("data", {}).get("attributes", {}) or {}
    print(f"  Name:                {attrs.get('name')}")
    print(f"  Status:              {attrs.get('status')}")
    print(f"  Trigger type:        {attrs.get('trigger_type') or attrs.get('triggerType')}")
    print(f"  All attribute keys:  {sorted(attrs.keys())}")
    print()
    for k in ("send_options", "send_strategy", "tracking_options",
              "conversion_metric_id", "trigger_filters"):
        v = attrs.get(k)
        if v is None or v == {} or v == []:
            print(f"  {k}: (not set or not exposed by API)")
        else:
            print(f"  {k}:")
            print("    " + json.dumps(v, indent=2).replace("\n", "\n    "))

    # Per-action message-level config
    actions = get_flow_actions(flow_id)
    print(f"\n  Per-action config ({len(actions)} actions):")
    print(f"  {'ACTION':<10} {'TYPE':<18} {'STATUS':<8} {'SMART':<6} {'TRANS':<6} {'TRACK':<6} {'TEMPLATE'}")
    print("  " + "-" * 100)
    for action in actions:
        full = safe_get(f"flow-actions/{action['id']}")
        if not full:
            continue
        a_attrs = full.get("data", {}).get("attributes", {}) or {}
        defn = a_attrs.get("definition") or {}
        if not isinstance(defn, dict):
            continue
        d_data = defn.get("data") or {}
        msg = d_data.get("message") if isinstance(d_data, dict) else None
        if not isinstance(msg, dict):
            print(f"  {action['id']:<10} {(defn.get('type') or '?'):<18} (no message — non-email action)")
            continue
        smart = "Y" if msg.get("smart_sending_enabled") else "N"
        trans = "Y" if msg.get("transactional") else "N"
        track = "Y" if msg.get("add_tracking_params") else "N"
        tid = msg.get("template_id") or "?"
        status = (d_data.get("status") or "?")[:7]
        print(f"  {action['id']:<10} {(defn.get('type') or '?'):<18} {status:<8} {smart:<6} {trans:<6} {track:<6} {tid}")

        # Show extra config when present
        extras = []
        if msg.get("additional_filters"):
            extras.append(f"additional_filters={msg['additional_filters']}")
        if msg.get("custom_tracking_params"):
            extras.append(f"custom_tracking_params={msg['custom_tracking_params']}")
        if extras:
            for e in extras:
                print(f"               {e}")


def deploy_replenishment_template(slot_number, confirm=False):
    """Deploy a single retail-first Replenishment template to its flow-action.
    Process:
      1. Render HTML for the slot via replenishment_templates.SLOTS
      2. POST as a new template to Klaviyo (creates [BC-Replenishment]
         <category> entry in the template library)
      3. PATCH the corresponding flow-action with the new template_id,
         preserving definition.links (the unlock we discovered today)
      4. Verify by re-reading the action's bound template_id

    Use --confirm to actually deploy (otherwise dry-run preview).
    Smoke-test on slot 16 (First aid) before bulk deploying — its action
    is currently draft so a misconfiguration won't ship to customers."""
    # Late import so the script can be used without replenishment_templates.py
    try:
        from replenishment_templates import SLOTS, render_slot
    except ImportError:
        # Allow running from repo root: scripts/replenishment_templates.py
        import os
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from replenishment_templates import SLOTS, render_slot

    print(f"\n🚀 DEPLOY REPLENISHMENT TEMPLATE — slot {slot_number}")
    print("=" * 80)

    slot = next((s for s in SLOTS if s["slot"] == slot_number), None)
    if not slot:
        print(f"  ❌ Slot {slot_number} not found. Available: {sorted(s['slot'] for s in SLOTS)}")
        return

    action_id = slot["action_id"]
    template_name = f"[BC-Replenishment] {slot['category']}"
    print(f"  Slot:           {slot_number}")
    print(f"  Action ID:      {action_id}")
    print(f"  Category:       {slot['category']}")
    print(f"  Template name:  {template_name}")
    print(f"  Subject:        {slot['subject']}")
    print(f"  Preview text:   {slot['preview_text']}")

    # 1. Render HTML
    html = render_slot(slot)
    print(f"  HTML length:    {len(html):,} chars, {len(slot['products'])} products")

    # 2. Read current action state to capture existing definition.links
    print("\n  Reading current flow-action state...")
    current = safe_get(f"flow-actions/{action_id}")
    if not current:
        print(f"  ❌ Could not fetch action {action_id}")
        return
    attrs = current.get("data", {}).get("attributes", {}) or {}
    defn = attrs.get("definition") or {}
    if not isinstance(defn, dict):
        print(f"  ❌ Unexpected definition shape on action")
        return
    existing_msg = (defn.get("data") or {}).get("message") or {}
    existing_links = defn.get("links")
    existing_status = (defn.get("data") or {}).get("status") or "?"
    existing_template = existing_msg.get("template_id") or "?"
    print(f"  Current status:        {existing_status}")
    print(f"  Current template_id:   {existing_template}")

    if not confirm:
        print(f"\n  Dry-run mode. Re-run with --confirm to deploy.")
        print(f"  Will: (1) POST new template '{template_name}' to Klaviyo")
        print(f"        (2) PATCH flow-action {action_id} to use it (preserving links)")
        print(f"        (3) Keep status='draft' so the email doesn't ship until you flip it live")
        return

    # 3. POST new template
    print(f"\n  Creating template '{template_name}'...")
    create_payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": template_name,
                "editor_type": "CODE",
                "html": html,
            }
        }
    }
    new_tpl = api_post("templates", create_payload)
    if not new_tpl:
        print(f"  ❌ Template POST failed")
        return
    new_template_id = new_tpl["data"]["id"]
    print(f"  ✅ Template created: {new_template_id}")

    # 4. PATCH flow-action with new template_id, preserving links + status
    print(f"\n  Rebinding flow-action {action_id} to template {new_template_id}...")
    new_msg = dict(existing_msg)
    new_msg["template_id"] = new_template_id
    # Update subject + preview text from the slot config
    new_msg["subject_line"] = slot["subject"]
    new_msg["preview_text"] = slot["preview_text"]

    definition_payload = {
        "id": action_id,
        "type": "send-email",
        "data": {
            "message": new_msg,
            "status": existing_status if existing_status in ("live", "draft", "manual") else "draft",
        }
    }
    if existing_links is not None:
        definition_payload["links"] = existing_links

    patch_payload = {
        "data": {
            "type": "flow-action",
            "id": action_id,
            "attributes": {
                "definition": definition_payload,
            }
        }
    }
    r = requests.patch(f"{BASE_URL}/flow-actions/{action_id}",
                       headers=HEADERS, json=patch_payload, timeout=REQUEST_TIMEOUT)
    if r.status_code in (200, 204):
        print(f"  ✅ Rebind succeeded ({r.status_code})")
    else:
        print(f"  ❌ Rebind failed: HTTP {r.status_code}")
        print(f"     Response: {r.text[:600]}")
        print(f"     Note: template {new_template_id} was still created; you may want to delete it.")
        return

    # 5. Verify
    print("\n  Verifying...")
    verify = safe_get(f"flow-actions/{action_id}")
    if verify:
        v_msg = ((verify.get("data", {}).get("attributes", {}).get("definition") or {})
                 .get("data") or {}).get("message") or {}
        v_template = v_msg.get("template_id")
        v_subject = v_msg.get("subject_line")
        if v_template == new_template_id:
            print(f"  ✅ Verified: action now bound to {new_template_id}")
            print(f"  ✅ Verified subject: {v_subject}")
        else:
            print(f"  ⚠️  Verification: template_id is {v_template!r} (expected {new_template_id})")


def deploy_all_replenishment_templates(confirm=False):
    """Bulk deploy all 15 retail-first templates. Calls deploy_replenishment_template
    for each slot. Stops on the first failure to avoid partial state."""
    try:
        from replenishment_templates import SLOTS
    except ImportError:
        import os
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from replenishment_templates import SLOTS

    print(f"\n🚀 BULK DEPLOY {len(SLOTS)} REPLENISHMENT TEMPLATES")
    print("=" * 80)
    if not confirm:
        print("  Dry-run. Re-run with --confirm to deploy all.")
        for s in SLOTS:
            print(f"  Slot {s['slot']:>2} → action {s['action_id']} → category {s['category']}")
        return

    for s in SLOTS:
        deploy_replenishment_template(s["slot"], confirm=True)
        time.sleep(1.0)  # pace the deploys

    print("\n" + "=" * 80)
    print(f"✅ Deployed {len(SLOTS)} templates. All flow-actions remain in 'draft' until you flip them live.")
    print("=" * 80)


def pause_flow_action(action_id, confirm=False):
    """Pause a single flow-action by setting its definition.data.status to 'manual'.
    Preserves the rest of the action's definition (message, template_id, etc.) untouched."""
    print(f"\n⏸️  PAUSE FLOW ACTION {action_id}")
    print("=" * 80)

    data = safe_get(f"flow-actions/{action_id}")
    if not data:
        print(f"  ❌ Could not fetch action {action_id}")
        return
    attrs = data.get("data", {}).get("attributes", {}) or {}
    defn = attrs.get("definition") or {}
    if not isinstance(defn, dict):
        print(f"  ❌ Unexpected definition shape: {type(defn).__name__}")
        return

    current_status = (defn.get("data") or {}).get("status") or "?"
    msg = (defn.get("data") or {}).get("message") or {}
    defn_type = defn.get("type") or "?"

    print(f"  Action ID:       {action_id}")
    print(f"  Definition type: {defn_type}")
    print(f"  Current status:  {current_status}")
    print(f"  Template:        {msg.get('template_id')}")
    print(f"  Subject:         {msg.get('subject_line')}")
    print(f"  From:            {msg.get('from_label')} <{msg.get('from_email')}>")

    if current_status == "manual":
        print("\n  ✅ Already paused (status=manual). Nothing to do.")
        return

    if defn_type != "send-email":
        print(f"\n  ⚠️  Action is not 'send-email' (type={defn_type!r}). Aborting to be safe.")
        return

    if not confirm:
        print(f"\n  Dry-run mode. Re-run with --confirm to actually pause.")
        return

    # Preserve the action's existing definition.links if present (Klaviyo errors
    # with "cannot change the links of an action" when this is omitted)
    existing_links = defn.get("links")
    definition_payload = {
        "id": action_id,
        "type": "send-email",
        "data": {
            "message": msg,
            "status": "manual",
        }
    }
    if existing_links is not None:
        definition_payload["links"] = existing_links

    payload = {
        "data": {
            "type": "flow-action",
            "id": action_id,
            "attributes": {
                "definition": definition_payload
            }
        }
    }

    print(f"\n  Pausing (variant 1: with links preserved)...")
    r = requests.patch(f"{BASE_URL}/flow-actions/{action_id}",
                       headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    if r.status_code not in (200, 204):
        # Variant 2: try minimal payload — status only, no message, no links
        print(f"    variant 1 failed (HTTP {r.status_code}); trying variant 2 (status-only)...")
        minimal_payload = {
            "data": {
                "type": "flow-action",
                "id": action_id,
                "attributes": {
                    "definition": {
                        "id": action_id,
                        "type": "send-email",
                        "data": {"status": "manual"}
                    }
                }
            }
        }
        r = requests.patch(f"{BASE_URL}/flow-actions/{action_id}",
                           headers=HEADERS, json=minimal_payload, timeout=REQUEST_TIMEOUT)
    if r.status_code in (200, 204):
        print(f"  ✅ Paused. PATCH returned {r.status_code}.")
    else:
        print(f"  ❌ PATCH failed: HTTP {r.status_code}")
        print(f"     Response: {r.text[:500]}")
        return

    # Verify
    print("\n  Verifying...")
    verify = safe_get(f"flow-actions/{action_id}")
    if verify:
        new_status = ((verify.get("data", {}).get("attributes", {}).get("definition") or {})
                      .get("data") or {}).get("status") or "?"
        if new_status == "manual":
            print(f"  ✅ Verified: status is now {new_status!r}.")
        else:
            print(f"  ⚠️  Verification: status is {new_status!r} (expected 'manual'). Check Klaviyo UI.")


def resume_flow_action(action_id, confirm=False):
    """Reverse pause_flow_action by setting status back to 'live'."""
    print(f"\n▶️  RESUME FLOW ACTION {action_id}")
    print("=" * 80)
    data = safe_get(f"flow-actions/{action_id}")
    if not data:
        print(f"  ❌ Could not fetch action")
        return
    defn = (data.get("data", {}).get("attributes", {}) or {}).get("definition") or {}
    msg = (defn.get("data") or {}).get("message") or {}
    current = (defn.get("data") or {}).get("status") or "?"
    print(f"  Current status: {current}")
    if current == "live":
        print("  ✅ Already live. Nothing to do.")
        return
    if not confirm:
        print(f"  Dry-run. Re-run with --confirm.")
        return
    payload = {
        "data": {
            "type": "flow-action",
            "id": action_id,
            "attributes": {
                "definition": {
                    "id": action_id,
                    "type": "send-email",
                    "data": {"message": msg, "status": "live"},
                }
            }
        }
    }
    r = requests.patch(f"{BASE_URL}/flow-actions/{action_id}",
                       headers=HEADERS, json=payload, timeout=REQUEST_TIMEOUT)
    print(f"  PATCH → HTTP {r.status_code}: {r.text[:200] if r.status_code not in (200, 204) else 'OK'}")


def show_flow_content(flow_id):
    """Print every email message in a flow: subject, preview text, from, and HTML excerpt.
    Use to verify what each message is actually about before making decisions."""
    print(f"\n📖 FLOW CONTENT: {flow_id}")
    print("=" * 100)

    flow_data = safe_get(f"flows/{flow_id}")
    if flow_data:
        a = flow_data.get("data", {}).get("attributes", {})
        print(f"  Name:    {a.get('name')}")
        print(f"  Status:  {a.get('status')}  Trigger: {a.get('trigger_type')}")

    actions = get_flow_actions(flow_id)
    for action in actions:
        for msg in get_messages_for_action(action["id"]):
            content = get_message_content(msg["id"])
            if not content.get("from_email"):
                continue
            print("\n  " + "-" * 96)
            print(f"  Action {action['id']} → Message {msg['id']}")
            print(f"  Subject:      {content.get('subject_line')}")
            print(f"  Preview text: {content.get('preview_text') or '(empty)'}")
            print(f"  From:         {content.get('from_label')} <{content.get('from_email')}>")
            tid = content.get("template_id")
            print(f"  Template:     {tid}")
            if tid:
                html = get_template_html(tid) or ""
                # Strip tags + collapse whitespace for a readable excerpt
                text = re.sub(r"<[^>]+>", " ", html)
                text = re.sub(r"\s+", " ", text).strip()
                print(f"  Excerpt:      {text[:600]}{'...' if len(text) > 600 else ''}")
    print("=" * 100)


def cleanup_duplicate_compliance_templates(dry_run=False):
    """Find duplicate [COMPLIANCE] templates created across multiple --fix-footers runs.
    For each duplicated name, keep ONE (preferring the one currently bound to a flow
    message, or else the newest), and delete the rest."""
    print("\n🧹 CLEANING UP DUPLICATE [COMPLIANCE] TEMPLATES")
    print("=" * 80)

    # 1. Build in-use set from local cache (fast — avoids ~150 GET requests).
    # The cache maps msg_name → keeper template_id and is updated every --fix-footers run.
    in_use_template_ids = set()
    cache = _load_compliance_cache() if os.path.exists(COMPLIANCE_CACHE_PATH) else {}
    for tid in cache.values():
        in_use_template_ids.add(tid)
    print(f"  Loaded {len(in_use_template_ids)} 'keeper' template IDs from local cache")
    if not in_use_template_ids:
        print("  ⚠️  Cache is empty — will fall back to keeping the NEWEST template per name.")

    # 2. List [COMPLIANCE] templates. Try server-side filters in order of preference;
    # fall back to full scan if all filters reject. Klaviyo filter operators vary by revision.
    all_compliance = []

    def _list_with_filter(filter_expr):
        out = []
        cursor = None
        page_no = 0
        while True:
            params = {}
            if filter_expr:
                params["filter"] = filter_expr
            if cursor:
                params["page[cursor]"] = cursor
            try:
                data = api_get("templates", params)
            except Exception as e:
                return None, f"{e}"
            page_no += 1
            for t in data.get("data", []):
                name = t.get("attributes", {}).get("name") or ""
                # If filter was server-side rejected, we still need to client-filter
                if not filter_expr and not name.startswith("[COMPLIANCE]"):
                    continue
                out.append({
                    "id": t["id"],
                    "name": name,
                    "created": t.get("attributes", {}).get("created") or "",
                })
            print(f"    page {page_no}: returned {len(data.get('data', []))} (matches so far: {len(out)})")
            next_link = data.get("links", {}).get("next") or ""
            m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
            if not m:
                return out, None
            cursor = requests.utils.unquote(m.group(1))

    # Try filters in order: contains → equals (impossible for prefix) → no filter
    tried = []
    for filter_expr, label in [
        ('contains(name,"[COMPLIANCE]")', 'contains'),
        (None, 'unfiltered'),
    ]:
        print(f"\n  Listing templates ({label})...")
        result, err = _list_with_filter(filter_expr)
        tried.append((label, err))
        if result is not None:
            all_compliance = result
            break
        print(f"    ⚠️  {label} failed: {err}")

    if not all_compliance:
        print("  ⚠️  No [COMPLIANCE] templates returned by API.")
        print("     If duplicates exist in the Klaviyo UI, GET /api/templates may be hiding them.")
        print("     Try: Klaviyo UI → Email → Templates → search '[COMPLIANCE]' → delete duplicates manually.")
        return

    # 3. Group by name and decide keep vs delete
    by_name = {}
    for t in all_compliance:
        by_name.setdefault(t["name"], []).append(t)

    to_delete = []
    to_keep = []
    print(f"\n  Found {len(all_compliance)} [COMPLIANCE] templates across {len(by_name)} unique names")
    print(f"  {'KEEP':<8} {'DELETE':<8} NAME")
    print("  " + "-" * 80)
    for name in sorted(by_name.keys()):
        ts = by_name[name]
        if len(ts) == 1:
            to_keep.append(ts[0])
            continue
        in_use = [t for t in ts if t["id"] in in_use_template_ids]
        if in_use:
            keep = in_use[0]
        else:
            ts.sort(key=lambda x: x["created"], reverse=True)
            keep = ts[0]
        to_keep.append(keep)
        dups = [t for t in ts if t["id"] != keep["id"]]
        to_delete.extend(dups)
        print(f"  {keep['id']:<8} ×{len(dups):<6}  {name}")

    if not to_delete:
        print("\n  ✅ No duplicates to delete.")
        return

    print(f"\n  Total: keep {len(to_keep)}, delete {len(to_delete)}")
    if dry_run:
        print("  (dry run — no deletes performed)")
        return

    # 4. Delete duplicates
    print(f"\n  Deleting {len(to_delete)} duplicate templates...")
    deleted = failed = 0
    for t in to_delete:
        r = requests.delete(f"{BASE_URL}/templates/{t['id']}",
                            headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if r.status_code in (200, 204, 404):
            deleted += 1
            if deleted % 10 == 0:
                print(f"    ...{deleted}/{len(to_delete)} deleted")
        else:
            print(f"  ❌ {t['id']} ({t['name']}): HTTP {r.status_code}: {r.text[:120]}")
            failed += 1
        time.sleep(0.3)

    print(f"\n  ✅ Deleted: {deleted}")
    if failed:
        print(f"  ❌ Failed:  {failed}")
    print("=" * 80)


def verify_flows():
    """Verify operational state: flow statuses (Triple Pixel paused?), volume per flow,
    and recent activity. Use this before deciding rebuild vs UI swap vs draft-flip."""
    print("\n🔍 VERIFYING FLOW STATE")
    print("=" * 100)

    # 1. List every flow with status, trigger, archived, last update
    flows = []
    cursor = None
    while True:
        params = {
            "fields[flow]": "name,status,trigger_type,archived,created,updated",
            "page[size]": 10,
        }
        if cursor:
            params["page[cursor]"] = cursor
        page = safe_get("flows", params=params)
        if not page:
            break
        flows.extend(page.get("data", []))
        next_link = page.get("links", {}).get("next") or ""
        m = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
        if not m:
            break
        cursor = requests.utils.unquote(m.group(1))

    # Sort by name
    flows.sort(key=lambda x: (x.get("attributes", {}).get("name") or "").lower())

    print(f"\n📋 ALL FLOWS ({len(flows)} total)\n")
    print(f"  {'ID':<10} {'STATUS':<10} {'ARCH':<6} {'TRIGGER':<28} {'UPDATED':<22} NAME")
    print("  " + "-" * 110)
    by_status = {}
    for f in flows:
        a = f.get("attributes", {})
        s = (a.get("status") or "?").lower()
        by_status[s] = by_status.get(s, 0) + 1
        archived = "yes" if a.get("archived") else "no"
        trigger = (a.get("trigger_type") or "?")[:26]
        updated = (a.get("updated") or "?")[:19]
        name = a.get("name") or "?"
        print(f"  {f['id']:<10} {s:<10} {archived:<6} {trigger:<28} {updated:<22} {name}")

    print(f"\n  Status breakdown: {by_status}")

    # 2. Triple Pixel pause verification
    print("\n🔴 TRIPLE PIXEL FLOW STATUS:")
    for tid, name in TRIPLE_PIXEL_FLOWS.items():
        f = next((x for x in flows if x["id"] == tid), None)
        if not f:
            print(f"  ⚠️  {tid} ({name}) — NOT FOUND in flow list")
            continue
        s = (f["attributes"].get("status") or "?").lower()
        # In Klaviyo, 'draft' and 'manual' both mean not-sending; only 'live' is concerning
        ok = "✅ NOT SENDING" if s in ("manual", "draft") else f"🚨 STILL LIVE"
        print(f"  {ok}  status={s:<8}  {tid} — {name}")

    # 3. Per-flow email count (proxy for "how big is this flow")
    print(f"\n📧 EMAIL ACTIONS PER FLOW (skipping archived):")
    print(f"  {'ID':<10} {'STATUS':<10} {'ACTIONS':<9} {'EMAILS':<8} NAME")
    print("  " + "-" * 110)
    for f in flows:
        a = f.get("attributes", {})
        if a.get("archived"):
            continue
        s = (a.get("status") or "?").lower()
        actions = get_flow_actions(f["id"])
        email_count = 0
        for action in actions:
            msgs = get_messages_for_action(action["id"])
            for m in msgs:
                ch = (m.get("attributes", {}).get("channel") or "").lower()
                if not ch or ch == "email":
                    email_count += 1
        name = a.get("name") or "?"
        print(f"  {f['id']:<10} {s:<10} {len(actions):<9} {email_count:<8} {name}")
        time.sleep(0.1)  # rate limit

    # 4. Recent send volume via flow-values-reports (last 30 days)
    print(f"\n📊 LAST 30 DAYS RECIPIENTS PER FLOW (proxy for active mid-flow subscribers):")
    # Try common ecommerce conversion metric names; if all fail, list what we found
    placed_order_id = None
    for candidate in ("Placed Order", "Ordered Product", "Order Placed",
                      "Checkout Started", "Started Checkout"):
        mid, mname = get_metric_id(candidate)
        if mid:
            placed_order_id = mid
            print(f"  Using conversion metric: {mname} ({mid})")
            break
    if not placed_order_id:
        print("  ⚠️  Could not find a conversion metric — listing available metrics:")
        cursor = None
        listed = 0
        while listed < 30:
            params = {"page[cursor]": cursor} if cursor else None
            try:
                data = api_get("metrics", params)
            except Exception as e:
                print(f"    error fetching metrics: {e}")
                break
            for m in data.get("data", []):
                print(f"    {m['id']}  {m['attributes'].get('name')}")
                listed += 1
            next_link = data.get("links", {}).get("next") or ""
            match = re.search(r"page%5Bcursor%5D=([^&]+)", next_link)
            if not match:
                break
            cursor = requests.utils.unquote(match.group(1))
        print("  Set the metric ID manually if needed and re-run.")
    else:
        live_flows = [f for f in flows if (f["attributes"].get("status") or "").lower() == "live"
                      and not f["attributes"].get("archived")]
        for f in live_flows:
            a = f.get("attributes", {})
            payload = {
                "data": {
                    "type": "flow-values-report",
                    "attributes": {
                        "statistics": ["recipients", "delivered", "opens"],
                        "timeframe": {"key": "last_30_days"},
                        "conversion_metric_id": placed_order_id,
                        "filter": f'equals(flow_id,"{f["id"]}")',
                    }
                }
            }
            # Retry on 429 with exponential backoff (flow-values-reports has tight rate limits)
            for attempt in range(5):
                r = requests.post(f"{BASE_URL}/flow-values-reports/", headers=HEADERS,
                                  json=payload, timeout=REQUEST_TIMEOUT)
                if r.status_code == 429:
                    wait = 2 ** attempt + 2
                    print(f"  ⏳ {f['id']:<10} throttled, sleeping {wait}s (attempt {attempt + 1}/5)...")
                    time.sleep(wait)
                    continue
                break
            if r.status_code == 200:
                results = r.json().get("data", {}).get("attributes", {}).get("results", [])
                if results:
                    stats = results[0].get("statistics", {})
                    print(f"  {f['id']:<10} recipients={stats.get('recipients', 0):<6} "
                          f"delivered={stats.get('delivered', 0):<6} "
                          f"opens={stats.get('opens', 0):<6} {a.get('name')}")
                else:
                    print(f"  {f['id']:<10} no data — {a.get('name')}")
            else:
                print(f"  {f['id']:<10} ⚠️  HTTP {r.status_code}: {r.text[:120]} — {a.get('name')}")
            time.sleep(3.0)  # flow-values-reports burst limit ~1 req/3s

    print("\n" + "=" * 100)
    print("VERIFICATION COMPLETE")
    print("=" * 100)
    print("""
What to check:
  1. Triple Pixel flows above should all show '✅ PAUSED' (status=manual).
  2. Flows with HIGH 'recipients' last 30d → mid-flow subscribers exist → rebuild is risky.
  3. Flows with 0 recipients → safe to rebuild.
  4. Status='draft' = never went live; 'live' = active; 'manual' = paused.
""")


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Bargain Chemist Klaviyo Flow Manager")
    parser.add_argument("--pause-triple-pixel", action="store_true",
                        help="Pause all 3 Triple Pixel flows")
    parser.add_argument("--create-flows", action="store_true",
                        help="Create draft flow shells in Klaviyo")
    parser.add_argument("--audit-flows", action="store_true",
                        help="Audit all flow templates for compliance, brand voice, $79 threshold, coupon residue")
    parser.add_argument("--fix-templates", action="store_true",
                        help="Auto-fix: inject UEMA footer + fix stale $49/$50 thresholds in all templates")
    parser.add_argument("--fix-footers", action="store_true",
                        help="Auto-fix: inject UEMA/ASA compliance footer into templates missing it")
    parser.add_argument("--fix-thresholds", action="store_true",
                        help="Auto-fix: replace stale $49/$50 free-shipping copy with $79 in known templates")
    parser.add_argument("--rebind-templates", action="store_true",
                        help="Rebind each flow's email action to its [COMPLIANCE] template via PATCH /api/flow-actions (revision 2025-10-15+)")
    parser.add_argument("--report-manual-fixes", action="store_true",
                        help="Print list of issues that require manual action (coupons, fear language, etc.)")
    parser.add_argument("--verify-flows", action="store_true",
                        help="Verify operational state: flow statuses, Triple Pixel pause, recipients last 30 days")
    parser.add_argument("--cleanup-duplicate-templates", action="store_true",
                        help="Delete duplicate [COMPLIANCE] templates created by repeated --fix-footers runs")
    parser.add_argument("--cleanup-duplicate-templates-dry-run", action="store_true",
                        help="Preview what --cleanup-duplicate-templates would delete (no actual deletion)")
    parser.add_argument("--show-flow", metavar="FLOW_ID",
                        help="Print every email's subject/preview/from/excerpt for a single flow")
    parser.add_argument("--show-template", metavar="TEMPLATE_ID",
                        help="Print a single template's full HTML")
    parser.add_argument("--audit-our-templates", action="store_true",
                        help="Check which flows the 4 templates we created (--create-templates) are bound to and whether those flows are live/draft")
    parser.add_argument("--pause-action", metavar="ACTION_ID",
                        help="Pause a single flow-action (sets definition.data.status to 'manual'). Dry-run unless --confirm.")
    parser.add_argument("--resume-action", metavar="ACTION_ID",
                        help="Resume a previously paused flow-action (status=live). Dry-run unless --confirm.")
    parser.add_argument("--audit-action-statuses", action="store_true",
                        help="Walk every flow's email-send actions and print each one's individual status (live/draft/manual) — flow-level status can mask action-level status")
    parser.add_argument("--deploy-replenishment-template", metavar="SLOT", type=int,
                        help="Deploy a single retail-first Replenishment template (POST template + PATCH flow-action). Dry-run unless --confirm. Test on slot 16 first.")
    parser.add_argument("--deploy-all-replenishment-templates", action="store_true",
                        help="Bulk deploy all 15 retail-first Replenishment templates. Dry-run unless --confirm.")
    parser.add_argument("--inspect-flow-config", metavar="FLOW_ID",
                        help="Pull deep config (send_options, tracking_options, send_strategy, conversion_metric_id, per-action smart_sending/transactional/add_tracking_params) for a single flow. Pass 'all' to inspect every non-archived flow.")
    parser.add_argument("--confirm", action="store_true",
                        help="Required by --pause-action / --resume-action to actually execute (otherwise dry-run)")
    parser.add_argument("--all", action="store_true",
                        help="Run all steps")
    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
        sys.exit(1)

    templates = {}
    flows = {}

    if args.all or args.pause_triple_pixel:
        pause_triple_pixel_flows()

    if args.all or args.create_flows:
        flows = create_flow_shells()

    if args.audit_flows:
        audit_all_flows()

    if args.fix_templates:
        fix_all_templates()

    if args.fix_footers:
        fix_compliance_footers()

    if args.fix_thresholds:
        fix_stale_thresholds()

    if args.rebind_templates:
        rebind_compliance_templates()

    if args.report_manual_fixes:
        report_manual_fixes_required()

    if args.verify_flows:
        verify_flows()

    if args.cleanup_duplicate_templates_dry_run:
        cleanup_duplicate_compliance_templates(dry_run=True)

    if args.cleanup_duplicate_templates:
        cleanup_duplicate_compliance_templates(dry_run=False)

    if args.show_flow:
        show_flow_content(args.show_flow)

    if args.show_template:
        show_template(args.show_template)

    if args.audit_our_templates:
        audit_our_templates()

    if args.audit_action_statuses:
        audit_action_statuses()

    if args.deploy_replenishment_template is not None:
        deploy_replenishment_template(args.deploy_replenishment_template, confirm=args.confirm)

    if args.deploy_all_replenishment_templates:
        deploy_all_replenishment_templates(confirm=args.confirm)

    if args.inspect_flow_config:
        inspect_flow_config(args.inspect_flow_config)

    if args.pause_action:
        pause_flow_action(args.pause_action, confirm=args.confirm)

    if args.resume_action:
        resume_flow_action(args.resume_action, confirm=args.confirm)

    if args.all:
        print_setup_guide(templates, flows)

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()
