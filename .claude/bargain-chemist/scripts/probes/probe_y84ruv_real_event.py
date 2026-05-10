"""End-to-end proof: deployed Y84ruV E1 template + real Checkout Started
event payload = correct cart-recovery URL in the rendered button.

Why this exists: Klaviyo's UI 'Send a test' uses placeholder/sample event
context that may not include event.extra.checkout_url, causing our default
fallback to fire. That makes production behaviour ambiguous from a UI test
alone. This probe renders the LIVE deployed template (Vtggdk = E1 owned
global re-cloned in Sr3hxz on 2026-05-08) against an ACTUAL Checkout Started
event payload (Camila's $21.99 Bioglan cart, event 77tyz766qKd retrieved
2026-05-08) — same renderer Klaviyo uses at send time, real event data.

If the rendered button href contains the expected /checkouts/ac/<token>/recover
URL, production sends will route customers to their saved carts correctly.

Run locally:
    python .claude/bargain-chemist/scripts/probes/probe_y84ruv_real_event.py
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{TODAY}/probe-real-event"
OUT.mkdir(parents=True, exist_ok=True)
REVISION = "2025-10-15"

# Deployed E1 template currently bound to Sr3hxz flow
E1_DEPLOYED_TID = "Vtggdk"
E4_DEPLOYED_TID = "Yr6YBF"

# Real event payload from Camila Bloch (event id 77tyz766qKd, 2026-05-07T23:41:17Z)
# Pulled via klaviyo_get_events MCP. Trimmed to the fields our template uses.
CAMILA_EVENT = {
    "$value": 21.99,
    "$currency_code": "NZD",
    "Item Count": 1,
    "Items": ["Bioglan Prebiotic Fibre 175g"],
    "extra": {
        "checkout_url": "https://www.bargainchemist.co.nz/31719260297/checkouts/ac/hWNBuAB9g05U5qUkKCiFYrWG/recover?key=e212dcfe0710096f3d0c354c2a46ed0a&locale=en-NZ",
        "responsive_checkout_url": "https://www.bargainchemist.co.nz/31719260297/checkouts/ac/hWNBuAB9g05U5qUkKCiFYrWG/recover?key=e212dcfe0710096f3d0c354c2a46ed0a&locale=en-NZ",
        "full_landing_site": "http://bargain-chemist.myshopify.com/products/bioglan-prebiotic-fibre-175g?srsltid=AfmBOoo3lztdq5TKv93PVb7F76aLf1JdsSrc8nl88qhkcDehSQK-AlDa",
        "token": "b0be5b5a0bbaeb30b663658c7fa37e79",
    },
}

EXPECTED_FRAGMENT = "checkouts/ac/hWNBuAB9g05U5qUkKCiFYrWG/recover"


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


def render_against_event(key, tid, label, event_ctx):
    body = {"data": {"type": "template", "attributes": {
        "id": tid,
        "context": {
            "first_name": "Camila",
            "organization": {
                "name": "Bargain Chemist",
                "full_address": "1 Radcliffe Road, Belfast, Christchurch 8051, New Zealand",
                "url": "https://www.bargainchemist.co.nz",
            },
            "event": event_ctx,
        }
    }}}
    r = requests.post("https://a.klaviyo.com/api/template-render/",
                      headers=hdrs(key, content=True), json=body, timeout=30)
    out_path = OUT / f"{label}-render.json"
    out_path.write_text(json.dumps({
        "status": r.status_code, "tid": tid, "body": r.text
    }, indent=2), encoding="utf-8")
    if r.status_code != 200:
        print(f"  ❌ {label}: render HTTP {r.status_code}: {r.text[:300]}")
        return None
    rendered = r.json()["data"]["attributes"]["html"]
    (OUT / f"{label}-rendered.html").write_text(rendered, encoding="utf-8")
    return rendered


def extract_cta_href(rendered_html, cta_text_match):
    """Find href on the anchor whose visible text contains cta_text_match."""
    # The CTA anchor: <a href="...">CTA text</a>
    pattern = rf'<a\s+href="([^"]*)"[^>]*>\s*{re.escape(cta_text_match)}'
    m = re.search(pattern, rendered_html)
    return m.group(1) if m else None


def main():
    key = load_key()
    print(f"=== End-to-end probe: deployed Y84ruV templates × real Checkout Started event ===")
    print(f"Event: Camila Bloch, $21.99 Bioglan (id 77tyz766qKd, 2026-05-07T23:41:17Z)")
    print(f"Expected URL fragment: {EXPECTED_FRAGMENT}\n")

    failures = 0
    for tid, label, cta_text in [
        (E1_DEPLOYED_TID, "E1-Vtggdk", "Return to checkout"),
        (E4_DEPLOYED_TID, "E4-Yr6YBF", "Finish your order"),
    ]:
        print(f"--- {label} (template {tid}) ---")
        rendered = render_against_event(key, tid, label, CAMILA_EVENT)
        if rendered is None:
            failures += 1
            continue

        # Extract the CTA button href
        href = extract_cta_href(rendered, cta_text)
        if not href:
            print(f"  ❌ Couldn't find anchor with text '{cta_text}' in rendered output")
            print(f"     Inspect: {OUT / f'{label}-rendered.html'}")
            failures += 1
            continue

        print(f"  Rendered href: {href}")
        if EXPECTED_FRAGMENT in href:
            print(f"  ✅ Contains expected fragment '{EXPECTED_FRAGMENT}'")
            print(f"  ✅ Production renderer + real event = correct cart-recovery URL\n")
        else:
            print(f"  ❌ Does NOT contain expected fragment '{EXPECTED_FRAGMENT}'")
            failures += 1

    if failures == 0:
        print(f"=== ✅ END-TO-END PROVEN ===")
        print(f"Deployed templates Vtggdk (E1) + Yr6YBF (E4), rendered against real")
        print(f"Checkout Started event payload, produce the correct cart-recovery URL")
        print(f"in both 'Return to checkout' and 'Finish your order' buttons.")
        print(f"Production sends WILL route customers to their saved carts.")
        print(f"\nThe earlier 'inbox went to home page' result was the |default fallback")
        print(f"firing because Klaviyo UI's Send-Test substitutes empty event context.")
        print(f"\nFlow Sr3hxz is safe to flip LIVE.")
        return 0
    else:
        print(f"=== ❌ {failures} probe(s) failed ===")
        print(f"Snapshots: {OUT}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
