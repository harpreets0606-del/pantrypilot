"""Probe: how does Klaviyo Django handle missing / null / empty event properties?

Decides whether Y84ruV templates need defensive `|default:0` wrappers around
$value lookups. If `event|lookup:'$missing'` returns "" (empty string), then
numeric comparisons like `{% if event|lookup:'$missing' < 79 %}` may
silently evaluate as truthy/falsy in unexpected ways.

Run locally:
    python .claude/bargain-chemist/scripts/probes/probe_null_value_handling.py

Snapshots to .claude/bargain-chemist/snapshots/<today>/probe-null/.
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

REPO = Path(__file__).resolve().parents[4]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/probe-null"
OUT.mkdir(parents=True, exist_ok=True)
TID = "UH72Vm"
REVISION = "2025-10-15"

# Each test wraps the lookup in a marker so we can extract the rendered value.
TESTS = [
    # (label, template_body, context.event, what-we-want-to-learn)
    ("present-numeric",
     "MARK[{{ event|lookup:'$value' }}]",
     {"$value": 50},
     "Baseline. Should render MARK[50]."),
    ("missing-bare",
     "MARK[{{ event|lookup:'$value' }}]",
     {},
     "What does lookup return for a missing key? Empty? 'None'?"),
    ("missing-with-default",
     "MARK[{{ event|lookup:'$value'|default:0 }}]",
     {},
     "Does default:0 catch missing? Should render MARK[0]."),
    ("null-explicit",
     "MARK[{{ event|lookup:'$value' }}]",
     {"$value": None},
     "Explicit JSON null."),
    ("null-with-default",
     "MARK[{{ event|lookup:'$value'|default:0 }}]",
     {"$value": None},
     "Does default catch null vs only catch missing?"),
    ("empty-string",
     "MARK[{{ event|lookup:'$value' }}]",
     {"$value": ""},
     "Empty string."),
    ("string-numeric",
     "MARK[{{ event|lookup:'$value' }}]",
     {"$value": "50"},
     "String that looks numeric."),
    ("conditional-missing",
     "MARK[{% if event|lookup:'$value' < 79 %}LOW{% else %}HIGH{% endif %}]",
     {},
     "How does numeric < behave with missing? LOW or HIGH or render-error?"),
    ("conditional-null",
     "MARK[{% if event|lookup:'$value' < 79 %}LOW{% else %}HIGH{% endif %}]",
     {"$value": None},
     "Numeric < with explicit null."),
    ("conditional-string-numeric",
     "MARK[{% if event|lookup:'$value' < 79 %}LOW{% else %}HIGH{% endif %}]",
     {"$value": "50"},
     "Numeric < with string-typed value. Does Django coerce?"),
    ("conditional-defensive-missing",
     "MARK[{% with v=event|lookup:'$value'|default:0 %}{% if v < 79 %}LOW{% else %}HIGH{% endif %}{% endwith %}]",
     {},
     "Does the {% with %} + default:0 defensive pattern recover gracefully?"),
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


def patch_template(key, html):
    body = {"data": {"type": "template", "id": TID,
                     "attributes": {"html": html}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{TID}/",
                       headers=hdrs(key, content=True), json=body, timeout=20)
    r.raise_for_status()


def extract_marker(text):
    import re
    m = re.search(r"MARK\[(.*?)\]", text)
    return m.group(1) if m else None


def main():
    key = load_key()
    r = requests.get(f"https://a.klaviyo.com/api/templates/{TID}/",
                     headers=hdrs(key), timeout=20)
    r.raise_for_status()
    rollback = r.json()["data"]["attributes"]["html"]
    (OUT / "rollback.html").write_text(rollback, encoding="utf-8")

    print(f"Probing null/missing/empty handling — {len(TESTS)} cases\n")

    findings = []
    for label, body_tpl, event_ctx, learn in TESTS:
        full_html = f"<html><body>{body_tpl}</body></html>"
        patch_template(key, full_html)
        time.sleep(0.25)

        body = {"data": {"type": "template", "attributes": {
            "id": TID,
            "context": {
                "first_name": "Sam",
                "organization": {"full_address": "1 Test St"},
                "event": event_ctx,
            }
        }}}
        r = requests.post("https://a.klaviyo.com/api/template-render/",
                          headers=hdrs(key, content=True), json=body, timeout=20)
        rendered = ""
        if r.status_code == 200:
            try:
                rendered = r.json()["data"]["attributes"]["html"]
            except Exception:
                rendered = r.text[:200]
        marker = extract_marker(rendered) if r.status_code == 200 else None

        out = OUT / f"{label}.json"
        out.write_text(json.dumps({
            "status": r.status_code,
            "template": full_html,
            "context_event": event_ctx,
            "rendered": rendered[:500],
            "marker_extracted": marker,
            "what_we_wanted_to_learn": learn,
        }, indent=2), encoding="utf-8")

        marker_disp = repr(marker) if marker is not None else f"HTTP-{r.status_code}"
        print(f"  {label:>32}  marker={marker_disp}")
        findings.append({"label": label, "marker": marker, "http": r.status_code, "learn": learn})

    patch_template(key, rollback)
    print(f"\nRollback applied. Snapshots in {OUT}")

    print("\n=== INTERPRETATION GUIDE ===")
    print("- present-numeric -> MARK[50]   confirms baseline")
    print("- missing-bare    -> MARK[X]    X reveals what lookup returns when key absent")
    print("- conditional-missing -> if 'HIGH' = falls through (Django treats missing as not-less-than)")
    print("                       if 'LOW'  = treats missing as < 79 (treats as 0 or empty < num)")
    print("                       if HTTP 400 = render error, MUST use defensive default")
    print("- conditional-defensive-missing -> 'LOW' is the safe fallback we'd want for prod templates")
    print("\nDecision: if conditional-missing fails or routes wrong -> REQUIRE defensive {% with %}+default:0 in Y84ruV templates.")


if __name__ == "__main__":
    raise SystemExit(main())
