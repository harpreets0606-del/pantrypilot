"""Patch V9XmEm E1 (SRspqe) — add the standard brand footer.

Issue (verified live 2026-05-08):
  SRspqe ends with a minimal disclaimer + a dark-gray copyright footer that
  references {{ organization.full_address }} but is MISSING the {{ organization.name }}
  macro AND the standard Bargain Chemist red brand footer (social block,
  full ASA red disclaimer, on-brand unsubscribe). The dark navy seasonal
  hero + body content is preserved — that's the deliberate creative choice.

Fix:
  Replace the footer section (from `<!-- DISCLAIMER -->` to closing </body>)
  with the W2Sbja-aligned standard brand footer:
    1. White "Get social with us!" heading
    2. White social icons row (TikTok, Facebook, Instagram, LinkedIn)
    3. Red full ASA legal disclaimer block (price-beat guarantee, label,
       healthcare professional, weight-management caveats)
    4. Red unsubscribe with {% unsubscribe %} + {{ organization.name }}
       {{ organization.full_address }}

Validation:
  - Pre-flight static check: replacement contains all required markers
  - Render-test against realistic flu-flow context via /api/template-render/
  - Verify rendered output has no Liquid leakage and includes both
    organization.name and organization.full_address
  - Atomic: PATCH only writes if every check passes

Run locally:
    py .claude/bargain-chemist/scripts/patch_v9xmem_e1_footer_fix.py
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/patch-v9xmem-e1-footer"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE_ID = "SRspqe"
ACTION_ID = "105627866"
FLOW_ID = "V9XmEm"
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
    h = {"Authorization": f"Klaviyo-API-Key {key}",
         "revision": REVISION,
         "Accept": "application/vnd.api+json"}
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, payload):
    p = OUT / name
    p.write_text(payload if isinstance(payload, str) else json.dumps(payload, indent=2),
                 encoding="utf-8")


# ---------------------------------------------------------------------------
# The replacement footer block (W2Sbja-aligned, standard brand)
# Inserted in place of SRspqe's current `<!-- DISCLAIMER -->` ...end-of-body.
# Includes wrapper closing tags so the HTML stays well-formed.
# ---------------------------------------------------------------------------
NEW_FOOTER = """<!-- Brand Footer: Disclaimer text (white background) -->
<tr>
<td class="mobile-pad" style="padding:24px 40px;background-color:#ffffff">
<p style="font-family:Helvetica,Arial,sans-serif;font-size:12px;color:#999999;line-height:1.6;text-align:center;margin:0;">Always read the label and use as directed. Supplementation should complement, not replace, a balanced diet. If symptoms persist, see your healthcare professional.</p>
</td>
</tr>
<!-- Brand Footer: Get social heading -->
<tr>
<td align="center" style="background-color:#ffffff;padding:18px 18px 6px;">
<p style="font-family:Helvetica,Arial,sans-serif;font-size:22px;font-weight:bold;color:#222222;text-align:center;margin:0;padding:0;">Get social with us!</p>
</td>
</tr>
<!-- Brand Footer: Social icons -->
<tr>
<td align="center" style="background-color:#ffffff;padding:9px 18px 24px;">
<a href="https://tiktok.com/@bargainchemistnz" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="TikTok" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/tiktok_96.png" style="width:40px;display:inline-block;" width="40"/></a>
<a href="https://www.facebook.com/BargainChemist/" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="Facebook" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/facebook_96.png" style="width:40px;display:inline-block;" width="40"/></a>
<a href="https://instagram.com/bargainchemistnz" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="Instagram" src="https://d3k81ch9hvuctc.cloudfront.net/assets/email/buttons/black/instagram_96.png" style="width:40px;display:inline-block;" width="40"/></a>
<a href="https://nz.linkedin.com/company/bargain-chemist" style="text-decoration:none;display:inline-block;margin:0 5px;" target="_blank"><img alt="LinkedIn" src="https://d3k81ch9hvuctc.cloudfront.net/company/XCgiqg/images/791081ec-bce5-4d35-9ee4-aa35ada53088.png" style="width:40px;display:inline-block;" width="40"/></a>
</td>
</tr>
<!-- Brand Footer: Red ASA legal disclaimer -->
<tr>
<td align="center" style="background-color:#FF0031;padding:15px 30px 9px;">
<p style="font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#ffffff;line-height:1.5;text-align:center;margin:0;font-weight:100;">Please note that not all products may be available in all stores, please call your closest Bargain Chemist pharmacy or visit our <a href="https://www.bargainchemist.co.nz/pages/find-a-store" style="color:#ffffff;text-decoration:underline;">store locator</a>. Prices shown are online prices only and may differ to in store. <a href="https://www.bargainchemist.co.nz/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist" style="color:#ffffff;text-decoration:underline;">Price beat guarantee</a> &mdash; if you find a cheaper everyday price on an identical in-stock item at a New Zealand pharmacy we will beat the difference by 10%. *Vitamins and minerals are supplementary to and not a replacement for a balanced diet. Always read the label, use only as directed. If symptoms persist, see your healthcare professional. Weight management products should be used with a balanced diet and exercise.</p>
</td>
</tr>
<!-- Brand Footer: Red unsubscribe with org.name + org.full_address -->
<tr>
<td align="center" style="background-color:#FF0031;padding:8px 18px 22px;">
<p style="font-family:Helvetica,Arial,sans-serif;font-size:11px;color:#ffffff;text-align:center;line-height:1.5;margin:0;font-weight:100;">No longer want to receive these emails? {% unsubscribe 'Unsubscribe' %}.<br/>{{ organization.name }} {{ organization.full_address }}</p>
</td>
</tr>
"""


# ---------------------------------------------------------------------------
# Surgical replacement — locate SRspqe's existing footer span and swap
# ---------------------------------------------------------------------------
START_MARKER = "<!-- DISCLAIMER -->"
# We replace EVERYTHING from START_MARKER through the closing 3 table tags
# before </body>. Anchor on "</body>" to be safe — closing tags before it
# represent the end of the wrapper structure.
END_ANCHOR = "</body>"


def construct_patched_html(original_html):
    si = original_html.find(START_MARKER)
    ei = original_html.find(END_ANCHOR)
    if si < 0:
        sys.exit("❌ DISCLAIMER marker not found in SRspqe — template structure changed?")
    if ei <= si:
        sys.exit("❌ </body> not found after DISCLAIMER marker — template structure unexpected")

    # Capture the closing-tag tail before </body> so we preserve well-formedness
    tail = original_html[si:ei]
    # Count opening + closing table tags in the tail to figure out closures
    closes = tail.count("</table>")
    closing_tail = "</table>\n" * closes + "</td></tr></table>\n"

    head = original_html[:si]
    end = original_html[ei:]
    return head + NEW_FOOTER + closing_tail + end


# ---------------------------------------------------------------------------
# Static + render validation
# ---------------------------------------------------------------------------
REQUIRED_MARKERS = [
    "{% unsubscribe",
    "{{ organization.name }}",
    "{{ organization.full_address }}",
    "Always read the label",
    "see your healthcare professional",
    "Price beat guarantee",
]


def static_check(html):
    fails = []
    for marker in REQUIRED_MARKERS:
        if marker not in html:
            fails.append(f"missing required marker: '{marker}'")
    # Sanity: must still have the seasonal navy hero + flu-season body intact
    if "#1a3a5c" not in html and "1a3a5c" not in html:
        fails.append("seasonal navy hero color #1a3a5c missing — body content lost?")
    if "flu season" not in html:
        fails.append("hero/body content 'flu season' missing — body content lost?")
    return fails


SCRATCH_NAME = "BC PROBE - flu-e1 footer scratch (delete me)"


def render_check(key, candidate_html):
    """Render-test the candidate via Klaviyo /api/template-render/."""
    # Create scratch template with candidate
    body = {"data": {"type": "template", "attributes": {
        "name": SCRATCH_NAME,
        "editor_type": "CODE",
        "html": candidate_html,
    }}}
    rc = requests.post("https://a.klaviyo.com/api/templates/",
                       headers=hdrs(key, content=True), json=body, timeout=30)
    if rc.status_code not in (200, 201):
        return False, [f"scratch creation HTTP {rc.status_code}: {rc.text[:200]}"]
    sid = rc.json()["data"]["id"]
    print(f"  scratch: {sid}")

    diags = []
    try:
        ctx = {
            "person": {"first_name": "Sam"},
            "first_name": "Sam",
            "organization": {
                "name": "Bargain Chemist",
                "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
                "url": "https://www.bargainchemist.co.nz",
            },
            "event": {},
        }
        ctx_body = {"data": {"type": "template", "attributes": {
            "id": sid,
            "context": ctx,
        }}}
        rr = requests.post("https://a.klaviyo.com/api/template-render/",
                           headers=hdrs(key, content=True), json=ctx_body, timeout=30)
        save("render-response.json", {"status": rr.status_code, "body": rr.text[:5000]})
        if rr.status_code != 200:
            return False, [f"render HTTP {rr.status_code}: {rr.text[:200]}"]
        rendered = rr.json()["data"]["attributes"]["html"]
        save("rendered.html", rendered)
        # Liquid leakage check
        if "{%" in rendered or "{{" in rendered:
            m = re.search(r"(\{[%{][^}]{0,80})", rendered)
            diags.append(f"Liquid leakage in render: {m.group(1) if m else '?'}")
        # Required content checks against rendered (post-Liquid resolution)
        if "Bargain Chemist" not in rendered:
            diags.append("organization.name didn't resolve")
        if "1 Radcliffe Road" not in rendered:
            diags.append("organization.full_address didn't resolve")
        if "flu season" not in rendered:
            diags.append("seasonal hero body content missing in render")
        if "Get social with us" not in rendered:
            diags.append("social block missing in render")
    finally:
        # Cleanup scratch
        rd = requests.delete(f"https://a.klaviyo.com/api/templates/{sid}/",
                             headers=hdrs(key), timeout=30)
        print(f"  scratch cleanup: HTTP {rd.status_code} ({sid})")

    return (len(diags) == 0), diags


# ---------------------------------------------------------------------------
# Klaviyo doesn't allow PATCH on cloned templates bound to flow-actions
# (returns 404 "template does not exist" even when GET works). The proven
# pattern is: POST new owned global → PATCH flow-action template_id →
# Klaviyo creates a new clone bound to the action.
# ---------------------------------------------------------------------------
def create_owned_global(key, html):
    body = {"data": {"type": "template", "attributes": {
        "name": f"BC OWNED - V9XmEm E1 footer fix {TODAY}",
        "editor_type": "CODE",
        "html": html,
    }}}
    r = requests.post("https://a.klaviyo.com/api/templates/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    save("create-owned-global-response.json", {"status": r.status_code, "body": r.text[:2000]})
    if r.status_code not in (200, 201):
        sys.exit(f"❌ POST owned global HTTP {r.status_code}\n{r.text[:500]}")
    new_id = r.json()["data"]["id"]
    print(f"  new owned global: {new_id}")
    return new_id


def patch_flow_action(key, new_template_id):
    # Get current flow-action definition
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ GET flow-action {ACTION_ID} HTTP {r.status_code}")
    defn = r.json()["data"]["attributes"]["definition"]
    save("flow-action-before.json", defn)
    old_template_id = defn["data"]["message"].get("template_id")
    print(f"  current cloned template_id: {old_template_id}")

    # Set new template_id (the owned global) — Klaviyo will clone it
    defn["data"]["message"]["template_id"] = new_template_id
    body = {"data": {"type": "flow-action", "id": ACTION_ID,
                     "attributes": {"definition": defn}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    save("flow-action-patch-response.json", {"status": rp.status_code, "body": rp.text[:2000]})
    if rp.status_code != 200:
        sys.exit(f"❌ PATCH flow-action {ACTION_ID} HTTP {rp.status_code}\n{rp.text[:500]}")

    # Klaviyo's PATCH response can return stale (old) template_id due to
    # eventual consistency. Always do a fresh GET 2s later.
    time.sleep(2)
    r2 = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                      headers=hdrs(key), timeout=30)
    new_clone = r2.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
    save("flow-action-after-fresh.json",
         r2.json()["data"]["attributes"]["definition"])
    print(f"  new cloned template_id (fresh GET): {new_clone}")
    return new_clone


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    key = load_key()
    print(f"=== V9XmEm E1 footer fix — atomic in-place PATCH on {TEMPLATE_ID} ===")
    print(f"Snapshots: {OUT}\n")

    print("--- Step 1: Fetch current SRspqe ---")
    rg = requests.get(f"https://a.klaviyo.com/api/templates/{TEMPLATE_ID}/",
                      headers=hdrs(key), timeout=30)
    if rg.status_code != 200:
        sys.exit(f"❌ GET SRspqe HTTP {rg.status_code}: {rg.text[:200]}")
    original_html = rg.json()["data"]["attributes"]["html"]
    save("srspqe-before.html", original_html)
    print(f"  current HTML: {len(original_html)} bytes")

    print("\n--- Step 2: Construct patched HTML (replace footer section) ---")
    candidate_html = construct_patched_html(original_html)
    save("srspqe-candidate.html", candidate_html)
    print(f"  candidate HTML: {len(candidate_html)} bytes "
          f"(delta: {len(candidate_html) - len(original_html):+d})")

    print("\n--- Step 3: Static check ---")
    static_fails = static_check(candidate_html)
    if static_fails:
        print(f"  ❌ static check FAIL ({len(static_fails)}):")
        for f in static_fails:
            print(f"     - {f}")
        sys.exit(1)
    print(f"  ✅ static check PASS — all required markers present, body preserved")

    print("\n--- Step 4: Render-test candidate (via /api/template-render/) ---")
    ok, diags = render_check(key, candidate_html)
    if not ok:
        print(f"  ❌ render-test FAIL ({len(diags)}):")
        for d in diags:
            print(f"     - {d}")
        sys.exit(1)
    print(f"  ✅ render-test PASS — Liquid resolves cleanly, no leakage, all blocks rendered")

    print("\n--- Step 5a: POST new owned-global template with patched HTML ---")
    new_owned_id = create_owned_global(key, candidate_html)

    print("\n--- Step 5b: PATCH flow-action to assign new owned global ---")
    new_clone_id = patch_flow_action(key, new_owned_id)
    if not new_clone_id or new_clone_id == TEMPLATE_ID:
        print(f"  ⚠️  new clone id ({new_clone_id}) equals old or null — Klaviyo eventual-consistency? Retrying after 3s...")
        time.sleep(3)
        r3 = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                          headers=hdrs(key), timeout=30)
        new_clone_id = r3.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
        print(f"  retry result: new clone id = {new_clone_id}")

    print(f"\n--- Step 6: Verify new clone {new_clone_id} contains the fix ---")
    rv = requests.get(f"https://a.klaviyo.com/api/templates/{new_clone_id}/",
                      headers=hdrs(key), timeout=30)
    if rv.status_code != 200:
        sys.exit(f"❌ verify GET HTTP {rv.status_code}")
    after_html = rv.json()["data"]["attributes"]["html"]
    save("new-clone-after.html", after_html)
    has_org_name = "{{ organization.name }}" in after_html
    has_social = "Get social with us!" in after_html
    has_red_disclaimer = "background-color:#FF0031" in after_html and "Price beat guarantee" in after_html
    print(f"  organization.name macro:    {'✅ present' if has_org_name else '❌ missing'}")
    print(f"  social block:               {'✅ present' if has_social else '❌ missing'}")
    print(f"  red ASA disclaimer:         {'✅ present' if has_red_disclaimer else '❌ missing'}")

    if has_org_name and has_social and has_red_disclaimer:
        print(f"\n=== ✅ V9XmEm E1 FOOTER FIX DEPLOYED ===")
        print(f"Flow:           {FLOW_ID} (status=live)")
        print(f"Action:         {ACTION_ID}")
        print(f"Old clone:      {TEMPLATE_ID} (no longer bound)")
        print(f"New owned:      {new_owned_id}")
        print(f"New clone:      {new_clone_id} (now bound to action)")
        print(f"\nNext:")
        print(f"  1. Open https://www.klaviyo.com/flow/{FLOW_ID}/edit")
        print(f"  2. Click Email #1 (Stay well this winter)")
        print(f"  3. Send a test send to confirm visual on desktop + mobile")
        print(f"  4. Confirm: red brand footer with social + ASA disclaimer + unsubscribe")
    else:
        print(f"\n❌ Verification gaps — see snapshots/.../srspqe-after.html")
        sys.exit(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
