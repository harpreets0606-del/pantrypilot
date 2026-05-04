"""
Final comprehensive rebuild of all 5 [Z] flows.

Fixes from audit:
  - Adds preview text to all 22 email actions (was empty on all)
  - Subject line audit was false-positive (template tags inflate raw length;
    rendered subjects are all within 60 chars)
  - Adds FLASH Eyelash Serum, Razene, Omeprazole to replenishment
    (top-volume products missing from the flow)

Preserves everything correct:
  - All conditions (profile-metric format, confirmed working)
  - All template IDs
  - All delays, triggers, split routing

Flow IDs are auto-discovered by name so you don't need to hard-code them.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py fix_all_flows.py           # dry run - prints payloads, makes no changes
    py fix_all_flows.py --apply   # deletes existing [Z] flows and recreates
"""

import os, sys, json, time, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"
APPLY    = "--apply" in sys.argv

FROM_EMAIL = "hello@bargainchemist.co.nz"
FROM_LABEL = "Bargain Chemist"
REPLY_TO   = "orders@bargainchemist.co.nz"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

ALL_DAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

PLACED_ORDER_METRIC_ID  = "Sxnb5T"   # Placed Order
REPLENISHMENT_METRIC_ID = "UWP7cZ"   # Placed Order (replenishment trigger)
BACK_IN_STOCK_METRIC_ID = "USbQRB"   # Back In Stock
WINBACK_SEGMENT_ID      = "Srd5Qr"
FLU_SEASON_SEGMENT_ID   = "VGQby3"


# ── Template map ───────────────────────────────────────────────────────────────

TPL = {
    "[Z] Back in Stock Email 1":            "UCeqPt",
    "[Z] Back in Stock Email 2":            "XXcqNf",
    "[Z] Post-Purchase Email 1":            "RHfcDs",
    "[Z] Post-Purchase Email 2":            "Sy929J",
    "[Z] Post-Purchase Email 3":            "UNjrA4",
    "[Z] Post-Purchase Email 4":            "SQD3nM",
    "[Z] Flu Season Email 1":               "SMDszN",
    "[Z] Flu Season Email 2":               "WALe6F",
    "[Z] Win-back Email 1":                 "RDNsnL",
    "[Z] Win-back Email 2":                 "YuYX38",
    "[Z] Win-back Email 3":                 "VEpKb4",
    # Replenishment — generic fallback
    "[Z] Replenishment Reminder":           "UXVWhK",
    # Replenishment — product-specific
    "[Z] Replenishment Reminder (Regaine)":   "SkCfgY",
    "[Z] Replenishment Reminder (Magnesium)": "UXVWhK",
    "[Z] Replenishment Reminder (Elevit)":    "UXVWhK",
    "[Z] Replenishment Reminder (Sanderson)": "UXVWhK",
    "[Z] Replenishment Reminder (GO Healthy)":"UXVWhK",
    "[Z] Replenishment Reminder (Hayfexo)":   "RyVVZV",
    "[Z] Replenishment Reminder (FLASH)":     "UXVWhK",
    "[Z] Replenishment Reminder (Clinicians)":"UXVWhK",
    "[Z] Replenishment Reminder (Goli)":      "UXVWhK",
    "[Z] Replenishment Reminder (LIVON)":     "UXVWhK",
    "[Z] Replenishment Reminder (Razene)":    "UXVWhK",
    "[Z] Replenishment Reminder (Omeprazole)":"UXVWhK",
    "[Z] Replenishment Reminder (Ensure)":    "UXVWhK",
    "[Z] Replenishment Reminder (Oracoat)":   "STBhAz",
    "[Z] Replenishment Reminder (Optifast)":  "RFAcvQ",
    "[Z] Replenishment Reminder (Optislim)":  "RFAcvQ",
}

