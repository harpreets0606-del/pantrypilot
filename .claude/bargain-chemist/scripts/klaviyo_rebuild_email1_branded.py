"""Rebuild Y84ruV-v2 email-1 PRESERVING the original brand design (header, logo,
footer, styling) — only surgically replace the broken cart-iteration block.

Input: existing TuHa4f live HTML (full Bargain Chemist brand)
Output: same HTML but the broken `{{ item.product.title }}` / `{{ item.quantity }}` /
        `{% currency_format ... %}` block replaced with:
          - Greeting paragraph
          - Cart-aware Jinja conditional (verified syntax: event|lookup:'$value')
          - Single "Return To Your Cart" CTA button (existing brand button styling)
        Everything else (header, hero, footer, brand colors) preserved.

Render-tests with both contexts before deploy. Auto-rollback on fail.
Run --apply to keep new HTML and force re-clone.
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
OUT_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/email1-branded"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REVISION = "2025-10-15"
OWNED_TEMPLATE_ID = "UH72Vm"
FLOW_ACTION_ID = "105955340"
SOURCE_TEMPLATE_ID = "TuHa4f"  # The original branded template


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
    save(f"render-value{event_value}.json", {"status": r.status_code, "body": r.text[:3000]})
    if r.status_code not in (200, 201):
        return None
    return r.json()["data"]["attributes"]["html"]


def reassign_flow_action(action_id, owned_tid, key):
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                     headers=hdrs(key), timeout=30)
    r.raise_for_status()
    defn = r.json()["data"]["attributes"]["definition"]
    defn["data"]["message"]["template_id"] = owned_tid
    body = {"data": {"type": "flow-action", "id": action_id,
                     "attributes": {"definition": defn}}}
    r = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                       headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"patch-action-{action_id}.json", {"status": r.status_code, "body": r.text[:2000]})
    if r.status_code != 200:
        raise RuntimeError(f"PATCH flow-action HTTP {r.status_code}: {r.text[:400]}")
    return r.json()["data"]["attributes"]["definition"]["data"]["message"]["template_id"]


# Surgically rewrite the broken cart-iteration block.
# The original block has structure like (paraphrased):
#   <h1>Hi {{ first_name|default:'there' }}</h1>
#   <p>Just a reminder...</p>
#   <table>
#     <tr><td>{{ item.product.title }}</td></tr>
#     <tr><td>Quantity: {{ item.quantity|floatformat:0 }}</td></tr>
#     <tr><td>Total: {% currency_format item.line_price|floatformat:2 %}</td></tr>
#   </table>
#   <a class="btn" href="...cart">Return To Your Cart</a>
#
# We replace the cart-iteration table + greeting with a clean block, KEEPING
# the surrounding header/footer/brand styling.

REPLACEMENT_BODY = """
<!-- BEGIN cart-aware body (rebuilt 2026-05-07) -->
<table border="0" cellpadding="0" cellspacing="0" width="100%">
  <tr>
    <td align="center" style="padding:32px 28px 0 28px;">
      <h1 style="font-family:Helvetica,Arial,sans-serif;font-size:22px;font-weight:700;color:#222;margin:0 0 16px 0;line-height:1.3;">
        Hi {{ first_name|default:'there' }},
      </h1>
      <p style="font-family:Helvetica,Arial,sans-serif;font-size:16px;color:#444;line-height:1.6;margin:0 0 22px 0;">
        Your cart is saved at NZ's lowest pharmacy prices. Pick up where you left off &mdash; everything's ready when you are.
      </p>
    </td>
  </tr>

  <!-- CART-AWARE NUDGE -->
  {% if event|lookup:'$value' < 79 %}
  <tr>
    <td align="center" style="padding:0 28px 22px 28px;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#FFF7E6;border-radius:6px;">
        <tr><td style="padding:18px 24px;text-align:center;">
          <p style="font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#7A4F00;margin:0;">
            <strong>Your cart is under $79</strong> &mdash; add a few more items to unlock FREE shipping at NZ's lowest pharmacy prices.
          </p>
        </td></tr>
      </table>
    </td>
  </tr>
  {% else %}
  <tr>
    <td align="center" style="padding:0 28px 22px 28px;">
      <table border="0" cellpadding="0" cellspacing="0" width="100%" style="background-color:#E8F5E9;border-radius:6px;">
        <tr><td style="padding:18px 24px;text-align:center;">
          <p style="font-family:Helvetica,Arial,sans-serif;font-size:15px;line-height:1.5;color:#1B5E20;margin:0;">
            <strong>Free shipping is yours</strong> &mdash; finish checkout in just a few clicks.
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
        Free shipping over $79  &middot;  Price Beat 10% Guarantee  &middot;  30+ stores nationwide
      </p>
    </td>
  </tr>
