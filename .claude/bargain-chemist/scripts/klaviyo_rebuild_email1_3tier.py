"""Rebuild Y84ruV-v2 email-1 with verified 3-tier cart-value conditional.

Data-driven design (see memory/klaviyo-best-practices.md cart-value tier playbook):
  Tier A (<$30, 29%):    trust + price, no free-ship push
  Tier B ($30-$78, 36%): free-ship gap nudge (highest leverage)
  Tier C (>=$79, 36%):   honest reassurance, past-tense (avoids ASA misleading-promise risk)

Subject + preview: universal (single line, all tiers).
Body: 3-tier {% if/elif/else %} (verified working — probe-elif 2026-05-08).
HTML: surgical edit of TuHa4f to keep brand chrome (header/logo/footer/styling).

Deploy guards:
  - Snapshot UH72Vm before PATCH
  - Render-test all 3 tier values ($value=20/50/120) via /api/template-render
  - Each render must contain expected tier-specific phrase
  - No leftover {% %} or {{ item.* }} in any rendered output
  - Auto-rollback if any check fails
  - Live flow VaRyRc untouched until --apply

Run: python klaviyo_rebuild_email1_3tier.py [--apply]
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
OUT_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/email1-3tier"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REVISION = "2025-10-15"
OWNED_TEMPLATE_ID = "UH72Vm"
FLOW_ACTION_ID = "105955340"
SOURCE_TEMPLATE_ID = "TuHa4f"

# Subject + preview (universal, applied at flow-action level — separate PATCH)
SUBJECT_LINE = "{{ first_name|default:'Hey' }}, your cart's still saved at Bargain Chemist"
PREVIEW_TEXT = "Pick up where you left off — NZ's lowest pharmacy prices, free shipping over $79."


# Body content per tier — Klaviyo Django syntax verified
REPLACEMENT_BODY = """
<!-- BEGIN cart-aware body — 3-tier (rebuilt 2026-05-08) -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td align="center" style="padding:32px 28px 0 28px;">
      <h1 style="font-family:Helvetica,Arial,sans-serif;font-size:22px;font-weight:700;color:#222;margin:0 0 16px 0;line-height:1.3;">
        Hi {{ first_name|default:'there' }},
      </h1>
      <p style="font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#444;line-height:1.6;margin:0 0 22px 0;">
        Your cart is saved &mdash; pick up where you left off whenever you're ready.
      </p>
    </td>
  </tr>

  <!-- 3-TIER NUDGE (verified Klaviyo Django syntax) -->
  {% if event|lookup:'$value' < 30 %}
  <!-- Tier A: small impulse cart (under $30) — no free-ship push, lead with price/trust -->
  <tr>
    <td align="center" style="padding:0 28px 22px 28px;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#FDDDD9;border-radius:6px;">
        <tr><td style="padding:18px 24px;text-align:center;">
          <p style="font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#7B1523;margin:0;">
            <strong>NZ's lowest pharmacy prices</strong> &mdash; backed by our Price Beat 10% Guarantee. Your cart's exactly where you left it.
          </p>
        </td></tr>
      </table>
    </td>
  </tr>
  {% elif event|lookup:'$value' < 79 %}
  <!-- Tier B: gap-actionable cart ($30-$78) — free-ship nudge -->
  <tr>
    <td align="center" style="padding:0 28px 22px 28px;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#FFF7E6;border-radius:6px;">
        <tr><td style="padding:18px 24px;text-align:center;">
          <p style="font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#7A4F00;margin:0;">
            <strong>Free shipping kicks in at $79.</strong> Add a few more items at NZ's lowest pharmacy prices to unlock it.
          </p>
        </td></tr>
      </table>
    </td>
  </tr>
  {% else %}
  <!-- Tier C: free-ship qualified (>=$79) — past-tense, ASA-safe -->
  <tr>
    <td align="center" style="padding:0 28px 22px 28px;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#E8F5E9;border-radius:6px;">
        <tr><td style="padding:18px 24px;text-align:center;">
          <p style="font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#1B5E20;margin:0;">
            Your cart was at our <strong>free-shipping tier ($79+)</strong>. Finish checkout when you're ready.
          </p>
        </td></tr>
      </table>
    </td>
  </tr>
  {% endif %}

  <!-- CTA -->
  <tr>
    <td align="center" style="padding:8px 28px 32px 28px;">
      <a class="btn" href="https://www.bargainchemist.co.nz/cart" target="_blank" style="display:inline-block;background-color:#FF0031;color:#ffffff;font-family:Helvetica,Arial,sans-serif;font-size:14px;font-weight:700;text-decoration:none;padding:14px 36px;border-radius:4px;letter-spacing:1px;text-transform:uppercase;">
        Return To Your Cart
      </a>
    </td>
  </tr>

  <!-- TRUST STRIP -->
  <tr>
    <td align="center" style="padding:0 28px 24px 28px;">
      <p style="font-family:Helvetica,Arial,sans-serif;font-size:13px;color:#666;text-align:center;margin:0;line-height:1.6;">
        Price Beat 10% Guarantee  &middot;  Free shipping over $79  &middot;  30+ stores nationwide
      </p>
    </td>
  </tr>