# Preview texts (genuine fix — were empty across all 22 emails)
PREVIEW = {
    "[Z] Back in Stock Email 1":
        "Great news - it's back in stock. Grab yours before it sells out again.",
    "[Z] Back in Stock Email 2":
        "Limited stock remaining. Don't miss your chance to grab one.",
    "[Z] Post-Purchase Email 1":
        "Your order is confirmed and being prepared. Here's what happens next.",
    "[Z] Post-Purchase Email 2":
        "Get the best results - tips from our pharmacists on your recent purchase.",
    "[Z] Post-Purchase Email 3":
        "Customers who bought similar products also loved these picks.",
    "[Z] Post-Purchase Email 4":
        "It only takes 30 seconds. Your feedback helps us serve you better.",
    "[Z] Flu Season Email 1":
        "Your guide to staying healthy and protected this flu season.",
    "[Z] Flu Season Email 2":
        "Flu vaccines are one of the best ways to protect yourself and family.",
    "[Z] Win-back Email 1":
        "It's been a while. Here's what's new at Bargain Chemist since your last visit.",
    "[Z] Win-back Email 2":
        "We've saved something special for you. Come back and see what's changed.",
    "[Z] Win-back Email 3":
        "This is our final message. We hope to see you again soon.",
}

REPLENISHMENT_PREVIEW = (
    "Running low? It might be time to restock. Order today and never run out."
)


# ── Filter builders ────────────────────────────────────────────────────────────

def placed_order_filter(min_count: int) -> dict:
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "profile-metric",
                "metric_id": PLACED_ORDER_METRIC_ID,
                "measurement": "count",
                "measurement_filter": {
                    "type": "numeric",
                    "operator": "greater-than",
                    "value": min_count - 1,
                },
                "timeframe_filter": {
                    "type": "date",
                    "operator": "flow-start",
                },
                "metric_filters": None,
            }]
        }]
    }


def replenishment_filter(keyword: str) -> dict:
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "profile-metric",
                "metric_id": REPLENISHMENT_METRIC_ID,
                "measurement": "count",
                "measurement_filter": {
                    "type": "numeric",
                    "operator": "greater-than",
                    "value": 0,
                },
                "timeframe_filter": {
                    "type": "date",
                    "operator": "flow-start",
                },
                "metric_filters": [{
                    "property": "Item Names",
                    "filter": {
                        "type": "string",
                        "operator": "contains",
                        "value": keyword,
                    },
                }],
            }]
        }]
    }


# ── ID counter ─────────────────────────────────────────────────────────────────

_counter = 0

def new_id() -> str:
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0


# ── Action builders ────────────────────────────────────────────────────────────

def email_action(subject: str, template_id, name: str, preview: str = "") -> dict:
    msg = {
        "from_email": FROM_EMAIL,
        "from_label": FROM_LABEL,
        "reply_to_email": REPLY_TO,
        "cc_email": None,
        "bcc_email": None,
        "subject_line": subject,
        "preview_text": preview,
        "smart_sending_enabled": True,
        "transactional": False,
        "add_tracking_params": True,
        "custom_tracking_params": None,
        "additional_filters": None,
        "name": name,
    }
    if template_id:
        msg["template_id"] = template_id
    return {"type": "send-email", "data": {"message": msg, "status": "draft"}}


def delay_action(value: int, unit: str = "days") -> dict:
    data: dict = {"unit": unit, "value": value, "secondary_value": None}
    if unit == "days":
        data["timezone"] = "profile"
        data["delay_until_weekdays"] = ALL_DAYS
    return {"type": "time-delay", "data": data}


def split_action(profile_filter, yes_branch: list, no_branch: list) -> dict:
    return {
        "type": "conditional-split",
        "data": {"profile_filter": profile_filter},
        "_yes": yes_branch,
        "_no": no_branch,
    }


def build_definition(trigger, node_list: list) -> dict:
    actions = []

    def process(nodes):
        if not nodes:
            return None
        tids = [new_id() for _ in nodes]
        for i, (node, tid) in enumerate(zip(nodes, tids)):
            ntype = node["type"]
            action = {"temporary_id": tid, "type": ntype, "data": node["data"]}
            if ntype == "conditional-split":
                yes_first = process(node.get("_yes", []))
                no_first  = process(node.get("_no", []))
                action["links"] = {"next_if_true": yes_first, "next_if_false": no_first}
            else:
                next_tid = tids[i + 1] if i < len(nodes) - 1 else None
                action["links"] = {"next": next_tid}
            actions.append(action)
        return tids[0]

    entry_id = process(node_list)
    return {
        "triggers": [trigger] if trigger else [],
        "profile_filter": None,
        "actions": actions,
        "entry_action_id": entry_id,
    }


