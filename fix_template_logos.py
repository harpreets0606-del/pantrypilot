"""
Audits every [Z] email template and replaces a wrong/placeholder logo URL
with the correct Bargain Chemist logo URL.

Usage:
    # 1. Dry-run — print which templates need fixing (no changes made)
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_template_logos.py

    # 2. Live fix — pass --fix to actually update the templates
    py fix_template_logos.py --fix

How it works:
  • Fetches all templates whose name starts with "[Z]" (paginated, 10/page).
  • Searches their HTML for any <img> whose src contains a logo-like filename
    (logo, header, brand, bargain).
  • Groups templates by the logo URL they use.
  • Prints a summary so you can confirm which URL is correct.
  • With --fix, replaces every non-canonical logo src with CORRECT_LOGO_URL.

Set CORRECT_LOGO_URL below once you know the right CDN URL.
If left blank the script auto-detects it as the most-common logo URL found.
"""

import os, sys, re, time, json
import requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Override with the known-good logo URL if you already have it.
# Leave as "" to auto-detect from the most common logo found across templates.
CORRECT_LOGO_URL = ""

# Regex: find src="..." or src='...' inside <img> tags that look like logos
LOGO_SRC_RE = re.compile(
    r'<img[^>]+src=["\']([^"\']*(?:logo|header|brand|bargain|chemist)[^"\']*)["\']',
    re.IGNORECASE,
)


def fetch_z_templates() -> list[dict]:
    """Return list of {id, name} for all templates whose name starts with [Z]."""
    templates = []
    url = f"{BASE_URL}/templates"
    params: dict = {
        "filter": "contains(name,'[Z]')",
        "fields[template]": "name",
        "page[size]": 10,
    }
    page = 0
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        for t in data.get("data", []):
            templates.append({"id": t["id"], "name": t["attributes"]["name"]})
        url  = data.get("links", {}).get("next")
        params = {}
        page += 1
        print(f"  fetched page {page} ({len(templates)} templates so far)…", end="\r")
        time.sleep(0.2)
    print()
    return templates


def fetch_html(template_id: str) -> str:
    r = requests.get(
        f"{BASE_URL}/templates/{template_id}",
        headers=HEADERS,
        params={"fields[template]": "html"},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()["data"]["attributes"].get("html", "")


def update_template_html(template_id: str, name: str, html: str) -> None:
    payload = {
        "data": {
            "type": "template",
            "id": template_id,
            "attributes": {"name": name, "html": html},
        }
    }
    r = requests.patch(
        f"{BASE_URL}/templates/{template_id}",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")


def main():
    fix_mode = "--fix" in sys.argv

    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print("Fetching [Z] templates…")
    templates = fetch_z_templates()
    print(f"Found {len(templates)} [Z] templates.\n")

    # ── Step 1: audit logos ────────────────────────────────────────────────────
    logo_map: dict[str, list[str]] = {}   # logo_url → [template names]
    template_logos: dict[str, str | None] = {}  # template_id → logo_url or None

    print("Inspecting template HTML for logo URLs…")
    for t in templates:
        html = fetch_html(t["id"])
        matches = LOGO_SRC_RE.findall(html)
        logo_url = matches[0] if matches else None
        template_logos[t["id"]] = logo_url
        if logo_url:
            logo_map.setdefault(logo_url, []).append(t["name"])
        time.sleep(0.15)

    print()
    print("═" * 70)
    print("LOGO AUDIT RESULTS")
    print("═" * 70)

    if not logo_map:
        print("No logo <img> tags found matching the search pattern.")
        print("Check LOGO_SRC_RE pattern or template HTML structure.")
        return

    # Show logo usage counts
    sorted_logos = sorted(logo_map.items(), key=lambda x: -len(x[1]))
    for url, names in sorted_logos:
        print(f"\n[{len(names)} templates] {url}")
        for n in names:
            print(f"    • {n}")

    # Templates with no logo at all
    missing = [t["name"] for t in templates if template_logos[t["id"]] is None]
    if missing:
        print(f"\n[{len(missing)} templates — NO logo img found]")
        for n in missing:
            print(f"    • {n}")

    # ── Step 2: determine canonical logo ──────────────────────────────────────
    canonical = CORRECT_LOGO_URL or sorted_logos[0][0]
    print(f"\n{'═' * 70}")
    print(f"Canonical logo URL (most common): {canonical}")

    needs_fix = [
        t for t in templates
        if template_logos[t["id"]] is not None
        and template_logos[t["id"]] != canonical
    ]
    print(f"Templates with wrong logo:  {len(needs_fix)}")
    print(f"Templates with no logo img: {len(missing)}")

    if not fix_mode:
        print("\nRun with --fix to update the wrong-logo templates.")
        return

    # ── Step 3: apply fix ─────────────────────────────────────────────────────
    print(f"\nFixing {len(needs_fix)} templates…")
    for t in needs_fix:
        old_url = template_logos[t["id"]]
        print(f"  Patching '{t['name']}'…", end=" ")
        try:
            html = fetch_html(t["id"])
            new_html = html.replace(old_url, canonical)
            update_template_html(t["id"], t["name"], new_html)
            print("✓")
        except Exception as e:
            print(f"✗ {e}")
        time.sleep(0.3)

    print("\nDone.")


if __name__ == "__main__":
    main()
