"""Deploy browse-recover-w2sbja.html into RtiVC5 (Browse Abandonment) flow.

Workflow:
  1. Pre-flight: read local browse-recover-w2sbja.html, assert required
     markers present + banned phrases absent.
  2. POST new owned global template ('BC OWNED - Browse Recover W2Sbja
     <date>') with the HTML. Captures new template_id.
  3. GET RtiVC5 flow-action 98627563 (the single send-email action) to
     fetch its current definition.
  4. PATCH the action: replace template_id with the new owned global
     ID, replace subject_line and preview_text from the build spec.
     Klaviyo clones the owned global on assign.
  5. Verify the new live clone contains our W2Sbja markers + no fear
     phrases.

Run locally (after build_browse_search_templates.py succeeds):
    python .claude/bargain-chemist/scripts/patch_browse_abandonment_fix.py
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/patch-browse"
OUT.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = REPO / ".claude/bargain-chemist/templates"

FLOW_ID = "RtiVC5"
ACTION_ID = "98627563"  # the single send-email action in RtiVC5
HTML_FILE = TEMPLATES_DIR / "browse-recover-w2sbja.html"
NEW_TEMPLATE_NAME = f"BC OWNED - Browse Recover W2Sbja ({TODAY})"
NEW_SUBJECT = "Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?"
NEW_PREVIEW = "Take another look — Price Beat 10% means you won't find it cheaper."
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
    (OUT / name).write_text(
        payload if isinstance(payload, str) else json.dumps(payload, indent=2),
        encoding="utf-8",
    )


def preflight(html):
    fails = []
    if "popular products don" in html.lower():
        fails.append("FEAR phrase 'popular products don' still present (was meant to be removed)")
    for required in ["$79", "Price Beat", "Always read the label",
                     "{% unsubscribe", "{{ organization.full_address }}",
                     "{{ event.Name", "{{ event.URL"]:
        if required not in html:
            fails.append(f"required marker missing: '{required}'")
    return fails


def main():
    key = load_key()
    print(f"=== Deploying browse-recover to {FLOW_ID} (action {ACTION_ID}) ===")
    print(f"Snapshots: {OUT}")

    if not HTML_FILE.exists():
        sys.exit(f"❌ {HTML_FILE} missing — run build_browse_search_templates.py first")
    html = HTML_FILE.read_text(encoding="utf-8")
    print(f"  Source HTML: {len(html)} bytes")

    print("\n=== Pre-flight ===")
    fails = preflight(html)
    if fails:
        print("❌ pre-flight failed:")
        for f in fails: print(f"   - {f}")
        sys.exit(1)
    print("  ✅ all required markers present, no fear phrase")

    # Step 1: POST new owned global
    print("\n=== Step 1: POST new owned global template ===")
    body = {"data": {"type": "template", "attributes": {
        "name": NEW_TEMPLATE_NAME, "editor_type": "CODE", "html": html,
    }}}
    r = requests.post("https://a.klaviyo.com/api/templates/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    save("01-post-template.json", {"status": r.status_code, "body": r.text[:3000]})
    if r.status_code not in (200, 201):
        sys.exit(f"❌ POST template failed HTTP {r.status_code}\n{r.text[:500]}")
    new_tid = r.json()["data"]["id"]
    print(f"  ✅ new template_id: {new_tid}")

    # Step 2: GET current action definition
    print("\n=== Step 2: GET current flow-action definition ===")
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                     headers=hdrs(key), timeout=30)
    save("02-get-action.json", {"status": r.status_code, "body": r.text[:5000]})
    if r.status_code != 200:
        sys.exit(f"❌ GET flow-action {ACTION_ID} HTTP {r.status_code}")
    action = r.json()["data"]
    defn = action["attributes"]["definition"]
    old_tid = defn["data"]["message"].get("template_id")
    print(f"  current template_id: {old_tid}")
    defn["data"]["message"]["template_id"] = new_tid
    defn["data"]["message"]["subject_line"] = NEW_SUBJECT
    defn["data"]["message"]["preview_text"] = NEW_PREVIEW

    # Step 3: PATCH action
    print("\n=== Step 3: PATCH flow-action with new template + subject + preview ===")
    body = {"data": {"type": "flow-action", "id": ACTION_ID,
                     "attributes": {"definition": defn}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{ACTION_ID}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    save("03-patch-action.json", {"status": rp.status_code, "body": rp.text[:3000]})
    if rp.status_code != 200:
        sys.exit(f"❌ PATCH flow-action HTTP {rp.status_code}\n{rp.text[:500]}")
    new_clone_tid = rp.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
    print(f"  ✅ new clone template_id: {new_clone_tid}")

    # Step 4: Verify new clone
    print("\n=== Step 4: Verify new clone contains W2Sbja markers + no fear ===")
    time.sleep(0.5)
    r = requests.get(f"https://a.klaviyo.com/api/templates/{new_clone_tid}/",
                     headers=hdrs(key), timeout=30)
    save("04-verify-clone.json", {"status": r.status_code, "body": r.text[:5000]})
    if r.status_code != 200:
        print(f"  ⚠️  GET clone {new_clone_tid} HTTP {r.status_code}")
        sys.exit(1)
    clone_html = r.json()["data"]["attributes"]["html"]
    has_w2sbja = "<!-- BC Header: Free Shipping bar -->" in clone_html
    has_fear = "popular products don" in clone_html.lower()
    has_event_name = "{{ event.Name" in clone_html
    print(f"  W2Sbja chrome:        {'✅ present' if has_w2sbja else '❌ MISSING'}")
    print(f"  fear phrase absent:   {'✅' if not has_fear else '❌ STILL PRESENT'}")
    print(f"  event.Name reference: {'✅ present' if has_event_name else '❌ MISSING'}")

    if has_w2sbja and not has_fear and has_event_name:
        print(f"\n=== ✅ BROWSE ABANDONMENT PATCH DEPLOYED ===")
        print(f"Flow:     {FLOW_ID} (status=draft — flip live in Klaviyo UI after test sends)")
        print(f"Action:   {ACTION_ID}")
        print(f"New clone:{new_clone_tid}")
        print(f"\nNext:")
        print(f"  1. Open https://www.klaviyo.com/flow/{FLOW_ID}/edit")
        print(f"  2. Send a test send (use a real Viewed Product event from a recent profile)")
        print(f"  3. Confirm: hero says 'Still thinking about it...', value strip shows $79/Price Beat/30+ stores,")
        print(f"     pharmacist disclaimer present, CTA goes to the product page")
        print(f"  4. Flip RtiVC5 to LIVE via 'Set Live' button")
        return 0
    else:
        print(f"\n❌ Verification failed. See {OUT} for details.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
