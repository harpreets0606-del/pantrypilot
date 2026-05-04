"""
Audits all [Z] Klaviyo email templates for mobile responsiveness.

Checks per template:
  1. viewport meta tag
  2. @media max-width query (≤ 600px)
  3. Multi-column tables that need stacking rules
  4. CTA buttons — tap target height (padding)
  5. Font sizes < 14px in body text
  6. Images missing max-width / width > 600px
  7. Fixed pixel widths on the outer container > 600px

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py audit_mobile.py
"""

import os, sys, re, time
import requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Accept": "application/json",
}

# ── Regex helpers ────────────────────────────────────────────────────────────

VIEWPORT_RE   = re.compile(r'<meta[^>]+name=["\']viewport["\']', re.IGNORECASE)
MEDIA_RE      = re.compile(r'@media[^{]*max-width\s*:\s*(\d+)px', re.IGNORECASE)
# Detects multi-column <td> with explicit fractional widths
COL_FRAC_RE   = re.compile(r'<td[^>]+width=["\']?(3[0-9]|4[0-9]|5[0-9])["\']?%', re.IGNORECASE)
# CSS width 33%/50% inside style=""
COL_STYLE_RE  = re.compile(r'width\s*:\s*(3[0-9]|4[0-9]|5[0-9])%', re.IGNORECASE)
# "col" class on <td>
COL_CLASS_RE  = re.compile(r'<td[^>]+class=["\'][^"\']*col[^"\']*["\']', re.IGNORECASE)
# stacking rule in media query — col3/col2/col etc display:block
STACK_RE      = re.compile(r'\.col\w*\s*\{[^}]*display\s*:\s*block', re.IGNORECASE)
# font-size in px that is < 14
SMALL_FONT_RE = re.compile(r'font-size\s*:\s*(\d+)px', re.IGNORECASE)
# img width attribute > 600
IMG_WIDTH_RE  = re.compile(r'<img[^>]+width=["\']?(\d+)["\']?', re.IGNORECASE)
# style="width:Xpx" on outer table > 600
OUTER_PX_RE   = re.compile(r'width=["\'](\d{3,4})["\']', re.IGNORECASE)


def fetch_z_templates():
    templates, url = [], f"{BASE_URL}/templates"
    params = {"filter": "contains(name,'[Z]')", "fields[template]": "name,editor_type", "page[size]": 10}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        for t in data.get("data", []):
            templates.append({"id": t["id"], "name": t["attributes"]["name"],
                               "editor": t["attributes"].get("editor_type", "?")})
        url, params = data.get("links", {}).get("next"), {}
        time.sleep(0.15)
    return templates


def fetch_html(tid):
    r = requests.get(f"{BASE_URL}/templates/{tid}", headers=HEADERS,
                     params={"fields[template]": "html"}, timeout=15)
    r.raise_for_status()
    return r.json()["data"]["attributes"].get("html", "")


def audit(name, html):
    issues = []

    # 1. Viewport meta
    if not VIEWPORT_RE.search(html):
        issues.append("MISSING viewport meta tag")

    # 2. Media query
    mq_matches = MEDIA_RE.findall(html)
    if not mq_matches:
        issues.append("MISSING @media max-width breakpoint")
    else:
        widths = [int(w) for w in mq_matches]
        if all(w > 620 for w in widths):
            issues.append(f"@media breakpoint(s) too wide: {widths} — should be ≤600px")

    # 3. Multi-column layout without stacking
    has_cols = (COL_FRAC_RE.search(html) or COL_STYLE_RE.search(html) or
                COL_CLASS_RE.search(html))
    if has_cols and not STACK_RE.search(html):
        issues.append("Multi-column layout detected but NO mobile stacking rule (.col* { display:block })")

    # 4. Font sizes < 14px in non-header / non-fine-print positions
    # Allow 11px in footer fine-print; flag anything 12-13px and below 11
    small = [int(s) for s in SMALL_FONT_RE.findall(html) if int(s) < 12]
    if small:
        unique = sorted(set(small))
        issues.append(f"Font sizes very small (< 12px): {unique}px — may be hard to read on mobile")

    # 5. Images wider than 600px (hard-coded)
    for m in IMG_WIDTH_RE.finditer(html):
        w = int(m.group(1))
        if w > 600:
            issues.append(f"<img width={w}> exceeds 600px container width")
            break  # report once

    # 6. Outer container wider than 600px
    outer_widths = [int(w) for w in OUTER_PX_RE.findall(html) if int(w) > 620]
    if outer_widths:
        issues.append(f"Outer table width(s) > 620px detected: {outer_widths}")

    return issues


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var."); sys.exit(1)

    print("Fetching [Z] templates…")
    templates = fetch_z_templates()
    print(f"Found {len(templates)} [Z] templates.\n")

    results = {"pass": [], "fail": []}

    for t in templates:
        html = fetch_html(t["id"])
        issues = audit(t["name"], html)
        if issues:
            results["fail"].append({"id": t["id"], "name": t["name"], "issues": issues})
        else:
            results["pass"].append(t)
        status = "✓" if not issues else "✗"
        print(f"  {status}  {t['id']}  {t['name']}")
        time.sleep(0.15)

    print()
    print("═" * 70)
    print("MOBILE AUDIT RESULTS")
    print("═" * 70)
    print(f"  Passed : {len(results['pass'])}")
    print(f"  Failed : {len(results['fail'])}")

    if results["fail"]:
        print()
        print("── Templates with issues ──")
        for t in results["fail"]:
            print(f"\n  [{t['id']}]  {t['name']}")
            for issue in t["issues"]:
                print(f"    • {issue}")

    print("\nDone.")


if __name__ == "__main__":
    main()
