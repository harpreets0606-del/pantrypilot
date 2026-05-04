"""
Fixes two [Z] template issues:
  1. Deletes [Z] Post-Purchase Email 2 - Tips & Value (T99zJf)
     — misbranded draft (text header, wrong red #CC1B2A) superseded by
       the correctly branded "Tips and Value" copy.
  2. Rebuilds [Z] Flow — Flu Season Email 1 (SMDszN)
     — was truncated mid-template with a broken CTA; replaces with
       a complete, on-brand flu season email.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_template_designs.py
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

TIPS_VALUE_ID = "T99zJf"   # delete — misbranded, good copy "Tips and Value" already exists
FLU_SEASON_ID = "SMDszN"   # rebuild — was truncated


FLU_SEASON_HTML = """\
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta content="text/html; charset=utf-8" http-equiv="Content-Type"/>
<meta content="width=device-width, initial-scale=1" name="viewport"/>
<title>Stay Well This Winter</title>
<style>
body{margin:0;padding:0;background-color:#f7f7f7;font-family:Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%}
table,td{border-collapse:collapse;mso-table-lspace:0;mso-table-rspace:0}
img{border:0;line-height:100%;outline:none;text-decoration:none;max-width:100%;height:auto}
p{margin:0;padding:0}
a{color:#FF0031}
@media only screen and (max-width:600px){
  .container{width:100%!important}
  .mobile-pad{padding-left:20px!important;padding-right:20px!important}
  .mobile-stack{display:block!important;width:100%!important;margin-bottom:12px!important}
  .hero-text{font-size:28px!important;line-height:1.2!important}
  .btn{width:80%!important}
}
</style>
</head>
<body style="background-color:#f7f7f7;margin:0;padding:0">

<!-- Preheader -->
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all">Flu season is here, {{ person.first_name|default:'friend' }}. Here&#8217;s how to stay well this winter &#8203;&#8204;&#8205;</div>

<table align="center" border="0" cellpadding="0" cellspacing="0" style="background-color:#f7f7f7" width="100%">
<tr><td align="center" style="padding:20px 10px">
<table align="center" border="0" cellpadding="0" cellspacing="0" class="container" style="background-color:#ffffff" width="600">

<!-- HEADER -->
<tr>
<td style="background-color:#FF0031;padding:24px 20px 16px 20px;text-align:center">
<a href="https://www.bargainchemist.co.nz/" target="_blank">
<img alt="Bargain Chemist" src="https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218" style="display:block;margin:0 auto 16px auto" width="200"/>
</a>
<table align="center" border="0" cellpadding="0" cellspacing="0">
<tr>
<td style="padding:0 8px"><a href="https://www.bargainchemist.co.nz/" style="color:#ffffff;font-family:Helvetica,Arial;font-size:12px;text-decoration:none;letter-spacing:1px" target="_blank">Shop Now</a></td>
<td style="color:#ffffff;font-size:10px">|</td>
<td style="padding:0 8px"><a href="https://www.bargainchemist.co.nz/pages/find-a-store" style="color:#ffffff;font-family:Helvetica,Arial;font-size:12px;text-decoration:none;letter-spacing:1px" target="_blank">Find a Pharmacy</a></td>
<td style="color:#ffffff;font-size:10px">|</td>
<td style="padding:0 8px"><a href="https://www.bargainchemist.co.nz/pages/flu-vaccination" style="color:#ffffff;font-family:Helvetica,Arial;font-size:12px;text-decoration:none;letter-spacing:1px" target="_blank">Book Flu Vaccine</a></td>
</tr>
</table>
</td>
</tr>

<!-- HERO -->
<tr>
<td style="background-color:#1a3a5c;padding:40px 40px 36px 40px;text-align:center">
<p style="font-family:Helvetica,Arial;font-size:13px;color:#7eb8e8;letter-spacing:2px;text-transform:uppercase;margin-bottom:12px">Winter Wellness</p>
<h1 class="hero-text" style="font-family:Helvetica,Arial;font-size:36px;font-weight:700;color:#ffffff;line-height:1.15;margin:0 0 16px 0">Stay well this<br/>flu season, {{ person.first_name|default:'friend' }}</h1>
<p style="font-family:Helvetica,Arial;font-size:16px;color:#b8d4f0;line-height:1.6;margin:0 0 28px 0">NZ flu season peaks May&#8211;July. Give your immune<br/>system the support it needs before symptoms strike.</p>
<a class="btn" href="https://www.bargainchemist.co.nz/collections/cold-flu" style="display:inline-block;background-color:#FF0031;color:#ffffff;font-family:Helvetica,Arial;font-size:14px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:4px;letter-spacing:1px;text-transform:uppercase" target="_blank">Shop Winter Wellness</a>
</td>
</tr>

<!-- INTRO -->
<tr>
<td class="mobile-pad" style="padding:36px 40px 24px 40px">
<p style="font-family:Helvetica,Arial;font-size:16px;color:#1a1a1a;line-height:1.7">Hi {{ person.first_name|default:'there' }},</p>
<p style="font-family:Helvetica,Arial;font-size:16px;color:#444444;line-height:1.7;margin-top:16px">With flu season just around the corner, now is the perfect time to stock up on the essentials and make sure your immune system is ready. Here are our top recommendations for staying well this winter.</p>
</td>
</tr>

<!-- 3 TIPS -->
<tr>
<td class="mobile-pad" style="padding:0 40px 32px 40px">
<p style="font-family:Helvetica,Arial;font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:20px">3 simple ways to stay ahead this winter</p>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td style="padding:16px;background-color:#f0f6ff;border-radius:6px" valign="top">
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td style="width:36px;vertical-align:top;padding-right:14px"><p style="font-size:22px;margin:0">&#128521;</p></td>
<td valign="top">
<p style="font-family:Helvetica,Arial;font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:6px">Get your flu vaccine</p>
<p style="font-family:Helvetica,Arial;font-size:14px;color:#555555;line-height:1.6">The most effective protection available. Book yours at your nearest Bargain Chemist pharmacy &#8212; walk-ins welcome at most locations.</p>
</td>
</tr></table>
</td>
</tr>
<tr><td style="height:10px"></td></tr>
<tr>
<td style="padding:16px;background-color:#f0f6ff;border-radius:6px" valign="top">
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td style="width:36px;vertical-align:top;padding-right:14px"><p style="font-size:22px;margin:0">&#129697;</p></td>
<td valign="top">
<p style="font-family:Helvetica,Arial;font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:6px">Support your immune system daily</p>
<p style="font-family:Helvetica,Arial;font-size:14px;color:#555555;line-height:1.6">Vitamin C, Zinc and Vitamin D are proven to support immune function. Start supplementing now &#8212; before you feel rundown.</p>
</td>
</tr></table>
</td>
</tr>
<tr><td style="height:10px"></td></tr>
<tr>
<td style="padding:16px;background-color:#f0f6ff;border-radius:6px" valign="top">
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td style="width:36px;vertical-align:top;padding-right:14px"><p style="font-size:22px;margin:0">&#127968;</p></td>
<td valign="top">
<p style="font-family:Helvetica,Arial;font-size:15px;font-weight:700;color:#1a1a1a;margin-bottom:6px">Stock your medicine cabinet now</p>
<p style="font-family:Helvetica,Arial;font-size:14px;color:#555555;line-height:1.6">Have cold and flu treatments ready before you need them &#8212; paracetamol, decongestants, throat lozenges and nasal sprays are winter must-haves.</p>
</td>
</tr></table>
</td>
</tr>
</table>
</td>
</tr>

<!-- PRODUCT CATEGORIES -->
<tr>
<td class="mobile-pad" style="background-color:#f7f7f7;padding:32px 40px">
<p style="font-family:Helvetica,Arial;font-size:18px;font-weight:700;color:#1a1a1a;margin-bottom:20px;text-align:center">Shop winter wellness essentials</p>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td class="mobile-stack" style="width:31%;background-color:#ffffff;border-radius:6px;padding:20px;text-align:center;vertical-align:top">
<p style="font-size:28px;margin:0 0 10px 0">&#129302;</p>
<p style="font-family:Helvetica,Arial;font-size:13px;font-weight:700;color:#1a1a1a;margin-bottom:8px">Cold &amp; Flu</p>
<p style="font-family:Helvetica,Arial;font-size:12px;color:#666666;line-height:1.5;margin-bottom:14px">Treatments &amp; relief for when it hits</p>
<a href="https://www.bargainchemist.co.nz/collections/cold-flu" style="display:inline-block;background-color:#FF0031;color:#ffffff;font-family:Helvetica,Arial;font-size:11px;font-weight:700;text-decoration:none;padding:9px 18px;border-radius:4px;text-transform:uppercase" target="_blank">Shop Now</a>
</td>
<td style="width:3%"></td>
<td class="mobile-stack" style="width:31%;background-color:#ffffff;border-radius:6px;padding:20px;text-align:center;vertical-align:top">
<p style="font-size:28px;margin:0 0 10px 0">&#128138;</p>
<p style="font-family:Helvetica,Arial;font-size:13px;font-weight:700;color:#1a1a1a;margin-bottom:8px">Vitamins &amp; Immunity</p>
<p style="font-family:Helvetica,Arial;font-size:12px;color:#666666;line-height:1.5;margin-bottom:14px">Vitamin C, D, Zinc &amp; more</p>
<a href="https://www.bargainchemist.co.nz/collections/vitamins-supplements" style="display:inline-block;background-color:#FF0031;color:#ffffff;font-family:Helvetica,Arial;font-size:11px;font-weight:700;text-decoration:none;padding:9px 18px;border-radius:4px;text-transform:uppercase" target="_blank">Shop Now</a>
</td>
<td style="width:3%"></td>
<td class="mobile-stack" style="width:31%;background-color:#ffffff;border-radius:6px;padding:20px;text-align:center;vertical-align:top">
<p style="font-size:28px;margin:0 0 10px 0">&#127807;</p>
<p style="font-family:Helvetica,Arial;font-size:13px;font-weight:700;color:#1a1a1a;margin-bottom:8px">Natural Remedies</p>
<p style="font-family:Helvetica,Arial;font-size:12px;color:#666666;line-height:1.5;margin-bottom:14px">Echinacea, elderberry &amp; herbal</p>
<a href="https://www.bargainchemist.co.nz/collections/natural-health" style="display:inline-block;background-color:#FF0031;color:#ffffff;font-family:Helvetica,Arial;font-size:11px;font-weight:700;text-decoration:none;padding:9px 18px;border-radius:4px;text-transform:uppercase" target="_blank">Shop Now</a>
</td>
</tr>
</table>
</td>
</tr>

<!-- FLU VACCINE BANNER -->
<tr>
<td class="mobile-pad" style="background-color:#1a3a5c;padding:32px 40px;text-align:center">
<p style="font-family:Helvetica,Arial;font-size:13px;color:#7eb8e8;letter-spacing:2px;text-transform:uppercase;margin-bottom:10px">Available at Bargain Chemist</p>
<p style="font-family:Helvetica,Arial;font-size:22px;font-weight:700;color:#ffffff;margin-bottom:10px;line-height:1.3">Book your flu vaccination today</p>
<p style="font-family:Helvetica,Arial;font-size:14px;color:#b8d4f0;line-height:1.6;margin-bottom:24px">Fast, convenient and affordable. Walk-ins welcome at most locations.<br/>Protect yourself and those around you this winter.</p>
<a class="btn" href="https://www.bargainchemist.co.nz/pages/flu-vaccination" style="display:inline-block;background-color:#FF0031;color:#ffffff;font-family:Helvetica,Arial;font-size:14px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:4px;letter-spacing:1px;text-transform:uppercase" target="_blank">Book Now</a>
</td>
</tr>

<!-- DISCLAIMER -->
<tr>
<td class="mobile-pad" style="padding:24px 40px;background-color:#ffffff">
<p style="font-family:Helvetica,Arial;font-size:12px;color:#999999;line-height:1.6;text-align:center">Always read the label and use as directed. Supplementation should complement, not replace, a balanced diet. If symptoms persist, see your healthcare professional.</p>
</td>
</tr>

<!-- FOOTER -->
<tr>
<td class="mobile-pad" style="background-color:#f7f7f7;padding:20px 40px;text-align:center;border-top:1px solid #eeeeee">
<p style="font-family:Helvetica,Arial;font-size:13px;color:#888888;margin-bottom:8px">Questions? <a href="mailto:hello@bargainchemist.co.nz" style="color:#FF0031;text-decoration:none">hello@bargainchemist.co.nz</a></p>
</td>
</tr>
<tr>
<td class="mobile-pad" style="background-color:#1a1a1a;padding:24px 40px;text-align:center">
<p style="font-family:Helvetica,Arial;font-size:12px;color:#888888;margin-bottom:8px">&#169; 2026 Bargain Chemist. All rights reserved.</p>
<p style="font-family:Helvetica,Arial;font-size:12px;color:#888888">{% unsubscribe 'Unsubscribe' %} &nbsp;&#183;&nbsp; <a href="https://bargainchemist.co.nz/pages/privacy-policy" style="color:#888888;text-decoration:none">Privacy Policy</a></p>
</td>
</tr>

</table>
</td></tr></table>
</body>
</html>
"""


def delete_template(tid: str) -> None:
    r = requests.delete(f"{BASE_URL}/templates/{tid}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")


def update_template(tid: str, name: str, html: str) -> None:
    payload = {
        "data": {
            "type": "template",
            "id": tid,
            "attributes": {"name": name, "html": html},
        }
    }
    r = requests.patch(
        f"{BASE_URL}/templates/{tid}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print(f"1. Deleting {TIPS_VALUE_ID}  [Z] Post-Purchase Email 2 - Tips & Value")
    print("   (misbranded draft — correct 'Tips and Value' copy already exists)")
    try:
        delete_template(TIPS_VALUE_ID)
        print("   ✓ Deleted")
    except Exception as e:
        print(f"   ✗ {e}")

    print()
    print(f"2. Rebuilding {FLU_SEASON_ID}  [Z] Flow — Flu Season Email 1")
    print("   (was truncated mid-template with a broken CTA)")
    try:
        update_template(
            FLU_SEASON_ID,
            "[Z] Flow — Flu Season Email 1 (Immune Support)",
            FLU_SEASON_HTML,
        )
        print("   ✓ Updated")
        print(f"   Preview: https://www.klaviyo.com/email-editor/{FLU_SEASON_ID}/edit")
    except Exception as e:
        print(f"   ✗ {e}")


if __name__ == "__main__":
    main()
