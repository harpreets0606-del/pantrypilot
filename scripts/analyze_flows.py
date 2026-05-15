#!/usr/bin/env python3
"""
Analyze all manual Klaviyo flows for Bargain Chemist and classify each
as Simple / Mixed / Complex based on template content patterns.

Traversal (two-step because Klaviyo's API doesn't support
'?include=flow-messages' on flow-actions):
  1. GET /api/flows/{id}/flow-actions/                  -> all actions
  2. For each send-email action:
       GET /api/flow-actions/{action_id}/flow-messages/ -> messages
       GET /api/flow-messages/{msg_id}/template/        -> template id
       GET /api/templates/{tpl_id}/                     -> HTML

Then scans the HTML for:
- Jinja merge tags ({{ ... }})
- Loop tags ({% for %}) and conditionals ({% if %})
- Universal content block references (data-klaviyo-universal-block)
- Event-driven dynamic content (event.*, line_items, product, etc.)

Classifies each flow:
  SIMPLE  - pure brand creative, no per-customer dynamic content
  MIXED   - has personalization (name, generic merge tags), no event-driven blocks
  COMPLEX - renders content from event data (cart, product, search term)

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/analyze_flows.py
"""

import os
import re
import sys

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"

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

EVENT_DRIVEN_PATTERNS = [
    (r"\{\{\s*event\.", "event.* variable (cart, browse, etc)"),
    (r"\{\{\s*Items\b", "Items array"),
    (r"\{\{\s*line_items", "line_items"),
    (r"\{\{\s*product\b", "product.*"),
    (r"\{\{\s*items\.\d", "items[N] indexed"),
    (r"\{%\s*for\b", "{% for %} loop"),
    (r"\{\{\s*search_term\b", "search_term"),
    (r"\{\{\s*viewed_product", "viewed_product"),
    (r"checkout_url", "checkout_url"),
    (r"\{\{\s*order\.", "order.*"),
    (r"\{\{\s*ProductID", "ProductID"),
    (r"\{\{\s*RecommendedProducts", "RecommendedProducts"),
]

SIMPLE_PERSONALIZATION = [
    (r"\{\{\s*first_name", "first_name"),
    (r"\{\{\s*person\.", "person.*"),
    (r"\{\{\s*organization\.", "organization.*"),
    (r"\{%\s*unsubscribe", "unsubscribe link"),
]

# Klaviyo "send-email" action types vary by API version
SEND_EMAIL_ACTION_TYPES = {
    "send-email",
    "send_email",
    "SEND_EMAIL",
}


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
    }


def fetch(url, api_key, label=""):
    r = requests.get(url, headers=headers(api_key), timeout=30)
    if r.status_code != 200:
        return None, f"{r.status_code} {r.text[:200]}"
    return r.json(), None


def analyze_html(html):
    event_hits = []
    for pat, label in EVENT_DRIVEN_PATTERNS:
        if re.search(pat, html, re.IGNORECASE):
            event_hits.append(label)
    simple_hits = []
    for pat, label in SIMPLE_PERSONALIZATION:
        if re.search(pat, html, re.IGNORECASE):
            simple_hits.append(label)
    universal_blocks = re.findall(r'data-klaviyo-universal-block="([^"]+)"', html)
    return event_hits, simple_hits, list(set(universal_blocks))


