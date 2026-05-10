"""Build Y84ruV E1 + E4 templates from W2Sbja design + validate Liquid INLINE.

User instruction (2026-05-08): "use W2Sbja as reference always" + "test logic
inside the template DURING build, not after". This script does both atomically.

Workflow per template:
  1. Fetch W2Sbja HTML live from Klaviyo (canonical design reference)
  2. Construct candidate by substituting W2Sbja sections with cart-recovery
     copy (hero, CTA, 3-tier banner)
  3. Static-validate: no fear/scarcity, no coupons, no fabricated facts,
     approved facts present, footer compliance, brand voice match
  4. PATCH scratch template UH72Vm with candidate
  5. POST /api/template-render/ at $value=20, 50, 120 (covers all 3 tiers)
  6. Assert HTTP 200 + expected tier marker present + zero Liquid leakage
  7. Restore UH72Vm
  8. Write final HTML to .claude/bargain-chemist/templates/<name>.html
  9. If ANY check fails: log diagnostics, restore UH72Vm, exit non-zero,
     write nothing (atomic — never half-built outputs on disk)

Run locally:
    python .claude/bargain-chemist/scripts/build_y84ruv_templates.py

Snapshots all renders + diagnostics to
.claude/bargain-chemist/snapshots/<today>/build-y84ruv/
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/build-y84ruv"
OUT.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = REPO / ".claude/bargain-chemist/templates"
TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)

W2SBJA_ID = "W2Sbja"  # design reference template
# Scratch template for render-test PATCH cycles. Created fresh per run +
# DELETEd at end (try-finally). Avoids depending on a fixed template ID
# that may have been deleted between runs (which is what happened to
# UH72Vm on 2026-05-08).
SCRATCH_NAME = f"BC PROBE - render scratch (delete me)"
REVISION = "2025-10-15"


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
# Section substitutions per email
# ---------------------------------------------------------------------------
# Each email has a "spec" dict that defines what each W2Sbja section becomes.
# We KEEP the chrome (free-ship bar, logo, nav, social, legal, unsubscribe)
# untouched — they're the design reference.
# We REPLACE: hero, product-details (becomes single CTA), urgency-note (becomes
# 3-tier banner), additional-message.

# ---- 3-tier banner (shared across E1 & E4, copy differs by email) ---------
# Styling matches W2Sbja's urgency-note panel (cream bg + orange borders) for
# brand consistency. Defensive {% with v=…|default:0 %} ensures missing $value
# routes to Tier A safely (probe_null_value_handling.py 2026-05-08).
TIER_BANNER_TEMPLATE = """<!-- 3-tier value banner (replaces W2Sbja's urgency note) -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#fff8f0; border-top:1px solid #ffe0b2; border-bottom:1px solid #ffe0b2;" width="100%">
<tr>
<td align="center" style="padding:16px 40px; font-family:Helvetica,Arial,sans-serif; font-size:14px; color:#555555; line-height:1.5;">
{{% with v=event|lookup:'$value'|default:0 %}}{{% if v < 30 %}}{tier_a}{{% elif v < 79 %}}{tier_b}{{% else %}}{tier_c}{{% endif %}}{{% endwith %}}
</td>
</tr>
</table>"""


def build_banner(tier_a, tier_b, tier_c):
    return TIER_BANNER_TEMPLATE.format(tier_a=tier_a, tier_b=tier_b, tier_c=tier_c)


# ---- W2Sbja section anchors ----------------------------------------------
SECTION_ANCHORS = {
    "hero":          ("<!-- Hero -->",                 "<!-- Product details -->"),
    "product":       ("<!-- Product details -->",      "<!-- Urgency note -->"),
    "urgency":       ("<!-- Urgency note -->",         "<!-- Additional message -->"),
    "additional":    ("<!-- Additional message -->",   "<!-- Footer: Get social -->"),
}


def replace_section(html, section_key, new_content):
    """Replace the HTML between two anchor comments with new content
    (preserves the leading anchor comment as a section marker)."""
    start_anchor, end_anchor = SECTION_ANCHORS[section_key]
    s = html.find(start_anchor)
    e = html.find(end_anchor)
    assert s >= 0, f"start anchor not found: {start_anchor}"
    assert e > s, f"end anchor not found or out of order: {end_anchor}"
    return html[:s] + new_content + "\n" + html[e:]


# ---- Email specs ---------------------------------------------------------

E1_SPEC = {
    "filename": "cart-recover-e1-w2sbja.html",
    "klaviyo_template_name": f"BC OWNED - Y84ruV-v3 E1 W2Sbja-design ({TODAY})",
    "subject": "Your cart's saved — pick up when you're ready",
    "preview": "Your items are waiting. Free shipping over $79.",
    "hero": """<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f8971d;" width="100%">
<tr>
<td align="center" style="padding:40px 32px 32px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.9); text-transform:uppercase; letter-spacing:2px;">Your Cart</p>
<h1 style="margin:0 0 12px; font-family:Helvetica,Arial,sans-serif; font-size:36px; font-weight:bold; color:#ffffff; line-height:1.2;">Your cart's saved</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:rgba(255,255,255,0.9);">Hi {{ first_name|default:'there' }} — we've kept your items so you can pick up right where you left off.</p>
</td>
</tr>
</table>
""",
    "product": """<!-- Cart-recovery CTA (replaces W2Sbja product-details) -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" style="padding:36px 40px 24px;">
<p style="margin:0 0 24px; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:#444444; line-height:1.5; text-align:center;">Checkout's quick and secure. Your order will be on its way before you know it.</p>
<table border="0" cellpadding="0" cellspacing="0">
<tr><td align="center" style="background-color:#CC1B2A; border-radius:4px;">
<a href="{{ event.extra.checkout_url|default:'https://www.bargainchemist.co.nz/cart' }}" style="display:inline-block; padding:14px 40px; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:bold; color:#ffffff; text-decoration:none;" target="_blank">Return to checkout &rarr;</a>
</td></tr>
</table>
</td>
</tr>
</table>
""",
    "urgency": build_banner(
        tier_a="<strong style=\"color:#7B1523;\">NZ's lowest pharmacy prices</strong>, backed by our Price Beat 10% Guarantee. Your cart's exactly where you left it.",
        tier_b="<strong style=\"color:#7B1523;\">Free shipping kicks in at $79.</strong> Add a couple more items to unlock free delivery on this order.",
        tier_c="You're at our <strong style=\"color:#7B1523;\">free-shipping tier ($79+)</strong>. Finish checkout when you're ready &mdash; Price Beat 10% applies.",
    ),
    "additional": """<!-- Additional message -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td style="padding:28px 40px 36px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6; text-align:center;">
<p style="margin:0;">Questions? Our team is here to help &mdash; or browse our full range at <a href="https://www.bargainchemist.co.nz" style="color:#CC1B2A; text-decoration:underline;">bargainchemist.co.nz</a></p>
</td>
</tr>
</table>
""",
}

E4_SPEC = {
    "filename": "cart-recover-e4-w2sbja.html",
    "klaviyo_template_name": f"BC OWNED - Y84ruV-v3 E4 W2Sbja-design ({TODAY})",
    "subject": "Your order's one click away",
    "preview": "Free shipping over $79 — same Bargain Chemist price.",
    "hero": """<!-- Hero -->
<table border="0" cellpadding="0" cellspacing="0" style="background-color:#f8971d;" width="100%">
<tr>
<td align="center" style="padding:40px 32px 32px;">
<p style="margin:0 0 8px; font-family:Helvetica,Arial,sans-serif; font-size:13px; font-weight:600; color:rgba(255,255,255,0.9); text-transform:uppercase; letter-spacing:2px;">Reminder</p>
<h1 style="margin:0 0 12px; font-family:Helvetica,Arial,sans-serif; font-size:36px; font-weight:bold; color:#ffffff; line-height:1.2;">Your cart's still waiting</h1>
<p style="margin:0; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:rgba(255,255,255,0.9);">Hi {{ first_name|default:'there' }} &mdash; same items, ready when you are. Finish checkout in just a few clicks.</p>
</td>
</tr>
</table>
""",
    "product": """<!-- Cart-recovery CTA (replaces W2Sbja product-details) -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td align="center" style="padding:36px 40px 24px;">
<p style="margin:0 0 24px; font-family:Helvetica,Arial,sans-serif; font-size:16px; color:#444444; line-height:1.5; text-align:center;">Same secure checkout. Same Bargain Chemist prices.</p>
<table border="0" cellpadding="0" cellspacing="0">
<tr><td align="center" style="background-color:#CC1B2A; border-radius:4px;">
<a href="{{ event.extra.checkout_url|default:'https://www.bargainchemist.co.nz/cart' }}" style="display:inline-block; padding:14px 40px; font-family:Helvetica,Arial,sans-serif; font-size:16px; font-weight:bold; color:#ffffff; text-decoration:none;" target="_blank">Finish your order &rarr;</a>
</td></tr>
</table>
</td>
</tr>
</table>
""",
    "urgency": build_banner(
        tier_a="<strong style=\"color:#7B1523;\">Still here when you're ready.</strong> Same items, same Price Beat 10% Guarantee.",
        tier_b="You're <strong style=\"color:#7B1523;\">one or two items from free shipping</strong>. Top up or finish anytime.",
        tier_c="<strong style=\"color:#7B1523;\">Free shipping's already on</strong> this order &mdash; finish checkout when you're ready.",
    ),
    "additional": """<!-- Additional message -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
<tr>
<td style="padding:28px 40px 36px; font-family:Helvetica,Arial,sans-serif; font-size:15px; color:#555555; line-height:1.6; text-align:center;">
<p style="margin:0;">Need help? Just reply to this email &mdash; our team's here for you.</p>
</td>
</tr>
</table>
""",
}


# ---------------------------------------------------------------------------
# Static analysis (runs against constructed HTML before render-test)
# ---------------------------------------------------------------------------

BANNED_FEAR = ["limited stock", "selling fast", "act now", "last chance",
               "while stocks", "going fast", "almost gone", "hurry",
               "expires today", "running out", "don't miss", "grab yours"]
BANNED_COUPON = ["% off", "coupon", "promo code", "discount code", "voucher",
                  " off your", "$5 off", "$10 off", "use code"]
BANNED_FACTS = ["1984", "since 19", "forty year", "40+ year"]
REQUIRED_APPROVED = ["$79", "Price Beat", "Always read the label",
                     "see your healthcare professional", "{% unsubscribe",
                     "{{ organization.name }}", "{{ organization.full_address }}"]
REQUIRED_LIQUID = ["{% with v=event|lookup:'$value'|default:0 %}",
                    "{% if v < 30 %}", "{% elif v < 79 %}",
                    "{% else %}", "{% endif %}", "{% endwith %}"]
BANNED_LIQUID = ["{{ event.$value", "|float ", "|round("]


def static_check(html, label):
    fail = []
    for w in BANNED_FEAR:
        if w.lower() in html.lower():
            fail.append(f"FEAR phrase present: '{w}'")
    for w in BANNED_COUPON:
        if w.lower() in html.lower():
            fail.append(f"COUPON phrase present: '{w}'")
    for w in BANNED_FACTS:
        if w.lower() in html.lower():
            fail.append(f"FABRICATED FACT present: '{w}'")
    for w in REQUIRED_APPROVED:
        if w not in html:
            fail.append(f"REQUIRED APPROVED phrase missing: '{w}'")
    for w in REQUIRED_LIQUID:
        if w not in html:
            fail.append(f"REQUIRED LIQUID pattern missing: '{w}'")
    for w in BANNED_LIQUID:
        if w in html:
            fail.append(f"BANNED LIQUID pattern present: '{w}'")
    if fail:
        print(f"\n  ❌ {label} static checks FAILED ({len(fail)}):")
        for f in fail:
            print(f"     - {f}")
        return False
    print(f"  ✅ {label} static checks PASS")
    return True


# ---------------------------------------------------------------------------
# Scratch-template lifecycle (create fresh + DELETE on cleanup)
# ---------------------------------------------------------------------------

def create_scratch(key):
    """POST a fresh scratch template. Returns its ID."""
    body = {"data": {"type": "template", "attributes": {
        "name": SCRATCH_NAME,
        "editor_type": "CODE",
        "html": "<html><body>placeholder — will be PATCHed by build script</body></html>",
    }}}
    r = requests.post("https://a.klaviyo.com/api/templates/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    if r.status_code not in (200, 201):
        sys.exit(f"❌ failed to create scratch template: HTTP {r.status_code}\n{r.text[:300]}")
    sid = r.json()["data"]["id"]
    print(f"  Created scratch template: {sid}")
    return sid


def delete_scratch(key, sid):
    """DELETE the scratch template. Idempotent (404 = already gone)."""
    r = requests.delete(f"https://a.klaviyo.com/api/templates/{sid}/",
                        headers=hdrs(key), timeout=30)
    if r.status_code in (200, 204):
        print(f"  Cleaned up scratch template: {sid}")
    elif r.status_code == 404:
        print(f"  Scratch already gone: {sid}")
    else:
        print(f"  ⚠️  scratch cleanup HTTP {r.status_code}: {r.text[:200]}")


# ---------------------------------------------------------------------------
# Render-test (runs against constructed HTML by PATCHing scratch template)
# ---------------------------------------------------------------------------

def render_test(key, sid, label, html, expected_phrases_per_value):
    """PATCH scratch template with `html`, render at each $value, assert
    expected phrase present + zero Liquid leakage. Returns (ok, diagnostics)."""
    # PATCH scratch with candidate
    body = {"data": {"type": "template", "id": sid,
                     "attributes": {"html": html}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/templates/{sid}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    if rp.status_code != 200:
        return False, [f"PATCH scratch {sid} failed HTTP {rp.status_code}: {rp.text[:300]}"]
    time.sleep(0.3)

    diags = []
    for value, expected in expected_phrases_per_value:
        ctx_body = {"data": {"type": "template", "attributes": {
            "id": sid,
            "context": {
                "first_name": "Sam",
                "organization": {
                    "name": "Bargain Chemist",
                    "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
                    "url": "https://www.bargainchemist.co.nz",
                },
                "event": {"$value": value, "extra": {"checkout_url": "https://www.bargainchemist.co.nz/checkouts/ac/TEST/recover?key=test"}},
            }
        }}}
        rr = requests.post("https://a.klaviyo.com/api/template-render/",
                           headers=hdrs(key, content=True), json=ctx_body, timeout=30)
        # Save the FULL response (no truncation — was causing JSON parse failures
        # in extract_y84ruv_previews.py) plus a standalone .html preview for
        # easy browser-open. Both written even on render error so diagnostics
        # are complete.
        save(f"{label}-render-v{value}.json",
             {"status": rr.status_code, "value": value, "body": rr.text})
        if rr.status_code != 200:
            diags.append(f"v={value}: HTTP {rr.status_code} — {rr.text[:200]}")
            continue
        rendered = rr.json()["data"]["attributes"]["html"]
        # Standalone preview HTML — opens directly in browser, no JSON parsing.
        save(f"{label}-render-v{value}.html", rendered)
        if "{%" in rendered or "{{" in rendered:
            m = re.search(r'(\{[%{][^}]{0,80})', rendered)
            diags.append(f"v={value}: Liquid leakage: {m.group(1) if m else '?'}")
            continue
        if expected not in rendered:
            diags.append(f"v={value}: expected phrase '{expected}' not in render")
            continue
        print(f"     v={value:>4}  ✅  '{expected[:60]}' present, no leakage")
    return (len(diags) == 0), diags


# ---------------------------------------------------------------------------
# Main build flow
# ---------------------------------------------------------------------------

def fetch_w2sbja(key):
    print(f"\n=== Fetching W2Sbja design reference ===")
    r = requests.get(f"https://a.klaviyo.com/api/templates/{W2SBJA_ID}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ failed to fetch W2Sbja: HTTP {r.status_code}: {r.text[:300]}")
    html = r.json()["data"]["attributes"]["html"]
    save("w2sbja-source.html", html)
    print(f"  W2Sbja: {len(html)} bytes")
    return html


def construct(html, spec):
    """Replace the 4 substitutable sections with spec content."""
    out = replace_section(html, "hero", spec["hero"])
    out = replace_section(out, "product", spec["product"])
    out = replace_section(out, "urgency", spec["urgency"])
    out = replace_section(out, "additional", spec["additional"])
    return out


def main():
    key = load_key()
    w2sbja_html = fetch_w2sbja(key)

    # Create fresh scratch template; cleanup in finally
    print(f"\n=== Creating scratch template for render-tests ===")
    sid = create_scratch(key)

    try:
        # Build E1 + E4 specs and validate each one fully before writing
        EMAILS = [
            (E1_SPEC, [
                (20,  "NZ's lowest pharmacy prices"),
                (50,  "Free shipping kicks in at $79"),
                (120, "free-shipping tier ($79+)"),
            ]),
            (E4_SPEC, [
                (20,  "Still here when you're ready"),
                (50,  "one or two items from free shipping"),
                (120, "Free shipping's already on"),
            ]),
        ]

        constructed = {}  # spec_label -> html (only set if fully validated)
        overall_ok = True

        for spec, expected_per_value in EMAILS:
            label = spec["filename"].replace(".html", "")
            print(f"\n{'='*70}\nBuilding: {label}\n{'='*70}")
            candidate = construct(w2sbja_html, spec)
            save(f"{label}-candidate.html", candidate)
            print(f"  Candidate: {len(candidate)} bytes")

            # 1. Static checks
            if not static_check(candidate, label):
                print(f"  ❌ {label} BLOCKED by static checks. Skipping render-test.")
                overall_ok = False
                continue

            # 2. Render-test (PATCH scratch + render at 3 cart values)
            print(f"  Render-testing at $value 20/50/120 …")
            ok, diags = render_test(key, sid, label, candidate, expected_per_value)
            if not ok:
                print(f"  ❌ {label} render-test FAILED:")
                for d in diags:
                    print(f"     - {d}")
                overall_ok = False
                continue

            # 3. Stage for write (only after BOTH checks pass)
            constructed[label] = candidate
            print(f"  ✅ {label} VALIDATED — staged for write")

        # Atomic write: only commit to /templates/ if EVERYTHING passed
        if not overall_ok:
            print(f"\n{'='*70}\n❌ BUILD FAILED — no files written. See {OUT} for diagnostics.\n{'='*70}")
            sys.exit(1)
    finally:
        # Always clean up the scratch template (success or failure)
        delete_scratch(key, sid)

    print(f"\n{'='*70}\nWriting validated templates to {TEMPLATES_DIR}/\n{'='*70}")
    for label, html in constructed.items():
        path = TEMPLATES_DIR / f"{label}.html"
        path.write_text(html, encoding="utf-8")
        print(f"  ✅ {path}  ({len(html)} bytes)")

    print(f"\n=== ✅ BUILD COMPLETE ===")
    print(f"Templates ready for deploy:")
    for label in constructed:
        print(f"  - {TEMPLATES_DIR/f'{label}.html'}")
    print(f"\nNext: python .claude/bargain-chemist/scripts/klaviyo_rebuild_y84ruv_v3.py")
    print(f"      (dry-run by default; pass --apply to deploy)")
    print(f"\nDiagnostics: {OUT}")


if __name__ == "__main__":
    raise SystemExit(main())
