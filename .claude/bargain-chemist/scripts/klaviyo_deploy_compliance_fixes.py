"""End-to-end: create owned global templates from fix files, then re-assign each
flow-action so Klaviyo re-clones with the fixed HTML.

For each of the 13 (flow, action, template) tuples:
  1. POST /api/templates/         -> new owned global template (with fixed HTML)
  2. GET  /api/flow-actions/{id}  -> current definition
  3. PATCH /api/flow-actions/{id} -> definition.data.message.template_id swapped
                                     to the new owned template
  4. GET  /api/flow-actions/{id}  -> verify new template_id is now live
  5. GET  /api/templates/{newCloneId} -> spot-check that '1984' is gone

Each step's response is saved to snapshots/<date>/deploy/.

Revision 2025-10-15 throughout.
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
SNAP_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/deploy"
SNAP_DIR.mkdir(parents=True, exist_ok=True)

REVISION = "2025-10-15"

# Verified mapping (flow_id, action_id, current_cloned_template_id, label)
PLAN = [
    ("YdejKf", "105917207", "UpdhCT", "Welcome E1 - Welcome to the Family"),
    ("YdejKf", "105917209", "UVB5U8", "Welcome E2 - Best Sellers"),
    ("YdejKf", "105917211", "XgqKFQ", "Welcome E3 - Last Nudge"),
    ("RPQXaa", "98627502",  "TgFsGf", "Cart E1 - You Forgot Something"),
    ("RPQXaa", "98628345",  "QRewz9", "Cart E2 - Don't Miss Out"),
    ("Ua5LdS", "105926049", "VjuB7J", "Replenishment E1 - Vitamins"),
    ("Ua5LdS", "105926052", "WuTrZA", "Replenishment E2 - Skincare"),
    ("Ua5LdS", "105926055", "U5svSu", "Replenishment E3 - Hair Care"),
    ("Ua5LdS", "105926058", "RDZzKn", "Replenishment E4 - Oral Care"),
    ("Ua5LdS", "105926061", "X3hegP", "Replenishment E5 - Baby & Family"),
    ("Ua5LdS", "105926062", "SPqqDe", "Replenishment E6 - Fallback"),
    ("V9XmEm", "105627868", "YtcgUa", "Flu E2"),
    ("Ysj7sg", "105627854", "W2Sbja", "Back in Stock E1"),
]


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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY not found")


def headers(key):
    return {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
        "Content-Type": "application/vnd.api+json",
    }


def save_resp(name, r):
    out = SNAP_DIR / name
    try:
        out.write_text(json.dumps(r.json(), indent=2))
    except Exception:
        out.write_text(r.text)


def main():
    key = load_key()
    h = headers(key)
    h_get = {k: v for k, v in h.items() if k != "Content-Type"}

    summary = []

    for flow_id, action_id, cloned_id, label in PLAN:
        print(f"\n=== {label}  (flow={flow_id} action={action_id} cloned_tmpl={cloned_id}) ===")

        fix_path = FIXES_DIR / f"{cloned_id}.html"
        if not fix_path.exists():
            print(f"  SKIP — fix file missing: {fix_path}")
            summary.append((label, "skip-no-fix", None))
            continue
        html = fix_path.read_text(encoding="utf-8")

        # --- Phase 2: create new owned global template ---
        post_body = {
            "data": {
                "type": "template",
                "attributes": {
                    "name": f"BC OWNED - {cloned_id} - 1984 fix {date.today():%Y-%m-%d}",
                    "editor_type": "CODE",
                    "html": html,
                },
            }
        }
        r = requests.post("https://a.klaviyo.com/api/templates/", headers=h, json=post_body, timeout=30)
        save_resp(f"{action_id}-01-post-template.json", r)
        if r.status_code != 201:
            print(f"  POST template FAIL HTTP {r.status_code}: {r.text[:200]}")
            summary.append((label, f"post-fail-{r.status_code}", None))
            continue
        new_owned_id = r.json()["data"]["id"]
        print(f"  Created owned template: {new_owned_id}")

        # --- Phase 3: GET current flow-action definition ---
        r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/", headers=h_get, timeout=25)
        save_resp(f"{action_id}-02-get-action.json", r)
        if r.status_code != 200:
            print(f"  GET action FAIL HTTP {r.status_code}: {r.text[:200]}")
            summary.append((label, f"get-action-fail-{r.status_code}", new_owned_id))
            continue
        defn = r.json()["data"]["attributes"]["definition"]
        old_tpl = defn["data"]["message"]["template_id"]
        defn["data"]["message"]["template_id"] = new_owned_id

        # --- PATCH flow-action ---
        patch_body = {
            "data": {
                "type": "flow-action",
                "id": action_id,
                "attributes": {"definition": defn},
            }
        }
        r = requests.patch(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                           headers=h, json=patch_body, timeout=30)
        save_resp(f"{action_id}-03-patch-action.json", r)
        if r.status_code != 200:
            print(f"  PATCH action FAIL HTTP {r.status_code}: {r.text[:300]}")
            summary.append((label, f"patch-fail-{r.status_code}", new_owned_id))
            continue
        new_clone_id = r.json()["data"]["attributes"]["definition"]["data"]["message"]["template_id"]
        print(f"  PATCH OK. old_clone={old_tpl}  ->  new_template_id={new_clone_id}")

        # --- Spot-check: GET the new clone & confirm '1984' is gone ---
        r = requests.get(f"https://a.klaviyo.com/api/templates/{new_clone_id}/", headers=h_get, timeout=20)
        save_resp(f"{action_id}-04-verify-clone.json", r)
        if r.status_code == 200:
            new_html = r.json()["data"]["attributes"]["html"]
            has1984 = "1984" in new_html
            print(f"  verify: 1984={'YES (BAD)' if has1984 else 'no'}")
            summary.append((label, "ok" if not has1984 else "bad-1984-still-there", new_clone_id))
        else:
            print(f"  verify GET HTTP {r.status_code}")
            summary.append((label, f"verify-{r.status_code}", new_clone_id))

        time.sleep(0.4)

    print("\n\n=== SUMMARY ===")
    for label, status, tid in summary:
        print(f"  [{status:<22}] {label}  -> {tid}")
    ok = sum(1 for _, s, _ in summary if s == "ok")
    print(f"\n{ok} / {len(summary)} OK")
    return 0 if ok == len(summary) else 1


if __name__ == "__main__":
    raise SystemExit(main())
