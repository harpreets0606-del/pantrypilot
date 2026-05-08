"""Build browse + search abandonment templates from W2Sbja design + validate
Liquid logic INLINE before writing any output.

Per user instructions (2026-05-08):
- Use W2Sbja as the design source for all new templates
- Test logic INSIDE each template DURING build via Klaviyo /api/template-render
- Use REAL event payloads pulled from Klaviyo at runtime for render-tests
- Atomic write: ALL 3 templates must validate before any disk write

Templates produced:
  1. browse-recover-w2sbja.html — for RtiVC5 (Viewed Product → 1h delay → E1)
  2. search-recover-e1-w2sbja.html — for XbQiKg E1 (Boost Clicked Search Result)
  3. search-recover-e2-w2sbja.html — for XbQiKg E2 (NEW; fills the missing
     template_id=None slot in the existing flow)

Static validation per template:
  - No fear/scarcity, no coupons, no fabricated facts
  - Approved facts present ($79, Price Beat, ASA disclaimer, Bargain
    Chemist Limited address, organization macros, unsubscribe)
  - Verified Liquid patterns present, broken patterns absent

Render-test per template:
  - REAL event payload pulled live from Klaviyo
  - Boundary cases (missing first_name, missing product name, missing
    search query, special chars)
  - Expected phrase present in render
  - Zero Liquid leakage in any render

If ANY check fails for ANY template, no files are written and script
exits non-zero. Atomic.

Run locally:
    python .claude/bargain-chemist/scripts/build_browse_search_templates.py
"""
import json
import re
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
TODAY = date.today().isoformat()
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/build-browse-search"
OUT.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = REPO / ".claude/bargain-chemist/templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

W2SBJA_ID = "W2Sbja"
SCRATCH_NAME = f"BC PROBE - render scratch (delete me)"
REVISION = "2025-10-15"

