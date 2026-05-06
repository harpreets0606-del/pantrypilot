"""
Browse Abandonment + Search Abandonment templates for Bargain Chemist.

Designed for activation in Klaviyo with multi-step structure
(E1 + E2) to maximise recovery. Subjects, hero, body, CTAs all
follow BRAND_VOICE.md (warm, factual, no fear, $79 free shipping,
{{ first_name|default:'there' }} variables).

Reuses the BC anatomy from replenishment_templates.py (HEADER_HTML,
FOOTER_HTML, RESPONSIVE_CSS) so we don't duplicate the chrome.
"""

from replenishment_templates import (
    BRAND_RED,
    BODY_TEXT,
    DARK,
    HEADER_HTML,
    FOOTER_HTML,
    RESPONSIVE_CSS,
    HOMEPAGE,
)


# ─────────────────────────────────────────────────────────────────
# Browse Abandonment — uses {{ event.* }} for product personalisation
#   event.URL          → product page link
#   event.ProductName  → product name
#   event.ImageURL     → product image (Shopify CDN)
#   event.Price        → product price
#   event.Categories   → category tags (for category-fallback grid)
# ─────────────────────────────────────────────────────────────────

BROWSE_E1_SUBJECT = "Still thinking it over, {{ first_name|default:'there' }}?"
BROWSE_E1_PREVIEW = "Pick up where you left off — your wellness pick is still here."

BROWSE_E2_SUBJECT = "Take another look, {{ first_name|default:'there' }}"
BROWSE_E2_PREVIEW = "Saved for you, plus a few related picks."

SEARCH_E1_SUBJECT = "Still looking for {{ event.searchQuery|default:'something' }}?"
SEARCH_E1_PREVIEW = "Pick up where you left off."

SEARCH_E2_SUBJECT = "More like '{{ event.searchQuery|default:'that' }}'"
SEARCH_E2_PREVIEW = "Top picks across our range."


def render_browse_e1():
    """Browse Abandonment E1 — single product hero (uses event vars)."""
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Still thinking it over?</title>
<style>{RESPONSIVE_CSS}</style>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px; width:100%; margin:0 auto; background-color:#ffffff;">
{HEADER_HTML}
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED};" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.75); text-transform:uppercase; letter-spacing:2px;">Saved for you</p>
<h1 style="margin:0 0 10px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#ffffff; line-height:1.25;">Still thinking it over, {{{{ first_name|default:'there' }}}}?</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:rgba(255,255,255,0.85);">Pick up where you left off — no pressure.</p>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f9f9f9;" width="100%">
<tr><td align="center" style="padding:24px 30px;">
<a href="{{{{ event.URL }}}}" target="_blank" style="display:block; text-decoration:none;">
<img alt="{{{{ event.ProductName }}}}" src="{{{{ event.ImageURL }}}}" width="400" style="width:100%; max-width:400px; height:auto; display:block; margin:0 auto 16px; border:0; border-radius:6px;" border="0"/>
</a>
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:18px; font-weight:bold; color:{DARK};">{{{{ event.ProductName }}}}</p>
<p style="margin:0 0 16px; font-family:Helvetica,Arial,sans-serif; font-size:24px; font-weight:bold; color:{BRAND_RED};">NZ${{{{ event.Price }}}}</p>
<a href="{{{{ event.URL }}}}" target="_blank" style="display:inline-block; background-color:{BRAND_RED}; color:#ffffff; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; text-decoration:none; padding:14px 36px; border-radius:4px;">View Product</a>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:24px 40px; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:{BODY_TEXT}; line-height:1.7; text-align:center;">
<p style="margin:0 0 8px; font-weight:bold; color:{BRAND_RED};">We'll beat any pharmacy price</p>
<p style="margin:0;">Find it cheaper at another NZ pharmacy? We'll beat the difference by 10%.</p>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:0 40px 32px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#888888; line-height:1.5; text-align:center;">Always read the label and use as directed. If symptoms persist, see your healthcare professional.</td></tr>
</table>
{FOOTER_HTML}
</div>
</body></html>"""


def render_browse_e2():
    """Browse Abandonment E2 — same product + 'Customers also viewed'."""
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Take another look</title>
<style>{RESPONSIVE_CSS}</style>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px; width:100%; margin:0 auto; background-color:#ffffff;">
{HEADER_HTML}
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED};" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.75); text-transform:uppercase; letter-spacing:2px;">Saved for you</p>
<h1 style="margin:0 0 10px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#ffffff; line-height:1.25;">Take another look, {{{{ first_name|default:'there' }}}}</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:rgba(255,255,255,0.85);">Your pick is still here, plus a few related staples.</p>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f9f9f9;" width="100%">
<tr><td align="center" style="padding:24px 30px;">
<a href="{{{{ event.URL }}}}" target="_blank" style="display:block; text-decoration:none;">
<img alt="{{{{ event.ProductName }}}}" src="{{{{ event.ImageURL }}}}" width="400" style="width:100%; max-width:400px; height:auto; display:block; margin:0 auto 16px; border:0; border-radius:6px;" border="0"/>
</a>
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:18px; font-weight:bold; color:{DARK};">{{{{ event.ProductName }}}}</p>
<p style="margin:0 0 16px; font-family:Helvetica,Arial,sans-serif; font-size:24px; font-weight:bold; color:{BRAND_RED};">NZ${{{{ event.Price }}}}</p>
<a href="{{{{ event.URL }}}}" target="_blank" style="display:inline-block; background-color:{BRAND_RED}; color:#ffffff; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; text-decoration:none; padding:14px 36px; border-radius:4px;">View Product</a>
</td></tr>
</table>
<!-- Klaviyo dynamic block placeholder: customers also viewed -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:24px 40px;">
<p style="margin:0 0 16px; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:bold; color:{BRAND_RED}; text-transform:uppercase; letter-spacing:1px; text-align:center;">Kiwis also love</p>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:{BODY_TEXT}; line-height:1.6; text-align:center;">In Klaviyo's flow editor, drop a Product Block here filtered by event.Categories — shows 3 related products dynamically.</p>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td align="center" style="padding:24px 40px;">
<a href="{HOMEPAGE}/collections/all" target="_blank" style="display:inline-block; background-color:{BRAND_RED}; color:#ffffff; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; text-decoration:none; padding:14px 36px; border-radius:4px;">Browse Full Range</a>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:0 40px 32px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#888888; line-height:1.5; text-align:center;">Always read the label and use as directed. If symptoms persist, see your healthcare professional.</td></tr>
</table>
{FOOTER_HTML}
</div>
</body></html>"""


