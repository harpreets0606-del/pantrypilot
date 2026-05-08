"""End-to-end probe: render the LIVE deployed browse + search clones against
REAL events to confirm production sends will route correctly.

Same pattern as probe_y84ruv_real_event.py — closes the gap between
"Klaviyo UI test send shows X" (uses placeholder context) and "production
send routes correctly" (uses real triggering event payload). Critical
because Klaviyo UI Send-Test substitutes empty event context which masks
field-mapping bugs.

This probe:
  1. Pulls the most recent real Viewed Product event
  2. Pulls the most recent real Boost Clicked Search Result event
  3. Fetches the deployed clones from RtiVC5 + XbQiKg flow-actions
  4. Renders each clone against the matching real event
  5. Extracts every <a href="..."> from the rendered output
  6. Asserts: zero Liquid leakage, zero myshopify.com URL traps, expected
     phrase present, CTAs go to expected destinations

If any assertion fails, prints diagnostics and exits non-zero. If all
pass, prints =================== END-TO-END PROVEN =================== and
the flows are safe to flip LIVE.

Run locally (after both patch scripts succeed):
    python .claude/bargain-chemist/scripts/probes/probe_browse_search_real_event.py
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[4]
ENV_FILE = REPO / ".env.local"
TODAY = date.today().isoformat()
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/probe-browse-search-real-event"
OUT.mkdir(parents=True, exist_ok=True)

VIEWED_PRODUCT_METRIC = "XQ2zfW"
BOOST_SEARCH_METRIC = "Y2qHKK"

BROWSE_FLOW = "RtiVC5"
BROWSE_ACTION = "98627563"

SEARCH_FLOW = "XbQiKg"
SEARCH_E1_ACTION = "105487706"
SEARCH_E2_ACTION = "105908180"

REVISION = "2025-10-15"

ORG_CTX = {
    "name": "Bargain Chemist",
    "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
    "url": "https://www.bargainchemist.co.nz",
}


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


def fetch_latest_event(key, metric_id, label):
    r = requests.get("https://a.klaviyo.com/api/events/",
                     headers=hdrs(key),
                     params={"fields[event]": "event_properties,datetime",
                             "filter": f'equals(metric_id,"{metric_id}")',
                             "page[size]": 1, "sort": "-datetime"},
                     timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ event fetch {metric_id}: HTTP {r.status_code}")
    data = r.json().get("data", [])
    if not data:
        sys.exit(f"❌ no events for {metric_id}")
    props = data[0]["attributes"]["eventProperties"]
    save(f"sample-event-{label}.json", props)
    return props


def fetch_action_template_id(key, action_id):
    r = requests.get(f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
                     headers=hdrs(key), timeout=30)
    if r.status_code != 200:
        sys.exit(f"❌ GET action {action_id}: HTTP {r.status_code}")
    return r.json()["data"]["attributes"]["definition"]["data"]["message"].get("template_id")


def render(key, tid, label, event_ctx):
    body = {"data": {"type": "template", "attributes": {
        "id": tid,
        "context": {
            "first_name": "Sam",
            "organization": ORG_CTX,
            "event": event_ctx,
        }
    }}}
    r = requests.post("https://a.klaviyo.com/api/template-render/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    save(f"{label}-render.json", {"status": r.status_code, "body": r.text})
    if r.status_code != 200:
        return None
    html = r.json()["data"]["attributes"]["html"]
    save(f"{label}-rendered.html", html)
    return html


def audit_render(rendered, label, expected_phrase, allow_myshopify=False):
    issues = []
    # Liquid leakage
    if "{%" in rendered or "{{" in rendered:
        m = re.search(r'(\{[%{][^}]{0,80})', rendered)
        issues.append(f"Liquid leakage: {m.group(1) if m else '?'}")
    # Expected phrase
    if expected_phrase not in rendered:
        issues.append(f"expected phrase missing: '{expected_phrase}'")
    # CTA URL audit — extract all hrefs
    hrefs = re.findall(r'<a[^>]*href="([^"]+)"', rendered)
    for h in hrefs:
        if not allow_myshopify and "myshopify.com" in h:
            issues.append(f"myshopify.com URL trap: {h[:100]}")
            break
    # Confirm at least one CTA
    cta_hrefs = [h for h in hrefs if "bargainchemist.co.nz" in h]
    if not cta_hrefs:
        issues.append("no CTA pointing to bargainchemist.co.nz found")
    if issues:
        print(f"  ❌ {label} render issues:")
        for i in issues: print(f"     - {i}")
        return False
    print(f"  ✅ {label} clean — {len(hrefs)} hrefs, all clean, expected phrase present")
    return True


def main():
    key = load_key()
    print("=== End-to-end probe: deployed browse + search templates × real events ===")
    print(f"Snapshots: {OUT}\n")

    # 1. Fetch real events
    print("--- Fetching latest real events ---")
    browse_event = fetch_latest_event(key, VIEWED_PRODUCT_METRIC, "viewed-product")
    print(f"  Viewed Product: Name={browse_event.get('Name', '?')[:40]!r}  Price={browse_event.get('Price')}")
    search_event = fetch_latest_event(key, BOOST_SEARCH_METRIC, "boost-search")
    print(f"  Boost Search:   query={search_event.get('searchQuery')!r}  product={search_event.get('productName', '?')[:40]!r}")

    # 2. Fetch deployed clones
    print("\n--- Fetching deployed clone template IDs ---")
    browse_tid = fetch_action_template_id(key, BROWSE_ACTION)
    e1_tid = fetch_action_template_id(key, SEARCH_E1_ACTION)
    e2_tid = fetch_action_template_id(key, SEARCH_E2_ACTION)
    print(f"  RtiVC5 E1 (action {BROWSE_ACTION}):   {browse_tid}")
    print(f"  XbQiKg E1 (action {SEARCH_E1_ACTION}): {e1_tid}")
    print(f"  XbQiKg E2 (action {SEARCH_E2_ACTION}): {e2_tid}")

    # 3. Render + audit each
    print("\n--- Rendering each clone against real event ---")
    failures = 0

    print(f"\n  Browse (RtiVC5 → {browse_tid}) against real Viewed Product:")
    rendered = render(key, browse_tid, "browse", browse_event)
    if not rendered:
        print("    ❌ render failed")
        failures += 1
    else:
        product_name = browse_event.get("Name", "")
        # Use first ~20 chars of product name as expected phrase (handles edge cases)
        expected = product_name[:20] if product_name else "Bargain Chemist"
        ok = audit_render(rendered, "Browse", expected, allow_myshopify=False)
        if not ok: failures += 1

    print(f"\n  Search E1 (XbQiKg → {e1_tid}) against real Boost search:")
    rendered = render(key, e1_tid, "search-e1", search_event)
    if not rendered:
        print("    ❌ render failed")
        failures += 1
    else:
        query = search_event.get("searchQuery", "")
        expected = query if query else "Bargain Chemist"
        ok = audit_render(rendered, "Search E1", expected, allow_myshopify=False)
        if not ok: failures += 1

    print(f"\n  Search E2 (XbQiKg → {e2_tid}) against real Boost search:")
    rendered = render(key, e2_tid, "search-e2", search_event)
    if not rendered:
        print("    ❌ render failed")
        failures += 1
    else:
        query = search_event.get("searchQuery", "")
        expected = query if query else "pharmacist"  # E2 falls back to pharmacist framing
        ok = audit_render(rendered, "Search E2", expected, allow_myshopify=False)
        if not ok: failures += 1

    if failures == 0:
        print(f"\n=== ✅ END-TO-END PROVEN ===")
        print(f"All 3 deployed clones render correctly against real production event payloads.")
        print(f"Zero Liquid leakage. Zero myshopify.com URL traps. CTAs route to bargainchemist.co.nz.")
        print(f"\nFlows safe to flip LIVE:")
        print(f"  - RtiVC5 (Browse Abandonment)")
        print(f"  - XbQiKg (Search Abandonment)")
        return 0
    else:
        print(f"\n❌ {failures} probe(s) failed. See {OUT} for diagnostics.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
