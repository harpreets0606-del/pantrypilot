#!/usr/bin/env python3
"""
Refined flow analyzer with 4-tier classification.

The first version only detected Klaviyo Jinja patterns ({{ }}, {% %}).
That missed an important category: templates that have NO dynamic
merge tags BUT contain hardcoded product showcases with specific
product URLs, prices, and images — which need brand-team maintenance
work even though they're not Klaviyo-COMPLEX.

This version classifies into 4 tiers:

  CREATIVE-ONLY    - first_name + footer only; no products or category
                     links. Brand re-skins freely, zero maintenance.

  CATEGORY LINKS   - hardcoded links to Shopify collections
                     (/collections/vitamins, /collections/skincare).
                     Durable; collection URLs rarely change.

  PRODUCT SHOWCASE - hardcoded specific products with /products/ URLs,
                     prices, images. NEEDS QUARTERLY REFRESH when
                     stock/prices/SKUs change.

  EVENT-DRIVEN     - Klaviyo Jinja loops over event payload (cart,
                     browse, search, back-in-stock). Engineering-locked
                     dynamic blocks.

Run:
    KLAVIYO_API_KEY="pk_xxx" python3 scripts/analyze_flows_v2.py
"""

import os
import re
import sys

import requests

KLAVIYO_BASE = "https://a.klaviyo.com/api"
REVISION = "2024-10-15"

MANUAL_FLOWS = [
    "RDJQYM", "RPQXaa", "RtiVC5", "Sr3hxz", "T7pmf6",
    "Ua5LdS", "V9XmEm", "XbQiKg", "YdejKf", "Ysj7sg",
]

EVENT_DRIVEN_PATTERNS = [
    r"\{\{\s*event\.",
    r"\{\{\s*Items\b",
    r"\{\{\s*line_items",
    r"\{\{\s*product\b",
    r"\{\{\s*items\.\d",
    r"\{%\s*for\b",
    r"\{\{\s*search_term\b",
    r"\{\{\s*viewed_product",
    r"checkout_url",
    r"\{\{\s*order\.",
    r"\{\{\s*ProductID",
    r"\{\{\s*RecommendedProducts",
]


def headers(api_key):
    return {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "accept": "application/vnd.api+json",
        "revision": REVISION,
    }


def fetch(url, api_key):
    r = requests.get(url, headers=headers(api_key), timeout=30)
    if r.status_code != 200:
        return None, f"{r.status_code} {r.text[:200]}"
    return r.json(), None


def analyze_html(html):
    """Return rich analysis dict."""
    # Strip Klaviyo's tracking/preview URLs from analysis (they're not product links)
    is_event_driven = any(re.search(p, html, re.IGNORECASE) for p in EVENT_DRIVEN_PATTERNS)

    # Find product URLs (Shopify /products/{handle})
    product_urls = list(set(re.findall(r'(?:bargainchemist\.co\.nz|/)products/[a-z0-9-]+', html, re.IGNORECASE)))

    # Find collection URLs (excluding generic /all)
    all_collection_urls = list(set(re.findall(r'(?:bargainchemist\.co\.nz|/)collections/[a-z0-9-]+', html, re.IGNORECASE)))
    collection_urls = [u for u in all_collection_urls if not u.endswith('/all')]

    # Hardcoded prices (NZ$X.XX pattern, ignoring price-beat copy "10%")
    price_matches = re.findall(r'\$\d+\.\d{2}', html)
    # Dedupe — same price might appear multiple times in one card
    unique_prices = len(set(price_matches))

    # Product images on Shopify CDN
    cdn_images = len(re.findall(r'cdn\.shopify\.com', html))

    # Hardcoded markers in HTML comments
    has_hardcoded_marker = bool(re.search(r'(?:hardcoded|refresh\s+(?:quarterly|monthly)|update\s+manually)', html, re.IGNORECASE))

    # Universal content blocks
    universal_blocks = list(set(re.findall(r'data-klaviyo-universal-block="([^"]+)"', html)))

    # Simple personalization signals
    has_first_name = bool(re.search(r'\{\{\s*first_name', html))
    has_unsubscribe = bool(re.search(r'\{%\s*unsubscribe', html))

    return {
        "event_driven": is_event_driven,
        "product_urls": product_urls,
        "collection_urls": collection_urls,
        "unique_prices": unique_prices,
        "cdn_images": cdn_images,
        "has_hardcoded_marker": has_hardcoded_marker,
        "universal_blocks": universal_blocks,
        "has_first_name": has_first_name,
        "has_unsubscribe": has_unsubscribe,
        "html_size": len(html),
    }


