"""Binary-search-style probe to find which Django syntax Klaviyo's render endpoint accepts.

Tests progressively more complex HTML against POST /api/template-render.
Each test PATCHes UH72Vm with the test HTML, calls render, then rolls back.
First failing test pinpoints the broken syntax.
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
OUT_DIR = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/render-probe"
OUT_DIR.mkdir(parents=True, exist_ok=True)
REVISION = "2025-10-15"
TID = "UH72Vm"


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


TESTS = [
    ("01-bare", "<html><body>plain text</body></html>"),
    ("02-firstname", "<html><body>Hi {{ first_name }}</body></html>"),
    ("03-firstname-default", "<html><body>Hi {{ first_name|default:'there' }}</body></html>"),
    ("04-event-value-dollar", "<html><body>val={{ event.$value }}</body></html>"),
    ("05-event-value-no-dollar", "<html><body>val={{ event.value }}</body></html>"),
    ("06-event-lookup-dollar", "<html><body>val={{ event|lookup:'$value' }}</body></html>"),
    ("07-if-value-dollar", "<html><body>{% if event.$value < 79 %}low{% else %}high{% endif %}</body></html>"),
    ("08-if-value-no-dollar", "<html><body>{% if event.value < 79 %}low{% else %}high{% endif %}</body></html>"),
    ("09-organization-full", "<html><body>{{ organization.full_address }}</body></html>"),
    ("10-unsubscribe-tag", "<html><body>{% unsubscribe 'Click' %}</body></html>"),
    ("11-no-context-event-properties", "<html><body>val={{ event.extra.line_items }}</body></html>"),
    ("12-if-lookup-dollar", "<html><body>{% if event|lookup:'$value' < 79 %}low{% else %}high{% endif %}</body></html>"),
    ("13-with-lookup-dollar", "<html><body>{% with v=event|lookup:'$value' %}{% if v < 79 %}low{% else %}high{% endif %}{% endwith %}</body></html>"),
    ("14-if-only-dollar-context", "<html><body>{% if event.value < 79 %}low{% else %}high{% endif %}</body></html>"),
    ("15-elif-3way", "<html><body>{% if event|lookup:'$value' < 30 %}A{% elif event|lookup:'$value' < 79 %}B{% else %}C{% endif %}</body></html>"),
    ("16-elif-3way-tierB", "<html><body>{% if event|lookup:'$value' < 30 %}A{% elif event|lookup:'$value' < 79 %}B{% else %}C{% endif %}</body></html>"),
    ("17-elif-3way-tierC", "<html><body>{% if event|lookup:'$value' < 30 %}A{% elif event|lookup:'$value' < 79 %}B{% else %}C{% endif %}</body></html>"),
]


def patch_html(html, key):
    body = {"data": {"type": "template", "id": TID, "attributes": {"html": html}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{TID}/",
                       headers=hdrs(key, content=True), json=body, timeout=20)
    r.raise_for_status()


def render(event_value, key, dollar_only=False):
    """If dollar_only=True, context has only '$value' — simulates production where
    only the $-prefixed field exists. Tests if Klaviyo auto-maps it."""
    event = {"$value": event_value, "extra": {"checkout_url": "https://x.test/cart"}}
    if not dollar_only:
        event["value"] = event_value
    body = {"data": {"type": "template", "attributes": {
        "id": TID,
        "context": {
            "first_name": "Sam",
            "organization": {"full_address": "1 Test St, Auckland NZ"},
            "event": event,
        }
    }}}
    return requests.post("https://a.klaviyo.com/api/template-render/",
                         headers=hdrs(key, content=True), json=body, timeout=20)


def main():
    key = load_key()
    # Snapshot current UH72Vm HTML to restore
    r = requests.get(f"https://a.klaviyo.com/api/templates/{TID}/",
                     headers=hdrs(key), timeout=20)
    r.raise_for_status()
    rollback = r.json()["data"]["attributes"]["html"]
    (OUT_DIR / "rollback.html").write_text(rollback, encoding="utf-8")
    print(f"Saved rollback ({len(rollback)} bytes)\n")

    results = []
    for name, html in TESTS:
        try:
            patch_html(html, key)
            time.sleep(0.2)
            # Simulate production-like context (only $value, no plain value)
            dollar_only = name.startswith(("04-", "06-", "07-", "12-", "13-"))
            resp = render(50, key, dollar_only=dollar_only)
            ok = resp.status_code == 200
            (OUT_DIR / f"{name}.json").write_text(
                json.dumps({"status": resp.status_code, "html": html, "body": resp.text[:1500]}, indent=2),
                encoding="utf-8")
            if ok:
                rendered = resp.json()["data"]["attributes"]["html"]
                print(f"  [{name}] PASS  -> {rendered[:100]!r}")
            else:
                err = resp.json().get("errors",[{}])[0].get("detail","?") if resp.text else "?"
                print(f"  [{name}] FAIL HTTP {resp.status_code}: {err[:120]}")
            results.append((name, ok))
        except Exception as e:
            print(f"  [{name}] EXCEPTION: {e}")
            results.append((name, False))

    # Restore
    print("\nRolling back...")
    patch_html(rollback, key)
    print("Restored.")

    print("\n=== SUMMARY ===")
    for n, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {n}")


if __name__ == "__main__":
    main()