def render_search_e1():
    """Search Abandonment E1 — echo their search query, return-to-search CTA."""
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>Still looking?</title>
<style>{RESPONSIVE_CSS}</style>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px; width:100%; margin:0 auto; background-color:#ffffff;">
{HEADER_HTML}
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED};" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.75); text-transform:uppercase; letter-spacing:2px;">Picking up your search</p>
<h1 style="margin:0 0 10px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#ffffff; line-height:1.25;">Still looking for {{{{ event.searchQuery|default:'something specific' }}}}, {{{{ first_name|default:'there' }}}}?</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:rgba(255,255,255,0.85);">Jump back into your search, or browse a few popular categories.</p>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td align="center" style="padding:32px 40px 24px;">
<a href="{HOMEPAGE}/search?q={{{{ event.searchQuery|default:'' }}}}" target="_blank" style="display:inline-block; background-color:{BRAND_RED}; color:#ffffff; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; text-decoration:none; padding:14px 36px; border-radius:4px;">Return to Search</a>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f9f9f9;" width="100%">
<tr><td style="padding:24px 40px;">
<p style="margin:0 0 16px; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:bold; color:{BRAND_RED}; text-transform:uppercase; letter-spacing:1px; text-align:center;">Or browse a popular category</p>
<table border="0" cellpadding="0" cellspacing="0" width="100%"><tr>
<td width="50%" style="padding:8px; vertical-align:top; text-align:center;">
<a href="{HOMEPAGE}/collections/vitamins-supplements" style="display:block; padding:12px; background:#fff; border-radius:6px; color:{BRAND_RED}; text-decoration:none; font-weight:bold; font-size:13px;">Vitamins & Supplements</a>
</td>
<td width="50%" style="padding:8px; vertical-align:top; text-align:center;">
<a href="{HOMEPAGE}/collections/skin-care" style="display:block; padding:12px; background:#fff; border-radius:6px; color:{BRAND_RED}; text-decoration:none; font-weight:bold; font-size:13px;">Skin Care</a>
</td>
</tr><tr>
<td width="50%" style="padding:8px; vertical-align:top; text-align:center;">
<a href="{HOMEPAGE}/collections/baby" style="display:block; padding:12px; background:#fff; border-radius:6px; color:{BRAND_RED}; text-decoration:none; font-weight:bold; font-size:13px;">Baby & Postpartum</a>
</td>
<td width="50%" style="padding:8px; vertical-align:top; text-align:center;">
<a href="{HOMEPAGE}/collections/cold-flu" style="display:block; padding:12px; background:#fff; border-radius:6px; color:{BRAND_RED}; text-decoration:none; font-weight:bold; font-size:13px;">Cold & Flu</a>
</td>
</tr></table>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:20px 40px 32px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#888888; line-height:1.5; text-align:center;">Always read the label and use as directed. If symptoms persist, see your healthcare professional.</td></tr>
</table>
{FOOTER_HTML}
</div>
</body></html>"""


def render_search_e2():
    """Search Abandonment E2 — broader 'top picks' nudge."""
    return f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>More like that</title>
<style>{RESPONSIVE_CSS}</style>
</head>
<body style="margin:0; padding:0; background-color:#f5f5f5; font-family:Helvetica,Arial,sans-serif;">
<div style="max-width:600px; width:100%; margin:0 auto; background-color:#ffffff;">
{HEADER_HTML}
<table border="0" cellpadding="0" cellspacing="0" style="background-color:{BRAND_RED};" width="100%">
<tr><td align="center" style="padding:36px 32px 28px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.75); text-transform:uppercase; letter-spacing:2px;">Top picks for you</p>
<h1 style="margin:0 0 10px; font-family:Helvetica,Arial,sans-serif; font-size:28px; font-weight:bold; color:#ffffff; line-height:1.25;">More like '{{{{ event.searchQuery|default:'that' }}}}'</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:rgba(255,255,255,0.85);">Quality picks across our range, with NZ's best prices and free delivery over $79.</p>
</td></tr>
</table>
<!-- Klaviyo dynamic block placeholder: top sellers -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:24px 40px;">
<p style="margin:0 0 16px; font-family:Helvetica,Arial,sans-serif; font-size:14px; font-weight:bold; color:{BRAND_RED}; text-transform:uppercase; letter-spacing:1px; text-align:center;">What Kiwis are loving</p>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:{BODY_TEXT}; line-height:1.6; text-align:center;">In Klaviyo, drop a Product Block here filtered by event.searchQuery (or top sellers as fallback) — 3-5 products, dynamic.</p>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td align="center" style="padding:24px 40px;">
<a href="{HOMEPAGE}/collections/all" target="_blank" style="display:inline-block; background-color:{BRAND_RED}; color:#ffffff; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; text-decoration:none; padding:14px 36px; border-radius:4px;">Browse Full Range</a>
</td></tr>
</table>
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr><td style="padding:0 40px 32px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#888888; line-height:1.5; text-align:center;">Always read the label and use as directed. If symptoms persist, see your healthcare professional.</td></tr>
</table>
{FOOTER_HTML}
</div>
</body></html>"""


