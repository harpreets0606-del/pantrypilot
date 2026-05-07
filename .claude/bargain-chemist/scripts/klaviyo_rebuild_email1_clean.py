"""Rebuild Y84ruV-v2 email-1 with clean, Klaviyo-Django-safe HTML.

Strategy:
  1. Build a minimal, valid HTML template (no broken cart iteration, no Jinja2 filters)
  2. Render-test via Klaviyo's POST /api/template-render endpoint with two contexts:
     - cart $value = 50 (should produce under-$79 copy)
     - cart $value = 120 (should produce over-$79 copy)
  3. Check both renders for literal `{{` or `{%` leftovers (= syntax error)
  4. If clean: PATCH owned template UH72Vm with new HTML, then PATCH flow-action
     105955340 to force re-clone with the corrected HTML.
  5. Re-pull the clone and re-render to confirm.

Run:
  python klaviyo_rebuild_email1_clean.py            # builds + render-tests, no deploy
  python klaviyo_rebuild_email1_clean.py --apply    # builds + tests + deploys
"""
import argparse
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
OUT_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/email1-clean"
OUT_DIR.mkdir(parents=True, exist_ok=True)

REVISION = "2025-10-15"
OWNED_TEMPLATE_ID = "UH72Vm"
FLOW_ACTION_ID = "105955340"


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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing")


def hdrs(key, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, data):
    p = OUT_DIR / name
    p.write_text(
        json.dumps(data, indent=2) if isinstance(data, dict) else str(data),
        encoding="utf-8",
    )


