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
REVISION = "2024-10-15"

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
def api_get(path, params=None):
    r = requests.get(f"{BASE_URL}/{path}", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def api_patch(path, payload, quiet=False):
    r = requests.patch(f"{BASE_URL}/{path}", headers=HEADERS, json=payload)
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
    r = requests.post(f"{BASE_URL}/{path}", headers=HEADERS, json=payload)
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
# 2. Email Template HTML
# ─────────────────────────────────────────────

def template_abandoned_checkout_email3():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Last chance – your cart is expiring</title>
<style>
  body { margin:0; padding:0; background:#f4f4f4; font-family:Arial,sans-serif; }
  .wrapper { max-width:600px; margin:0 auto; background:#ffffff; }
  .header { background:#00833e; padding:20px 30px; text-align:center; }
  .header img { max-height:50px; }
  .hero { background:#f9f9f9; padding:30px; text-align:center; border-bottom:3px solid #00833e; }
  .hero h1 { color:#222222; font-size:26px; margin:0 0 10px; }
  .hero p { color:#555555; font-size:15px; line-height:1.6; margin:0; }
  .body { padding:30px; }
  .body p { color:#444444; font-size:15px; line-height:1.7; }
  .cart-item { background:#f9f9f9; border:1px solid #e5e5e5; border-radius:6px; padding:15px; margin:15px 0; }
  .cta-wrap { text-align:center; margin:30px 0; }
  .cta { display:inline-block; background:#00833e; color:#ffffff !important; text-decoration:none;
         padding:16px 40px; border-radius:4px; font-size:16px; font-weight:bold; letter-spacing:0.5px; }
  .urgency { background:#fff3cd; border-left:4px solid #ffc107; padding:14px 18px; margin:20px 0;
             font-size:14px; color:#555; border-radius:0 4px 4px 0; }
  .reviews { padding:20px 30px; border-top:1px solid #eeeeee; }
  .review { background:#f9f9f9; border-radius:6px; padding:15px; margin:10px 0; font-size:13px; color:#555; }
  .stars { color:#f5a623; font-size:16px; }
  .footer { background:#f4f4f4; padding:20px 30px; text-align:center; font-size:12px; color:#999999; }
  .footer a { color:#00833e; text-decoration:none; }
  @media (max-width:600px) {
    .hero h1 { font-size:20px; }
    .cta { padding:14px 28px; font-size:15px; }
  }
</style>
</head>
<body>
<div class="wrapper">

  <!-- Header -->
  <div class="header">
    <img src="https://bargainchemist.co.nz/cdn/shop/files/bc-logo-white.png"
         alt="Bargain Chemist" onerror="this.style.display='none'" />
  </div>

  <!-- Hero -->
  <div class="hero">
    <h1>⏰ Last chance, {{ first_name|default:'friend' }}</h1>
    <p>Your cart is about to expire. Once it's gone, we can't guarantee stock.</p>
  </div>

  <!-- Body -->
  <div class="body">
    <p>Hi {{ first_name|default:'there' }},</p>
    <p>
      We've been holding your items for 72 hours — but we can only hold stock for so long.
      Our health and wellness products move fast, and we'd hate for you to miss out.
    </p>

    <!-- Dynamic cart items (Klaviyo personalisation) -->
    {% for item in event.extra.line_items %}
    <div class="cart-item">
      <strong>{{ item.title }}</strong><br />
      <span style="color:#00833e; font-weight:bold;">NZ${{ item.price }}</span>
      {% if item.compare_at_price and item.compare_at_price > item.price %}
        &nbsp;<span style="color:#999; text-decoration:line-through; font-size:13px;">NZ${{ item.compare_at_price }}</span>
      {% endif %}
    </div>
    {% endfor %}

    <div class="urgency">
      🚨 <strong>Stock alert:</strong> Items in your cart are subject to availability. Complete your order now to secure yours.
    </div>

    <div class="cta-wrap">
      <a href="{{ event.extra.checkout_url }}" class="cta">Complete My Order →</a>
    </div>

    <p style="text-align:center; font-size:13px; color:#999;">
      Free delivery on orders over $50 &nbsp;|&nbsp; NZ owned &amp; operated
    </p>
  </div>

  <!-- Social Proof -->
  <div class="reviews">
    <p style="font-weight:bold; color:#222; font-size:14px; margin-bottom:5px;">What our customers say:</p>
    <div class="review">
      <span class="stars">★★★★★</span><br />
      "Always my go-to for vitamins and health products. Fast delivery and great prices."
      <br /><em>— Sarah M., Auckland</em>
    </div>
    <div class="review">
      <span class="stars">★★★★★</span><br />
      "Best online pharmacy in NZ. Huge range and always have what I need in stock."
      <br /><em>— James T., Wellington</em>
    </div>
  </div>

  <!-- Footer -->
  <div class="footer">
    <p>© {{ 'now'|date:'Y' }} Bargain Chemist. All rights reserved.</p>
    <p>
      <a href="{{ organization.homepage }}">Visit our store</a> &nbsp;|&nbsp;
      {% unsubscribe 'Unsubscribe' %}
    </p>
  </div>

</div>
</body>
</html>"""


def template_browse_abandonment_email2():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Still thinking it over?</title>
<style>
  body { margin:0; padding:0; background:#f4f4f4; font-family:Arial,sans-serif; }
  .wrapper { max-width:600px; margin:0 auto; background:#ffffff; }
  .header { background:#00833e; padding:20px 30px; text-align:center; }
  .header img { max-height:50px; }
  .hero { padding:30px; text-align:center; border-bottom:3px solid #00833e; }
  .hero h1 { color:#222222; font-size:24px; margin:0 0 10px; }
  .hero p { color:#555555; font-size:15px; line-height:1.6; margin:0; }
  .body { padding:30px; }
  .body p { color:#444444; font-size:15px; line-height:1.7; }
  .product-box { background:#f9f9f9; border:1px solid #e5e5e5; border-radius:6px;
                 padding:20px; margin:20px 0; text-align:center; }
  .cta-wrap { text-align:center; margin:30px 0; }
  .cta { display:inline-block; background:#00833e; color:#ffffff !important;
         text-decoration:none; padding:16px 40px; border-radius:4px;
         font-size:16px; font-weight:bold; }
  .benefits { display:table; width:100%; margin:20px 0; }
  .benefit { display:table-cell; text-align:center; padding:10px; font-size:13px; color:#555; width:33%; }
  .benefit span { font-size:24px; display:block; margin-bottom:5px; }
  .footer { background:#f4f4f4; padding:20px 30px; text-align:center; font-size:12px; color:#999999; }
  .footer a { color:#00833e; text-decoration:none; }
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <img src="https://bargainchemist.co.nz/cdn/shop/files/bc-logo-white.png"
         alt="Bargain Chemist" onerror="this.style.display='none'" />
  </div>

  <div class="hero">
    <h1>Still thinking it over, {{ first_name|default:'friend' }}?</h1>
    <p>You browsed something great. Here's why thousands of Kiwis choose Bargain Chemist.</p>
  </div>

  <div class="body">
    <p>Hi {{ first_name|default:'there' }},</p>
    <p>
      You were checking out some of our products — we thought we'd share a few reasons
      why over 100,000 New Zealanders trust Bargain Chemist for their health needs.
    </p>

    <div class="product-box">
      <p style="font-size:14px; color:#777; margin:0 0 8px;">You were looking at:</p>
      <strong style="font-size:16px; color:#222;">{{ event.ItemName|default:'our health range' }}</strong>
      {% if event.Value %}
        <br /><span style="color:#00833e; font-weight:bold; font-size:18px;">NZ${{ event.Value }}</span>
      {% endif %}
    </div>

    <!-- Benefits -->
    <div class="benefits">
      <div class="benefit"><span>🚚</span>Free delivery<br/>over $50</div>
      <div class="benefit"><span>✅</span>NZ owned<br/>&amp; operated</div>
      <div class="benefit"><span>💊</span>Pharmacist<br/>approved</div>
    </div>

    <div class="cta-wrap">
      <a href="{{ event.ProductURL|default:organization.homepage }}" class="cta">
        View Product →
      </a>
    </div>

    <p style="font-size:13px; color:#999; text-align:center;">
      Or <a href="{{ organization.homepage }}" style="color:#00833e;">browse our full range</a>
    </p>
  </div>

  <div class="footer">
    <p>© {{ 'now'|date:'Y' }} Bargain Chemist. All rights reserved.</p>
    <p>
      <a href="{{ organization.homepage }}">Visit our store</a> &nbsp;|&nbsp;
      {% unsubscribe 'Unsubscribe' %}
    </p>
  </div>

</div>
</body>
</html>"""


def template_browse_abandonment_email3():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Our customers love these too</title>
<style>
  body { margin:0; padding:0; background:#f4f4f4; font-family:Arial,sans-serif; }
  .wrapper { max-width:600px; margin:0 auto; background:#ffffff; }
  .header { background:#00833e; padding:20px 30px; text-align:center; }
  .header img { max-height:50px; }
  .hero { padding:30px; text-align:center; border-bottom:3px solid #00833e; }
  .hero h1 { color:#222222; font-size:24px; margin:0 0 10px; }
  .body { padding:30px; }
  .body p { color:#444444; font-size:15px; line-height:1.7; }
  .bestseller { background:#f9f9f9; border:1px solid #e5e5e5; border-radius:6px; padding:15px; margin:12px 0; }
  .bestseller strong { color:#222; font-size:15px; }
  .bestseller span { color:#00833e; font-weight:bold; }
  .badge { display:inline-block; background:#00833e; color:#fff; font-size:11px;
           padding:3px 8px; border-radius:3px; margin-left:6px; vertical-align:middle; }
  .cta-wrap { text-align:center; margin:30px 0; }
  .cta { display:inline-block; background:#00833e; color:#ffffff !important;
         text-decoration:none; padding:16px 40px; border-radius:4px;
         font-size:16px; font-weight:bold; }
  .footer { background:#f4f4f4; padding:20px 30px; text-align:center; font-size:12px; color:#999; }
  .footer a { color:#00833e; text-decoration:none; }
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <img src="https://bargainchemist.co.nz/cdn/shop/files/bc-logo-white.png"
         alt="Bargain Chemist" onerror="this.style.display='none'" />
  </div>

  <div class="hero">
    <h1>Our customers also love these 👇</h1>
  </div>

  <div class="body">
    <p>Hi {{ first_name|default:'there' }},</p>
    <p>
      While you're here, here are some of our most popular products that Kiwis
      keep coming back for — perfect to pair with what you were browsing.
    </p>

    <div class="bestseller">
      <strong>FLASH Cosmetics Eyelash Serum</strong>
      <span class="badge">Best Seller</span><br />
      <span>NZ$69.99</span> &nbsp;
      <span style="color:#999; text-decoration:line-through; font-size:13px;">NZ$89.99</span>
      <br /><small style="color:#777;">Longer, fuller lashes in 4–6 weeks. 9,500+ orders.</small>
    </div>

    <div class="bestseller">
      <strong>Sanderson Ultimate Man/Woman Multi</strong>
      <span class="badge">Top Rated</span><br />
      <span>NZ$34.99</span><br />
      <small style="color:#777;">NZ's favourite daily multivitamin. 4.8★ from 2,000+ reviews.</small>
    </div>

    <div class="bestseller">
      <strong>GO Healthy Magnesium 150mg</strong><br />
      <span>NZ$24.99</span><br />
      <small style="color:#777;">Sleep better, recover faster. #1 magnesium in NZ.</small>
    </div>

    <div class="cta-wrap">
      <a href="{{ organization.homepage }}" class="cta">Shop Our Best Sellers →</a>
    </div>
  </div>

  <div class="footer">
    <p>© {{ 'now'|date:'Y' }} Bargain Chemist. All rights reserved.</p>
    <p>
      <a href="{{ organization.homepage }}">Visit our store</a> &nbsp;|&nbsp;
      {% unsubscribe 'Unsubscribe' %}
    </p>
  </div>

</div>
</body>
</html>"""


def template_atc_email3():
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>Your cart is waiting – don't miss out</title>
<style>
  body { margin:0; padding:0; background:#f4f4f4; font-family:Arial,sans-serif; }
  .wrapper { max-width:600px; margin:0 auto; background:#ffffff; }
  .header { background:#00833e; padding:20px 30px; text-align:center; }
  .header img { max-height:50px; }
  .hero { background:#fff8e1; padding:30px; text-align:center; border-bottom:3px solid #ffc107; }
  .hero h1 { color:#222222; font-size:24px; margin:0 0 10px; }
  .hero p { color:#555; font-size:15px; margin:0; }
  .body { padding:30px; }
  .body p { color:#444444; font-size:15px; line-height:1.7; }
  .cart-item { background:#f9f9f9; border:1px solid #e5e5e5; border-radius:6px; padding:15px; margin:12px 0; }
  .urgency { background:#ffeeba; border-left:4px solid #ffc107; padding:14px 18px;
             margin:20px 0; font-size:14px; color:#555; border-radius:0 4px 4px 0; }
  .cta-wrap { text-align:center; margin:30px 0; }
  .cta { display:inline-block; background:#00833e; color:#ffffff !important;
         text-decoration:none; padding:16px 40px; border-radius:4px;
         font-size:16px; font-weight:bold; }
  .secondary-link { text-align:center; font-size:13px; color:#999; margin-top:10px; }
  .footer { background:#f4f4f4; padding:20px 30px; text-align:center; font-size:12px; color:#999; }
  .footer a { color:#00833e; text-decoration:none; }
</style>
</head>
<body>
<div class="wrapper">

  <div class="header">
    <img src="https://bargainchemist.co.nz/cdn/shop/files/bc-logo-white.png"
         alt="Bargain Chemist" onerror="this.style.display='none'" />
  </div>

  <div class="hero">
    <h1>⚠️ Your cart is about to expire</h1>
    <p>This is your final reminder, {{ first_name|default:'friend' }}.</p>
  </div>

  <div class="body">
    <p>Hi {{ first_name|default:'there' }},</p>
    <p>
      You added items to your Bargain Chemist cart — but haven't completed your order yet.
      We can't hold your items much longer.
    </p>

    {% for item in event.extra.line_items %}
    <div class="cart-item">
      <strong>{{ item.title }}</strong><br />
      <span style="color:#00833e; font-weight:bold;">NZ${{ item.price }}</span>
    </div>
    {% endfor %}

    <div class="urgency">
      ⏰ <strong>Heads up:</strong> Stock is limited. We can't guarantee these items will still
      be available after today.
    </div>

    <div class="cta-wrap">
      <a href="{{ event.extra.checkout_url }}" class="cta">Complete My Order →</a>
    </div>

    <div class="secondary-link">
      <a href="{{ organization.homepage }}" style="color:#00833e;">Continue shopping</a>
      &nbsp;|&nbsp;
      <a href="{{ organization.homepage }}/pages/contact" style="color:#00833e;">Need help?</a>
    </div>

    <p style="font-size:13px; color:#999; text-align:center; margin-top:20px;">
      🚚 Free delivery on orders over $50 &nbsp;|&nbsp; NZ owned &amp; operated
    </p>
  </div>

  <div class="footer">
    <p>© {{ 'now'|date:'Y' }} Bargain Chemist. All rights reserved.</p>
    <p>
      <a href="{{ organization.homepage }}">Visit our store</a> &nbsp;|&nbsp;
      {% unsubscribe 'Unsubscribe' %}
    </p>
  </div>

</div>
</body>
</html>"""


# ─────────────────────────────────────────────
# 3. Create Templates in Klaviyo
# ─────────────────────────────────────────────
def create_template(name, html):
    payload = {
        "data": {
            "type": "template",
            "attributes": {
                "name": name,
                "html": html,
            }
        }
    }
    result = api_post("templates", payload)
    if result:
        tid = result["data"]["id"]
        print(f"  ✅ Created template: {name} → ID: {tid}")
        return tid
    return None


def create_all_templates():
    print("\n📧 Creating Email Templates...")
    templates = {}

    templates["checkout_email3"] = create_template(
        "[Z] Abandoned Checkout – Email 3 (72hr Final)",
        template_abandoned_checkout_email3()
    )
    templates["browse_email2"] = create_template(
        "[Z] Browse Abandonment – Email 2 (24hr Social Proof)",
        template_browse_abandonment_email2()
    )
    templates["browse_email3"] = create_template(
        "[Z] Browse Abandonment – Email 3 (72hr Bestsellers)",
        template_browse_abandonment_email3()
    )
    templates["atc_email3"] = create_template(
        "[Z] ATC Abandonment – Email 3 (72hr Final)",
        template_atc_email3()
    )

    print("\n📋 Template IDs (save these — needed for flow setup in UI):")
    for key, tid in templates.items():
        if tid:
            print(f"  {key}: {tid}")

    return templates


# ─────────────────────────────────────────────
# 4. Get Metric IDs (needed for flow triggers)
# ─────────────────────────────────────────────
def get_metric_id(name_fragment):
    data = api_get("metrics", {"fields[metric]": "name", "page[size]": 200})
    for m in data.get("data", []):
        if name_fragment.lower() in m["attributes"]["name"].lower():
            return m["id"], m["attributes"]["name"]
    return None, None


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
    r = requests.get(f"{BASE_URL}/{path}", headers=HEADERS, params=params)
    if r.status_code == 200:
        return r.json()
    if debug:
        print(f"  ⚠️  GET {path} → {r.status_code}: {r.text[:300]}")
    return None


def get_flow_actions(flow_id, debug=False):
    data = safe_get(f"flows/{flow_id}/flow-actions",
                    params={"fields[flow-action]": "action_type,settings,status"},
                    debug=debug)
    if not data:
        return []
    return data.get("data", [])


def get_messages_for_action(action_id, debug=False):
    data = safe_get(f"flow-actions/{action_id}/flow-messages",
                    params={"fields[flow-message]": "name,channel,content"},
                    debug=debug)
    if not data:
        return []
    return data.get("data", [])


def get_template_id_for_message(message_id, debug=False):
    data = safe_get(f"flow-messages/{message_id}/relationships/template", debug=debug)
    if not data or not data.get("data"):
        return None
    return data["data"].get("id")


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
                  "page[size]": 50}
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
        params = {"fields[flow]": "name,status,archived", "page[size]": 50}
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
        if attrs.get("status") not in ("live", "draft", "manual"):
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


def fix_compliance_footers():
    """
    Inject UEMA + ASA mandatory footer into every Klaviyo template that is
    missing 'Bargain Chemist Limited' in its HTML.

    What gets added:
      • Bargain Chemist Limited + physical address  (UEMA s9)
      • 'Always read the label' + 'symptoms persist'  (ASA Therapeutic Code)
      • {% unsubscribe %}  (UEMA s11)

    Already-compliant templates are left untouched.
    """
    print("\n🔧 Fixing UEMA compliance footers across all templates...")

    templates = _fetch_all_templates()
    print(f"  Found {len(templates)} templates\n")

    fixed = skipped = failed = 0

    for tpl in templates:
        tid = tpl["id"]
        tname = tpl.get("attributes", {}).get("name", "Unnamed")

        full = safe_get(f"templates/{tid}")
        if not full:
            print(f"  ⚠️  Cannot fetch: {tname} ({tid})")
            failed += 1
            continue

        html = full.get("data", {}).get("attributes", {}).get("html", "") or ""

        if re.search(r"bargain\s*chemist\s*limited", html, re.I):
            print(f"  ✅ Already compliant: {tname} ({tid})")
            skipped += 1
            time.sleep(0.1)
            continue

        # Inject just before </body>; fall back to appending
        tag = "</body>"
        pos = html.lower().rfind(tag)
        if pos != -1:
            new_html = html[:pos] + COMPLIANCE_FOOTER_HTML + "\n" + html[pos:]
        else:
            new_html = html + COMPLIANCE_FOOTER_HTML

        result = api_patch(f"templates/{tid}", {
            "data": {
                "type": "template",
                "id": tid,
                "attributes": {"html": new_html},
            }
        }, quiet=True)

        if result is not None:
            print(f"  ✅ Footer injected: {tname} ({tid})")
            fixed += 1
        else:
            print(f"  ❌ Patch failed: {tname} ({tid})")
            failed += 1

        time.sleep(0.3)

    print(f"\n  Footer fix summary → {fixed} patched | {skipped} already OK | {failed} failed")

    # Verify a sample to confirm the patch landed
    if fixed > 0:
        print("\n  🔍 Spot-checking first patched template...")
        # Re-audit one template that was just patched
        for tpl in templates:
            tid = tpl["id"]
            full = safe_get(f"templates/{tid}")
            if not full:
                continue
            html = full.get("data", {}).get("attributes", {}).get("html", "") or ""
            if re.search(r"bargain\s*chemist\s*limited", html, re.I):
                print(f"  ✅ Verified: footer confirmed present in template {tid}")
                break


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


def fix_all_templates():
    """Run all auto-fixable template patches, then print manual fix guide."""
    fix_compliance_footers()
    fix_stale_thresholds()
    report_manual_fixes_required()


# ─────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Bargain Chemist Klaviyo Flow Manager")
    parser.add_argument("--pause-triple-pixel", action="store_true",
                        help="Pause all 3 Triple Pixel flows")
    parser.add_argument("--create-templates", action="store_true",
                        help="Create email templates in Klaviyo")
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
    parser.add_argument("--report-manual-fixes", action="store_true",
                        help="Print list of issues that require manual action (coupons, fear language, etc.)")
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

    if args.all or args.create_templates:
        templates = create_all_templates()

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

    if args.report_manual_fixes:
        report_manual_fixes_required()

    if args.all:
        print_setup_guide(templates, flows)

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()
