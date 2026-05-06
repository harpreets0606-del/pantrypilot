"""
Replenishment flow retail-first templates for Bargain Chemist.

Final 16-slot map locked 2026-05-06 based on 180-day Shopify analytics.
See klaviyo/FLOWS_AUDIT.md for the comprehensive analysis.

Each template uses BC's bespoke anatomy (shipping bar #7B1523 → red logo
#CC1B2A → nav → red hero → body + product grid → social row → red
#FF0031 legal block → unsubscribe block) and follows BRAND_VOICE.md:
- Variables: {{ first_name|default:'there' }} (double brace)
- $79 free shipping threshold
- ASA-appropriate disclaimers per category
- No fear language, no coupons, no 🚨 (Price Smash only)
- Subject 30-55 chars, BC pattern openers

Slot configurations map each Replenishment flow-action to a retail
category. Generate HTML on demand with render_replenishment_template().
"""

# ─────────────────────────────────────────────────────────────────
# Brand constants
# ─────────────────────────────────────────────────────────────────
BRAND_RED = "#CC1B2A"
LEGAL_RED = "#FF0031"
SHIPPING_RED = "#7B1523"
DARK = "#1a1a1a"
BODY_TEXT = "#333333"
MUTED = "#666666"
LIGHT_PINK = "#fef6f7"

LOGO_URL = "https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218"
HOMEPAGE = "https://www.bargainchemist.co.nz"


# ─────────────────────────────────────────────────────────────────
# Shared anatomy: header (shipping bar + logo + nav) and footer
# (social + legal block + unsubscribe). Both blocks match the
# bespoke BC template family found in production templates.
# ─────────────────────────────────────────────────────────────────
HEADER_HTML = f"""<!-- BC Header: Free Shipping bar -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{SHIPPING_RED};" width="100%">
<tr><td align="center" style="padding:8px 16px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#ffffff;">
<a href="{HOMEPAGE}" style="color:#ffffff; text-decoration:underline;" target="_blank">Free Shipping on Orders over $79*</a>
</td></tr>
</table>
<!-- BC Header: Logo -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED};" width="100%">
<tr><td align="center" style="padding:20px 24px;">
<a href="{HOMEPAGE}" style="text-decoration:none; display:block;" target="_blank">
<img alt="Bargain Chemist" border="0" src="{LOGO_URL}" style="display:block; margin:0 auto; max-width:100%; height:auto;" width="200"/>
</a>
</td></tr>
</table>
<!-- BC Header: Nav -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED}; border-top:1px solid rgba(255,255,255,0.25);" width="100%">
<tr><td align="center" class="bc-nav" style="padding:10px 8px;">
<table border="0" cellpadding="0" cellspacing="0"><tr>
<td style="padding:4px 10px;"><a href="{HOMEPAGE}/collections/all" style="font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#ffffff; text-decoration:none; font-weight:500;" target="_blank">Shop Products</a></td>
<td style="padding:4px 10px; border-left:1px solid rgba(255,255,255,0.3);"><a href="{HOMEPAGE}/collections/clearance" style="font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#ffffff; text-decoration:none; font-weight:500;" target="_blank">Clearance</a></td>
<td style="padding:4px 10px; border-left:1px solid rgba(255,255,255,0.3);"><a href="{HOMEPAGE}/pages/find-a-pharmacy" style="font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#ffffff; text-decoration:none; font-weight:500;" target="_blank">Find a Pharmacy</a></td>
<td style="padding:4px 10px; border-left:1px solid rgba(255,255,255,0.3);"><a href="{HOMEPAGE}/pages/contact" style="font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#ffffff; text-decoration:none; font-weight:500;" target="_blank">Contact Us</a></td>
</tr></table>
</td></tr>
</table>"""