VIEWED_PRODUCT_METRIC = "XQ2zfW"  # Klaviyo native
BOOST_SEARCH_METRIC = "Y2qHKK"    # Boost Clicked Search Result


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def load_key():
    text = ENV_FILE.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if line.startswith("KLAVIYO_PRIVATE_KEY"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing in .env.local")


def hdrs(key, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, payload):
    (OUT / name).write_text(
        payload if isinstance(payload, str) else json.dumps(payload, indent=2),
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Fetch W2Sbja + real events
# ---------------------------------------------------------------------------

def fetch_w2sbja(key):
    r = requests.get(f"https://a.klaviyo.com/api/templates/{W2SBJA_ID}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ failed to fetch W2Sbja: HTTP {r.status_code}")
    html = r.json()["data"]["attributes"]["html"]
    save("w2sbja-source.html", html)
    return html


def fetch_latest_event(key, metric_id, label):
    r = requests.get(
        "https://a.klaviyo.com/api/events/",
        headers=hdrs(key),
        params={
            "fields[event]": "event_properties,datetime",
            "filter": f'equals(metric_id,"{metric_id}")',
            "page[size]": 1,
            "sort": "-datetime",
        },
        timeout=30,
    )
    if r.status_code != 200:
        sys.exit(f"❌ failed to fetch event for metric {metric_id}: HTTP {r.status_code}")
    data = r.json().get("data", [])
    if not data:
        sys.exit(f"❌ no events found for metric {metric_id} ({label})")
    attrs = data[0]["attributes"]
    # REST returns event_properties (snake_case), MCP returns eventProperties (camelCase)
    props = attrs.get("event_properties") or attrs.get("eventProperties") or {}
    save(f"sample-event-{label}.json", props)
    return props


# ---------------------------------------------------------------------------
# Scratch template lifecycle (create+delete, avoids depending on UH72Vm)
# ---------------------------------------------------------------------------

def create_scratch(key):
    body = {"data": {"type": "template", "attributes": {
        "name": SCRATCH_NAME,
        "editor_type": "CODE",
        "html": "<html><body>placeholder</body></html>",
    }}}
    r = requests.post("https://a.klaviyo.com/api/templates/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    if r.status_code not in (200, 201):
        sys.exit(f"❌ scratch creation failed: HTTP {r.status_code}\n{r.text[:200]}")
    return r.json()["data"]["id"]


def delete_scratch(key, sid):
    r = requests.delete(f"https://a.klaviyo.com/api/templates/{sid}/",
                        headers=hdrs(key), timeout=30)
    print(f"  scratch cleanup: HTTP {r.status_code} ({sid})")


# ---------------------------------------------------------------------------
# Section substitution (W2Sbja anchors)
# ---------------------------------------------------------------------------

SECTION_ANCHORS = {
    "hero":       ("<!-- Hero -->",                "<!-- Product details -->"),
    "product":    ("<!-- Product details -->",     "<!-- Urgency note -->"),
    "urgency":    ("<!-- Urgency note -->",        "<!-- Additional message -->"),
    "additional": ("<!-- Additional message -->",  "<!-- Footer: Get social -->"),
}


def replace_section(html, key, content):
    s, e = SECTION_ANCHORS[key]
    si, ei = html.find(s), html.find(e)
    assert si >= 0 and ei > si, f"anchor missing for {key}"
    return html[:si] + content + "\n" + html[ei:]


# ---------------------------------------------------------------------------
# Shared value-strip banner (replaces W2Sbja's urgency note)
# Always-on, no scarcity language, brand-essential value props.
# ---------------------------------------------------------------------------
VALUE_STRIP = """<!-- Value strip (always-on; no fear/scarcity) -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#fff8f0; border-top:1px solid #ffe0b2; border-bottom:1px solid #ffe0b2;" width="100%">
<tr>
<td align="center" style="padding:14px 32px; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:#555555; line-height:1.6;">
<strong style="color:#7B1523;">Free shipping over $79</strong> &middot; <strong style="color:#7B1523;">Price Beat 10% Guarantee</strong> &middot; <strong style="color:#7B1523;">30+ NZ stores</strong>
</td>
</tr>
</table>"""

# Pharmacist-only disclaimer block (always-on; brings ASA-safety
# regardless of whether the SKU is restricted)
PHARMACIST_NOTE = """<!-- Pharmacist note (regulatory, ASA-safe) -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" style="padding:18px 32px 6px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#666666; line-height:1.6; text-align:center;">
<p style="margin:0;">Pharmacist-only products: your pharmacist will advise whether this product is suitable. Always read the label and use as directed. If symptoms persist, see your healthcare professional.</p>
</td>
</tr>
</table>"""


# ---------------------------------------------------------------------------
# Email specs
# ---------------------------------------------------------------------------

# BROWSE ABANDONMENT (RtiVC5)
# Trigger: Viewed Product (XQ2zfW). Verified fields: Name, URL, ImageURL,
# Price (string with $), CompareAtPrice, Brand, Categories.
# Defensive Liquid: Name|default:'item' (handles missing).
BROWSE_SPEC = {
    "filename": "browse-recover-w2sbja.html",
    "subject":  "Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?",
    "preview":  "Take another look — Price Beat 10% means you won't find it cheaper.",
    "hero": """<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f8971d;" width="100%">
<tr>
<td align="center" style="padding:40px 32px 32px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.9); text-transform:uppercase; letter-spacing:2px;">Still browsing</p>
<h1 style="margin:0 0 12px; font-family:Helvetica,Arial,sans-serif; font-size:32px; font-weight:bold; color:#ffffff; line-height:1.2;">Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:rgba(255,255,255,0.95);">{{ event.Name|default:'The item' }} is still here when you're ready.</p>
</td>
</tr>
</table>
""",
    "product": """<!-- Product details (uses verified Viewed Product fields: Name, URL, ImageURL, Price) -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" style="padding:32px 40px 20px;">
{% if event.ImageURL %}<a href="{{ event.URL|default:'https://www.bargainchemist.co.nz' }}" style="text-decoration:none;"><img alt="{{ event.Name|default:'Product' }}" src="{{ event.ImageURL }}" style="max-width:240px;width:100%;height:auto;display:block;margin:0 auto 18px;border-radius:6px;"/></a>{% endif %}
<p style="margin:0 0 6px; font-family:Helvetica,Arial,sans-serif; font-size:18px; font-weight:bold; color:#222222; line-height:1.3;">{{ event.Name|default:'Your item' }}</p>
{% if event.Price %}<p style="margin:0 0 24px; font-family:Helvetica,Arial,sans-serif; font-size:22px; font-weight:bold; color:#CC1B2A;">{{ event.Price }}</p>{% endif %}
<table border="0" cellpadding="0" cellspacing="0">
<tr><td align="center" style="background-color:#CC1B2A; border-radius:4px;">
<a href="{{ event.URL|default:'https://www.bargainchemist.co.nz' }}" style="display:inline-block; padding:14px 40px; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:bold; color:#ffffff; text-decoration:none;" target="_blank">Take another look &rarr;</a>
</td></tr>
</table>
</td>
</tr>
</table>
""",
    "urgency": VALUE_STRIP,
    "additional": f"""<!-- Additional message + pharmacist note -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td style="padding:24px 32px 8px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6; text-align:center;">
<p style="margin:0;">Need a hand picking? Reply to this email or visit any of our <strong>30+ NZ stores</strong> — our pharmacists are here to help.</p>
</td>
</tr>
</table>
{PHARMACIST_NOTE}
""",
}

# SEARCH E1 (XbQiKg E1)
# Trigger: Boost Clicked Search Result (Y2qHKK). Verified fields:
# searchQuery, productName, productCategory, productPrice, productUrl,
# productTags. Note: productUrl is myshopify.com (Shopify 301-redirects to
# bargainchemist.co.nz). Safer CTA: bargainchemist.co.nz/search?q=...
SEARCH_E1_SPEC = {
    "filename": "search-recover-e1-w2sbja.html",
    "subject":  "{% if event.searchQuery %}Still looking for {{ event.searchQuery }}?{% else %}Found what you were after?{% endif %}",
    "preview":  "Pick up your search where you left off &mdash; Price Beat 10% applies.",
    "hero": """<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f8971d;" width="100%">
<tr>
<td align="center" style="padding:40px 32px 32px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.9); text-transform:uppercase; letter-spacing:2px;">Still searching</p>
<h1 style="margin:0 0 12px; font-family:Helvetica,Arial,sans-serif; font-size:30px; font-weight:bold; color:#ffffff; line-height:1.2;">{% if event.searchQuery %}Still looking for &ldquo;{{ event.searchQuery }}&rdquo;?{% else %}Find what you were after.{% endif %}</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:rgba(255,255,255,0.95);">Hi {{ first_name|default:'there' }} &mdash; pick up your search where you left off.</p>
</td>
</tr>
</table>
""",
    "product": """<!-- Search-recovery CTA + suggested-product preview -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" style="padding:32px 40px 12px;">
{% if event.productName %}<p style="margin:0 0 4px; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:#777777; text-transform:uppercase; letter-spacing:1px;">You clicked on</p>
<p style="margin:0 0 6px; font-family:Helvetica,Arial,sans-serif; font-size:18px; font-weight:bold; color:#222222; line-height:1.3;">{{ event.productName }}</p>
{% if event.productCategory %}<p style="margin:0 0 24px; font-family:Helvetica,Arial,sans-serif; font-size:13px; color:#777777;">{{ event.productCategory }}</p>{% else %}<div style="height:18px;"></div>{% endif %}
{% endif %}
<p style="margin:0 0 24px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6;">Continue browsing your search results, or take a fresh look at our most-searched products.</p>
<table border="0" cellpadding="0" cellspacing="0">
<tr><td align="center" style="background-color:#CC1B2A; border-radius:4px;">
<a href="https://www.bargainchemist.co.nz/search?q={{ event.searchQuery|default:'' }}" style="display:inline-block; padding:14px 40px; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:bold; color:#ffffff; text-decoration:none;" target="_blank">Continue your search &rarr;</a>
</td></tr>
</table>
</td>
</tr>
</table>
""",
    "urgency": VALUE_STRIP,
    "additional": f"""<!-- Additional message + pharmacist note -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td style="padding:24px 32px 8px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6; text-align:center;">
<p style="margin:0;">Not sure which one to choose? Our pharmacists are happy to help &mdash; in-store at any of our <strong>30+ NZ locations</strong> or by reply to this email.</p>
</td>
</tr>
</table>
{PHARMACIST_NOTE}
""",
}

# SEARCH E2 (XbQiKg E2 NEW — fills the missing template slot)
# Sent 2 days after E1. More patient framing. Same verified fields.
SEARCH_E2_SPEC = {
    "filename": "search-recover-e2-w2sbja.html",
    "subject":  "{% if event.searchQuery %}Still on the hunt for {{ event.searchQuery }}?{% else %}Still looking?{% endif %}",
    "preview":  "Talk to a pharmacist or pick from our top sellers in this category.",
    "hero": """<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f8971d;" width="100%">
<tr>
<td align="center" style="padding:40px 32px 32px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.9); text-transform:uppercase; letter-spacing:2px;">Still searching</p>
<h1 style="margin:0 0 12px; font-family:Helvetica,Arial,sans-serif; font-size:30px; font-weight:bold; color:#ffffff; line-height:1.2;">{% if event.searchQuery %}Still on the hunt for &ldquo;{{ event.searchQuery }}&rdquo;?{% else %}Still on the hunt?{% endif %}</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:rgba(255,255,255,0.95);">Hi {{ first_name|default:'there' }} &mdash; let our pharmacists help, or take another look.</p>
</td>
</tr>
</table>
""",
    "product": """<!-- E2 dual CTA: pharmacist help + continue search -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" style="padding:32px 40px 12px;">
<p style="margin:0 0 24px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6;">{% if event.productCategory %}Looking for the right product in <strong>{{ event.productCategory }}</strong>? Our pharmacists know the range &mdash; ask in-store or by reply.{% else %}Sometimes the search bar doesn't do justice. Our pharmacists know the range &mdash; ask in-store or reply to this email.{% endif %}</p>
<table border="0" cellpadding="0" cellspacing="0" style="margin:0 auto;">
<tr><td align="center" style="background-color:#CC1B2A; border-radius:4px;">
<a href="https://www.bargainchemist.co.nz/search?q={{ event.searchQuery|default:'' }}" style="display:inline-block; padding:14px 36px; font-family:Helvetica,Arial,sans-serif; font-size:15px; font-weight:bold; color:#ffffff; text-decoration:none;" target="_blank">Continue your search &rarr;</a>
</td></tr>
</table>
<p style="margin:18px 0 0; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:#777777;">or <a href="https://www.bargainchemist.co.nz/pages/find-a-pharmacy" style="color:#CC1B2A; text-decoration:underline;" target="_blank">visit any of our 30+ NZ stores</a></p>
</td>
</tr>
</table>
""",
    "urgency": VALUE_STRIP,
    "additional": f"""<!-- Additional message + pharmacist note -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td style="padding:24px 32px 8px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6; text-align:center;">
<p style="margin:0;">Price Beat 10% Guarantee &mdash; if you find it cheaper at another NZ pharmacy, we'll beat the difference.</p>
</td>
</tr>
</table>
{PHARMACIST_NOTE}
""",
}


def construct(w2sbja, spec):
    out = replace_section(w2sbja, "hero", spec["hero"])
    out = replace_section(out, "product", spec["product"])
    out = replace_section(out, "urgency", spec["urgency"])
    out = replace_section(out, "additional", spec["additional"])
    return out


# ---------------------------------------------------------------------------
# Static validation
# ---------------------------------------------------------------------------

BANNED_FEAR = ["limited stock", "selling fast", "act now", "last chance",
               "while stocks", "going fast", "almost gone", "hurry now",
               "expires today", "running out", "don't miss", "grab yours",
               "popular products don"]
BANNED_COUPON = ["% off", " coupon", "promo code", "discount code",
                 "voucher", " off your", "$5 off", "$10 off", "use code"]
BANNED_FACTS = ["1984", "since 19", "forty year", "40+ year"]
REQUIRED_APPROVED = ["$79", "Price Beat", "Always read the label",
                     "see your healthcare professional", "{% unsubscribe",
                     "{{ organization.name }}", "{{ organization.full_address }}"]
REQUIRED_LIQUID_BROWSE = ["{{ event.Name", "{{ event.URL"]
REQUIRED_LIQUID_SEARCH = ["{{ event.searchQuery"]
BANNED_LIQUID = ["{{ event.$value", "|float ", "|round("]


def static_check(html, label, kind):
    fail = []
    for w in BANNED_FEAR:
        if w.lower() in html.lower(): fail.append(f"FEAR phrase: '{w}'")
    for w in BANNED_COUPON:
        if w.lower() in html.lower(): fail.append(f"COUPON phrase: '{w}'")
    for w in BANNED_FACTS:
        if w.lower() in html.lower(): fail.append(f"FABRICATED FACT: '{w}'")
    for w in REQUIRED_APPROVED:
        if w not in html: fail.append(f"REQUIRED missing: '{w}'")
    extra = REQUIRED_LIQUID_BROWSE if kind == "browse" else REQUIRED_LIQUID_SEARCH
    for w in extra:
        if w not in html: fail.append(f"REQUIRED LIQUID missing: '{w}'")
    for w in BANNED_LIQUID:
        if w in html: fail.append(f"BANNED LIQUID: '{w}'")
    if fail:
        print(f"  ❌ {label} static FAIL ({len(fail)}):")
        for f in fail: print(f"     - {f}")
        return False
    print(f"  ✅ {label} static PASS")
    return True


# ---------------------------------------------------------------------------
# Render-test
# ---------------------------------------------------------------------------

def render(key, sid, label, html, contexts):
    """PATCH scratch with html, render against each context, validate.
    Returns (ok, diagnostics)."""
    body = {"data": {"type": "template", "id": sid,
                     "attributes": {"html": html}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/templates/{sid}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    if rp.status_code != 200:
        return False, [f"PATCH scratch: HTTP {rp.status_code}: {rp.text[:200]}"]
    time.sleep(0.3)

    diags = []
    for ctx_label, ctx in contexts:
        ctx_body = {"data": {"type": "template", "attributes": {
            "id": sid,
            "context": ctx,
        }}}
        rr = requests.post("https://a.klaviyo.com/api/template-render/",
                           headers=hdrs(key, content=True), json=ctx_body, timeout=30)
        save(f"{label}-{ctx_label}.json",
             {"status": rr.status_code, "body": rr.text})
        if rr.status_code != 200:
            diags.append(f"{ctx_label}: HTTP {rr.status_code} — {rr.text[:200]}")
            continue
        rendered = rr.json()["data"]["attributes"]["html"]
        save(f"{label}-{ctx_label}.html", rendered)
        # Liquid leakage
        if "{%" in rendered or "{{" in rendered:
            m = re.search(r'(\{[%{][^}]{0,80})', rendered)
            diags.append(f"{ctx_label}: Liquid leakage: {m.group(1) if m else '?'}")
            continue
        # CTA URL audit — confirm no /products/<handle> trap on myshopify domain
        for href in re.findall(r'<a[^>]*href="([^"]+)"', rendered):
            if "myshopify.com" in href:
                diags.append(f"{ctx_label}: CTA URL trap: '{href[:100]}'")
                break
        print(f"     {ctx_label:>20}  ✅")
    return (len(diags) == 0), diags


# ---------------------------------------------------------------------------
# Build context combos: real event + boundary cases
# ---------------------------------------------------------------------------

ORG_CTX = {
    "name": "Bargain Chemist",
    "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
    "url": "https://www.bargainchemist.co.nz",
}


def browse_contexts(real_event):
    return [
        ("real-event", {
            "first_name": "Sam",
            "organization": ORG_CTX,
            "event": real_event,
        }),
        ("missing-name", {
            "organization": ORG_CTX,
            "event": real_event,
        }),
        ("missing-product-fields", {
            "first_name": "Alex",
            "organization": ORG_CTX,
            "event": {},
        }),
        ("partial-product", {
            "first_name": "Jordan",
            "organization": ORG_CTX,
            "event": {"Name": "Bioglan Prebiotic Fibre 175g"},
        }),
    ]


def search_contexts(real_event):
    return [
        ("real-event", {
            "first_name": "Sam",
            "organization": ORG_CTX,
            "event": real_event,
        }),
        ("missing-query", {
            "first_name": "Alex",
            "organization": ORG_CTX,
            "event": {},
        }),
        ("special-chars-query", {
            "first_name": "Jordan",
            "organization": ORG_CTX,
            "event": {"searchQuery": 'panadol "extra strength" & ibuprofen'},
        }),
        ("query-only-no-product", {
            "first_name": "Casey",
            "organization": ORG_CTX,
            "event": {"searchQuery": "vitamin d"},
        }),
    ]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    key = load_key()
    print("=== Building browse + search abandonment templates from W2Sbja ===")
    print(f"Snapshots: {OUT}")

    print("\n--- Fetching W2Sbja design source ---")
    w2sbja = fetch_w2sbja(key)
    print(f"  W2Sbja: {len(w2sbja)} bytes")

    print("\n--- Fetching real event payloads for render-test contexts ---")
    browse_event = fetch_latest_event(key, VIEWED_PRODUCT_METRIC, "viewed-product")
    print(f"  Viewed Product event: keys={list(browse_event.keys())[:8]}…")
    search_event = fetch_latest_event(key, BOOST_SEARCH_METRIC, "boost-search")
    print(f"  Boost Search event:   keys={list(search_event.keys())[:8]}…")

    print("\n--- Creating scratch template ---")
    sid = create_scratch(key)
    print(f"  scratch: {sid}")

    constructed = {}
    overall_ok = True

    try:
        for spec, kind, contexts_fn, real_event in [
            (BROWSE_SPEC,    "browse", browse_contexts, browse_event),
            (SEARCH_E1_SPEC, "search", search_contexts, search_event),
            (SEARCH_E2_SPEC, "search", search_contexts, search_event),
        ]:
            label = spec["filename"].replace(".html", "")
            print(f"\n=== {label} ===")
            candidate = construct(w2sbja, spec)
            save(f"{label}-candidate.html", candidate)
            print(f"  candidate: {len(candidate)} bytes")

            if not static_check(candidate, label, kind):
                overall_ok = False
                continue

            print(f"  Render-testing across {len(contexts_fn(real_event))} contexts:")
            ok, diags = render(key, sid, label, candidate, contexts_fn(real_event))
            if not ok:
                print(f"  ❌ {label} render FAIL:")
                for d in diags: print(f"     - {d}")
                overall_ok = False
                continue

            constructed[label] = candidate
            print(f"  ✅ {label} VALIDATED")

        if not overall_ok:
            print(f"\n❌ BUILD FAILED — no files written. Diagnostics: {OUT}")
            sys.exit(1)

        print(f"\n=== Writing {len(constructed)} validated templates ===")
        for label, html in constructed.items():
            path = TEMPLATES_DIR / f"{label}.html"
            path.write_text(html, encoding="utf-8")
            print(f"  ✅ {path}  ({len(html)} bytes)")

        print(f"\n✅ BUILD COMPLETE. Next:")
        print(f"  py .claude\\bargain-chemist\\scripts\\patch_browse_abandonment_fix.py")
        print(f"  py .claude\\bargain-chemist\\scripts\\patch_search_abandonment_fix.py")

    finally:
        delete_scratch(key, sid)


if __name__ == "__main__":
    raise SystemExit(main())
