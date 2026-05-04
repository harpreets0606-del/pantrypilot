"""
Fetches and inspects specific [Z] templates — Post-Purchase and Replenishment.
Prints each template's ID, logo status, and editor type so we can diagnose issues.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py inspect_templates.py
"""

import os, sys, re, time, json
import requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Accept": "application/json",
}

LOGO_URL = "https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218"
LOGO_RE  = re.compile(r'<img[^>]+src=["\']([^"\']*logo[^"\']*)["\']', re.IGNORECASE)
ANY_IMG  = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)

KEYWORDS = ["Post-Purchase", "Replenishment"]


def fetch_z_templates():
    templates = []
    url    = f"{BASE_URL}/templates"
    params = {"filter": "contains(name,'[Z]')", "fields[template]": "name,editor_type", "page[size]": 10}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        for t in data.get("data", []):
            templates.append({"id": t["id"], "name": t["attributes"]["name"], "editor": t["attributes"].get("editor_type","?")})
        url    = data.get("links", {}).get("next")
        params = {}
        time.sleep(0.15)
    return templates


def fetch_html(tid):
    r = requests.get(f"{BASE_URL}/templates/{tid}", headers=HEADERS,
                     params={"fields[template]": "html"}, timeout=15)
    r.raise_for_status()
    return r.json()["data"]["attributes"].get("html", "")


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var."); sys.exit(1)

    print("Fetching [Z] templates…")
    all_tpl = fetch_z_templates()

    targets = [t for t in all_tpl if any(k in t["name"] for k in KEYWORDS)]
    print(f"Found {len(targets)} Post-Purchase / Replenishment templates.\n")

    for t in targets:
        html  = fetch_html(t["id"])
        logo  = LOGO_RE.findall(html)
        imgs  = ANY_IMG.findall(html)
        has_logo = any(LOGO_URL in u for u in logo)
        first_img = imgs[0] if imgs else "(none)"

        status = "✓ logo OK" if has_logo else "✗ logo MISSING"
        print(f"[{status}]  {t['id']}  {t['name']}")
        print(f"  editor : {t['editor']}")
        if not has_logo:
            print(f"  first img: {first_img[:100]}")
        time.sleep(0.15)

    print("\nDone.")


if __name__ == "__main__":
    main()