FOOTER_HTML = """<!-- Social -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;" width="100%">
<tr><td align="center" style="padding:9px 18px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#222222; text-align:center;">Get social with us!</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#ffffff;" width="100%">
<tr><td align="center" style="padding:9px;">
<a href="https://tiktok.com/@bargainchemistnz" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank"><img alt="TikTok" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/tiktok_96.png" style="width:48px; display:inline-block;" width="48"/></a>
<a href="https://www.facebook.com/BargainChemist/" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank"><img alt="Facebook" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/facebook_96.png" style="width:48px; display:inline-block;" width="48"/></a>
<a href="https://instagram.com/bargainchemistnz" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank"><img alt="Instagram" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/instagram_96.png" style="width:48px; display:inline-block;" width="48"/></a>
<a href="https://nz.linkedin.com/company/bargain-chemist" style="text-decoration:none; display:inline-block; margin:0 5px;" target="_blank"><img alt="LinkedIn" src="https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/791081ec-bce5-4d35-9ee4-aa35ada53088.png" style="width:48px; display:inline-block;" width="48"/></a>
</td></tr>
</table>
<!-- Legal disclaimer -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FF0031;" width="100%">
<tr><td style="padding:15px 30px 9px; font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#ffffff; line-height:1.3; text-align:center; font-weight:100;">
Please note that not all products may be available in all stores, please call your closest Bargain Chemist pharmacy or visit our store locator to find a <a href="https://www.bargainchemist.co.nz/pages/find-a-store" style="color:#ffffff; text-decoration:underline;">pharmacy near you</a>. Prices shown are online prices only and may differ to in store. Save price, and Why Pay pricing is based on the recommended retailer price (RRP). Where no RRP is supplied, RRP is based on what is found at competing New Zealand retailers. Actual delivered product packaging may differ slightly from the product image shown online. <a href="https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist" style="color:#ffffff; text-decoration:underline;">Price beat guarantee</a> - If you find a cheaper everyday price on an identical in stock item at a New Zealand pharmacy we will beat the difference by 10%. *Vitamins and minerals are supplementary to and not a replacement for a balanced diet. Always read the label, use only as directed. If symptoms persist, see your healthcare professional. Weight management products should be used with a balanced diet and exercise. **Pharmacist only products - your pharmacist will advise you whether this preparation is suitable for your condition.
</td></tr>
</table>
<!-- Unsubscribe -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#FF0031;" width="100%">
<tr><td align="center" style="padding:5px 18px 20px; font-family:Helvetica,Arial,sans-serif; font-size:11px; color:#ffffff; font-weight:100; text-align:center; line-height:1.1;">
No longer want to receive these emails? {% unsubscribe %}.<br/>
{{ organization.name }} {{ organization.full_address }}
</td></tr>
</table>"""

RESPONSIVE_CSS = """@media only screen and (max-width: 620px) {
  td[style*="padding:36px 32px"], td[style*="padding:36px 40px"], td[style*="padding:32px 40px"], td[style*="padding:28px 40px"], td[style*="padding:24px 40px"], td[style*="padding:20px 40px"] {
    padding-left: 20px !important;
    padding-right: 20px !important;
  }
  h1 { font-size: 22px !important; line-height: 1.3 !important; }
  td[style*="font-size:28px"] { font-size: 20px !important; }
  td[width="33%"] { display: block !important; width: 100% !important; border-left: none !important; border-right: none !important; padding: 12px 16px !important; border-bottom: 1px solid #eee; }
  .bc-nav a { font-size: 10px !important; }
  .bc-nav td { padding: 4px 5px !important; }
  td[width="50%"] { display: block !important; width: 100% !important; box-sizing: border-box !important; }
}"""


# ─────────────────────────────────────────────────────────────────
# Renderers
# ─────────────────────────────────────────────────────────────────
def render_product_grid(products):
    """Render a 3-column product list. Each product dict has:
       name, price, url (collection or product page).
    For 4-5 products, the grid wraps. Mobile collapses to single column."""
    if not products:
        return ""
    cells = []
    for p in products:
        cells.append(
            f"""<td style="padding:0 6px 14px 0; vertical-align:top; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:{BODY_TEXT}; line-height:1.5;" width="50%">
<p style="margin:0 0 4px;"><strong>{p['name']}</strong></p>
<p style="margin:0 0 8px; color:{BRAND_RED}; font-weight:bold;">NZ${p['price']}</p>
<a href="{p['url']}" style="color:{BRAND_RED}; text-decoration:underline; font-size:13px;" target="_blank">View →</a>
</td>"""
        )
    # Pair up cells into rows of 2
    rows = []
    for i in range(0, len(cells), 2):
        pair = cells[i : i + 2]
        if len(pair) == 1:
            pair.append('<td width="50%">&nbsp;</td>')
        rows.append("<tr>" + "".join(pair) + "</tr>")
    return f"""<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f9f9f9; border-top:1px solid #eeeeee; border-bottom:1px solid #eeeeee;" width="100%">
<tr><td style="padding:24px 40px;">
<p style="margin:0 0 16px; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:bold; color:{BRAND_RED}; text-transform:uppercase; letter-spacing:1px;">Top picks</p>
<table border="0" cellpadding="0" cellspacing="0" width="100%">{''.join(rows)}</table>
</td></tr>
</table>"""


