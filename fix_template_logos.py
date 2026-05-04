"""
Audits and fixes the Bargain Chemist logo across all [Z] email templates.

Usage:
    # 1. Audit — show which templates are missing the logo (no changes)
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_template_logos.py

    # 2. Fix — inject the correct logo into templates that are missing it
    py fix_template_logos.py --fix

    # 3. Delete duplicates — remove the "no logo" copy when a "with logo" copy
    #    of the same name already exists
    py fix_template_logos.py --delete-dupes
"""

import os, sys, re, time
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

CORRECT_LOGO_URL = "https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218"

# Matches any <img src="..."> containing "logo", "brand", "bargain", or "chemist"
LOGO_SRC_RE = re.compile(
    r'<img[^>]+src=["\']([^"\']*(?:logo|header|brand|bargain|chemist)[^"\']*)["\']',
    re.IGNORECASE,
)
# Broader: any shopify CDN <img> at the top of the template (for diagnosis)
ANY_IMG_RE = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)
# background-image in CSS
BG_IMG_RE = re.compile(r'background(?:-image)?\s*:\s*url\(["\']?([^"\')\s]+)["\']?\)', re.IGNORECASE)


def fetch_z_templates() -> list[dict]:
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
        url    = data.get("links", {}).get("next")
        params = {}
        page  += 1
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


def delete_template(template_id: str) -> None:
    r = requests.delete(
        f"{BASE_URL}/templates/{template_id}",
        headers=HEADERS,
        timeout=15,
    )
    if not r.ok and r.status_code != 404:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")


def main():
    fix_mode         = "--fix" in sys.argv
    delete_dupe_mode = "--delete-dupes" in sys.argv

    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print("Fetching [Z] templates…")
    templates = fetch_z_templates()
    print(f"Found {len(templates)} [Z] templates.\n")

    # ── Inspect each template ──────────────────────────────────────────────────
    print("Inspecting template HTML…")
    for t in templates:
        html = t["html"] = fetch_html(t["id"])
        logo_matches = LOGO_SRC_RE.findall(html)
        t["logo_url"] = logo_matches[0] if logo_matches else None
        # For no-logo templates, grab the first <img> src and any background-image
        t["first_img"]  = (ANY_IMG_RE.findall(html) or [None])[0]
        t["bg_img"]     = (BG_IMG_RE.findall(html) or [None])[0]
        time.sleep(0.15)
    print()

    # ── Split into good / missing ──────────────────────────────────────────────
    good    = [t for t in templates if t["logo_url"] == CORRECT_LOGO_URL]
    missing = [t for t in templates if t["logo_url"] != CORRECT_LOGO_URL]

    # Detect duplicates: "missing" templates whose name matches a "good" template
    good_names = {t["name"] for t in good}
    dupes    = [t for t in missing if t["name"] in good_names]
    no_dupe  = [t for t in missing if t["name"] not in good_names]

    print("═" * 70)
    print("LOGO AUDIT")
    print("═" * 70)
    print(f"  Correct logo already:  {len(good)}")
    print(f"  Missing logo total:    {len(missing)}")
    print(f"    └ duplicate of a good copy:  {len(dupes)}  (safe to delete)")
    print(f"    └ no good copy exists:       {len(no_dupe)}  (need logo injected)")

    if dupes:
        print(f"\n── Duplicates (have a same-name copy WITH logo) ──")
        for t in dupes:
            print(f"  {t['id']}  {t['name']}")

    if no_dupe:
        print(f"\n── Unique missing-logo templates ──")
        for t in no_dupe:
            first = t["first_img"] or "(none)"
            bg    = t["bg_img"] or "(none)"
            print(f"  {t['id']}  {t['name']}")
            print(f"    first <img> src : {first[:120]}")
            print(f"    background-image: {bg[:120]}")

    if not fix_mode and not delete_dupe_mode:
        print("\nOptions:")
        print("  --delete-dupes   delete the 'no logo' copy when a good copy already exists")
        print("  --fix            inject the correct logo into templates with no good duplicate")
        return

    # ── Delete duplicates ──────────────────────────────────────────────────────
    if delete_dupe_mode and dupes:
        print(f"\nDeleting {len(dupes)} duplicate no-logo templates…")
        for t in dupes:
            print(f"  Deleting {t['id']}  '{t['name']}'…", end=" ")
            try:
                delete_template(t["id"])
                print("✓")
            except Exception as e:
                print(f"✗ {e}")
            time.sleep(0.3)

    # ── Inject logo into no-dupe missing templates ─────────────────────────────
    if fix_mode and no_dupe:
        # Insert logo as the very first <img> in the template, replacing whatever
        # placeholder is currently in the first img src that looks like a logo slot.
        # Strategy: if the template has ANY <img> near the top whose alt contains
        # "logo" or "bargain", replace its src. Otherwise prepend a logo block.
        print(f"\nFixing {len(no_dupe)} templates with no good duplicate…")
        LOGO_ALT_RE = re.compile(
            r'(<img[^>]+(?:alt=["\'][^"\']*(?:logo|bargain|chemist)[^"\']*["\'])[^>]*src=["\'])([^"\']+)(["\'])',
            re.IGNORECASE,
        )
        LOGO_IMG_BLOCK = (
            f'<img src="{CORRECT_LOGO_URL}" alt="Bargain Chemist" '
            f'width="200" style="display:block;margin:0 auto;" />'
        )
        for t in no_dupe:
            print(f"  Patching '{t['name']}'…", end=" ")
            try:
                html = t["html"]
                new_html, n = LOGO_ALT_RE.subn(
                    lambda m: m.group(1) + CORRECT_LOGO_URL + m.group(3), html
                )
                if n == 0:
                    # No alt-based slot found — replace first <img> src if it's a
                    # shopify CDN image in the first 3000 chars (likely the header)
                    snippet = html[:3000]
                    m = ANY_IMG_RE.search(snippet)
                    if m and "cdn.shopify.com" in m.group(1):
                        new_html = html.replace(m.group(1), CORRECT_LOGO_URL, 1)
                    else:
                        print("⚠ Could not locate logo slot — skipping (fix manually)")
                        continue
                update_template_html(t["id"], t["name"], new_html)
                print("✓")
            except Exception as e:
                print(f"✗ {e}")
            time.sleep(0.3)

    print("\nDone.")


if __name__ == "__main__":
    main()
