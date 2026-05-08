"""Deploy search-recover-e1 + e2 templates into XbQiKg (Search Abandonment).

XbQiKg currently has:
  - E1 action 105487706 with template RPZh8V (rebuilding to W2Sbja design)
  - E2 action 105908180 with template_id=None (filling the gap)

Workflow:
  1. Pre-flight: read both local HTMLs, assert markers + no banned phrases
  2. POST 2 new owned global templates (E1 + E2)
  3. GET both flow-action definitions
  4. PATCH each with new template_id + new subject + new preview
  5. Verify both new clones contain W2Sbja chrome and required markers

Run locally (after build_browse_search_templates.py succeeds):
    python .claude/bargain-chemist/scripts/patch_search_abandonment_fix.py
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/patch-search"
OUT.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = REPO / ".claude/bargain-chemist/templates"

FLOW_ID = "XbQiKg"
E1_ACTION = "105487706"
E2_ACTION = "105908180"

E1_HTML_FILE = TEMPLATES_DIR / "search-recover-e1-w2sbja.html"
E2_HTML_FILE = TEMPLATES_DIR / "search-recover-e2-w2sbja.html"

E1_NAME = f"BC OWNED - Search Recover E1 W2Sbja ({TODAY})"
E2_NAME = f"BC OWNED - Search Recover E2 W2Sbja ({TODAY})"

E1_SUBJECT = "{% if event.searchQuery %}Still looking for {{ event.searchQuery }}?{% else %}Found what you were after?{% endif %}"
E1_PREVIEW = "Pick up your search where you left off — Price Beat 10% applies."
E2_SUBJECT = "{% if event.searchQuery %}Still on the hunt for {{ event.searchQuery }}?{% else %}Still looking?{% endif %}"
E2_PREVIEW = "Talk to a pharmacist or pick from our top sellers in this category."

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
         "revision": REVISION, "Accept": "application/vnd.api+json"}
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, payload):
    (OUT / name).write_text(
        payload if isinstance(payload, str) else json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def preflight(html, label):
    fails = []
    for w in ["popular products don", "limited stock", "selling fast"]:
        if w in html.lower(): fails.append(f"{label}: FEAR phrase '{w}'")
    for required in ["$79", "Price Beat", "Always read the label",
                     "{% unsubscribe", "{{ organization.full_address }}",
                     "{{ event.searchQuery"]:
        if required not in html:
            fails.append(f"{label}: required marker missing: '{required}'")
    return fails


def post_template(key, name, html):
    body = {"data": {"type": "template", "attributes": {
        "name": name, "editor_type": "CODE", "html": html,
    }}}
    r = requests.post("https://a.klaviyo.com/api/templates/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    if r.status_code not in (200, 201):
        sys.exit(f"❌ POST template '{name}' HTTP {r.status_code}\n{r.text[:300]}")
    return r.json()["data"]["id"]


def patch_action(key, action_id, new_tid, subject, preview, label):
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ GET action {action_id} HTTP {r.status_code}")
    defn = r.json()["data"]["attributes"]["definition"]
    save(f"action-{action_id}-before.json", defn)
    defn["data"]["message"]["template_id"] = new_tid
    defn["data"]["message"]["subject_line"] = subject
    defn["data"]["message"]["preview_text"] = preview
    body = {"data": {"type": "flow-action", "id": action_id,
                     "attributes": {"definition": defn}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"action-{action_id}-after.json", {"status": rp.status_code, "body": rp.text[:3000]})
    if rp.status_code != 200:
        sys.exit(f"❌ PATCH action {action_id} HTTP {rp.status_code}\n{rp.text[:500]}")
    new_clone = rp.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
    print(f"  ✅ {label} action {action_id} patched; new clone={new_clone}")
    return new_clone


def verify_clone(key, clone_id, label, expect_query_marker=True):
    r = requests.get(f"https://a.klaviyo.com/api/templates/{clone_id}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        print(f"  ❌ GET clone {clone_id} HTTP {r.status_code}")
        return False
    html = r.json()["data"]["attributes"]["html"]
    save(f"verify-{label}-{clone_id}.html", html)
    has_chrome = "<!-- BC Header: Free Shipping bar -->" in html
    has_query = "{{ event.searchQuery" in html
    has_value_strip = "Free shipping over $79" in html
    no_fear = "popular products don" not in html.lower()
    print(f"  {label} ({clone_id}): chrome={'✅' if has_chrome else '❌'} query={'✅' if has_query else '❌'} value_strip={'✅' if has_value_strip else '❌'} no_fear={'✅' if no_fear else '❌'}")
    return has_chrome and has_query and has_value_strip and no_fear


def main():
    key = load_key()
    print(f"=== Deploying search-recover E1+E2 to {FLOW_ID} ===")
    print(f"Snapshots: {OUT}")

    if not (E1_HTML_FILE.exists() and E2_HTML_FILE.exists()):
        sys.exit(f"❌ template HTMLs missing — run build_browse_search_templates.py first")
    e1_html = E1_HTML_FILE.read_text(encoding="utf-8")
    e2_html = E2_HTML_FILE.read_text(encoding="utf-8")
    print(f"  E1: {len(e1_html)} bytes")
    print(f"  E2: {len(e2_html)} bytes")

    print("\n=== Pre-flight ===")
    fails = preflight(e1_html, "E1") + preflight(e2_html, "E2")
    if fails:
        print("❌ pre-flight failed:")
        for f in fails: print(f"   - {f}")
        sys.exit(1)
    print("  ✅ E1 + E2 markers OK, no banned phrases")

    print("\n=== Step 1: POST new owned global templates ===")
    e1_tid = post_template(key, E1_NAME, e1_html)
    print(f"  E1 owned global: {e1_tid}")
    e2_tid = post_template(key, E2_NAME, e2_html)
    print(f"  E2 owned global: {e2_tid}")
    save("template-ids.json", {"e1": e1_tid, "e2": e2_tid})

    print("\n=== Step 2: PATCH flow-actions to assign + set subject/preview ===")
    e1_clone = patch_action(key, E1_ACTION, e1_tid, E1_SUBJECT, E1_PREVIEW, "E1")
    time.sleep(0.5)
    e2_clone = patch_action(key, E2_ACTION, e2_tid, E2_SUBJECT, E2_PREVIEW, "E2")

    print("\n=== Step 3: Verify new clones ===")
    time.sleep(0.5)
    e1_ok = verify_clone(key, e1_clone, "E1")
    e2_ok = verify_clone(key, e2_clone, "E2")

    if e1_ok and e2_ok:
        print(f"\n=== ✅ SEARCH ABANDONMENT PATCH DEPLOYED ===")
        print(f"Flow:     {FLOW_ID} (status=draft — flip live after test sends)")
        print(f"E1 action: {E1_ACTION}, clone {e1_clone}")
        print(f"E2 action: {E2_ACTION}, clone {e2_clone}")
        print(f"\nNext:")
        print(f"  1. Open https://www.klaviyo.com/flow/{FLOW_ID}/edit")
        print(f"  2. Send test sends (use real Boost Clicked Search Result events)")
        print(f"     - Confirm E1 hero shows the search query, CTA goes to /search?q=...")
        print(f"     - Confirm E2 hero is patient framing, CTA dual (search + pharmacist)")
        print(f"  3. Flip XbQiKg to LIVE via 'Set Live' button")
        return 0
    else:
        print(f"\n❌ Verification failed. See {OUT} for details.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
