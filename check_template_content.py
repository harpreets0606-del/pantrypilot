"""
Checks whether the template copies Klaviyo created for the flow messages
actually have HTML content, and if empty, copies the HTML from the
original source templates.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py check_template_content.py            # dry run - shows what needs copying
    py check_template_content.py --apply    # applies the HTML copies
"""

import os, sys, requests, time

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"
APPLY    = "--apply" in sys.argv

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# Flow IDs to check
FLOWS = {
    "UqpyKS": "[Z] Back in Stock",
    "Vvb9ik": "[Z] Post-Purchase Series",
    "XKmyJE": "[Z] Replenishment - Reorder Reminders",
    "U6e3uf": "[Z] Flu Season - Winter Wellness",
    "YdtALs": "[Z] Win-back - Lapsed Customers",
}

# Original source template IDs (the ones we passed during flow creation)
SOURCE_TPL = {
    "[Z] Back in Stock Email 1":                  "UCeqPt",
    "[Z] Back in Stock Email 2":                  "XXcqNf",
    "[Z] Post-Purchase Email 1":                  "RHfcDs",
    "[Z] Post-Purchase Email 2":                  "Sy929J",
    "[Z] Post-Purchase Email 3":                  "UNjrA4",
    "[Z] Post-Purchase Email 4":                  "SQD3nM",
    "[Z] Flu Season Email 1":                     "SMDszN",
    "[Z] Flu Season Email 2":                     "WALe6F",
    "[Z] Win-back Email 1":                       "RDNsnL",
    "[Z] Win-back Email 2":                       "YuYX38",
    "[Z] Win-back Email 3":                       "VEpKb4",
    "[Z] Replenishment Reminder (Regaine)":       "SkCfgY",
    "[Z] Replenishment Reminder (Magnesium)":     "UXVWhK",
    "[Z] Replenishment Reminder (Elevit)":        "UXVWhK",
    "[Z] Replenishment Reminder (Sanderson)":     "UXVWhK",
    "[Z] Replenishment Reminder (GO Healthy)":    "UXVWhK",
    "[Z] Replenishment Reminder (Hayfexo)":       "RyVVZV",
    "[Z] Replenishment Reminder (Clinicians)":    "UXVWhK",
    "[Z] Replenishment Reminder (Goli)":          "UXVWhK",
    "[Z] Replenishment Reminder (LIVON)":         "UXVWhK",
    "[Z] Replenishment Reminder (Ensure)":        "UXVWhK",
    "[Z] Replenishment Reminder (Oracoat)":       "STBhAz",
    "[Z] Replenishment Reminder (Optifast)":      "RFAcvQ",
    "[Z] Replenishment Reminder (Optislim)":      "RFAcvQ",
}


def get_template_html(tpl_id):
    r = requests.get(f"{BASE_URL}/templates/{tpl_id}",
                     headers=HEADERS,
                     params={"fields[template]": "name,html"},
                     timeout=15)
    if not r.ok:
        return None, None
    attrs = r.json()["data"]["attributes"]
    return attrs.get("name", ""), attrs.get("html", "")


def patch_template_html(tpl_id, name, html):
    payload = {"data": {"type": "template", "id": tpl_id,
                        "attributes": {"name": name, "html": html}}}
    r = requests.patch(f"{BASE_URL}/templates/{tpl_id}",
                       headers=HEADERS, json=payload, timeout=30)
    return r.ok, r.status_code


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"Template content check ({mode})\n")

    # Cache source HTML so we don't re-fetch the same source multiple times
    source_html_cache = {}

    to_fix = []

    for flow_id, flow_name in FLOWS.items():
        r = requests.get(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS,
                         params={"additional-fields[flow]": "definition"}, timeout=15)
        if not r.ok:
            print(f"ERROR reading {flow_name}: {r.status_code}")
            continue

        actions = r.json()["data"]["attributes"].get("definition", {}).get("actions", [])
        emails = [a for a in actions if a.get("type") == "send-email"]

        print(f"-- {flow_name} --")
        for a in emails:
            msg     = a.get("data", {}).get("message", {})
            msg_name = msg.get("name", "?")
            copy_id  = msg.get("template_id")
            if not copy_id:
                print(f"  !! {msg_name}: no template_id at all")
                continue

            # Check if the copy has HTML
            copy_name, copy_html = get_template_html(copy_id)
            time.sleep(0.1)

            if copy_html and len(copy_html.strip()) > 100:
                print(f"  OK {msg_name}: copy {copy_id} has content ({len(copy_html)} chars)")
            else:
                src_id = SOURCE_TPL.get(msg_name)
                if not src_id:
                    print(f"  ?? {msg_name}: copy {copy_id} EMPTY - no source template mapped")
                    continue

                # Fetch source HTML (cached)
                if src_id not in source_html_cache:
                    src_name, src_html = get_template_html(src_id)
                    source_html_cache[src_id] = (src_name, src_html)
                    time.sleep(0.1)
                src_name, src_html = source_html_cache[src_id]

                if not src_html or len(src_html.strip()) < 100:
                    print(f"  !! {msg_name}: copy {copy_id} EMPTY, source {src_id} also empty/missing")
                    continue

                print(f"  -> {msg_name}: copy {copy_id} EMPTY, will copy from source {src_id} ({len(src_html)} chars)")
                to_fix.append((msg_name, copy_id, copy_name or msg_name, src_html))

        print()
        time.sleep(0.2)

    print(f"{len(to_fix)} template copies need content copied from source.\n")

    if not to_fix:
        print("Nothing to fix.")
        return

    if not APPLY:
        print("Run with --apply to copy HTML content into the empty template copies.")
        return

    print("Copying HTML content...")
    ok = fail = 0
    for msg_name, copy_id, copy_name, html in to_fix:
        print(f"  Patching {copy_id} ({msg_name})...", end=" ")
        success, status = patch_template_html(copy_id, copy_name, html)
        if success:
            print("OK")
            ok += 1
        else:
            print(f"FAILED (HTTP {status})")
            fail += 1
        time.sleep(0.3)

    print(f"\nDone. {ok} updated, {fail} failed.")


if __name__ == "__main__":
    main()
