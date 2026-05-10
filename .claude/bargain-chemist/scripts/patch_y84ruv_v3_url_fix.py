"""In-place fix for Sr3hxz CTA URL bug — updates owned globals + re-clones
without recreating the flow.

Bug discovered 2026-05-08 in test sends: the deployed templates used
{{ event.extra.full_landing_site }} which is the PRODUCT PAGE the
customer was on before checkout (verified by inspecting 3 real Checkout
Started events via klaviyo_get_events MCP). Cart recovery URL lives at
{{ event.extra.checkout_url }} instead.

This script:
  1. Reads updated cart-recover-e1-w2sbja.html and cart-recover-e4-w2sbja.html
     from .claude/bargain-chemist/templates/ (which build_y84ruv_templates.py
     has already render-validated against the corrected URL field).
  2. PATCHes the 2 owned global templates (RqSXkv = E1, RXgKBJ = E4) with
     the corrected HTML.
  3. GETs flow Sr3hxz with definition + flow-actions to find the 2
     send-email actions and their CURRENT cloned template_ids.
  4. PATCHes each send-email flow-action to re-assign the same owned
     global template_id. This forces Klaviyo to re-clone, picking up
     the latest owned-global HTML.
  5. Verifies the new clones contain `event.extra.checkout_url` (our fix
     marker) and no longer contain `event.extra.full_landing_site` (the
     bug we're removing).

Workflow follows the verified PATCH-flow-actions pattern from the
2026-05-07 1984/ASA fix deploy.

Run locally:
    python .claude/bargain-chemist/scripts/patch_y84ruv_v3_url_fix.py

Snapshots all responses to .claude/bargain-chemist/snapshots/<today>/y84ruv-v3-urlfix/
"""
import json
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/y84ruv-v3-urlfix"
OUT.mkdir(parents=True, exist_ok=True)
TEMPLATES_DIR = REPO / ".claude/bargain-chemist/templates"

FLOW_ID = "Sr3hxz"
E1_OWNED_GLOBAL = "RqSXkv"
E4_OWNED_GLOBAL = "RXgKBJ"
E1_HTML_FILE = TEMPLATES_DIR / "cart-recover-e1-w2sbja.html"
E4_HTML_FILE = TEMPLATES_DIR / "cart-recover-e4-w2sbja.html"

REVISION_GA = "2025-10-15"


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
        "revision": REVISION_GA,
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


def assert_url_fix(html, label):
    """Pre-flight check on the local HTML — confirm we have the fix and not the bug."""
    fail = []
    if "event.extra.full_landing_site" in html:
        fail.append(f"{label}: still contains the BUG marker 'event.extra.full_landing_site'")
    if "event.extra.checkout_url" not in html:
        fail.append(f"{label}: missing the FIX marker 'event.extra.checkout_url'")
    return fail


def patch_owned_global(key, tid, html, label):
    body = {"data": {"type": "template", "id": tid,
                     "attributes": {"html": html}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{tid}/",
                       headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"01-patch-owned-{label}.json",
         {"status": r.status_code, "body": r.text[:3000]})
    if r.status_code != 200:
        sys.exit(f"❌ PATCH owned global {tid} failed HTTP {r.status_code}: {r.text[:300]}")
    print(f"  PATCH owned global {tid} ({label})  HTTP 200")


def get_flow_with_actions(key, fid):
    r = requests.get(
        f"https://a.klaviyo.com/api/flows/{fid}/",
        headers=hdrs(key),
        params={
            "additional-fields[flow]": "definition",
            "include": "flow-actions",
        },
        timeout=30,
    )
    save(f"02-flow-{fid}-snapshot.json", {"status": r.status_code, "body": r.text})
    if r.status_code != 200:
        sys.exit(f"❌ GET flow {fid} failed HTTP {r.status_code}")
    return r.json()


def find_send_email_actions(flow_response):
    """Returns [(action_id, template_id, message_name), ...] for send-email actions."""
    out = []
    for inc in flow_response.get("included", []):
        if inc.get("type") != "flow-action":
            continue
        attrs = inc.get("attributes", {})
        defn = attrs.get("definition", {})
        if defn.get("type") != "send-email":
            continue
        msg = defn.get("data", {}).get("message", {})
        out.append((inc["id"], msg.get("template_id"), msg.get("name", "?")))
    return out


def patch_flow_action_reassign(key, action_id, current_template_id, new_template_id, label):
    """PATCH the flow-action to re-assign the template_id (forces re-clone)."""
    # Need the full action definition to PATCH. Fetch first.
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ GET flow-action {action_id} failed HTTP {r.status_code}")
    action = r.json()["data"]
    defn = action["attributes"]["definition"]
    # Re-assign template_id (Klaviyo will clone fresh from the latest owned-global HTML)
    defn["data"]["message"]["template_id"] = new_template_id

    body = {"data": {"type": "flow-action", "id": action_id,
                     "attributes": {"definition": defn}}}
    rp = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                        headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"03-patch-action-{action_id}-{label}.json",
         {"status": rp.status_code, "body": rp.text[:3000]})
    if rp.status_code != 200:
        sys.exit(f"❌ PATCH flow-action {action_id} failed HTTP {rp.status_code}: {rp.text[:300]}")
    new_clone_id = rp.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")
    print(f"  PATCH action {action_id} ({label})  HTTP 200  new clone={new_clone_id}")
    return new_clone_id