def render_replenishment_template(*, hero_kicker, hero_headline, hero_subtitle,
                                  body_intro, body_continuation, products,
                                  cta_text, cta_url, disclaimer, title_tag):
    """Generate a complete BC-anatomy retail-first replenishment template.

    All copy parameters use BRAND_VOICE.md vocabulary: warm, factual,
    anti-fear ("top up", "stay consistent", "your routine"). No "running
    low", "selling fast", "don't miss out".

    Variables in copy use {{ first_name|default:'there' }} double-brace.
    """
    product_grid = render_product_grid(products)
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>{title_tag}</title>
<style>{RESPONSIVE_CSS}</style>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px; width:100%; margin:0 auto; background-color:#ffffff;">
{HEADER_HTML}
<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED};" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.75); text-transform:uppercase; letter-spacing:2px;">{hero_kicker}</p>
<h1 style="margin:0 0 10px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#ffffff; line-height:1.25;">{hero_headline}</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:rgba(255,255,255,0.85);">{hero_subtitle}</p>
</td></tr>
</table>
<!-- Body -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:32px 40px 24px; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:{BODY_TEXT}; line-height:1.7;">
<p style="margin:0 0 8px; font-size:18px; font-weight:bold; color:{DARK};">Hi {{{{ first_name|default:'there' }}}},</p>
<p style="margin:0 0 20px;">{body_intro}</p>
<p style="margin:0 0 28px;">{body_continuation}</p>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td align="center">
<table border="0" cellpadding="0" cellspacing="0">
<tr><td align="center" style="background-color:{BRAND_RED}; border-radius:4px;">
<a href="{cta_url}" style="display:inline-block; padding:14px 36px; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; color:#ffffff; text-decoration:none;" target="_blank">{cta_text} →</a>
</td></tr>
</table>
</td></tr>
</table>
</td></tr>
</table>
{product_grid}
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:20px 40px 32px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#888888; line-height:1.5; text-align:center;">{disclaimer}</td></tr>
</table>
{FOOTER_HTML}
</div>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────
# Slot configurations — 13 retail-first replacements + 3 keepers
# Each entry maps a Replenishment flow-action ID to a category template.
# Action IDs verified via --audit-action-statuses 2026-05-06.
# Product picks verified against 180-day Shopify analytics.
# ─────────────────────────────────────────────────────────────────
SHOP = HOMEPAGE


def _coll(slug):
    return f"{SHOP}/collections/{slug}"


def _prod(handle):
    return f"{SHOP}/products/{handle}"


# Default ASA disclaimer for non-medicine retail
RETAIL_DISCLAIMER = "Always read the label and use as directed. If symptoms persist, see your healthcare professional."
SUPPLEMENT_DISCLAIMER = "*Vitamins and minerals are supplementary to and not a replacement for a balanced diet. Always read the label, use only as directed. If symptoms persist, see your healthcare professional."
WEIGHT_DISCLAIMER = "Weight management products should be used with a balanced diet and exercise. Always read the label, use only as directed. If symptoms persist, see your healthcare professional."