def classify(per_template):
    has_event = any(t["event_hits"] for t in per_template)
    has_universal = any(t["universal_blocks"] for t in per_template)
    has_simple = any(t["simple_hits"] for t in per_template)
    if has_event:
        return "COMPLEX", has_universal
    if has_simple:
        return "MIXED", has_universal
    if has_universal:
        return "MIXED", True
    return "SIMPLE", False


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    overall = []
    for flow_id in MANUAL_FLOWS:
        print(f"\n{'=' * 60}\nFLOW: {flow_id}\n{'=' * 60}")
        meta, err = fetch(f"{KLAVIYO_BASE}/flows/{flow_id}/", api_key)
        flow_name = "?"
        if meta:
            flow_name = meta["data"]["attributes"].get("name", "?")
        print(f"Name: {flow_name}")

        # Step 1: Get all flow actions
        actions_resp, err = fetch(f"{KLAVIYO_BASE}/flows/{flow_id}/flow-actions/", api_key)
        if err:
            print(f"  ERROR fetching actions: {err}")
            overall.append({"id": flow_id, "name": flow_name, "verdict": "ERROR", "error": err})
            continue

        actions = actions_resp.get("data", [])
        # Identify which actions are send-email
        send_actions = []
        for a in actions:
            atype = a.get("attributes", {}).get("action_type", "")
            if atype in SEND_EMAIL_ACTION_TYPES:
                send_actions.append(a)

        print(f"Total actions: {len(actions)}  |  send-email actions: {len(send_actions)}")
        if not send_actions and actions:
            # Show action types so user can see what we're dealing with
            seen_types = sorted(set(a.get("attributes", {}).get("action_type", "?") for a in actions))
            print(f"  Action types in this flow: {seen_types}")

        per_template = []
        for action in send_actions:
            action_id = action["id"]
            # Step 2: Fetch flow-messages for this action
            msgs_resp, err = fetch(
                f"{KLAVIYO_BASE}/flow-actions/{action_id}/flow-messages/",
                api_key,
            )
            if err:
                print(f"  -- action {action_id}: messages fetch failed: {err}")
                continue
            messages = msgs_resp.get("data", [])

            for msg in messages:
                msg_id = msg["id"]
                attrs = msg.get("attributes", {})
                msg_name = attrs.get("name", msg_id)
                channel = attrs.get("definition", {}).get("channel", "email")
                if channel and channel != "email":
                    print(f"  -- skip {channel}: {msg_name}")
                    continue

                # Step 3: Fetch template id for this message
                tpl_resp, err = fetch(
                    f"{KLAVIYO_BASE}/flow-messages/{msg_id}/template/",
                    api_key,
                )
                if err:
                    print(f"  -- {msg_name}: no template ({err})")
                    continue
                tpl_data = tpl_resp.get("data")
                if not tpl_data:
                    print(f"  -- {msg_name}: template endpoint empty")
                    continue
                tpl_id = tpl_data["id"]

                # The template fetch returns the html in attributes
                html = tpl_data.get("attributes", {}).get("html") or ""

                event_hits, simple_hits, universal_blocks = analyze_html(html)
                per_template.append({
                    "msg_name": msg_name,
                    "tpl_id": tpl_id,
                    "html_len": len(html),
                    "event_hits": event_hits,
                    "simple_hits": simple_hits,
                    "universal_blocks": universal_blocks,
                })
                print(f"  -- {msg_name:50s}  tpl={tpl_id}  ({len(html):,}b)")
                if event_hits:
                    print(f"       event-driven: {', '.join(event_hits[:4])}{'...' if len(event_hits) > 4 else ''}")
                if simple_hits:
                    print(f"       simple personalization: {', '.join(simple_hits[:3])}")
                if universal_blocks:
                    print(f"       universal blocks: {universal_blocks}")

        if not per_template:
            print("  WARNING: no email templates found")
            overall.append({
                "id": flow_id, "name": flow_name, "verdict": "NO_EMAIL",
                "has_universal": False, "template_count": 0, "templates": [],
            })
            continue

        verdict, has_universal = classify(per_template)
        print(f"\nVERDICT: {verdict}{' (+ universal content)' if has_universal else ''}")
        overall.append({
            "id": flow_id, "name": flow_name, "verdict": verdict,
            "has_universal": has_universal, "template_count": len(per_template),
            "templates": per_template,
        })

    print("\n\n" + "=" * 70)
    print("SUMMARY — Brand Team Re-skin Difficulty")
    print("=" * 70)
    print()
    print("SIMPLE  - brand can re-skin freely, no engineering needed")
    print("MIXED   - re-skin OK but must preserve merge tags / universal blocks")
    print("COMPLEX - event-driven loops/blocks; brand designs AROUND them")
    print()
    for f in overall:
        u = " [+UC]" if f.get("has_universal") else "     "
        n = f.get("template_count", 0)
        print(f"  {f['verdict']:8}{u}  {f['name']}  ({n} email{'s' if n != 1 else ''})  [id={f['id']}]")


if __name__ == "__main__":
    main()