</table>
<!-- END cart-aware body -->
"""


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


def get_template_html(tid, key):
    r = requests.get(f"https://a.klaviyo.com/api/templates/{tid}/",
                     headers=hdrs(key), timeout=30)
    r.raise_for_status()
    return r.json()["data"]["attributes"]["html"]


def patch_template(tid, html, key):
    body = {"data": {"type": "template", "id": tid, "attributes": {"html": html}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{tid}/",
                       headers=hdrs(key, content=True), json=body, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"PATCH template HTTP {r.status_code}: {r.text[:300]}")


def render_test(tid, event_value, key):
    body = {"data": {"type": "template", "attributes": {
        "id": tid,
        "context": {
            "first_name": "Sam",
            "organization": {"full_address": "1 Test St, Auckland NZ"},
            "event": {"$value": event_value, "$extra": {}},
        }
    }}}
    r = requests.post("https://a.klaviyo.com/api/template-render/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"render-value{event_value}.json",
         {"status": r.status_code, "body": r.text[:5000]})
    if r.status_code not in (200, 201):
        return None
    return r.json()["data"]["attributes"]["html"]


def reassign_flow_action(action_id, owned_tid, key, subject, preview):
    """PATCH flow-action: re-assign template AND update subject/preview."""
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                     headers=hdrs(key), timeout=30)
    r.raise_for_status()
    defn = r.json()["data"]["attributes"]["definition"]
    msg = defn["data"]["message"]
    msg["template_id"] = owned_tid
    msg["subject_line"] = subject
    msg["preview_text"] = preview
    body = {"data": {"type": "flow-action", "id": action_id,
                     "attributes": {"definition": defn}}}
    r = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                       headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"patch-action-{action_id}.json", {"status": r.status_code, "body": r.text[:2000]})
    if r.status_code != 200:
        raise RuntimeError(f"PATCH flow-action HTTP {r.status_code}: {r.text[:400]}")
    return r.json()["data"]["attributes"]["definition"]["data"]["message"]["template_id"]


def surgical_rewrite(html):
    """Locate the broken cart-iteration block in TuHa4f and replace with our 3-tier body.
    Anchors: 'Hi {{ first_name' (greeting) and 'Return To Your Cart' (button).
    Replace the enclosing <table>...</table>."""
    g = html.find("Hi {{ first_name")
    if g == -1:
        raise RuntimeError("Greeting anchor not found in source")
    btn = re.search(r"Return\s+To\s+Your\s+Cart", html, re.IGNORECASE)
    if not btn:
        raise RuntimeError("Button anchor not found in source")
    open_t = html.rfind("<table", 0, g)
    close_t_rel = html[btn.end():].find("</table>")
    if open_t == -1 or close_t_rel == -1:
        raise RuntimeError("Could not bracket the body block")
    close_t = btn.end() + close_t_rel + len("</table>")
    return html[:open_t] + REPLACEMENT_BODY + html[close_t:]


# Test cases: ($value, expected_phrase_in_render)
TIER_TESTS = [
    (20, "NZ's lowest pharmacy prices"),
    (50, "Free shipping kicks in at $79"),
    (120, "free-shipping tier ($79+)"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    key = load_key()

    print(f"Phase 1: pull source brand template {SOURCE_TEMPLATE_ID}")
    src = get_template_html(SOURCE_TEMPLATE_ID, key)
    save("source.html", src)
    print(f"  source: {len(src)} chars")

    print("\nPhase 2: surgical rewrite (replace broken body, keep brand chrome)")
    new_html = surgical_rewrite(src)
    save("rewritten.html", new_html)
    print(f"  rewritten: {len(new_html)} chars (delta {len(new_html)-len(src):+d})")

    print(f"\nPhase 3: snapshot {OWNED_TEMPLATE_ID} for rollback")
    rollback = get_template_html(OWNED_TEMPLATE_ID, key)
    save("rollback.html", rollback)
    print(f"  saved {len(rollback)} bytes")

    print(f"\nPhase 4: PATCH {OWNED_TEMPLATE_ID} with rewritten HTML (no live impact)")
    patch_template(OWNED_TEMPLATE_ID, new_html, key)

    print("\nPhase 5: render-test all 3 tier paths")
    all_pass = True
    for value, expected in TIER_TESTS:
        rendered = render_test(OWNED_TEMPLATE_ID, value, key)
        if not rendered:
            print(f"  $value={value}: RENDER FAILED")
            all_pass = False
            continue
        save(f"rendered-{value}.html", rendered)
        ok_phrase = expected in rendered
        no_jinja = not re.search(r'\{%[^%]*%\}', rendered)
        no_brokenitem = not re.search(r'\{\{\s*item\.', rendered)
        ok = ok_phrase and no_jinja and no_brokenitem
        all_pass = all_pass and ok
        marker = "PASS" if ok else "FAIL"
        print(f"  $value={value:>3}: {marker}  expected={expected[:35]!r:<40} found={ok_phrase} no-jinja-leftover={no_jinja} no-broken-item={no_brokenitem}")

    if not all_pass:
        print("\n  TIER CHECKS FAILED — rolling back owned template")
        patch_template(OWNED_TEMPLATE_ID, rollback, key)
        return 1

    print("\n  ALL 3 TIER RENDERS PASSED.")

    if not args.apply:
        print("\n  DRY-RUN: rolling back owned template. Re-run with --apply to deploy.")
        patch_template(OWNED_TEMPLATE_ID, rollback, key)
        return 0

    print(f"\nPhase 6: re-assign flow-action {FLOW_ACTION_ID} (force re-clone + update subject/preview)")
    print(f"  subject: {SUBJECT_LINE}")
    print(f"  preview: {PREVIEW_TEXT}")
    new_clone = reassign_flow_action(FLOW_ACTION_ID, OWNED_TEMPLATE_ID, key, SUBJECT_LINE, PREVIEW_TEXT)
    print(f"  OK new clone: {new_clone}")

    time.sleep(1)
    new_html_clone = get_template_html(new_clone, key)
    save(f"new-clone-{new_clone}.html", new_html_clone)

    print(f"\nPhase 7: verify new clone {new_clone}")
    checks = {
        "Has 3-tier elif conditional": "{% elif event|lookup:'$value'" in new_html_clone,
        "Has Tier A trust copy":      "NZ's lowest pharmacy prices" in new_html_clone,
        "Has Tier B gap copy":        "Free shipping kicks in at $79" in new_html_clone,
        "Has Tier C past-tense copy": "free-shipping tier ($79+)" in new_html_clone,
        "Has brand red #FF0031":      "#FF0031" in new_html_clone,
        "Has organization.full_address": "{{ organization.full_address }}" in new_html_clone,
        "Has Always read the label":  "Always read the label" in new_html_clone,
        "Has healthcare professional": "healthcare professional" in new_html_clone,
        "Has unsubscribe":            "{% unsubscribe" in new_html_clone or "unsubscribe" in new_html_clone.lower(),
        "NO broken {{ item.* }}":     not re.search(r'\{\{\s*item\.', new_html_clone),
        "NO Jinja2 |float / |round":  not re.search(r'\|float|\|round\(', new_html_clone),
        "NO since 1984":              "since 1984" not in new_html_clone,
    }
    for k, v in checks.items():
        print(f"  [{'PASS' if v else 'FAIL'}] {k}")

    print(f"\nDone. Re-preview at: https://www.klaviyo.com/flow/VaRyRc/edit")
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
