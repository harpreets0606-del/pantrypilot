"""
Fixes two issues:
  1. Deletes duplicate Oracoat template UepUh6 (no-logo copy; STBhAz is the good one).
  2. Rebuilds Post-Purchase Email 2 (Sy929J) — was structurally broken:
       - double nav bar (table + div)
       - CSS class divs that don't render in Outlook
       - double footer
       - off-brand orange unsubscribe bar (#f8971d)
     Rebuilt to match Email 1's clean table-based layout.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_postpurchase2_and_oracoat.py
"""

import os, sys, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

ORACOAT_DUPE_ID    = "UepUh6"   # no-logo duplicate — delete
POST_PURCHASE_2_ID = "Sy929J"   # rebuild


POST_PURCHASE_2_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Getting the most from your products</title>
<style>
@media only screen and (max-width:620px){
  h1{font-size:22px!important;line-height:1.3!important}
  td[style*="padding:36px 32px"],td[style*="padding:36px 40px"],
  td[style*="padding:32px 40px"],td[style*="padding:28px 40px"],
  td[style*="padding:24px 40px"],td[style*="padding:20px 40px"]{
    padding-left:20px!important;padding-right:20px!important}
  td[style*="font-size:28px"]{font-size:20px!important}
  td[width="33%"]{display:block!important;width:100%!important;
    border-left:none!important;border-right:none!important;
    padding:12px 16px!important;border-bottom:1px solid #eee}
  .bc-nav a{font-size:10px!important}
  .bc-nav td{padding:4px 5px!important}
  img[alt="Bargain Chemist"]{width:160px!important;max-width:160px!important}
}
</style>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px;width:100%;margin:0 auto;background-color:#ffffff;">

<!-- Free shipping bar -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#7B1523;" width="100%">
<tr><td align="center" style="padding:8px 16px;font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#ffffff;">
<a href="https://www.bargainchemist.co.nz" style="color:#ffffff;text-decoration:underline;" target="_blank">Free Shipping on Orders over $79*</a>
</td></tr>
</table>

<!-- Logo -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#CC1B2A;" width="100%">
<tr><td align="center" style="padding:20px 24px;">
<a href="https://www.bargainchemist.co.nz" style="text-decoration:none;display:block;" target="_blank">
<img alt="Bargain Chemist" border="0" src="https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218" style="display:block;margin:0 auto;max-width:100%;height:auto;" width="200"/>
</a>
</td></tr>
</table>

<!-- Nav -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#CC1B2A;border-top:1px solid rgba(255,255,255,0.25);" width="100%">
<tr><td align="center" class="bc-nav" style="padding:10px 8px;">
<table border="0" cellpadding="0" cellspacing="0"><tr>
<td style="padding:4px 10px;"><a href="https://www.bargainchemist.co.nz/collections/all" style="font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#ffffff;text-decoration:none;font-weight:500;" target="_blank">Shop Products</a></td>
<td style="padding:4px 10px;border-left:1px solid rgba(255,255,255,0.3);"><a href="https://www.bargainchemist.co.nz/collections/clearance" style="font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#ffffff;text-decoration:none;font-weight:500;" target="_blank">Clearance</a></td>
<td style="padding:4px 10px;border-left:1px solid rgba(255,255,255,0.3);"><a href="https://www.bargainchemist.co.nz/pages/find-a-pharmacy" style="font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#ffffff;text-decoration:none;font-weight:500;" target="_blank">Find a Pharmacy</a></td>
<td style="padding:4px 10px;border-left:1px solid rgba(255,255,255,0.3);"><a href="https://www.bargainchemist.co.nz/pages/contact" style="font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#ffffff;text-decoration:none;font-weight:500;" target="_blank">Contact Us</a></td>
</tr></table>
</td></tr>
</table>

<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#1a3a5c;" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px;font-family:Helvetica,Arial,sans-serif;font-size:13px;font-weight:600;color:rgba(255,255,255,0.75);text-transform:uppercase;letter-spacing:2px;">Your recent order</p>
<h1 style="margin:0 0 10px;font-family:Helvetica,Arial,sans-serif;font-size:28px;font-weight:bold;color:#ffffff;line-height:1.25;">Getting the most from your new products</h1>
<p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:15px;color:rgba(255,255,255,0.8);">A few tips to help your supplements work harder for you</p>
</td></tr>
</table>

<!-- Body -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:32px 40px 8px;font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#333333;line-height:1.7;">
<p style="margin:0 0 8px;font-size:18px;font-weight:bold;color:#1a1a1a;">Hi {{ first_name|default:'there' }},</p>
<p style="margin:0 0 24px;">Your order should have arrived by now — we hope you're happy with it. Here are a few tips to help you get the most out of your supplements.</p>

<!-- Tip 1 -->
<table border="0" cellpadding="0" cellspacing="0" style="margin-bottom:16px;" width="100%"><tr>
<td style="width:40px;min-width:40px;height:40px;background-color:#CC1B2A;border-radius:50%;text-align:center;vertical-align:middle;font-family:Helvetica,Arial,sans-serif;font-size:18px;" width="40">🌅</td>
<td style="padding-left:14px;font-family:Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.6;vertical-align:middle;">
<strong style="color:#1a1a1a;display:block;margin-bottom:2px;">Take supplements consistently</strong>
Most supplements work best when taken at the same time each day. Pick a time that fits your routine and stick to it.
</td>
</tr></table>

<!-- Tip 2 -->
<table border="0" cellpadding="0" cellspacing="0" style="margin-bottom:16px;" width="100%"><tr>
<td style="width:40px;min-width:40px;height:40px;background-color:#CC1B2A;border-radius:50%;text-align:center;vertical-align:middle;font-family:Helvetica,Arial,sans-serif;font-size:18px;" width="40">🍽️</td>
<td style="padding-left:14px;font-family:Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.6;vertical-align:middle;">
<strong style="color:#1a1a1a;display:block;margin-bottom:2px;">Take with food for better absorption</strong>
Fat-soluble vitamins (A, D, E, K) absorb better with a meal. Water-soluble vitamins (B, C) can be taken anytime.
</td>
</tr></table>

<!-- Tip 3 -->
<table border="0" cellpadding="0" cellspacing="0" style="margin-bottom:16px;" width="100%"><tr>
<td style="width:40px;min-width:40px;height:40px;background-color:#CC1B2A;border-radius:50%;text-align:center;vertical-align:middle;font-family:Helvetica,Arial,sans-serif;font-size:18px;" width="40">🌙</td>
<td style="padding-left:14px;font-family:Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.6;vertical-align:middle;">
<strong style="color:#1a1a1a;display:block;margin-bottom:2px;">Evening is best for magnesium</strong>
Magnesium may support relaxation and sleep quality when taken in the evening.
</td>
</tr></table>

<!-- Tip 4 -->
<table border="0" cellpadding="0" cellspacing="0" style="margin-bottom:24px;" width="100%"><tr>
<td style="width:40px;min-width:40px;height:40px;background-color:#CC1B2A;border-radius:50%;text-align:center;vertical-align:middle;font-family:Helvetica,Arial,sans-serif;font-size:18px;" width="40">⏰</td>
<td style="padding-left:14px;font-family:Helvetica,Arial,sans-serif;font-size:14px;color:#333;line-height:1.6;vertical-align:middle;">
<strong style="color:#1a1a1a;display:block;margin-bottom:2px;">Probiotics on an empty stomach</strong>
Many probiotics work best taken 30 minutes before a meal or first thing in the morning.
</td>
</tr></table>

<!-- Did you know -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#fef6f7;border-left:4px solid #CC1B2A;margin:0 0 24px;" width="100%">
<tr><td style="padding:18px 22px;font-family:Helvetica,Arial,sans-serif;font-size:14px;color:#444;line-height:1.6;">
<strong style="color:#CC1B2A;">Did you know?</strong> Bargain Chemist stocks over 10,000 products across health, beauty, personal care and household — all at everyday low prices. Our pharmacists are available in-store and happy to help with any questions about your purchase.
</td></tr>
</table>

</td></tr>
</table>

<!-- Category links -->
<table border="0" cellpadding="0" cellspacing="0" style="padding:0 40px 28px;" width="100%">
<tr><td style="padding:0 40px 28px;">
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td style="width:48%;background-color:#f9f9f9;border-radius:6px;padding:18px;text-align:center;vertical-align:top;" width="48%">
<p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;font-size:20px;">💊</p>
<p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;font-size:13px;font-weight:bold;color:#1a1a1a;">Health &amp; Wellbeing</p>
<p style="margin:0 0 12px;font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#666666;line-height:1.5;">Vitamins, supplements &amp; more</p>
<a href="https://www.bargainchemist.co.nz/collections/health-wellbeing" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:12px;font-weight:bold;text-decoration:none;padding:10px 20px;border-radius:4px;" target="_blank">Shop Now</a>
</td>
<td width="4%"></td>
<td style="width:48%;background-color:#f9f9f9;border-radius:6px;padding:18px;text-align:center;vertical-align:top;" width="48%">
<p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;font-size:20px;">🏷️</p>
<p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;font-size:13px;font-weight:bold;color:#1a1a1a;">Clearance Deals</p>
<p style="margin:0 0 12px;font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#666666;line-height:1.5;">Great deals on hundreds of products</p>
<a href="https://www.bargainchemist.co.nz/collections/clearance" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:12px;font-weight:bold;text-decoration:none;padding:10px 20px;border-radius:4px;" target="_blank">View Deals</a>
</td>
</tr></table>
</td></tr>
</table>

<!-- CTA -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td align="center" style="padding:0 40px 12px;">
<table border="0" cellpadding="0" cellspacing="0">
<tr><td align="center" style="background-color:#CC1B2A;border-radius:4px;">
<a href="https://www.bargainchemist.co.nz/collections/all" style="display:inline-block;padding:14px 36px;font-family:Helvetica,Arial,sans-serif;font-size:15px;font-weight:bold;color:#ffffff;text-decoration:none;" target="_blank">Shop All Products</a>
</td></tr>
</table>
</td></tr>
</table>

<!-- Disclaimer -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:16px 40px 24px;font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#999999;text-align:center;line-height:1.6;">
Always read the label and use as directed. If symptoms persist, consult your healthcare professional.
</td></tr>
</table>

<!-- Social -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;" width="100%">
<tr><td align="center" style="padding:9px 18px;font-family:Helvetica,Arial,sans-serif;font-size:28px;font-weight:bold;color:#222222;text-align:center;">Get social with us!</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;" width="100%">
<tr><td align="center" style="padding:9px;">
<a href="https://tiktok.com/@bargainchemistnz" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="TikTok" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/tiktok_96.png" style="width:48px;display:inline-block;" width="48"/></a>
<a href="https://www.facebook.com/BargainChemist/" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="Facebook" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/facebook_96.png" style="width:48px;display:inline-block;" width="48"/></a>
<a href="https://instagram.com/bargainchemistnz" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="Instagram" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/instagram_96.png" style="width:48px;display:inline-block;" width="48"/></a>
<a href="https://nz.linkedin.com/company/bargain-chemist" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="LinkedIn" src="https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/791081ec-bce5-4d35-9ee4-aa35ada53088.png" style="width:48px;display:inline-block;" width="48"/></a>
</td></tr>
</table>

<!-- Legal footer -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FF0031;" width="100%">
<tr><td style="padding:15px 30px 9px;font-family:Helvetica,Arial,sans-serif;font-size:9px;color:#ffffff;line-height:1.3;text-align:center;font-weight:100;">
Please note that not all products may be available in all stores, please call your closest Bargain Chemist pharmacy or visit our store locator to find a <a href="https://www.bargainchemist.co.nz/pages/find-a-store" style="color:#ffffff;text-decoration:underline;">pharmacy near you</a>. Prices shown are online prices only and may differ to in store. Save price, and Why Pay pricing is based on the recommended retailer price (RRP). Where no RRP is supplied, RRP is based on what is found at competing New Zealand retailers. Actual delivered product packaging may differ slightly from the product image shown online. <a href="https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist" style="color:#ffffff;text-decoration:underline;">Price beat guarantee</a> - If you find a cheaper everyday price on an identical in stock item at a New Zealand pharmacy we will beat the difference by 10%. *Vitamins and minerals are supplementary to and not a replacement for a balanced diet. Always read the label, use only as directed. If symptoms persist, see your healthcare professional. Weight management products should be used with a balanced diet and exercise. **Pharmacist only products - your pharmacist will advise you whether this preparation is suitable for your condition. The pharmacist reserves the right not to supply when contrary to our professional and ethical obligation.
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FF0031;" width="100%">
<tr><td align="center" style="padding:5px 18px 20px;font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#ffffff;font-weight:100;text-align:center;line-height:1.1;">
No longer want to receive these emails? {% unsubscribe %}.<br/>{{ organization.name }} {{ organization.full_address }}
</td></tr>
</table>

</div>
</body>
</html>
"""


def delete_template(tid: str) -> None:
    r = requests.delete(f"{BASE_URL}/templates/{tid}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")


def update_template(tid: str, name: str, html: str) -> None:
    payload = {"data": {"type": "template", "id": tid, "attributes": {"name": name, "html": html}}}
    r = requests.patch(f"{BASE_URL}/templates/{tid}", headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print(f"1. Deleting Oracoat duplicate {ORACOAT_DUPE_ID}...")
    try:
        delete_template(ORACOAT_DUPE_ID)
        print("   ✓ Deleted")
    except Exception as e:
        print(f"   ✗ {e}")

    print(f"\n2. Rebuilding Post-Purchase Email 2 {POST_PURCHASE_2_ID}...")
    print("   (removing double nav, CSS divs, double footer, off-brand orange bar)")
    try:
        update_template(POST_PURCHASE_2_ID, "[Z] Post-Purchase Email 2 - Tips and Value", POST_PURCHASE_2_HTML)
        print("   ✓ Updated")
        print(f"   Preview: https://www.klaviyo.com/email-editor/{POST_PURCHASE_2_ID}/edit")
    except Exception as e:
        print(f"   ✗ {e}")


if __name__ == "__main__":
    main()