def verify_clone(key, clone_id, label):
    """GET the new cloned template + check the URL fix is in its HTML."""
    r = requests.get(f"https://a.klaviyo.com/api/templates/{clone_id}/",
                     headers=hdrs(key), timeout=30)
    save(f"04-verify-clone-{label}.json", {"status": r.status_code, "body": r.text[:5000]})
    if r.status_code != 200:
        print(f"  ⚠️  GET clone {clone_id} HTTP {r.status_code}")
        return False
    html = r.json()["data"]["attributes"]["html"]
    has_fix = "event.extra.checkout_url" in html
    has_bug = "event.extra.full_landing_site" in html
    if has_fix and not has_bug:
        print(f"  ✅ clone {clone_id} ({label}): fix=present, bug=absent")
        return True
    else:
        print(f"  ❌ clone {clone_id} ({label}): fix={has_fix}, bug={has_bug}")
        return False


def main():
    key = load_key()
    print(f"=== Y84ruV v3 in-place URL fix on flow {FLOW_ID} ===")
    print(f"Snapshots: {OUT}")

    # Pre-flight: load + check local HTML files
    if not (E1_HTML_FILE.exists() and E4_HTML_FILE.exists()):
        sys.exit(f"❌ template HTMLs missing. Run build_y84ruv_templates.py first.")
    e1_html = E1_HTML_FILE.read_text(encoding="utf-8")
    e4_html = E4_HTML_FILE.read_text(encoding="utf-8")
    fails = assert_url_fix(e1_html, "E1") + assert_url_fix(e4_html, "E4")
    if fails:
        print("❌ Pre-flight failed:")
        for f in fails: print(f"   - {f}")
        sys.exit(1)
    print(f"  Pre-flight: E1 + E4 local HTML contain checkout_url, no full_landing_site")

    # Step 1: PATCH owned globals
    print(f"\n=== Step 1: PATCH owned global templates ===")
    patch_owned_global(key, E1_OWNED_GLOBAL, e1_html, "E1")
    patch_owned_global(key, E4_OWNED_GLOBAL, e4_html, "E4")

    # Step 2: GET flow + find send-email actions
    print(f"\n=== Step 2: locate send-email actions in {FLOW_ID} ===")
    flow = get_flow_with_actions(key, FLOW_ID)
    actions = find_send_email_actions(flow)
    print(f"  Found {len(actions)} send-email action(s):")
    for aid, tid, name in actions:
        print(f"    action={aid}  current_template={tid}  name='{name}'")

    if len(actions) != 2:
        sys.exit(f"❌ expected exactly 2 send-email actions, found {len(actions)}")

    # Match action -> owned global by current template_id pattern OR by message name
    # The actions were created in order: Email #1 first, Email #4 second.
    # We can also match by message name (contains 'Email #1' vs 'Email #4').
    e1_action = e4_action = None
    for aid, tid, name in actions:
        if "Email #1" in name or "1h" in name:
            e1_action = (aid, tid)
        elif "Email #4" in name or "24h" in name:
            e4_action = (aid, tid)
    if not (e1_action and e4_action):
        # Fallback: assign in order
        e1_action = (actions[0][0], actions[0][1])
        e4_action = (actions[1][0], actions[1][1])

    # Step 3: PATCH each action to re-assign its owned global -> forces re-clone
    print(f"\n=== Step 3: PATCH flow-actions to re-clone with new HTML ===")
    new_e1_clone = patch_flow_action_reassign(key, e1_action[0], e1_action[1], E1_OWNED_GLOBAL, "E1")
    time.sleep(0.5)
    new_e4_clone = patch_flow_action_reassign(key, e4_action[0], e4_action[1], E4_OWNED_GLOBAL, "E4")
    time.sleep(0.5)

    # Step 4: Verify new clones contain the fix and not the bug
    print(f"\n=== Step 4: verify new clones contain the URL fix ===")
    ok_e1 = verify_clone(key, new_e1_clone, "E1") if new_e1_clone else False
    ok_e4 = verify_clone(key, new_e4_clone, "E4") if new_e4_clone else False

    if ok_e1 and ok_e4:
        print(f"\n=== ✅ URL FIX DEPLOYED to {FLOW_ID} ===")
        print(f"\nNext: re-run test sends from Klaviyo UI flow editor.")
        print(f"  https://www.klaviyo.com/flow/{FLOW_ID}/edit")
        print(f"  Send a test at $value=20, $50, $120 — confirm 'Return to checkout' button")
        print(f"  in the email goes to bargainchemist.co.nz/.../checkouts/ac/<token>/recover")
        print(f"  (NOT to a /products/... URL).")
        return 0
    else:
        print(f"\n❌ Verification failed. See {OUT} for response details.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