SLOTS = [
    # Slot 2: Skincare daily — LRP + CeraVe + Wild Ferns + Sukin + Weleda
    {
        "slot": 2,
        "action_id": "105717126",
        "category": "skincare-daily",
        "subject": "Top up your skincare routine, {{ first_name|default:'there' }}",
        "preview_text": "Daily essentials your skin will thank you for.",
        "title_tag": "Top up your skincare routine",
        "hero_kicker": "Skincare reorder reminder",
        "hero_headline": "Top up your skincare, {{ first_name|default:'there' }}",
        "hero_subtitle": "Stay consistent — your skin's best friend is routine.",
        "body_intro": "Daily skincare delivers its best results when you stay consistent. Based on your last order, your essentials might be due for a top-up.",
        "body_continuation": "Reorder your favourites at NZ's best prices, with free delivery on orders over $79.",
        "products": [
            {"name": "La Roche-Posay Effaclar Duo+M 40ml", "price": "32.81", "url": _coll("skin-care")},
            {"name": "CeraVe Face Moisturising Lotion PM 52ml", "price": "26.99", "url": _coll("skin-care")},
            {"name": "Wild Ferns Bee Venom Moisturiser 100g", "price": "45.99", "url": _coll("skin-care")},
            {"name": "Weleda Skin Food 75ml", "price": "30.99", "url": _coll("skin-care")},
        ],
        "cta_text": "Shop Skincare",
        "cta_url": _coll("skin-care"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 3: Sun protection — LRP Anthelios + CeraVe SPF50 + Cetaphil Kids + Skinnies Kids + Natio
    {
        "slot": 3,
        "action_id": "105717129",
        "category": "sun-protection",
        "subject": "Top up your sun protection, {{ first_name|default:'there' }}",
        "preview_text": "NZ sun is brutal — daily SPF saves your skin.",
        "title_tag": "Top up your sun protection",
        "hero_kicker": "Sun care reorder reminder",
        "hero_headline": "Stay sun-safe, {{ first_name|default:'there' }}",
        "hero_subtitle": "Daily SPF is the single best thing you can do for your skin.",
        "body_intro": "Sunscreen only works when you keep using it — and NZ has some of the strongest UV in the world. Time to top up before the bottle runs out.",
        "body_continuation": "We stock dermatologist-loved SPF for adults and kids at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "La Roche-Posay Anthelios UVm400 SPF 50+ 50ml", "price": "35.34", "url": _coll("sunscreen")},
            {"name": "CeraVe Facial Lotion SPF50 52ml", "price": "26.64", "url": _coll("sunscreen")},
            {"name": "Cetaphil Sun Kids SPF50 150ml", "price": "32.72", "url": _coll("sunscreen")},
            {"name": "Skinnies Kids Sun Buster SPF50 100ml", "price": "36.49", "url": _coll("sunscreen")},
        ],
        "cta_text": "Shop Sun Protection",
        "cta_url": _coll("sunscreen"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 4: Body care — Palmer's + Vaseline
    {
        "slot": 4,
        "action_id": "105717132",
        "category": "body-care",
        "subject": "Top up your body care, {{ first_name|default:'there' }}",
        "preview_text": "Soft skin all year round — your body's daily ritual.",
        "title_tag": "Top up your body care",
        "hero_kicker": "Body care reorder reminder",
        "hero_headline": "Top up your body care, {{ first_name|default:'there' }}",
        "hero_subtitle": "Stay smooth and hydrated — daily care, daily results.",
        "body_intro": "Body lotion and oil are at their best when you use them daily. Based on your last order, you might be due for a top-up.",
        "body_continuation": "Reorder your favourites at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Palmer's Tahitian Vanilla Body Oil 192ml", "price": "20.29", "url": _coll("body-care")},
            {"name": "Palmer's Tahitian Vanilla Body Lotion 400ml", "price": "12.27", "url": _coll("body-care")},
            {"name": "Palmer's Foot Magic 60g", "price": "12.37", "url": _coll("body-care")},
            {"name": "Vaseline Petroleum Jelly 100g", "price": "7.55", "url": _coll("body-care")},
        ],
        "cta_text": "Shop Body Care",
        "cta_url": _coll("body-care"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 5: Hair care — BEING + Sukin + Hask + Shea Moisture + Neutrogena T/Gel
    {
        "slot": 5,
        "action_id": "105717135",
        "category": "hair-care",
        "subject": "Top up your hair care routine, {{ first_name|default:'there' }}",
        "preview_text": "Shampoo + conditioner, plus your styling staples.",
        "title_tag": "Top up your hair care routine",
        "hero_kicker": "Hair care reorder reminder",
        "hero_headline": "Top up your hair routine, {{ first_name|default:'there' }}",
        "hero_subtitle": "Healthy hair is built on consistent care.",
        "body_intro": "Daily shampoo, conditioner and styling products are due for a top-up. Stay on routine and reorder your favourites.",
        "body_continuation": "Curls, colour-care, scalp treatment, daily wash — we stock the full range at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "BEING Shampoo Curl Power 354ml", "price": "8.18", "url": _coll("hair-care")},
            {"name": "Sukin Natural Balance Shampoo 1L", "price": "27.87", "url": _coll("hair-care")},
            {"name": "Hask Curl Care Curl Defining Cream 198ml", "price": "14.60", "url": _coll("hair-care")},
            {"name": "Neutrogena T/Gel Salicylic Acid Shampoo 200ml", "price": "17.62", "url": _coll("hair-care")},
        ],
        "cta_text": "Shop Hair Care",
        "cta_url": _coll("hair-care"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 6: Daily multi & immune — Elevit, GO Healthy D+C+Zinc, Clinicians D3 (replaces paused Hayfexo)
    {
        "slot": 6,
        "action_id": "105717138",
        "category": "daily-multi-immune",
        "subject": "Top up your daily multi, {{ first_name|default:'there' }}",
        "preview_text": "Stay covered with your everyday immune essentials.",
        "title_tag": "Top up your daily multi",
        "hero_kicker": "Daily multi reorder reminder",
        "hero_headline": "Top up your daily essentials, {{ first_name|default:'there' }}",
        "hero_subtitle": "One a day. Routine pays off.",
        "body_intro": "Daily multivitamins and immune support work best when you stay consistent. Based on your last order, your supply might be due for a top-up.",
        "body_continuation": "Reorder your essentials at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Elevit Preconception & Pregnancy Multi 100 Tablets", "price": "79.62", "url": _coll("vitamins-supplements")},
            {"name": "GO Healthy Vitamin D + Vitamin C + Zinc Multi 60s", "price": "17.67", "url": _coll("vitamins-supplements")},
            {"name": "Clinicians Sunshine Vitamin D3 60 Tablets", "price": "17.04", "url": _coll("vitamins-supplements")},
            {"name": "Sanderson Co-Enzyme Q10 400mg 30s", "price": "34.87", "url": _coll("vitamins-supplements")},
        ],
        "cta_text": "Shop Daily Multi",
        "cta_url": _coll("vitamins-supplements"),
        "disclaimer": SUPPLEMENT_DISCLAIMER,
    },
    # Slot 7: Magnesium — GO Healthy + Nutra-life + Sanderson + Clinicians
    {
        "slot": 7,
        "action_id": "105717141",
        "category": "magnesium",
        "subject": "Top up your magnesium, {{ first_name|default:'there' }}",
        "preview_text": "Sleep, recovery, calm — magnesium does the heavy lifting.",
        "title_tag": "Top up your magnesium",
        "hero_kicker": "Magnesium reorder reminder",
        "hero_headline": "Top up your magnesium, {{ first_name|default:'there' }}",
        "hero_subtitle": "Stay consistent for the best results.",
        "body_intro": "Magnesium supports sleep, muscle recovery and everyday calm — and works best taken daily. Time to top up your supply.",
        "body_continuation": "We stock NZ's most popular magnesium formulas at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "GO Healthy Magnesium Sleep 120 VCaps", "price": "31.67", "url": _coll("magnesium")},
            {"name": "GO Healthy Magnesium Sleep 1-A-Day 200 Caps", "price": "58.09", "url": _coll("magnesium")},
            {"name": "Nutra-Life Magnesium Glycinate 60s", "price": "23.03", "url": _coll("magnesium")},
            {"name": "Sanderson High Absorption Magnesium FX 120 Tablets", "price": "26.31", "url": _coll("magnesium")},
        ],
        "cta_text": "Shop Magnesium",
        "cta_url": _coll("magnesium"),
        "disclaimer": SUPPLEMENT_DISCLAIMER,
    },
    # Slot 8: Probiotic / gut — Clinicians Flora Restore + GO Healthy Probiotic
    {
        "slot": 8,
        "action_id": "105717144",
        "category": "probiotic",
        "subject": "Top up your probiotic, {{ first_name|default:'there' }}",
        "preview_text": "Gut health is a daily commitment — keep going.",
        "title_tag": "Top up your probiotic",
        "hero_kicker": "Probiotic reorder reminder",
        "hero_headline": "Top up your probiotic, {{ first_name|default:'there' }}",
        "hero_subtitle": "Daily good bacteria. Big difference.",
        "body_intro": "Probiotics support gut health when you take them every day. Based on your last order, your supply might be due for a top-up.",
        "body_continuation": "Reorder your favourite probiotic at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Clinicians Flora Restore 30 Capsules", "price": "27.25", "url": _coll("probiotics")},
            {"name": "GO Healthy GO Probiotic 75 Billion 1-A-Day 60 Capsules", "price": "61.56", "url": _coll("probiotics")},
            {"name": "GO Healthy GO Probiotic 40 Billion 60 VCaps", "price": "49.99", "url": _coll("probiotics")},
        ],
        "cta_text": "Shop Probiotics",
        "cta_url": _coll("probiotics"),
        "disclaimer": SUPPLEMENT_DISCLAIMER,
    },
    # Slot 9: Omega 3 — Sanderson + GO Healthy + Clinicians Vegan
    {
        "slot": 9,
        "action_id": "105717147",
        "category": "omega-3",
        "subject": "Top up your Omega 3, {{ first_name|default:'there' }}",
        "preview_text": "Heart, brain, joints — daily fish oil supports it all.",
        "title_tag": "Top up your Omega 3",
        "hero_kicker": "Omega 3 reorder reminder",
        "hero_headline": "Top up your Omega 3, {{ first_name|default:'there' }}",
        "hero_subtitle": "Daily Omega 3 — your steady wellness anchor.",
        "body_intro": "Omega 3 fish oil supports heart, brain and joint health when you stay consistent. Time to top up your supply.",
        "body_continuation": "We stock concentrated and odourless options at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Sanderson Omega 3 Fish Oil 3000 150 Capsules", "price": "39.45", "url": _coll("fish-oils")},
            {"name": "Sanderson Odourless Fish Oil 2000 220 Caps", "price": "28.26", "url": _coll("fish-oils")},
            {"name": "GO Healthy Fish Oil 2000mg Odourless 230 Caps", "price": "31.55", "url": _coll("fish-oils")},
            {"name": "Clinicians Vegan Omega-3 Algae Oil 50 Capsules", "price": "45.71", "url": _coll("fish-oils")},
        ],
        "cta_text": "Shop Omega 3",
        "cta_url": _coll("fish-oils"),
        "disclaimer": SUPPLEMENT_DISCLAIMER,
    },
    # Slot 10: Hydration / electrolytes — Nothing Naughty
    {
        "slot": 10,
        "action_id": "105717150",
        "category": "hydration",
        "subject": "Top up your hydration, {{ first_name|default:'there' }}",
        "preview_text": "Electrolytes that actually taste good.",
        "title_tag": "Top up your hydration",
        "hero_kicker": "Hydration reorder reminder",
        "hero_headline": "Stay hydrated, {{ first_name|default:'there' }}",
        "hero_subtitle": "Electrolytes — daily summer essential.",
        "body_intro": "Electrolyte hydration powders work best when used regularly — pre-workout, post-workout, or on hot days. Time to top up your supply.",
        "body_continuation": "Choose your flavour at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Nothing Naughty Electrolyte Watermelon 515g", "price": "18.76", "url": _coll("hydration")},
            {"name": "Nothing Naughty Electrolyte Valencia Orange 515g", "price": "21.39", "url": _coll("hydration")},
            {"name": "Nothing Naughty Electrolyte Lemon & Lime 515g", "price": "21.53", "url": _coll("hydration")},
        ],
        "cta_text": "Shop Hydration",
        "cta_url": _coll("hydration"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 11: Sports / protein — Musashi + Nothing Naughty
    {
        "slot": 11,
        "action_id": "105717153",
        "category": "sports-protein",
        "subject": "Top up your training stack, {{ first_name|default:'there' }}",
        "preview_text": "Creatine, collagen, protein — your performance fuel.",
        "title_tag": "Top up your training stack",
        "hero_kicker": "Sports nutrition reorder",
        "hero_headline": "Top up your training stack, {{ first_name|default:'there' }}",
        "hero_subtitle": "Consistency builds results.",
        "body_intro": "Creatine and protein deliver their best results with daily use. Based on your last order, your stack might be ready for a top-up.",
        "body_continuation": "Reorder your performance staples at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Musashi Creatine Unflavoured 350g", "price": "32.48", "url": _coll("sports-nutrition")},
            {"name": "Nothing Naughty Pure Collagen Peptide Powder 500g", "price": "49.65", "url": _coll("sports-nutrition")},
            {"name": "Nothing Naughty Protein Bar 40g (Raspberry)", "price": "8.64", "url": _coll("sports-nutrition")},
        ],
        "cta_text": "Shop Sports Nutrition",
        "cta_url": _coll("sports-nutrition"),
        "disclaimer": SUPPLEMENT_DISCLAIMER,
    },
    # Slot 12: Cosmetics daily — FLASH + Maybelline + Natio
    {
        "slot": 12,
        "action_id": "105717156",
        "category": "cosmetics-daily",
        "subject": "Top up your cosmetic essentials, {{ first_name|default:'there' }}",
        "preview_text": "Mascara, lash, brow — your daily go-tos.",
        "title_tag": "Top up your cosmetic essentials",
        "hero_kicker": "Cosmetics reorder reminder",
        "hero_headline": "Top up your essentials, {{ first_name|default:'there' }}",
        "hero_subtitle": "Daily-wear cosmetics — replenish before they run out.",
        "body_intro": "Mascara, lash serums and daily-wear cosmetics have a finite shelf life. Time to refresh.",
        "body_continuation": "Discover our most-loved cosmetic essentials at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "FLASH Amplifying Eyelash Serum 2ml", "price": "56.10", "url": _coll("cosmetics")},
            {"name": "Maybelline Falsies Lash Lift Volumising Mascara", "price": "22.81", "url": _coll("cosmetics")},
            {"name": "Maybelline Great Lash Volumizing Mascara", "price": "12.54", "url": _coll("cosmetics")},
            {"name": "1000HOUR Lash & Brow Tint Kit Light Brown", "price": "21.28", "url": _coll("cosmetics")},
        ],
        "cta_text": "Shop Cosmetics",
        "cta_url": _coll("cosmetics"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 13: Baby & postpartum — Sudocrem + Bepanthen + Viva la Vulva + Lansinoh
    {
        "slot": 13,
        "action_id": "105717159",
        "category": "baby-postpartum",
        "subject": "Top up your baby & postpartum essentials",
        "preview_text": "Nappy creams, wipes, postpartum care.",
        "title_tag": "Top up your baby & postpartum essentials",
        "hero_kicker": "Baby & postpartum reorder",
        "hero_headline": "Top up your essentials, {{ first_name|default:'there' }}",
        "hero_subtitle": "The basics that get you through the day.",
        "body_intro": "Nappy creams, wipes and postpartum care are everyday essentials. Based on your last order, you might be due for a top-up.",
        "body_continuation": "We stock NZ's favourite baby and postpartum brands at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Sudocrem Antiseptic Healing Cream 125g", "price": "14.16", "url": _coll("baby")},
            {"name": "Bepanthen Nappy Rash Ointment 30g", "price": "9.54", "url": _coll("baby")},
            {"name": "Viva la Vulva Healing Perineal Spray 100ml", "price": "35.49", "url": _coll("baby")},
            {"name": "Lansinoh HPA Lanolin Nipple Cream 15g", "price": "14.19", "url": _coll("baby")},
        ],
        "cta_text": "Shop Baby & Postpartum",
        "cta_url": _coll("baby"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 14: Oral care daily (broadened from Oracoat-only) — Oracoat + Biotene + Miradent + Oral-B
    {
        "slot": 14,
        "action_id": "105717162",
        "category": "oral-care",
        "subject": "Top up your oral care routine, {{ first_name|default:'there' }}",
        "preview_text": "Daily mouth care — Xylimelts, Biotene, gum, floss.",
        "title_tag": "Top up your oral care routine",
        "hero_kicker": "Oral care reorder reminder",
        "hero_headline": "Top up your oral care, {{ first_name|default:'there' }}",
        "hero_subtitle": "Daily comfort and dental health, made easy.",
        "body_intro": "Oral comfort lozenges, mouthwash, xylitol gum and floss work best as part of a daily routine. Time to top up your essentials.",
        "body_continuation": "Reorder your favourites at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Oracoat Xylimelts Mild Mint 40 Pack", "price": "41.92", "url": _coll("oral-care")},
            {"name": "Oracoat Xylimelts Mint Free 40 Pack", "price": "44.21", "url": _coll("oral-care")},
            {"name": "Biotene Mouthwash 470ml", "price": "34.11", "url": _coll("oral-care")},
            {"name": "Miradent Xylitol Spearmint Chewing Gum 30s", "price": "12.86", "url": _coll("oral-care")},
        ],
        "cta_text": "Shop Oral Care",
        "cta_url": _coll("oral-care"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
    # Slot 15: Meal replacement (Optifast — keep, broadened from one flavour to full range)
    {
        "slot": 15,
        "action_id": "105717165",
        "category": "meal-replacement",
        "subject": "Top up your meal plan, {{ first_name|default:'there' }}",
        "preview_text": "Stay on programme — full Optifast range.",
        "title_tag": "Top up your meal plan",
        "hero_kicker": "Meal plan reorder reminder",
        "hero_headline": "Top up your meal plan, {{ first_name|default:'there' }}",
        "hero_subtitle": "Stay consistent — your programme works best uninterrupted.",
        "body_intro": "Your Optifast supply might be ready for a top-up. To get the best results from your weight management programme, it helps to stay on routine.",
        "body_continuation": "We stock the full Optifast range at NZ's best prices — with free delivery on orders over $79.",
        "products": [
            {"name": "OPTIFAST VLCD Shake Vanilla 18×53g", "price": "83.02", "url": _coll("vlcd-meal-replacement")},
            {"name": "OPTIFAST VLCD Shake Chocolate 12×53g", "price": "58.11", "url": _coll("vlcd-meal-replacement")},
            {"name": "OPTIFAST VLCD Shake Banana 12×53g", "price": "50.75", "url": _coll("vlcd-meal-replacement")},
            {"name": "OPTIFAST VLCD Shake Strawberry 12×53g", "price": "46.08", "url": _coll("vlcd-meal-replacement")},
        ],
        "cta_text": "Shop Optifast",
        "cta_url": _coll("vlcd-meal-replacement"),
        "disclaimer": WEIGHT_DISCLAIMER,
    },
    # Slot 16: First aid & wound care (replaces Optifast clone) — Band-Aid + Savlon + USL Swabs + Multisorb
    {
        "slot": 16,
        "action_id": "105717169",
        "category": "first-aid",
        "subject": "Top up your first aid kit, {{ first_name|default:'there' }}",
        "preview_text": "Plasters, antiseptic, swabs — kit ready when you need it.",
        "title_tag": "Top up your first aid kit",
        "hero_kicker": "First aid reorder reminder",
        "hero_headline": "Top up your first aid kit, {{ first_name|default:'there' }}",
        "hero_subtitle": "Be ready for the everyday scrapes.",
        "body_intro": "First aid essentials — plasters, antiseptic, swabs — are best stocked before you need them. Based on your last order, you might be due for a top-up.",
        "body_continuation": "Reorder your home first aid kit at NZ's best prices, with free delivery over $79.",
        "products": [
            {"name": "Band-Aid Tough Strips Regular Plasters 40", "price": "7.97", "url": _coll("first-aid")},
            {"name": "Savlon Antiseptic Cream 30g", "price": "12.87", "url": _coll("first-aid")},
            {"name": "USL Medical Alcohol Swabs 70% 200 Pack", "price": "14.60", "url": _coll("first-aid")},
            {"name": "Multisorb Non Woven Swabs 7.5×7.5cm 100 Swabs", "price": "13.58", "url": _coll("first-aid")},
        ],
        "cta_text": "Shop First Aid",
        "cta_url": _coll("first-aid"),
        "disclaimer": RETAIL_DISCLAIMER,
    },
]


def get_slot_by_action_id(action_id):
    for slot in SLOTS:
        if slot["action_id"] == action_id:
            return slot
    return None


if __name__ == "__main__":
    # Smoke test: render slot 2 to stdout
    import sys
    slot = SLOTS[0]
    html = render_replenishment_template(
        hero_kicker=slot["hero_kicker"],
        hero_headline=slot["hero_headline"],
        hero_subtitle=slot["hero_subtitle"],
        body_intro=slot["body_intro"],
        body_continuation=slot["body_continuation"],
        products=slot["products"],
        cta_text=slot["cta_text"],
        cta_url=slot["cta_url"],
        disclaimer=slot["disclaimer"],
        title_tag=slot["title_tag"],
    )
    sys.stdout.write(html)