def flow_payload(name: str, trigger, nodes: list) -> dict:
    return {"data": {"type": "flow", "attributes": {
        "name": name,
        "definition": build_definition(trigger, nodes),
    }}}


# ── Flow builders ──────────────────────────────────────────────────────────────

def build_back_in_stock() -> dict:
    reset_ids()
    n = "[Z] Back in Stock Email 1"
    nodes = [
        email_action(
            "{{ event.ProductName }} is back!",
            TPL[n], n, PREVIEW[n],
        ),
        delay_action(1),
        split_action(
            profile_filter=placed_order_filter(1),
            yes_branch=[],   # YES: already purchased -> exit
            no_branch=[
                email_action(
                    "Still available - but selling fast",
                    TPL["[Z] Back in Stock Email 2"],
                    "[Z] Back in Stock Email 2",
                    PREVIEW["[Z] Back in Stock Email 2"],
                )
            ],
        ),
    ]
    return flow_payload("[Z] Back in Stock",
                        {"type": "metric", "id": BACK_IN_STOCK_METRIC_ID},
                        nodes)


def build_post_purchase() -> dict:
    reset_ids()
    nodes = [
        delay_action(1, "hours"),
        email_action(
            "{{ person.first_name|default:'friend' }}, order confirmed!",
            TPL["[Z] Post-Purchase Email 1"],
            "[Z] Post-Purchase Email 1",
            PREVIEW["[Z] Post-Purchase Email 1"],
        ),
        delay_action(3),
        email_action(
            "Getting the most from your order",
            TPL["[Z] Post-Purchase Email 2"],
            "[Z] Post-Purchase Email 2",
            PREVIEW["[Z] Post-Purchase Email 2"],
        ),
        delay_action(4),
        email_action(
            "{{ person.first_name|default:'friend' }}, more to love",
            TPL["[Z] Post-Purchase Email 3"],
            "[Z] Post-Purchase Email 3",
            PREVIEW["[Z] Post-Purchase Email 3"],
        ),
        delay_action(7),
        split_action(
            profile_filter=placed_order_filter(2),
            yes_branch=[],   # YES: repeat buyer -> exit
            no_branch=[
                email_action(
                    "How did we do, {{ person.first_name|default:'friend' }}?",
                    TPL["[Z] Post-Purchase Email 4"],
                    "[Z] Post-Purchase Email 4",
                    PREVIEW["[Z] Post-Purchase Email 4"],
                )
            ],
        ),
    ]
    return flow_payload("[Z] Post-Purchase Series",
                        {"type": "metric", "id": PLACED_ORDER_METRIC_ID},
                        nodes)


def build_flu_season() -> dict:
    reset_ids()
    nodes = [
        email_action(
            "Stay well this winter, {{ person.first_name|default:'friend' }}",
            TPL["[Z] Flu Season Email 1"],
            "[Z] Flu Season Email 1",
            PREVIEW["[Z] Flu Season Email 1"],
        ),
        delay_action(7),
        email_action(
            "Have you booked your flu vaccine yet?",
            TPL["[Z] Flu Season Email 2"],
            "[Z] Flu Season Email 2",
            PREVIEW["[Z] Flu Season Email 2"],
        ),
    ]
    return flow_payload("[Z] Flu Season - Winter Wellness",
                        {"type": "segment", "id": FLU_SEASON_SEGMENT_ID},
                        nodes)


