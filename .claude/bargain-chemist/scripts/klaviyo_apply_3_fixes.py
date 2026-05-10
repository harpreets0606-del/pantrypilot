"""Apply three audit-identified fixes via PATCH /api/flow-actions/{id}.

Fix 1: Ysj7sg E2 (action 105627857)  — preview text replaced (drop ASA fear phrases)
Fix 2: YdejKf E3 (action 105917211)  — preview text replaced (drop "since 1984")
Fix 3: V9XmEm E1 (action 105627866)  — re-assign to new owned global template
                                        (SJwrxf rebuilt with full_address in footer)

Saves every GET/POST/PATCH response under snapshots/<date>/deploy-fix3/.
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
FIXES_DIR = REPO / ".claude/bargain-chemist/templates/fixes"
SNAP_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/deploy-fix3"
SNAP_DIR.mkdir(parents=True, exist_ok=True)
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


def save(name, r):
    p = SNAP_DIR / name
    try: p.write_text(json.dumps(r.json(), indent=2))
    except Exception: p.write_text(r.text)


def get_action(action_id, key):
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                     headers=hdrs(key), timeout=25)
    save(f"{action_id}-before.json", r)
    r.raise_for_status()
    return r.json()["data"]["attributes"]["definition"]


def patch_action(action_id, defn, key, label):
    body = {"data": {"type": "flow-action", "id": action_id, "attributes": {"definition": defn}}}
    r = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                       headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"{action_id}-after.json", r)
    if r.status_code != 200:
        print(f"  PATCH {label} FAIL HTTP {r.status_code}: {r.text[:300]}")
        return False
    new_msg = r.json()["data"]["attributes"]["definition"]["data"]["message"]
    print(f"  PATCH {label} OK")
    print(f"    new preview: {(new_msg.get('preview_text') or '')[:80]!r}")
    print(f"    template_id: {new_msg.get('template_id')}")
    return True


def fix1_ysj7sg_e2(key):
    print("\n=== Fix 1: Ysj7sg E2 (105627857) preview text ===")
    aid = "105627857"
    defn = get_action(aid, key)
    msg = defn["data"]["message"]
    print(f"  current subj   : {msg.get('subject_line')!r}")
    print(f"  current preview: {msg.get('preview_text')!r}")
    new_preview = "It's still here when you're ready. Same item, same Bargain Chemist price."
    msg["preview_text"] = new_preview
    print(f"  new preview    : {new_preview!r}")
    return patch_action(aid, defn, key, "Ysj7sg E2 preview")


def fix2_ydejkf_e3(key):
    print("\n=== Fix 2: YdejKf E3 (105917211) preview text ===")
    aid = "105917211"
    defn = get_action(aid, key)
    msg = defn["data"]["message"]
    print(f"  current preview: {msg.get('preview_text')!r}")
    new_preview = "Price beat guarantee, free shipping, trusted Kiwi pharmacy."
    msg["preview_text"] = new_preview
    print(f"  new preview    : {new_preview!r}")
    return patch_action(aid, defn, key, "YdejKf E3 preview")


def fix3_v9xmem_e1(key):
    print("\n=== Fix 3: V9XmEm E1 (105627866) re-assign template (footer fix) ===")
    aid = "105627866"
    fix_path = FIXES_DIR / "SJwrxf.html"
    if not fix_path.exists():
        print(f"  SKIP — fix file missing: {fix_path}")
        return False
    html = fix_path.read_text(encoding="utf-8")
    if "{{ organization.full_address }}" not in html:
        print("  ABORT — fix file missing full_address variable")
        return False

    # Step A: create owned global
    post_body = {
        "data": {
            "type": "template",
            "attributes": {
                "name": f"BC OWNED - SJwrxf - footer fix {date.today():%Y-%m-%d}",
                "editor_type": "CODE",
                "html": html,
            },
        }
    }
    r = requests.post("https://a.klaviyo.com/api/templates/", headers=hdrs(key, content=True),
                      json=post_body, timeout=30)
    save(f"{aid}-01-post-template.json", r)
    if r.status_code != 201:
        print(f"  POST template FAIL HTTP {r.status_code}: {r.text[:300]}")
        return False
    new_owned = r.json()["data"]["id"]
    print(f"  Created owned template: {new_owned}")

    # Step B: PATCH flow-action to re-assign
    defn = get_action(aid, key)
    old_tpl = defn["data"]["message"]["template_id"]
    defn["data"]["message"]["template_id"] = new_owned
    if not patch_action(aid, defn, key, "V9XmEm E1 reassign"):
        return False

    # Step C: verify new clone has full_address
    new_clone = defn["data"]["message"]["template_id"]  # actually this is what we sent; new clone returned in patch response
    # Re-GET action to find the actual new cloned template_id
    defn2 = get_action(aid + "-after-verify", key) if False else None
    # Pull the patch-after response to find the actual cloned id
    after_path = SNAP_DIR / f"{aid}-after.json"
    after = json.loads(after_path.read_text())
    new_clone_id = after["data"]["attributes"]["definition"]["data"]["message"]["template_id"]
    r = requests.get(f"https://a.klaviyo.com/api/templates/{new_clone_id}/",
                     headers=hdrs(key), timeout=20)
    save(f"{aid}-02-verify-clone.json", r)
    if r.status_code == 200:
        new_html = r.json()["data"]["attributes"]["html"]
        ok = "{{ organization.full_address }}" in new_html
        print(f"  verify (new clone {new_clone_id}): full_address present = {ok}")
        return ok
    print(f"  verify GET HTTP {r.status_code}")
    return False


def main():
    key = load_key()
    results = []
    results.append(("Ysj7sg E2 preview", fix1_ysj7sg_e2(key))); time.sleep(0.4)
    results.append(("YdejKf E3 preview", fix2_ydejkf_e3(key))); time.sleep(0.4)
    results.append(("V9XmEm E1 footer", fix3_v9xmem_e1(key)))

    print("\n=== SUMMARY ===")
    for label, ok in results:
        print(f"  {'OK ' if ok else 'FAIL'}  {label}")
    return 0 if all(r[1] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
