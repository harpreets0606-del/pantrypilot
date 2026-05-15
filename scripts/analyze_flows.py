#!/usr/bin/env python3
"""
Analyze all manual Klaviyo flows for Bargain Chemist and classify each
as Simple / Mixed / Complex based on template content patterns.

For each flow, this script:
1. Walks flow -> actions -> messages -> templates via Klaviyo REST API
2. Pulls the HTML for each email template
3. Scans the HTML for:
   - Jinja merge tags ({{ ... }})
   - Klaviyo loop tags ({% for %})
   - Conditional tags ({% if %})
   - Universal content block references (data-klaviyo-universal-block)
   - Event-driven dynamic content (event.*, person.*, etc.)
4. Classifies each flow:
   - SIMPLE  — pure brand creative, no per-customer dynamic content
   - MIXED   — has personalization (name, generic merge tags) but no event-driven blocks
   - COMPLEX — renders content from event data (cart, product, search term)

The output tells the brand team exactly which flows they can freely
re-skin vs. which need engineering coordination.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/analyze_flows.py
"""

import os
import re
import sys

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"

# All 10 manual flow IDs from the audit
MANUAL_FLOWS = [
    "RDJQYM",  # Post-Purchase Series
    "RPQXaa",  # Added to Cart Abandonment
    "RtiVC5",  # Browse Abandonment
    "Sr3hxz",  # Abandoned Checkout v3
    "T7pmf6",  # Win-back - Lapsed Customers
    "Ua5LdS",  # Replenishment - Category Based
    "V9XmEm",  # Flu Season - Winter Wellness
    "XbQiKg",  # Search Abandonment V4
    "YdejKf",  # Welcome Series 2026 - No Coupon
    "Ysj7sg",  # Back in Stock
]

# Patterns that indicate event-driven dynamic content (COMPLEX)
EVENT_DRIVEN_PATTERNS = [
    (r"\{\{\s*event\.", "event.* variable (e.g. event.extra.line_items)"),
    (r"\{\{\s*Items\b", "Items array (cart line items)"),
    (r"\{\{\s*line_items", "line_items (checkout abandonment)"),
    (r"\{\{\s*product\b", "product.* (browse abandonment)"),
    (r"\{\{\s*items\.\d", "items[N] indexed access"),
    (r"\{%\s*for\b", "loop ({% for %})"),
    (r"\{\{\s*search_term\b", "search_term (search abandonment)"),
    (r"\{\{\s*viewed_product", "viewed_product"),
    (r"checkout_url", "abandoned checkout URL"),
    (r"\{\{\s*order\.", "order.* (post-purchase)"),
    (r"\{\{\s*ProductID", "ProductID merge tag"),
]

# Patterns indicating simple personalization (MIXED, not COMPLEX)
SIMPLE_PERSONALIZATION = [
    (r"\{\{\s*first_name", "first_name"),
    (r"\{\{\s*person\.", "person.* (basic personalization)"),
    (r"\{\{\s*organization\.", "organization.*"),
    (r"\{\{\s*unsubscribe", "unsubscribe link"),
]


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
    }


def get_flow_actions(api_key, flow_id):
    """Returns list of actions in a flow, including flow-messages inline."""
    url = f"{KLAVIYO_BASE}/flows/{flow_id}/flow-actions/?include=flow-messages"
    r = requests.get(url, headers=headers(api_key), timeout=30)
    if r.status_code != 200:
        return None, f"actions fetch failed: {r.status_code} {r.text[:200]}"
    return r.json(), None


def get_template_html(api_key, template_id):
    url = f"{KLAVIYO_BASE}/templates/{template_id}/"
    r = requests.get(url, headers=headers(api_key), timeout=30)
    if r.status_code != 200:
        return None, f"{r.status_code}"
    data = r.json().get("data", {}).get("attributes", {})
    return data.get("html") or "", None


def get_message_template_id(api_key, message_id):
    url = f"{KLAVIYO_BASE}/flow-messages/{message_id}/template/"
    r = requests.get(url, headers=headers(api_key), timeout=30)
    if r.status_code != 200:
        return None, f"{r.status_code}"
    data = r.json().get("data") or {}
    if not data:
        return None, "no template assigned"
    return data.get("id"), None