# Clean HTML — no cart iteration, no Jinja2 filters, just a documented Klaviyo
# Django conditional on event.$value plus a single recovery CTA.
CLEAN_HTML = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>You forgot something at Bargain Chemist</title>
<style type="text/css">
  body { margin:0; padding:0; background-color:#f4f4f4; font-family:Helvetica,Arial,sans-serif; color:#222; }
  table { border-collapse:collapse; }
  .container { max-width:600px; margin:0 auto; background:#ffffff; }
  .pad { padding:32px 28px; }
  .btn { display:inline-block; background:#FF0031; color:#ffffff !important; text-decoration:none; padding:16px 36px; border-radius:4px; font-weight:700; letter-spacing:0.5px; text-transform:uppercase; }
  .nudge-low { background:#FFF7E6; color:#7A4F00; }
  .nudge-ok  { background:#E8F5E9; color:#1B5E20; }
  .footer { background:#1a1a1a; color:#888; padding:20px 28px; text-align:center; font-size:12px; line-height:1.6; }
  .footer a { color:#cccccc; }
</style>
</head>
<body>
<table width="100%" border="0" cellspacing="0" cellpadding="0">
<tr><td align="center">
<table class="container" width="600" border="0" cellspacing="0" cellpadding="0">

<!-- HEADER -->
<tr><td style="background:#CC1B2A;text-align:center;padding:18px;">
  <a href="https://www.bargainchemist.co.nz/" target="_blank" style="color:#ffffff;text-decoration:none;font-weight:700;font-size:20px;letter-spacing:1px;">BARGAIN CHEMIST</a>
</td></tr>

<!-- CART-AWARE NUDGE (Klaviyo Django; no |float, no math) -->
{% if event.$value < 79 %}
<tr><td class="nudge-low" style="padding:18px 28px;text-align:center;">
  <p style="margin:0;font-size:16px;line-height:1.5;color:#7A4F00;">
    Your cart is under $79 &mdash; add a few more items to unlock <strong>FREE shipping</strong> at NZ's lowest pharmacy prices.
  </p>
</td></tr>
{% else %}
<tr><td class="nudge-ok" style="padding:18px 28px;text-align:center;">
  <p style="margin:0;font-size:16px;line-height:1.5;color:#1B5E20;">
    <strong>Free shipping is yours</strong> &mdash; finish checkout in just a few clicks.
  </p>
</td></tr>
{% endif %}

<!-- BODY -->
<tr><td class="pad" style="padding:32px 28px;">
  <p style="font-size:18px;margin:0 0 16px 0;line-height:1.4;">Hi {{ first_name|default:'there' }},</p>
  <p style="font-size:16px;margin:0 0 24px 0;line-height:1.6;color:#444;">
    Your cart is saved at NZ's lowest pharmacy prices. Pick up where you left off &mdash; everything's ready when you are.
  </p>
  <p style="text-align:center;margin:0 0 24px 0;">
    <a class="btn" href="{{ event.extra.checkout_url|default:'https://www.bargainchemist.co.nz/cart' }}" target="_blank">Return To Your Cart</a>
  </p>
  <p style="font-size:14px;color:#666;text-align:center;margin:0;line-height:1.6;">
    Free shipping over $79  &middot;  Price Beat 10% Guarantee  &middot;  30+ stores nationwide
  </p>
</td></tr>

<!-- TRUST -->
<tr><td style="background:#f9f9f9;padding:18px 28px;text-align:center;border-top:1px solid #eee;">
  <p style="font-size:13px;color:#666;margin:0;line-height:1.6;">
    Trusted NZ pharmacists. Safe &amp; secure checkout. Trusted by thousands of Kiwis.
  </p>
</td></tr>

<!-- ASA DISCLAIMER -->
<tr><td style="padding:18px 28px;text-align:center;background:#ffffff;">
  <p style="font-size:12px;color:#888;margin:0;line-height:1.6;">
    Always read the label and use as directed. If symptoms persist, see your healthcare professional.
  </p>
</td></tr>

<!-- FOOTER -->
<tr><td class="footer">
  <p style="margin:0 0 6px 0;">{{ organization.full_address }}</p>
  <p style="margin:0 0 6px 0;">&copy; 2026 Bargain Chemist. All rights reserved.</p>
  <p style="margin:0;">{% unsubscribe 'Unsubscribe' %}  &middot;  <a href="https://bargainchemist.co.nz/pages/privacy-policy" style="color:#cccccc;">Privacy Policy</a></p>
</td></tr>

</table>
</td></tr>
</table>
</body>
</html>
"""


def render_test(html, event_value, key):
    """POST /api/template-render to validate Klaviyo can parse the template.
    Returns rendered HTML or None on error."""
    body = {
        "data": {
            "type": "template-render",
            "attributes": {
                "html": html,
                "context": {
                    "first_name": "Sam",
                    "organization": {
                        "full_address": "Bargain Chemist, NZ"
                    },
                    "event": {
                        "$value": event_value,
                        "extra": {"checkout_url": "https://www.bargainchemist.co.nz/cart"}
                    },
                },
            }
        }
    }
    r = requests.post(
        "https://a.klaviyo.com/api/template-render/",
        headers=hdrs(key, content=True), json=body, timeout=30,
    )
    save(f"render-test-value{event_value}.json", {"status": r.status_code, "body": r.text[:5000]})
    if r.status_code not in (200, 201):
        print(f"  Render HTTP {r.status_code}: {r.text[:300]}")
        return None
    try:
        return r.json()["data"]["attributes"]["html"]
    except Exception:
        print(f"  Could not extract html from response: {r.text[:300]}")
        return None


def check_rendered(html, expected_phrase, label):
    """Check rendered HTML — no leftover Jinja, contains expected phrase."""
    issues = []
    leftover_jinja = re.findall(r'\{%\s*(?:if|else|endif|for|endfor|with|endwith)[^%]*%\}', html)
    leftover_vars = re.findall(r'\{\{\s*[^}]*\}\}', html)
    if leftover_jinja:
        issues.append(f"unrendered {{% %}} tags: {leftover_jinja[:3]}")
    if leftover_vars:
        issues.append(f"unrendered {{{{ }}}} tags: {leftover_vars[:3]}")
    if expected_phrase not in html:
        issues.append(f"expected phrase NOT found: {expected_phrase!r}")
    if issues:
        print(f"  [{label}] FAIL: {issues}")
        return False
    print(f"  [{label}] OK: rendered cleanly, expected copy present")
    return True


def patch_template(template_id, html, key):
    body = {
        "data": {
            "type": "template",
            "id": template_id,
            "attributes": {"html": html},
        }
    }
    r = requests.patch(
        f"https://a.klaviyo.com/api/templates/{template_id}/",
        headers=hdrs(key, content=True), json=body, timeout=30,
    )
    save(f"patch-template-{template_id}.json",
         {"status": r.status_code, "body": r.text[:1000]})
    if r.status_code != 200:
        raise RuntimeError(f"PATCH template {template_id} HTTP {r.status_code}: {r.text[:300]}")


def reassign_flow_action(action_id, owned_template_id, key):
    """Re-PATCH flow-action with same owned template_id to force re-clone."""
    r = requests.get(
        f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
        headers=hdrs(key), timeout=30,
    )
    r.raise_for_status()
    defn = r.json()["data"]["attributes"]["definition"]
    defn["data"]["message"]["template_id"] = owned_template_id
    body = {
        "data": {
            "type": "flow-action",
            "id": action_id,
            "attributes": {"definition": defn},
        }
    }
    r = requests.patch(
        f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
        headers=hdrs(key, content=True), json=body, timeout=30,
    )
    save(f"patch-action-{action_id}.json",
         {"status": r.status_code, "body": r.text[:2000]})
    if r.status_code != 200:
        raise RuntimeError(f"PATCH flow-action HTTP {r.status_code}: {r.text[:400]}")
    new_clone = r.json()["data"]["attributes"]["definition"]["data"]["message"]["template_id"]
    return new_clone


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    key = load_key()

    save("email1-clean.html", CLEAN_HTML)
    print(f"Phase 1: HTML saved -> {OUT_DIR}/email1-clean.html ({len(CLEAN_HTML)} chars)")

    print("\nPhase 2: render-test via /api/template-render")
    rendered_low = render_test(CLEAN_HTML, 50, key)
    if rendered_low:
        save("rendered-value50.html", rendered_low)
        ok_low = check_rendered(rendered_low,
                                "Your cart is under $79", "value=50 (under-79 path)")
    else:
        ok_low = False

    rendered_high = render_test(CLEAN_HTML, 120, key)
    if rendered_high:
        save("rendered-value120.html", rendered_high)
        ok_high = check_rendered(rendered_high,
                                 "Free shipping is yours", "value=120 (over-79 path)")
    else:
        ok_high = False

    if not (ok_low and ok_high):
        print("\nRender tests FAILED — DO NOT deploy. Inspect saved files.")
        return 1

    print("\nBoth render tests PASSED. HTML is Klaviyo-Django-safe.")

    if not args.apply:
        print("\nDry-run complete. Re-run with --apply to PATCH the owned template + re-clone.")
        return 0

    print(f"\nPhase 3: PATCH owned template {OWNED_TEMPLATE_ID}")
    patch_template(OWNED_TEMPLATE_ID, CLEAN_HTML, key)
    print(f"  OK")

    print(f"\nPhase 4: Re-assign flow-action {FLOW_ACTION_ID} (forces re-clone)")
    new_clone_id = reassign_flow_action(FLOW_ACTION_ID, OWNED_TEMPLATE_ID, key)
    print(f"  OK. New cloned template_id: {new_clone_id}")

    print(f"\nPhase 5: verify new clone has clean HTML")
    time.sleep(1.0)
    r = requests.get(
        f"https://a.klaviyo.com/api/templates/{new_clone_id}/",
        headers=hdrs(key), timeout=30,
    )
    if r.status_code != 200:
        print(f"  Verify GET HTTP {r.status_code}")
        return 1
    new_html = r.json()["data"]["attributes"]["html"]
    save(f"new-clone-{new_clone_id}.html", new_html)
    leftover = re.findall(r'\{%\s*for\s+item\b', new_html)
    has_jinja2 = re.findall(r'\|float|\|round\(', new_html)
    print(f"  new clone: {len(new_html)} chars")
    print(f"  has broken {{% for item %}}: {bool(leftover)}")
    print(f"  has Jinja2 |float / |round(): {bool(has_jinja2)}")
    print(f"  has event.$value conditional: {'event.$value' in new_html}")

    print(f"\nDone. Re-preview at: https://www.klaviyo.com/flow/VaRyRc/edit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
