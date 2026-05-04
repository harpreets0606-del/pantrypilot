"""
Fixes mobile responsiveness across all [Z] Klaviyo email templates.

Fixes applied:
  1. font-size:9px → font-size:11px in the legal footer (too small on mobile)
  2. Add missing stacking rules for 50% / 48% wide 2-column grids

Run in dry-run mode first (default), then --apply to commit changes.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_mobile.py            # dry run — shows what would change
    py fix_mobile.py --apply    # applies all fixes
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

APPLY = "--apply" in sys.argv

# ── Regex helpers ─────────────────────────────────────────────────────────────

# Matches font-size:9px (only appears in the legal footer)
FONT_9PX_RE = re.compile(r'font-size\s*:\s*9px', re.IGNORECASE)

# Detects <td> with width="50%" or width="48%" (body content, not media query)
COL_50_RE = re.compile(r'<td[^>]+width=["\']48%["\']', re.IGNORECASE)
COL_48_RE = re.compile(r'<td[^>]+width=["\']50%["\']', re.IGNORECASE)
# Also catches style="width:50%" / style="width:48%"
COL_50S_RE = re.compile(r'<td[^>]+style=["\'][^"\']*width\s*:\s*50%', re.IGNORECASE)
COL_48S_RE = re.compile(r'<td[^>]+style=["\'][^"\']*width\s*:\s*48%', re.IGNORECASE)

# Detect whether a 50% or 48% stacking rule already exists in the media query
STACK_50_RE = re.compile(r'td\[width=["\']50%["\'][^\{]*\{[^}]*display\s*:\s*block', re.IGNORECASE)
STACK_48_RE = re.compile(r'td\[width=["\']48%["\'][^\{]*\{[^}]*display\s*:\s*block', re.IGNORECASE)

# Closing brace of the last @media block — we inject before this
MEDIA_CLOSE_RE = re.compile(r'(@media[^{]*\{.*?)(\s*\}(?:\s*</style>|\s*<\/style>))', re.DOTALL | re.IGNORECASE)


def fetch_z_templates():
    templates, url = [], f"{BASE_URL}/templates"
    params = {"filter": "contains(name,'[Z]')", "fields[template]": "name", "page[size]": 10}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        for t in data.get("data", []):
            templates.append({"id": t["id"], "name": t["attributes"]["name"]})
        url, params = data.get("links", {}).get("next"), {}
        time.sleep(0.15)
    return templates


def fetch_html(tid):
    r = requests.get(f"{BASE_URL}/templates/{tid}", headers=HEADERS,
                     params={"fields[template]": "html"}, timeout=15)
    r.raise_for_status()
    return r.json()["data"]["attributes"].get("html", "")


def patch_template(tid, name, html):
    payload = {"data": {"type": "template", "id": tid, "attributes": {"name": name, "html": html}}}
    r = requests.patch(f"{BASE_URL}/templates/{tid}", headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")


def inject_stacking_rules(html, need_50, need_48):
    """
    Injects missing td-width stacking rules into the @media block.
    Finds the closing } of the last @media rule in the <style> block and
    inserts the new rule just before it.
    """
    rules = ""
    if need_50:
        rules += (
            "\n    td[width=\"50%\"] {\n"
            "        display: block !important;\n"
            "        width: 100% !important;\n"
            "        box-sizing: border-box !important\n"
            "        }"
        )
    if need_48:
        rules += (
            "\n    td[width=\"48%\"] {\n"
            "        display: block !important;\n"
            "        width: 100% !important;\n"
            "        box-sizing: border-box !important\n"
            "        }"
        )

    # Strategy: find the last `}` inside the `<style>` block that closes a @media rule
    # We look for the pattern: last occurrence of `}` before `</style>`
    style_close = re.search(r'(</style>)', html, re.IGNORECASE)
    if not style_close:
        return html, False

    # Find the last `}` before </style>
    style_end_pos = style_close.start()
    style_block = html[:style_end_pos]
    last_brace = style_block.rfind("}")
    if last_brace == -1:
        return html, False

    new_html = html[:last_brace] + rules + "\n    " + html[last_brace:]
    return new_html, True


def fix_template(html):
    changes = []
    new_html = html

    # ── Fix 1: font-size:9px → 11px ─────────────────────────────────────────
    count_9px = len(FONT_9PX_RE.findall(new_html))
    if count_9px:
        new_html = FONT_9PX_RE.sub("font-size:11px", new_html)
        changes.append(f"9px→11px font ({count_9px} occurrence{'s' if count_9px>1 else ''})")

    # ── Fix 2: missing 50%/48% stacking rules ────────────────────────────────
    has_col50 = bool(COL_50_RE.search(new_html) or COL_50S_RE.search(new_html))
    has_col48 = bool(COL_50_RE.search(new_html) or COL_48S_RE.search(new_html))

    # Re-detect using correct patterns
    has_col50 = bool(re.search(r'<td[^>]+width=["\']50%["\']', new_html, re.IGNORECASE) or
                     re.search(r'<td[^>]+style=["\'][^"\']*width\s*:\s*50%', new_html, re.IGNORECASE))
    has_col48 = bool(re.search(r'<td[^>]+width=["\']48%["\']', new_html, re.IGNORECASE) or
                     re.search(r'<td[^>]+style=["\'][^"\']*width\s*:\s*48%', new_html, re.IGNORECASE))

    need_50 = has_col50 and not STACK_50_RE.search(new_html)
    need_48 = has_col48 and not STACK_48_RE.search(new_html)

    if need_50 or need_48:
        new_html, ok = inject_stacking_rules(new_html, need_50, need_48)
        if ok:
            parts = []
            if need_50: parts.append("50%-col stacking")
            if need_48: parts.append("48%-col stacking")
            changes.append("added " + " + ".join(parts))

    return new_html, changes


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var."); sys.exit(1)

    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"Mobile fix ({mode}) — fetching [Z] templates…\n")

    templates = fetch_z_templates()
    print(f"Found {len(templates)} [Z] templates.\n")

    to_fix = []

    for t in templates:
        html = fetch_html(t["id"])
        new_html, changes = fix_template(html)
        if changes:
            to_fix.append({"id": t["id"], "name": t["name"], "html": new_html, "changes": changes})
            status = "→ WILL FIX" if not APPLY else "→ FIXING"
            print(f"  {status}  {t['id']}  {t['name']}")
            for c in changes:
                print(f"      • {c}")
        else:
            print(f"  ✓ clean   {t['id']}  {t['name']}")
        time.sleep(0.15)

    print(f"\n{len(to_fix)} template(s) need changes.")

    if not APPLY:
        print("\nRun with --apply to apply all fixes.")
        return

    print("\nApplying fixes…")
    ok_count = 0
    for t in to_fix:
        print(f"  Patching '{t['name']}'…", end=" ")
        try:
            patch_template(t["id"], t["name"], t["html"])
            print("✓")
            ok_count += 1
        except Exception as e:
            print(f"✗ {e}")
        time.sleep(0.3)

    print(f"\nDone. {ok_count}/{len(to_fix)} templates updated.")


if __name__ == "__main__":
    main()