def build_winback() -> dict:
    reset_ids()
    nodes = [
        email_action(
            "We miss you, {{ person.first_name|default:'friend' }}",
            TPL["[Z] Win-back Email 1"],
            "[Z] Win-back Email 1",
            PREVIEW["[Z] Win-back Email 1"],
        ),
        delay_action(7),
        email_action(
            "Here's something for you, {{ person.first_name|default:'friend' }}",
            TPL["[Z] Win-back Email 2"],
            "[Z] Win-back Email 2",
            PREVIEW["[Z] Win-back Email 2"],
        ),
        delay_action(7),
        email_action(
            "Last chance - we'd hate to say goodbye",
            TPL["[Z] Win-back Email 3"],
            "[Z] Win-back Email 3",
            PREVIEW["[Z] Win-back Email 3"],
        ),
    ]
    return flow_payload("[Z] Win-back - Lapsed Customers",
                        {"type": "segment", "id": WINBACK_SEGMENT_ID},
                        nodes)


def build_replenishment() -> dict:
    reset_ids()
    rpl = TPL["[Z] Replenishment Reminder"]
    subject = "{{ person.first_name|default:'friend' }}, time to restock?"

    # Ordered so broader/brand keywords come AFTER more specific product keywords.
    # Supply window and reminder timing:
    #   Regaine 4-month pack          120 days  -> remind at 110
    #   Magnesium 120-tab             120 days  -> remind at 100
    #   Elevit 100-tab                100 days  -> remind at  80
    #   Sanderson (non-Mg) 90-day avg           -> remind at  90
    #   GO Healthy (non-Mg) 90-day avg          -> remind at  90
    #   Hayfexo 70-tab                 70 days  -> remind at  55
    #   FLASH Eyelash Serum ~30-day    30 days  -> remind at  25  [NEW]
    #   Clinicians 30-cap              30 days  -> remind at  22
    #   Goli gummies 60-pc             30 days  -> remind at  22
    #   LIVON 30-sachet                30 days  -> remind at  22
    #   Razene 30-tab                  30 days  -> remind at  22  [NEW]
    #   Omeprazole 28-cap              28 days  -> remind at  20  [NEW]
    #   Ensure 850 g powder            16 days  -> remind at  12
    #   Oracoat 40-pack                13 days  -> remind at  10
    #   Optislim 21-sachet             21 days  -> remind at  15
    #   Optifast 12-sachet             12 days  -> remind at   9
    products = [
        ("Regaine",    110),
        ("Magnesium",  100),
        ("Elevit",      80),
        ("Sanderson",   90),
        ("GO Healthy",  90),
        ("Hayfexo",     55),
        ("FLASH",       25),
        ("Clinicians",  22),
        ("Goli",        22),
        ("LIVON",       22),
        ("Razene",      22),
        ("Omeprazole",  20),
        ("Ensure",      12),
        ("Oracoat",     10),
        ("Optislim",    15),
        ("Optifast",     9),
    ]

    def branch(keyword: str, days: int) -> list:
        tpl_id = TPL.get(f"[Z] Replenishment Reminder ({keyword})", rpl)
        return [
            delay_action(days),
            email_action(subject, tpl_id,
                         f"[Z] Replenishment Reminder ({keyword})",
                         REPLENISHMENT_PREVIEW),
        ]

    no_branch: list = []
    for keyword, days in reversed(products):
        no_branch = [
            split_action(
                profile_filter=replenishment_filter(keyword),
                yes_branch=branch(keyword, days),
                no_branch=no_branch,
            )
        ]

    return flow_payload("[Z] Replenishment - Reorder Reminders",
                        {"type": "metric", "id": REPLENISHMENT_METRIC_ID},
                        no_branch)


# ── API helpers ────────────────────────────────────────────────────────────────

def get_z_flow_ids() -> dict:
    """Returns {name: id} for all [Z] flows currently in the account."""
    found = {}
    url = f"{BASE_URL}/flows"
    params = {"fields[flow]": "name"}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if not r.ok:
            print(f"  WARNING: could not list flows ({r.status_code}): {r.text[:200]}")
            break
        data = r.json()
        for item in data.get("data", []):
            name = item["attributes"]["name"]
            if name.startswith("[Z]"):
                found[name] = item["id"]
        next_url = (data.get("links") or {}).get("next")
        url = next_url if next_url and next_url != url else None
        params = {}
        time.sleep(0.2)
    return found