def classify_template(a):
    """4-tier classification per template."""
    if a["event_driven"]:
        return "EVENT-DRIVEN"
    # 3+ specific product URLs = product showcase (rough threshold)
    # OR explicit hardcoded marker + at least 1 product url
    if len(a["product_urls"]) >= 3 or (a["has_hardcoded_marker"] and len(a["product_urls"]) >= 1):
        return "PRODUCT SHOWCASE"
    # Multiple collection URLs (more than the generic Shop Now link)
    if len(a["collection_urls"]) >= 3:
        return "CATEGORY LINKS"
    # Has 1-2 product URLs but no hardcoded marker — borderline
    if len(a["product_urls"]) >= 1:
        return "PRODUCT SHOWCASE (light)"
    return "CREATIVE-ONLY"


def classify_flow(per_template):
    """Worst-case wins: flow takes the highest-maintenance tier of any template."""
    order = {
        "CREATIVE-ONLY": 0,
        "CATEGORY LINKS": 1,
        "PRODUCT SHOWCASE (light)": 2,
        "PRODUCT SHOWCASE": 3,
        "EVENT-DRIVEN": 4,
    }
    if not per_template:
        return "NO_TEMPLATES"
    worst = max(per_template, key=lambda t: order.get(t["tier"], 0))
    return worst["tier"]


def main():
    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        print("ERROR: KLAVIYO_API_KEY env var not set", file=sys.stderr)
        sys.exit(1)

    overall = []
    for flow_id in MANUAL_FLOWS:
        print(f"\n{'=' * 60}\nFLOW: {flow_id}\n{'=' * 60}")
        meta, _ = fetch(f"{KLAVIYO_BASE}/flows/{flow_id}/", api_key)
        flow_name = meta["data"]["attributes"].get("name", "?") if meta else "?"
        print(f"Name: {flow_name}")

        actions_resp, err = fetch(f"{KLAVIYO_BASE}/flows/{flow_id}/flow-actions/", api_key)
        if err:
            print(f"  ERROR: {err}")
            continue
        actions = actions_resp.get("data", [])
        send_actions = [a for a in actions if a.get("attributes", {}).get("action_type") == "send-email"]
        print(f"send-email actions: {len(send_actions)}")

        per_template = []
        for action in send_actions:
            action_id = action["id"]
            msgs_resp, err = fetch(f"{KLAVIYO_BASE}/flow-actions/{action_id}/flow-messages/", api_key)
            if err:
                continue
            for msg in msgs_resp.get("data", []):
                msg_id = msg["id"]
                attrs = msg.get("attributes", {})
                msg_name = attrs.get("name", msg_id)
                channel = attrs.get("definition", {}).get("channel", "email")
                if channel != "email":
                    continue
                tpl_resp, err = fetch(f"{KLAVIYO_BASE}/flow-messages/{msg_id}/template/", api_key)
                if err or not tpl_resp.get("data"):
                    continue
                tpl_data = tpl_resp["data"]
                tpl_id = tpl_data["id"]
                html = tpl_data.get("attributes", {}).get("html") or ""
                a = analyze_html(html)
                tier = classify_template(a)
                a["msg_name"] = msg_name
                a["tpl_id"] = tpl_id
                a["tier"] = tier
                per_template.append(a)

                print(f"  -- {msg_name[:50]:50s}  tpl={tpl_id}  -> {tier}")
                if a["product_urls"]:
                    print(f"       hardcoded products: {len(a['product_urls'])}  prices: {a['unique_prices']}  CDN images: {a['cdn_images']}")
                if a["collection_urls"]:
                    print(f"       collection links: {len(a['collection_urls'])}  ({', '.join(c.split('/')[-1] for c in a['collection_urls'][:5])}{'...' if len(a['collection_urls']) > 5 else ''})")
                if a["has_hardcoded_marker"]:
                    print(f"       ⚠ contains 'hardcoded'/'refresh' marker in HTML")
                if a["event_driven"]:
                    print(f"       event-driven (Klaviyo Jinja over event payload)")

        flow_tier = classify_flow(per_template)
        overall.append({
            "id": flow_id, "name": flow_name, "tier": flow_tier,
            "template_count": len(per_template), "templates": per_template,
        })
        print(f"\nFLOW TIER: {flow_tier}")

    print("\n\n" + "=" * 70)
    print("SUMMARY — 4-tier classification (worst tier per flow)")
    print("=" * 70)
    print()
    print("CREATIVE-ONLY        - pure brand creative; trivial re-skin")
    print("CATEGORY LINKS       - collection-link cards; low maintenance")
    print("PRODUCT SHOWCASE     - hardcoded products; QUARTERLY refresh required")
    print("EVENT-DRIVEN         - Klaviyo Jinja dynamic blocks; engineering-locked")
    print()
    for f in overall:
        print(f"  {f['tier']:25s}  {f['name']}  ({f['template_count']} email{'s' if f['template_count'] != 1 else ''})  [id={f['id']}]")


if __name__ == "__main__":
    main()
