"""
Rebuilds Post-Purchase Emails 3 and 4 — same issues as Email 2:
  - double nav (table header + stray div nav)
  - CSS class div body that breaks in Outlook
  - off-brand orange unsubscribe bar (#f8971d)
  - duplicate footer

Rebuilt to match Email 1's clean table-based structure.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_postpurchase3_and_4.py
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

EMAIL_3_ID = "UNjrA4"
EMAIL_4_ID = "SQD3nM"

SHARED_HEADER = """\
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
</table>"""

SHARED_FOOTER = """\
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
<!-- Legal -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FF0031;" width="100%">
<tr><td style="padding:15px 30px 9px;font-family:Helvetica,Arial,sans-serif;font-size:9px;color:#ffffff;line-height:1.3;text-align:center;font-weight:100;">
Please note that not all products may be available in all stores, please call your closest Bargain Chemist pharmacy or visit our store locator to find a <a href="https://www.bargainchemist.co.nz/pages/find-a-store" style="color:#ffffff;text-decoration:underline;">pharmacy near you</a>. Prices shown are online prices only and may differ to in store. Save price, and Why Pay pricing is based on the recommended retailer price (RRP). Where no RRP is supplied, RRP is based on what is found at competing New Zealand retailers. Actual delivered product packaging may differ slightly from the product image shown online. <a href="https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist" style="color:#ffffff;text-decoration:underline;">Price beat guarantee</a> - If you find a cheaper everyday price on an identical in stock item at a New Zealand pharmacy we will beat the difference by 10%. *Vitamins and minerals are supplementary to and not a replacement for a balanced diet. Always read the label, use only as directed. If symptoms persist, see your healthcare professional. Weight management products should be used with a balanced diet and exercise. **Pharmacist only products - your pharmacist will advise you whether this preparation is suitable for your condition. The pharmacist reserves the right not to supply when contrary to our professional and ethical obligation.
</td></tr>
</table>
<!-- Unsubscribe -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FF0031;" width="100%">
<tr><td align="center" style="padding:5px 18px 20px;font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#ffffff;font-weight:100;text-align:center;line-height:1.1;">
No longer want to receive these emails? {% unsubscribe %}.<br/>{{ organization.name }} {{ organization.full_address }}
</td></tr>
</table>"""

SHARED_CSS = """\
@media only screen and (max-width:620px){
  h1{font-size:22px!important;line-height:1.3!important}
  td[style*="padding:36px 32px"],td[style*="padding:36px 40px"],
  td[style*="padding:32px 40px"],td[style*="padding:28px 40px"],
  td[style*="padding:24px 40px"],td[style*="padding:20px 40px"]{
    padding-left:20px!important;padding-right:20px!important}
  td[style*="font-size:28px"]{font-size:20px!important}
  td[width="33%"],td[width="25%"]{display:block!important;width:100%!important;
    border-left:none!important;border-right:none!important;
    padding:12px 16px!important;border-bottom:1px solid #eee}
  .bc-nav a{font-size:10px!important}
  .bc-nav td{padding:4px 5px!important}
  img[alt="Bargain Chemist"]{width:160px!important;max-width:160px!important}
}"""


def build_email3():
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>How are you finding it?</title>
<style>{SHARED_CSS}</style>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px;width:100%;margin:0 auto;background-color:#ffffff;">

{SHARED_HEADER}

<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#CC1B2A;" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px;font-family:Helvetica,Arial,sans-serif;font-size:13px;font-weight:600;color:rgba(255,255,255,0.75);text-transform:uppercase;letter-spacing:2px;">One week on</p>
<h1 style="margin:0 0 10px;font-family:Helvetica,Arial,sans-serif;font-size:28px;font-weight:bold;color:#ffffff;line-height:1.25;">How are you finding it, {{ first_name|default:'there' }}?</h1>
<p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:15px;color:rgba(255,255,255,0.85);">A quick moment to share your thoughts would mean the world to us</p>
</td></tr>
</table>

<!-- Body -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:32px 40px 24px;font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#333333;line-height:1.7;">
<p style="margin:0 0 8px;font-size:18px;font-weight:bold;color:#1a1a1a;">Hi {{ first_name|default:'there' }},</p>
<p style="margin:0 0 24px;">You've had your order for about a week now — we hope you're loving it. If you have a moment, we'd really appreciate a quick review. It helps other Kiwis make confident choices.</p>

<!-- Stars box -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#fef6f7;border-radius:8px;margin-bottom:24px;" width="100%">
<tr><td align="center" style="padding:28px 24px;">
<p style="margin:0 0 12px;font-size:36px;letter-spacing:4px;">&#11088;&#11088;&#11088;&#11088;&#11088;</p>
<p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;font-size:17px;font-weight:bold;color:#CC1B2A;">How would you rate your experience?</p>
<p style="margin:0 0 18px;font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#666666;">Takes less than a minute — your feedback makes a real difference</p>
<table border="0" cellpadding="0" cellspacing="0"><tr>
<td align="center" style="background-color:#CC1B2A;border-radius:4px;">
<a href="https://www.bargainchemist.co.nz" style="display:inline-block;padding:13px 32px;font-family:Helvetica,Arial,sans-serif;font-size:15px;font-weight:bold;color:#ffffff;text-decoration:none;" target="_blank">Write a Review</a>
</td></tr></table>
</td></tr>
</table>

<p style="margin:0 0 24px;font-family:Helvetica,Arial,sans-serif;font-size:14px;color:#666666;text-align:center;">Not happy with something? Please reply to this email — we'd love the chance to make it right.</p>

<!-- Category links -->
<p style="margin:0 0 14px;font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#999999;text-transform:uppercase;letter-spacing:1.5px;text-align:center;">While you're here — explore more</p>
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td style="width:31%;background-color:#f9f9f9;border-radius:6px;padding:14px 6px;text-align:center;vertical-align:top;" width="31%">
<p style="font-size:20px;margin:0 0 4px 0;">&#128138;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:12px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Supplements</p>
<a href="https://www.bargainchemist.co.nz/collections/vitamins-supplements" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;text-decoration:none;padding:7px 14px;border-radius:4px;" target="_blank">Shop</a>
</td>
<td width="3%"></td>
<td style="width:31%;background-color:#f9f9f9;border-radius:6px;padding:14px 6px;text-align:center;vertical-align:top;" width="31%">
<p style="font-size:20px;margin:0 0 4px 0;">&#10024;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:12px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Skin Care</p>
<a href="https://www.bargainchemist.co.nz/collections/skincare" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;text-decoration:none;padding:7px 14px;border-radius:4px;" target="_blank">Shop</a>
</td>
<td width="3%"></td>
<td style="width:31%;background-color:#f9f9f9;border-radius:6px;padding:14px 6px;text-align:center;vertical-align:top;" width="31%">
<p style="font-size:20px;margin:0 0 4px 0;">&#127991;&#65039;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:12px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Clearance</p>
<a href="https://www.bargainchemist.co.nz/collections/clearance" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;text-decoration:none;padding:7px 14px;border-radius:4px;" target="_blank">Shop</a>
</td>
</tr></table>
</td></tr>
</table>

{SHARED_FOOTER}

</div>
</body>
</html>"""


def build_email4():
    return f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Running low?</title>
<style>{SHARED_CSS}</style>
</head>
<body style="margin:0;padding:0;background-color:#f5f5f5;font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px;width:100%;margin:0 auto;background-color:#ffffff;">

{SHARED_HEADER}

<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#1a1a1a;" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px;font-family:Helvetica,Arial,sans-serif;font-size:13px;font-weight:600;color:#CC1B2A;text-transform:uppercase;letter-spacing:2px;">Two-week reminder</p>
<h1 style="margin:0 0 10px;font-family:Helvetica,Arial,sans-serif;font-size:30px;font-weight:bold;color:#ffffff;line-height:1.2;">Running low, <span style="color:#CC1B2A;">{{ first_name|default:'there' }}</span>?</h1>
<p style="margin:0;font-family:Helvetica,Arial,sans-serif;font-size:15px;color:#cccccc;">It&#8217;s been two weeks — time to think about restocking</p>
</td></tr>
</table>

<!-- Body -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:32px 40px 24px;font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#333333;line-height:1.7;">
<p style="margin:0 0 8px;font-size:18px;font-weight:bold;color:#1a1a1a;">Hi {{ first_name|default:'there' }},</p>
<p style="margin:0 0 24px;">It&#8217;s been about two weeks since your last order. If you&#8217;re on a supplement or health routine, now&#8217;s a good time to reorder before you run out &#8212; staying consistent is what makes these products work.</p>

<!-- Reorder box -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#fef6f7;border:2px solid #CC1B2A;border-radius:8px;margin-bottom:24px;" width="100%">
<tr><td align="center" style="padding:24px;">
<p style="margin:0 0 6px;font-family:Helvetica,Arial,sans-serif;font-size:17px;font-weight:bold;color:#CC1B2A;">&#128260; Time to Restock?</p>
<p style="margin:0 0 18px;font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#555555;">Reorder in seconds &#8212; same products, same prices</p>
<table border="0" cellpadding="0" cellspacing="0"><tr>
<td align="center" style="background-color:#CC1B2A;border-radius:4px;">
<a href="https://www.bargainchemist.co.nz/collections/all" style="display:inline-block;padding:13px 32px;font-family:Helvetica,Arial,sans-serif;font-size:15px;font-weight:bold;color:#ffffff;text-decoration:none;" target="_blank">Reorder Now</a>
</td></tr></table>
</td></tr>
</table>

<!-- 4-column category grid -->
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td style="width:22%;background-color:#f9f9f9;border-radius:6px;padding:12px 4px;text-align:center;vertical-align:top;" width="22%">
<p style="font-size:18px;margin:0 0 4px 0;">&#128138;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Health</p>
<a href="https://www.bargainchemist.co.nz/collections/health-wellbeing" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:bold;text-decoration:none;padding:6px 12px;border-radius:4px;" target="_blank">Shop</a>
</td>
<td width="2%"></td>
<td style="width:22%;background-color:#f9f9f9;border-radius:6px;padding:12px 4px;text-align:center;vertical-align:top;" width="22%">
<p style="font-size:18px;margin:0 0 4px 0;">&#129404;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Personal Care</p>
<a href="https://www.bargainchemist.co.nz/collections/personal-care" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:bold;text-decoration:none;padding:6px 12px;border-radius:4px;" target="_blank">Shop</a>
</td>
<td width="2%"></td>
<td style="width:22%;background-color:#f9f9f9;border-radius:6px;padding:12px 4px;text-align:center;vertical-align:top;" width="22%">
<p style="font-size:18px;margin:0 0 4px 0;">&#10024;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Skin Care</p>
<a href="https://www.bargainchemist.co.nz/collections/skincare" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:bold;text-decoration:none;padding:6px 12px;border-radius:4px;" target="_blank">Shop</a>
</td>
<td width="2%"></td>
<td style="width:22%;background-color:#f9f9f9;border-radius:6px;padding:12px 4px;text-align:center;vertical-align:top;" width="22%">
<p style="font-size:18px;margin:0 0 4px 0;">&#127991;&#65039;</p>
<p style="font-family:Helvetica,Arial,sans-serif;font-size:11px;font-weight:bold;color:#333333;margin:0 0 10px 0;">Clearance</p>
<a href="https://www.bargainchemist.co.nz/collections/clearance" style="display:inline-block;background-color:#CC1B2A;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:10px;font-weight:bold;text-decoration:none;padding:6px 12px;border-radius:4px;" target="_blank">Shop</a>
</td>
</tr></table>

<p style="margin:20px 0 0;font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#999999;text-align:center;line-height:1.5;">Always read the label and use as directed. If symptoms persist, consult your healthcare professional.</p>
</td></tr>
</table>

{SHARED_FOOTER}

</div>
</body>
</html>"""


def update_template(tid: str, name: str, html: str) -> None:
    payload = {"data": {"type": "template", "id": tid, "attributes": {"name": name, "html": html}}}
    r = requests.patch(f"{BASE_URL}/templates/{tid}", headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print(f"1. Rebuilding {EMAIL_3_ID}  [Z] Post-Purchase Email 3 - Review Request")
    try:
        update_template(EMAIL_3_ID, "[Z] Post-Purchase Email 3 - Review Request", build_email3())
        print(f"   ✓ Updated  —  https://www.klaviyo.com/email-editor/{EMAIL_3_ID}/edit")
    except Exception as e:
        print(f"   ✗ {e}")

    print(f"\n2. Rebuilding {EMAIL_4_ID}  [Z] Post-Purchase Email 4 - Replenishment Signal")
    try:
        update_template(EMAIL_4_ID, "[Z] Post-Purchase Email 4 - Replenishment Signal", build_email4())
        print(f"   ✓ Updated  —  https://www.klaviyo.com/email-editor/{EMAIL_4_ID}/edit")
    except Exception as e:
        print(f"   ✗ {e}")


if __name__ == "__main__":
    main()