def create_flow(payload: dict):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:500]}"


def delete_flow(flow_id: str):
    r = requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        print(f"    Warning: delete {flow_id} returned {r.status_code}")


def edit_link(flow_id: str) -> str:
    return f"https://www.klaviyo.com/flow/{flow_id}/edit"


# ── Main ───────────────────────────────────────────────────────────────────────

FLOW_BUILDERS = [
    ("[Z] Back in Stock",                  build_back_in_stock),
    ("[Z] Post-Purchase Series",           build_post_purchase),
    ("[Z] Flu Season - Winter Wellness",   build_flu_season),
    ("[Z] Win-back - Lapsed Customers",    build_winback),
    ("[Z] Replenishment - Reorder Reminders", build_replenishment),
]

TARGET_NAMES = {name for name, _ in FLOW_BUILDERS}


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    mode = "APPLY" if APPLY else "DRY RUN"
    print(f"fix_all_flows.py  ({mode})")
    print("=" * 60)

    # Discover current [Z] flow IDs
    print("\nDiscovering existing [Z] flows...")
    existing = get_z_flow_ids()
    print(f"  Found {len(existing)} [Z] flow(s):")
    for name, fid in sorted(existing.items()):
        tag = "  [TARGET]" if name in TARGET_NAMES else ""
        print(f"    {fid}  {name}{tag}")

    to_delete = {name: fid for name, fid in existing.items() if name in TARGET_NAMES}

    if APPLY:
        print(f"\nDeleting {len(to_delete)} target flow(s)...")
        for name, fid in to_delete.items():
            print(f"  Deleting {fid} ({name})...", end=" ")
            delete_flow(fid)
            print("done")
            time.sleep(0.3)
    else:
        print(f"\n[DRY RUN] Would delete {len(to_delete)} flow(s): {list(to_delete.keys())}")

    print("\nBuilding flow payloads...")
    results = []
    for flow_name, builder in FLOW_BUILDERS:
        payload = builder()
        defn = payload["data"]["attributes"]["definition"]
        emails = [a for a in defn["actions"] if a["type"] == "send-email"]
        splits = [a for a in defn["actions"] if a["type"] == "conditional-split"]
        delays = [a for a in defn["actions"] if a["type"] == "time-delay"]
        has_preview = all(
            a["data"]["message"].get("preview_text", "").strip()
            for a in emails
        )
        print(f"\n  {flow_name}")
        print(f"    emails={len(emails)}  splits={len(splits)}  delays={len(delays)}")
        print(f"    preview text populated: {has_preview}")
        for e in emails:
            msg = e["data"]["message"]
            subj = msg["subject_line"]
            prev = msg.get("preview_text", "")
            tpl  = msg.get("template_id", "NONE")
            print(f"    [{tpl}] {subj[:55]}")
            if prev:
                print(f"           preview: {prev[:60]}")

        if APPLY:
            fid, err = create_flow(payload)
            if fid:
                print(f"    Created: {fid}  {edit_link(fid)}")
                results.append((flow_name, fid, None))
            else:
                print(f"    FAILED: {err}")
                results.append((flow_name, None, err))
            time.sleep(0.5)
        else:
            results.append((flow_name, "DRY-RUN", None))

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for name, fid, err in results:
        if err:
            print(f"  FAIL  {name}")
            print(f"        {err}")
        elif fid == "DRY-RUN":
            print(f"  DRY   {name}")
        else:
            print(f"  OK    {name}")
            print(f"        {edit_link(fid)}")
        print()

    if APPLY:
        ok = sum(1 for _, fid, err in results if fid and not err)
        print(f"{ok}/{len(results)} flows created successfully.")
        if ok == len(results):
            print()
            print("Next steps:")
            print("  1. Open each email block in the Klaviyo flow editor and save")
            print("     once to trigger the template preview thumbnail.")
            print("  2. Activate flows when ready (change from Draft to Live).")
    else:
        print("Run with --apply to execute the rebuild.")


if __name__ == "__main__":
    main()
