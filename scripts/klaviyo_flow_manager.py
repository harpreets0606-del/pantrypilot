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

import requests
import json
import argparse
import sys
import time

API_KEY = "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564"
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


def api_patch(path, payload):
    r = requests.patch(f"{BASE_URL}/{path}", headers=HEADERS, json=payload)
    if r.status_code not in (200, 204):
        print(f"  ⚠️  PATCH {path} → {r.status_code}: {r.text[:300]}")
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
                "attributes": {"status": "paused"},
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

    if args.all:
        print_setup_guide(templates, flows)

    print("\n✅ Done.\n")


if __name__ == "__main__":
    main()