def analyze_html(html):
    """Return (event_hits, simple_hits, universal_blocks)"""
    event_hits = []
    for pat, label in EVENT_DRIVEN_PATTERNS:
        if re.search(pat, html, re.IGNORECASE):
            event_hits.append(label)
    simple_hits = []
    for pat, label in SIMPLE_PERSONALIZATION:
        if re.search(pat, html, re.IGNORECASE):
            simple_hits.append(label)
    universal_blocks = re.findall(r'data-klaviyo-universal-block="([^"]+)"', html)
    return event_hits, simple_hits, universal_blocks


def classify_flow(per_template_analyses):
    has_event = any(t["event_hits"] for t in per_template_analyses)
    has_universal = any(t["universal_blocks"] for t in per_template_analyses)
    has_simple = any(t["simple_hits"] for t in per_template_analyses)
    if has_event:
        return "COMPLEX", has_universal
    if has_simple or has_universal:
        return "MIXED", has_universal
    return "SIMPLE", has_universal


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    overall = []

    for flow_id in MANUAL_FLOWS:
        print(f"\n{'=' * 60}\nFLOW: {flow_id}\n{'=' * 60}")

        # Get the flow's name from the flows list (fast: one extra call)
        meta = requests.get(f"{KLAVIYO_BASE}/flows/{flow_id}/", headers=headers(api_key), timeout=30)
        flow_name = "?"
        if meta.status_code == 200:
            flow_name = meta.json()["data"]["attributes"].get("name", "?")
        print(f"Name: {flow_name}")

        actions_resp, err = get_flow_actions(api_key, flow_id)
        if err:
            print(f"  ERROR: {err}")
            overall.append({"id": flow_id, "name": flow_name, "verdict": "ERROR", "error": err})
            continue

        # Extract flow-messages (email actions) from the included resources
        included = actions_resp.get("included", [])
        messages = [it for it in included if it.get("type") == "flow-message"]
        print(f"Flow messages: {len(messages)}")

        per_template = []
        for msg in messages:
            msg_id = msg["id"]
            msg_name = msg.get("attributes", {}).get("name", msg_id)
            channel = msg.get("attributes", {}).get("definition", {}).get("channel")
            if channel and channel != "email":
                print(f"  -- skip (channel={channel}): {msg_name}")
                continue

            tpl_id, err = get_message_template_id(api_key, msg_id)
            if err or not tpl_id:
                print(f"  -- {msg_name}: no template ({err})")
                continue

            html, err = get_template_html(api_key, tpl_id)
            if err:
                print(f"  -- {msg_name}: template fetch failed ({err})")
                continue

            event_hits, simple_hits, universal_blocks = analyze_html(html)
            per_template.append({
                "msg_name": msg_name,
                "tpl_id": tpl_id,
                "html_len": len(html),
                "event_hits": event_hits,
                "simple_hits": simple_hits,
                "universal_blocks": universal_blocks,
            })
            print(f"  -- {msg_name}  tpl={tpl_id}  ({len(html):,}b)")
            if event_hits:
                print(f"       event-driven: {', '.join(event_hits[:3])}{'...' if len(event_hits) > 3 else ''}")
            if simple_hits:
                print(f"       simple personalization: {', '.join(simple_hits[:3])}")
            if universal_blocks:
                print(f"       universal blocks: {universal_blocks}")

        if not per_template:
            print("  WARNING: no email templates found in this flow")
            verdict = "NO_EMAIL"
            has_universal = False
        else:
            verdict, has_universal = classify_flow(per_template)

        print(f"\nVERDICT: {verdict}{' (uses universal content)' if has_universal else ''}")

        overall.append({
            "id": flow_id,
            "name": flow_name,
            "verdict": verdict,
            "has_universal": has_universal,
            "template_count": len(per_template),
            "templates": per_template,
        })

    # Final report
    print("\n\n" + "=" * 70)
    print("SUMMARY — Brand Team Re-skin Difficulty")
    print("=" * 70)
    print()
    print("SIMPLE: brand can re-skin freely, no engineering needed")
    print("MIXED:  brand can re-skin but must preserve universal blocks / merge tags")
    print("COMPLEX: brand designs around event-driven loops/blocks; needs coord")
    print()
    for f in overall:
        u = " [+UC]" if f.get("has_universal") else ""
        n = f.get("template_count", 0)
        print(f"  {f['verdict']:8}{u:6}  {f['name']}  ({n} email{'s' if n != 1 else ''}) [id={f['id']}]")


if __name__ == "__main__":
    main()
