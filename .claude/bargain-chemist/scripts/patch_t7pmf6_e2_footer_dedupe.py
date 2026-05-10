"""Patch T7pmf6 E2 (RJhLMj) — remove the duplicate auto-injected UEMA/ASA footer.

Issue (verified live 2026-05-08 via direct GET):
  RJhLMj's HTML has the standard red Bargain Chemist footer (with full ASA
  disclaimer, {% unsubscribe %}, organization.name, organization.full_address)
  AND THEN a SECOND grey footer block appended OUTSIDE the main wrapper, marked
  with `<!-- ── UEMA & ASA Mandatory Footer (auto-injected) ── -->`. This
  duplicate block contains:
    - "Bargain Chemist Limited · 192 Moorhouse Avenue, Christchurch 8011..."
    - "Always read the label and use as directed..." (second time)
    - A SECOND {% unsubscribe 'Unsubscribe' %} link
  Subscribers see two unsubscribe buttons, two addresses, two ASA disclaimers.
  Looks unprofessional and confuses which "unsubscribe" is the real one.

Per CLAUDE.md mandatory verification: live-verified via direct fetch on
2026-05-08; T7pmf6 status=live; action 105721762 binding to RJhLMj confirmed
by audit_live_action_template_map.py walk.

Per mastery-index TOP RULES:
  - Rule 1: Cannot PATCH cloned template directly. Use POST owned + PATCH action.
  - Rule 2: Trust fresh GET, not PATCH response (eventual consistency).
  - Rule 4: Required compliance markers must still be present after removal.

Fix approach:
  1. Fetch RJhLMj live HTML
  2. Identify the auto-injected block: from `<!-- ── UEMA & ASA Mandatory
     Footer (auto-injected) ── -->` through the closing `</table>` of that
     block (it's the LAST table before </body>).
  3. Remove ONLY that block. The standard red footer above it remains intact
     with all required compliance markers.
  4. Static-validate the candidate against audit-rules.json compliance list
  5. Render-test against realistic Win-back context
  6. POST new owned global with patched HTML
  7. PATCH flow-action 105721762 to assign the new owned global
  8. Fresh GET to read new clone ID (handle eventual consistency)
  9. Verify the new clone has 1 unsubscribe link (not 2) and standard footer

Run locally:
    py .claude/bargain-chemist/scripts/patch_t7pmf6_e2_footer_dedupe.py
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
RULES_FILE = REPO / ".claude/bargain-chemist/audit-rules.json"
TODAY = date.today().isoformat()
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/patch-t7pmf6-e2-dedupe"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE_ID = "RJhLMj"
ACTION_ID = "105721762"
FLOW_ID = "T7pmf6"
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


def load_rules():
    """Load audit-rules.json — the canonical source of truth for compliance markers."""
    return json.loads(RULES_FILE.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Surgical removal — locate the auto-injected block and excise it
# ---------------------------------------------------------------------------
START_MARKER = "<!-- ── UEMA & ASA Mandatory Footer (auto-injected) ── -->"
END_ANCHOR = "</body>"


def construct_dedupe_html(original_html):
    si = original_html.find(START_MARKER)
    if si < 0:
        sys.exit(f"❌ Auto-injected marker not found in RJhLMj — has someone already fixed this? "
                 f"Or has Klaviyo changed the marker? Check live HTML before proceeding.")
    ei = original_html.find(END_ANCHOR, si)
    if ei <= si:
        sys.exit(f"❌ </body> not found after auto-injected marker — template structure unexpected.")

    # Everything from START_MARKER up to (but not including) END_ANCHOR is the
    # block to remove. END_ANCHOR (</body>) and beyond stays intact.
    head = original_html[:si]
    end = original_html[ei:]
    # Trim trailing whitespace from head before joining (the removed block
    # may have had leading whitespace that should also go)
    return head.rstrip() + "\n" + end


# ---------------------------------------------------------------------------
# Static validation against audit-rules.json
# ---------------------------------------------------------------------------
def static_check(candidate_html, rules):
    fails = []
    legal = rules["compliance_required_legal"]

    # All hard-required compliance markers must still be present
    for phrase in legal["phrases"]:
        if phrase not in candidate_html:
            fails.append(f"REQUIRED phrase missing: '{phrase}'")
    for macro in legal["liquid_macros"]:
        if macro not in candidate_html:
            fails.append(f"REQUIRED liquid macro missing: '{macro}'")

    # The auto-injected block must be GONE
    if START_MARKER in candidate_html:
        fails.append(f"BANNED block still present: '{START_MARKER}'")

    # Win-back hero copy preservation check
    if "Whenever you're ready" not in candidate_html and "Still Here For You" not in candidate_html:
        fails.append("Win-back hero copy missing — body content may have been over-deleted")

    # No banned phrases introduced
    fear = rules["banned_fear_strict"]["phrases"]
    for phrase in fear:
        if phrase.lower() in candidate_html.lower():
            fails.append(f"BANNED fear phrase present: '{phrase}'")
    coupon = rules["banned_coupons_strict"]["phrases"]
    for phrase in coupon:
        if phrase.lower() in candidate_html.lower():
            fails.append(f"BANNED coupon phrase present: '{phrase}'")

    # Counts: should be exactly 1 {% unsubscribe %} and 1 organization.full_address
    unsub_count = candidate_html.count("{% unsubscribe")
    addr_count = candidate_html.count("{{ organization.full_address }}")
    name_count = candidate_html.count("{{ organization.name }}")
    if unsub_count != 1:
        fails.append(f"Expected exactly 1 unsubscribe macro, got {unsub_count}")
    if addr_count != 1:
        fails.append(f"Expected exactly 1 organization.full_address, got {addr_count}")
    # organization.name should be present at least once
    if name_count < 1:
        fails.append(f"Expected organization.name >= 1, got {name_count}")

    return fails


# ---------------------------------------------------------------------------
# Render-test
# ---------------------------------------------------------------------------
SCRATCH_NAME = "BC PROBE - t7pmf6-e2 dedupe scratch (delete me)"


def render_check(key, candidate_html):
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
            "first_name": "Sam",
            "organization": {
                "name": "Bargain Chemist",
                "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
                "url": "https://www.bargainchemist.co.nz",
                "homepage": "https://www.bargainchemist.co.nz",
            },
            "event": {},
        }
        ctx_body = {"data": {"type": "template", "attributes": {"id": sid, "context": ctx}}}
        rr = requests.post("https://a.klaviyo.com/api/template-render/",
                           headers=hdrs(key, content=True), json=ctx_body, timeout=30)
        save("render-response.json", {"status": rr.status_code, "body": rr.text[:5000]})
        if rr.status_code != 200:
            return False, [f"render HTTP {rr.status_code}: {rr.text[:200]}"]
        rendered = rr.json()["data"]["attributes"]["html"]
        save("rendered.html", rendered)

        if "{%" in rendered or "{{" in rendered:
            m = re.search(r"(\{[%{][^}]{0,80})", rendered)
            diags.append(f"Liquid leakage in render: {m.group(1) if m else '?'}")

        # Critical post-render check: exactly 1 unsubscribe link in rendered HTML
        unsub_links = rendered.lower().count("unsubscribe")
        # Note: "unsubscribe" appears in: link text, link title, alt attribute. Be lenient.
        # The HARD check: count <a href="..."> elements that lead to unsubscribe
        unsub_anchor_count = len(re.findall(r"<a[^>]+href=\"[^\"]*unsubscribe", rendered, re.I))
        if unsub_anchor_count > 1:
            diags.append(f"DUPLICATE unsubscribe links in render: {unsub_anchor_count} found (expected 1)")

        # Body content preservation check
        if "Whenever you're ready" not in rendered and "Still Here For You" not in rendered:
            diags.append("Win-back hero content missing in render")

        # organization macros must resolve
        if "Bargain Chemist" not in rendered:
            diags.append("organization.name didn't resolve")
        if "1 Radcliffe Road" not in rendered:
            diags.append("organization.full_address didn't resolve")
    finally:
        rd = requests.delete(f"https://a.klaviyo.com/api/templates/{sid}/",
                             headers=hdrs(key), timeout=30)
        print(f"  scratch cleanup: HTTP {rd.status_code} ({sid})")
    return (len(diags) == 0), diags


# ---------------------------------------------------------------------------
# Owned global + flow-action assign (proven pattern from V9XmEm)
# ---------------------------------------------------------------------------
def create_owned_global(key, html):
    body = {"data": {"type": "template", "attributes": {
        "name": f"BC OWNED - T7pmf6 E2 dedupe footer fix {TODAY}",
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
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ GET flow-action {ACTION_ID} HTTP {r.status_code}")
    defn = r.json()["data"]["attributes"]["definition"]
    save("flow-action-before.json", defn)
    old_clone = defn["data"]["message"].get("template_id")
    print(f"  current cloned template_id: {old_clone}")

    defn["data"]["message"]["template_id"] = new_template_id
    body = {"data": {"type": "flow-action", "id": ACTION_ID,
                     "attributes": {"definition": defn}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    save("flow-action-patch-response.json", {"status": rp.status_code, "body": rp.text[:2000]})
    if rp.status_code != 200:
        sys.exit(f"❌ PATCH flow-action {ACTION_ID} HTTP {rp.status_code}\n{rp.text[:500]}")

    # Eventual consistency — fresh GET 2s later
    time.sleep(2)
    r2 = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                      headers=hdrs(key), timeout=30)
    new_clone = r2.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
    save("flow-action-after-fresh.json", r2.json()["data"]["attributes"]["definition"])
    print(f"  new cloned template_id (fresh GET): {new_clone}")
    return new_clone


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    key = load_key()
    rules = load_rules()
    print(f"=== T7pmf6 E2 footer dedupe — atomic in-place fix ===")
    print(f"Snapshots: {OUT}")
    print(f"Rules version: {rules['_meta']['version']}\n")

    print("--- Step 1: Fetch current RJhLMj ---")
    rg = requests.get(f"https://a.klaviyo.com/api/templates/{TEMPLATE_ID}/",
                      headers=hdrs(key), timeout=30)
    if rg.status_code != 200:
        sys.exit(f"❌ GET RJhLMj HTTP {rg.status_code}: {rg.text[:200]}")
    original_html = rg.json()["data"]["attributes"]["html"]
    save("rjhlmj-before.html", original_html)
    print(f"  current HTML: {len(original_html)} bytes")

    # Pre-flight diagnostic counts
    print(f"  unsubscribe count BEFORE: {original_html.count('{% unsubscribe')}")
    print(f"  org.full_address BEFORE:  {original_html.count('{{ organization.full_address }}')}")

    print("\n--- Step 2: Construct dedupe HTML (remove auto-injected block) ---")
    candidate_html = construct_dedupe_html(original_html)
    save("rjhlmj-candidate.html", candidate_html)
    print(f"  candidate HTML: {len(candidate_html)} bytes "
          f"(delta: {len(candidate_html) - len(original_html):+d})")
    print(f"  unsubscribe count AFTER:  {candidate_html.count('{% unsubscribe')}")
    print(f"  org.full_address AFTER:   {candidate_html.count('{{ organization.full_address }}')}")

    print("\n--- Step 3: Static check (against audit-rules.json) ---")
    static_fails = static_check(candidate_html, rules)
    if static_fails:
        print(f"  ❌ static check FAIL ({len(static_fails)}):")
        for f in static_fails:
            print(f"     - {f}")
        sys.exit(1)
    print(f"  ✅ static check PASS — required markers preserved, dupe block removed")

    print("\n--- Step 4: Render-test candidate ---")
    ok, diags = render_check(key, candidate_html)
    if not ok:
        print(f"  ❌ render-test FAIL ({len(diags)}):")
        for d in diags:
            print(f"     - {d}")
        sys.exit(1)
    print(f"  ✅ render-test PASS — single unsubscribe in render, body preserved")

    print("\n--- Step 5a: POST new owned-global template ---")
    new_owned_id = create_owned_global(key, candidate_html)

    print("\n--- Step 5b: PATCH flow-action to assign new owned global ---")
    new_clone_id = patch_flow_action(key, new_owned_id)
    if not new_clone_id or new_clone_id == TEMPLATE_ID:
        print(f"  ⚠️  template_id unchanged — retrying after 3s...")
        time.sleep(3)
        r3 = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                          headers=hdrs(key), timeout=30)
        new_clone_id = r3.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
        print(f"  retry: new clone id = {new_clone_id}")

    print(f"\n--- Step 6: Verify new clone {new_clone_id} ---")
    rv = requests.get(f"https://a.klaviyo.com/api/templates/{new_clone_id}/",
                      headers=hdrs(key), timeout=30)
    if rv.status_code != 200:
        sys.exit(f"❌ verify GET HTTP {rv.status_code}")
    after_html = rv.json()["data"]["attributes"]["html"]
    save("new-clone-after.html", after_html)
    after_unsub = after_html.count("{% unsubscribe")
    after_addr = after_html.count("{{ organization.full_address }}")
    has_dupe_marker = START_MARKER in after_html
    has_winback_hero = "Whenever you're ready" in after_html or "Still Here For You" in after_html
    print(f"  unsubscribe count:        {after_unsub} {'✅' if after_unsub == 1 else '❌'}")
    print(f"  org.full_address count:   {after_addr} {'✅' if after_addr == 1 else '❌'}")
    print(f"  auto-injected dupe block: {'❌ STILL PRESENT' if has_dupe_marker else '✅ removed'}")
    print(f"  Win-back hero preserved:  {'✅ present' if has_winback_hero else '❌ missing'}")

    if after_unsub == 1 and after_addr == 1 and not has_dupe_marker and has_winback_hero:
        print(f"\n=== ✅ T7pmf6 E2 FOOTER DEDUPE DEPLOYED ===")
        print(f"Flow:           {FLOW_ID} (status=live)")
        print(f"Action:         {ACTION_ID}")
        print(f"Old clone:      {TEMPLATE_ID} (no longer bound)")
        print(f"New owned:      {new_owned_id}")
        print(f"New clone:      {new_clone_id} (now bound to action)")
        print(f"\nNext:")
        print(f"  1. Open https://www.klaviyo.com/flow/{FLOW_ID}/edit")
        print(f"  2. Click Email #2 ('We're still here for you')")
        print(f"  3. Send a test send and confirm: ONE unsubscribe link, ONE address block")
    else:
        print(f"\n❌ Verification gaps — see {OUT}/new-clone-after.html")
        sys.exit(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