TEMPLATES = {
    "browse-e1": {
        "subject": BROWSE_E1_SUBJECT,
        "preview": BROWSE_E1_PREVIEW,
        "render": render_browse_e1,
        "name": "[BC-Abandonment] Browse E1",
    },
    "browse-e2": {
        "subject": BROWSE_E2_SUBJECT,
        "preview": BROWSE_E2_PREVIEW,
        "render": render_browse_e2,
        "name": "[BC-Abandonment] Browse E2",
    },
    "search-e1": {
        "subject": SEARCH_E1_SUBJECT,
        "preview": SEARCH_E1_PREVIEW,
        "render": render_search_e1,
        "name": "[BC-Abandonment] Search E1",
    },
    "search-e2": {
        "subject": SEARCH_E2_SUBJECT,
        "preview": SEARCH_E2_PREVIEW,
        "render": render_search_e2,
        "name": "[BC-Abandonment] Search E2",
    },
}


def deploy_templates(keys=None):
    """POST abandonment templates to Klaviyo. Returns dict of key → template_id."""
    import os
    import requests

    api_key = os.environ.get("KLAVIYO_API_KEY")
    if not api_key:
        raise SystemExit("KLAVIYO_API_KEY not set")

    headers = {
        "Authorization": f"Klaviyo-API-Key {api_key}",
        "revision": "2025-01-15",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    targets = {k: TEMPLATES[k] for k in (keys or TEMPLATES.keys())}
    results = {}

    for key, t in targets.items():
        payload = {
            "data": {
                "type": "template",
                "attributes": {
                    "name": t["name"],
                    "html": t["render"](),
                    "editor_type": "CODE",
                },
            }
        }
        r = requests.post("https://a.klaviyo.com/api/templates", json=payload, headers=headers)
        if r.status_code in (200, 201):
            tid = r.json()["data"]["id"]
            print(f"  ✅ {t['name']} → {tid}")
            results[key] = tid
        elif r.status_code == 409:
            # Already exists — fetch existing ID
            print(f"  ⚠️  {t['name']} already exists (409) — skipping. Delete old copy if you want to redeploy.")
        else:
            print(f"  ❌ {t['name']} failed: {r.status_code} {r.text[:200]}")

    return results


if __name__ == "__main__":
    import argparse
    import os
    import sys

    parser = argparse.ArgumentParser(description="Browse + Search Abandonment template previews")
    parser.add_argument("--key", choices=list(TEMPLATES.keys()), help="Single template")
    parser.add_argument("--all", action="store_true",
                        help="Write all 4 to ./previews/abandonment/")
    parser.add_argument("--deploy", action="store_true",
                        help="POST all 4 templates to Klaviyo")
    parser.add_argument("--out", help="Output file for --key")
    args = parser.parse_args()

    if args.deploy:
        print("Deploying abandonment templates to Klaviyo...")
        deploy_templates()
        sys.exit(0)

    if args.all:
        os.makedirs("previews/abandonment", exist_ok=True)
        for k, t in TEMPLATES.items():
            path = f"previews/abandonment/{k}.html"
            with open(path, "w", encoding="utf-8") as f:
                f.write(t["render"]())
            print(f"  wrote {path}")
        sys.exit(0)

    key = args.key or "browse-e1"
    t = TEMPLATES[key]
    html = t["render"]()
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"✅ Wrote {key} to {args.out}")
    else:
        sys.stdout.write(html)
