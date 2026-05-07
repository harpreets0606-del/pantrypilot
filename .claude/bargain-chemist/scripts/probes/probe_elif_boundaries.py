"""Probe: cart-value boundary edges for the 3-tier elif conditional.

Closes the gap left by `klaviyo_probe_elif.py`, which only covered mid-tier
values (20, 50, 120). Production cart values can land exactly on the boundary
($30, $79) and we need to know which tier the strict-less-than operator routes
them to. Also probes empty / null / string-typed $value handling.

Pattern under test (verified working at mid-values 2026-05-08):
  {% if event|lookup:'$value' < 30 %}A{% elif event|lookup:'$value' < 79 %}B{% else %}C{% endif %}

Tier expectations (strict-less-than semantics):
  $value < 30           -> A  (small cart)
  30 <= $value < 79     -> B  (gap-actionable)
  $value >= 79          -> C  (free-ship qualified)

Run locally:
    python .claude/bargain-chemist/scripts/probes/probe_elif_boundaries.py

Snapshots results to .claude/bargain-chemist/snapshots/<today>/probe-boundary/.
Idempotent: snapshots+restores the test template each run.
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/probe-boundary"
OUT.mkdir(parents=True, exist_ok=True)
TID = "UH72Vm"  # owned global template the prior probe-elif also used
REVISION = "2025-10-15"

TEMPLATE_BARE = """<html><body>{% if event|lookup:'$value' < 30 %}TIER_A{% elif event|lookup:'$value' < 79 %}TIER_B{% else %}TIER_C{% endif %}</body></html>"""

# Defensive variant — uses |default:0 to handle missing $value gracefully.
TEMPLATE_DEFENSIVE = """<html><body>{% with v=event|lookup:'$value'|default:0 %}{% if v < 30 %}TIER_A{% elif v < 79 %}TIER_B{% else %}TIER_C{% endif %}{% endwith %}</body></html>"""

# Each case: (label, context-event-dict, expected-tier-or-error)
CASES = [
    ("v=0",        {"$value": 0},          "TIER_A"),
    ("v=29",       {"$value": 29},         "TIER_A"),
    ("v=29.99",    {"$value": 29.99},      "TIER_A"),
    ("v=30",       {"$value": 30},         "TIER_B"),  # strict < 30 -> false
    ("v=30.01",    {"$value": 30.01},      "TIER_B"),
    ("v=78.99",    {"$value": 78.99},      "TIER_B"),
    ("v=79",       {"$value": 79},         "TIER_C"),  # strict < 79 -> false
    ("v=79.01",    {"$value": 79.01},      "TIER_C"),
    ("v=120",      {"$value": 120},        "TIER_C"),
    ("v=missing",  {},                     "?"),       # bare-template behaviour TBD
    ("v=str-50",   {"$value": "50"},       "?"),       # string vs numeric — production safety
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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing in .env.local")


def hdrs(key, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def render(key, value_label, context, run_label):
    body = {"data": {"type": "template", "attributes": {
        "id": TID,
        "context": {
            "first_name": "Sam",
            "organization": {"full_address": "1 Test St"},
            "event": context,
        }
    }}}
    r = requests.post("https://a.klaviyo.com/api/template-render/",
                      headers=hdrs(key, content=True), json=body, timeout=20)
    out = OUT / f"{run_label}-{value_label}.json"
    out.write_text(json.dumps({
        "status": r.status_code,
        "context_event": context,
        "body": r.text[:2000],
    }, indent=2), encoding="utf-8")
    return r


def patch_template(key, html):
    body = {"data": {"type": "template", "id": TID,
                     "attributes": {"html": html}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{TID}/",
                       headers=hdrs(key, content=True), json=body, timeout=20)
    r.raise_for_status()


def extract_tier(text):
    for tier in ("TIER_A", "TIER_B", "TIER_C"):
        if tier in text:
            return tier
    return None


def run_against_template(key, html, run_label):
    print(f"\n=== {run_label}: PATCHing template + rendering {len(CASES)} contexts ===")
    patch_template(key, html)
    time.sleep(0.3)

    pass_ct = 0
    fail_ct = 0
    for label, ctx, expected in CASES:
        r = render(key, label, ctx, run_label)
        actual = extract_tier(r.text) if r.status_code == 200 else f"HTTP-{r.status_code}"
        if expected == "?":
            verdict = "📋 noted"
        elif actual == expected:
            verdict = "✅ PASS"
            pass_ct += 1
        else:
            verdict = "❌ FAIL"
            fail_ct += 1
        print(f"  {label:>12}  ctx={str(ctx):<24} expect={expected:<8} actual={str(actual):<10} {verdict}")
    return pass_ct, fail_ct


def main():
    key = load_key()
    # Snapshot rollback so we can restore at end
    r = requests.get(f"https://a.klaviyo.com/api/templates/{TID}/",
                     headers=hdrs(key), timeout=20)
    r.raise_for_status()
    rollback = r.json()["data"]["attributes"]["html"]
    (OUT / "rollback.html").write_text(rollback, encoding="utf-8")
    print(f"Rolled back template snapshotted to {OUT/'rollback.html'} ({len(rollback)} bytes)")

    bare_pass, bare_fail = run_against_template(key, TEMPLATE_BARE, "bare")
    def_pass, def_fail = run_against_template(key, TEMPLATE_DEFENSIVE, "defensive")

    # Restore original template
    patch_template(key, rollback)
    print(f"\nRollback applied. Original template restored.")

    print(f"\n=== SUMMARY ===")
    print(f"Bare pattern:      {bare_pass} pass, {bare_fail} fail")
    print(f"Defensive pattern: {def_pass} pass, {def_fail} fail")
    print(f"Snapshots: {OUT}")
    if bare_fail == 0 and def_fail == 0:
        print("\n✅ All boundary cases routed as expected. Pattern safe to deploy.")
    else:
        print("\n❌ Some boundary cases failed. Review per-context JSON snapshots.")
    return 0 if (bare_fail == 0 and def_fail == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