</table>
<!-- END cart-aware body -->
"""


def surgical_rewrite(html):
    """Find the broken cart-iteration body and replace with REPLACEMENT_BODY.

    Strategy: locate `Hi {{ first_name` (greeting) and `Return To Your Cart`
    (button). Walk back from greeting to the most recent <table; walk forward
    from button to the next </table>. Replace that whole table with our clean
    branded body. The header (above) and footer (below) stay intact.
    """
    greeting_pos = html.find("Hi {{ first_name")
    if greeting_pos == -1:
        raise RuntimeError("Could not locate 'Hi {{ first_name' anchor in source HTML")
    btn_pos = re.search(r"Return\s+To\s+Your\s+Cart", html, re.IGNORECASE)
    if not btn_pos:
        raise RuntimeError("Could not locate 'Return To Your Cart' anchor")

    # Walk back from greeting to find enclosing <table
    open_table = html.rfind("<table", 0, greeting_pos)
    if open_table == -1:
        raise RuntimeError("No <table> tag found before greeting")

    # Walk forward from button to find closing </table>
    close_table_rel = html[btn_pos.end():].find("</table>")
    if close_table_rel == -1:
        raise RuntimeError("No </table> tag found after button")
    close_table_abs = btn_pos.end() + close_table_rel + len("</table>")

    block_to_replace = html[open_table:close_table_abs]
    print(f"  identified block to replace: {len(block_to_replace)} chars")
    print(f"  starts: {block_to_replace[:80]!r}")
    print(f"  ends:   {block_to_replace[-80:]!r}")

    return html[:open_table] + REPLACEMENT_BODY + html[close_table_abs:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()
    key = load_key()

    print(f"Phase 1: pull source brand template {SOURCE_TEMPLATE_ID}")
    src = get_template_html(SOURCE_TEMPLATE_ID, key)
    save("source.html", src)
    print(f"  source: {len(src)} chars")

    print("\nPhase 2: surgical rewrite (replace cart-iteration block, keep brand chrome)")
    new_html = surgical_rewrite(src)
    save("rewritten.html", new_html)
    print(f"  rewritten: {len(new_html)} chars (delta {len(new_html)-len(src):+d})")

    print(f"\nPhase 3: snapshot {OWNED_TEMPLATE_ID} for rollback")
    rollback = get_template_html(OWNED_TEMPLATE_ID, key)
    save("rollback.html", rollback)
    print(f"  saved {len(rollback)} bytes")

    print(f"\nPhase 4: PATCH {OWNED_TEMPLATE_ID} with rewritten HTML")
    patch_template(OWNED_TEMPLATE_ID, new_html, key)

    print("\nPhase 5: render-test both contexts")
    rendered_low = render_test(OWNED_TEMPLATE_ID, 50, key)
    rendered_high = render_test(OWNED_TEMPLATE_ID, 120, key)
    if rendered_low: save("rendered-50.html", rendered_low)
    if rendered_high: save("rendered-120.html", rendered_high)

    ok_low = rendered_low and "Your cart is under $79" in rendered_low
    ok_high = rendered_high and "Free shipping is yours" in rendered_high
    has_jinja_leftover = (rendered_low and re.search(r'\{%[^%]*%\}', rendered_low)) or \
                         (rendered_high and re.search(r'\{%[^%]*%\}', rendered_high))
    has_unrendered_var = (rendered_low and re.search(r'\{\{ item\.', rendered_low)) or \
                         (rendered_high and re.search(r'\{\{ item\.', rendered_high))

    print(f"  value=50  under-$79 copy: {ok_low}")
    print(f"  value=120 over-$79 copy:  {ok_high}")
    print(f"  Leftover {{% %}} blocks:  {bool(has_jinja_leftover)}")
    print(f"  Leftover {{{{ item.* }}}} (broken iteration): {bool(has_unrendered_var)}")

    if not (ok_low and ok_high) or has_jinja_leftover or has_unrendered_var:
        print("\n  Render checks FAILED — rolling back")
        patch_template(OWNED_TEMPLATE_ID, rollback, key)
        return 1

    print("\n  ALL CHECKS PASSED.")

    if not args.apply:
        print("\n  DRY-RUN: rolling back. Re-run with --apply to deploy.")
        patch_template(OWNED_TEMPLATE_ID, rollback, key)
        return 0

    print(f"\nPhase 6: re-assign flow-action {FLOW_ACTION_ID} (force re-clone)")
    new_clone_id = reassign_flow_action(FLOW_ACTION_ID, OWNED_TEMPLATE_ID, key)
    print(f"  OK new clone: {new_clone_id}")

    time.sleep(1)
    new_clone_html = get_template_html(new_clone_id, key)
    save(f"new-clone-{new_clone_id}.html", new_clone_html)
    has_old_loop = bool(re.search(r'\{\{\s*item\.', new_clone_html))
    print(f"  new clone {new_clone_id}: {len(new_clone_html)} chars, "
          f"has_old_for_item_iteration={has_old_loop}")

    print(f"\nDone. Re-preview at: https://www.klaviyo.com/flow/VaRyRc/edit")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
