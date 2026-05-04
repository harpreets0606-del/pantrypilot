"""
Creates 5 Klaviyo email flows via the Klaviyo REST API (revision 2024-10-15.pre).

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py klaviyo_flows.py
"""

import os, sys, json, time, requests

# ── Config ─────────────────────────────────────────────────────────────────────
API_KEY   = os.environ.get("KLAVIYO_API_KEY", "")
REVISION  = "2024-10-15.pre"
BASE_URL  = "https://a.klaviyo.com/api"

# Pulled from your existing flows — change if needed
FROM_EMAIL  = "hello@bargainchemist.co.nz"
FROM_LABEL  = "Bargain Chemist"
REPLY_TO    = "orders@bargainchemist.co.nz"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

ALL_DAYS = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"]

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

def email_action(subject: str, template_id: str | None, name: str) -> dict:
    msg = {
        "from_email": FROM_EMAIL,
        "from_label": FROM_LABEL,
        "reply_to_email": REPLY_TO,
        "cc_email": None,
        "bcc_email": None,
        "subject_line": subject,
        "preview_text": "",
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
    data: dict = {
        "unit": unit,
        "value": value,
        "secondary_value": None,
    }
    if unit == "days":
        data["timezone"] = "profile"
        data["delay_until_weekdays"] = ALL_DAYS
    return {"type": "time-delay", "data": data}


def split_action(profile_filter: dict | None, yes_branch: list, no_branch: list) -> dict:
    return {
        "type": "conditional-split",
        "data": {"profile_filter": profile_filter},
        "_yes": yes_branch,
        "_no": no_branch,
    }


# ── Definition builder ─────────────────────────────────────────────────────────

def build_definition(trigger: dict | None, node_list: list) -> dict:
    actions: list[dict] = []

    def process(nodes: list) -> str | None:
        if not nodes:
            return None
        tids = [new_id() for _ in nodes]
        for i, (node, tid) in enumerate(zip(nodes, tids)):
            ntype = node["type"]
            action: dict = {"temporary_id": tid, "type": ntype, "data": node["data"]}
            if ntype == "conditional-split":
                yes_first = process(node.get("_yes", []))
                no_first  = process(node.get("_no", []))
                action["links"] = {
                    "next_if_true":  yes_first,
                    "next_if_false": no_first,
                }
            else:
                next_tid = tids[i + 1] if i < len(nodes) - 1 else None
                action["links"] = {"next": next_tid}
            actions.append(action)
        return tids[0]

    entry_id = process(node_list)
    triggers = [trigger] if trigger else []
    return {
        "triggers": triggers,
        "profile_filter": None,
        "actions": actions,
        "entry_action_id": entry_id,
    }


def flow_payload(name: str, trigger: dict | None, nodes: list) -> dict:
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": name,
                "definition": build_definition(trigger, nodes),
            },
        }
    }


# ── Flow definitions ───────────────────────────────────────────────────────────

def build_winback(tpl: dict) -> dict:
    reset_ids()
    nodes = [
        email_action(
            "We miss you, {{ person.first_name|default:'friend' }} 👋",
            tpl.get("[Z] Win-back Email 1"),
            "[Z] Win-back Email 1",
        ),
        delay_action(7),
        email_action(
            "Here's something for you, {{ person.first_name|default:'friend' }}",
            tpl.get("[Z] Win-back Email 2"),
            "[Z] Win-back Email 2",
        ),
        delay_action(7),
        email_action(
            "Last chance — we'd hate to say goodbye",
            tpl.get("[Z] Win-back Email 3"),
            "[Z] Win-back Email 3",
        ),
    ]
    return flow_payload(
        "[Z] Win-back - Lapsed Customers",
        {"type": "segment", "id": "Srd5Qr"},
        nodes,
    )


def build_back_in_stock(tpl: dict) -> dict:
    reset_ids()
    nodes = [
        email_action(
            "{{ event.ProductName }} is back! 🎉",
            tpl.get("[Z] Back in Stock Email 1"),
            "[Z] Back in Stock Email 1",
        ),
        delay_action(1),
        split_action(
            profile_filter=None,
            yes_branch=[],
            no_branch=[
                email_action(
                    "Still available — but selling fast",
                    tpl.get("[Z] Back in Stock Email 2"),
                    "[Z] Back in Stock Email 2",
                )
            ],
        ),
    ]
    return flow_payload(
        "[Z] Back in Stock",
        {"type": "metric", "id": "USbQRB"},
        nodes,
    )


def build_post_purchase(tpl: dict) -> dict:
    reset_ids()
    nodes = [
        delay_action(1, "hours"),
        email_action(
            "Thank you {{ person.first_name|default:'friend' }} — your order is confirmed 🙌",
            tpl.get("[Z] Post-Purchase Email 1"),
            "[Z] Post-Purchase Email 1",
        ),
        delay_action(3),
        email_action(
            "Getting the most from your order",
            tpl.get("[Z] Post-Purchase Email 2"),
            "[Z] Post-Purchase Email 2",
        ),
        delay_action(4),
        email_action(
            "{{ person.first_name|default:'friend' }}, customers also loved these",
            tpl.get("[Z] Post-Purchase Email 3"),
            "[Z] Post-Purchase Email 3",
        ),
        delay_action(7),
        split_action(
            profile_filter=None,
            yes_branch=[],
            no_branch=[
                email_action(
                    "How did we do, {{ person.first_name|default:'friend' }}?",
                    tpl.get("[Z] Post-Purchase Email 4"),
                    "[Z] Post-Purchase Email 4",
                )
            ],
        ),
    ]
    return flow_payload(
        "[Z] Post-Purchase Series",
        {"type": "metric", "id": "Sxnb5T"},
        nodes,
    )


def build_flu_season(tpl: dict) -> dict:
    reset_ids()
    nodes = [
        email_action(
            "Stay well this winter, {{ person.first_name|default:'friend' }} 🛡️",
            tpl.get("[Z] Flu Season Email 1"),
            "[Z] Flu Season Email 1",
        ),
        delay_action(7),
        email_action(
            "Have you booked your flu vaccine yet?",
            tpl.get("[Z] Flu Season Email 2"),
            "[Z] Flu Season Email 2",
        ),
    ]
    return flow_payload(
        "[Z] Flu Season - Winter Wellness",
        {"type": "segment", "id": "VGQby3"},
        nodes,
    )


def build_replenishment(tpl: dict) -> dict:
    reset_ids()
    rpl = tpl.get("[Z] Replenishment Reminder")
    subject = "{{ person.first_name|default:'friend' }}, time to restock?"

    # Ordered so broader brand keywords come AFTER specific product keywords.
    # "Magnesium" is intentionally before "Sanderson" and "GO Healthy" so that
    # Sanderson Magnesium FX (4,240 orders) and GO Magnesium Sleep (2,217 orders)
    # receive the correct 100-day supply window rather than the 90-day brand fallback.
    #
    # Delay = days after purchase to send reminder (i.e. just before supply runs out).
    # Supply lengths:
    #   Regaine 4-month pack      → 120 days  → remind at 110
    #   Magnesium 120-tab pack    → 120 days  → remind at 100
    #   Elevit 100-tab pack       → 100 days  → remind at  80
    #   Sanderson (non-Mg) 90-day avg supply   → remind at  90
    #   GO Healthy (non-Mg) 90-day avg supply  → remind at  90
    #   Hayfexo 70-tab            →  70 days  → remind at  55
    #   Clinicians 30-cap         →  30 days  → remind at  22
    #   Goli gummies 60-pc        →  30 days  → remind at  22
    #   LIVON 30-sachet           →  30 days  → remind at  22
    #   Ensure 850 g powder       →  16 days  → remind at  12
    #   Oracoat 40-pack           →  13 days  → remind at  10
    #   Optifast 12-sachet pack   →  12 days  → remind at   9
    #   Optislim 21-sachet pack   →  21 days  → remind at  15  (was 5 — fixed)
    products = [
        ("Regaine",   110),
        ("Magnesium", 100),
        ("Elevit",     80),
        ("Sanderson",  90),
        ("GO Healthy", 90),
        ("Hayfexo",    55),
        ("Clinicians", 22),
        ("Goli",       22),
        ("LIVON",      22),
        ("Ensure",     12),
        ("Oracoat",    10),
        ("Optifast",    9),
        ("Optislim",   15),
    ]

    def branch(keyword: str, days: int) -> list:
        tpl_id = tpl.get(f"[Z] Replenishment Reminder ({keyword})", rpl)
        return [
            delay_action(days),
            email_action(subject, tpl_id, f"[Z] Replenishment Reminder ({keyword})"),
        ]

    no_branch: list = []
    for keyword, days in reversed(products):
        no_branch = [
            split_action(
                profile_filter=None,
                yes_branch=branch(keyword, days),
                no_branch=no_branch,
            )
        ]

    return flow_payload(
        "[Z] Replenishment - Reorder Reminders",
        {"type": "metric", "id": "UWP7cZ"},
        no_branch,
    )


# ── API helpers ────────────────────────────────────────────────────────────────

def create_flow(payload: dict) -> str:
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if not r.ok:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:400]}")
    return r.json()["data"]["id"]


def delete_flow(flow_id: str) -> None:
    r = requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=30)
    if not r.ok and r.status_code != 404:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:200]}")


def edit_link(flow_id: str) -> str:
    return f"https://www.klaviyo.com/flow/{flow_id}/edit"


# ── Main ───────────────────────────────────────────────────────────────────────

# All 5 draft [Z] flows are rebuilt with templates pre-populated.
# The REST API does not allow updating flow message templates after creation,
# so the only way is to delete and recreate with template_id in the payload.
#
# Current draft flow IDs to delete before recreating:
FLOWS_TO_DELETE = [
    "U6e3uf",  # [Z] Flu Season - Winter Wellness
    "XKmyJE",  # [Z] Replenishment - Reorder Reminders
    "UqpyKS",  # [Z] Back in Stock
    "Vvb9ik",  # [Z] Post-Purchase Series
    "YdtALs",  # [Z] Win-back - Lapsed Customers
]

# Template IDs for each flow message name used in the builders below
TPL_MAP: dict[str, str] = {
    # Post-Purchase
    "[Z] Post-Purchase Email 1": "RHfcDs",
    "[Z] Post-Purchase Email 2": "Sy929J",
    "[Z] Post-Purchase Email 3": "UNjrA4",
    "[Z] Post-Purchase Email 4": "SQD3nM",
    # Flu Season
    "[Z] Flu Season Email 1":    "SMDszN",
    "[Z] Flu Season Email 2":    "WALe6F",
    # Win-Back
    "[Z] Win-back Email 1":      "RDNsnL",
    "[Z] Win-back Email 2":      "YuYX38",
    "[Z] Win-back Email 3":      "VEpKb4",
    # Back in Stock
    "[Z] Back in Stock Email 1": "UCeqPt",
    "[Z] Back in Stock Email 2": "XXcqNf",
    # Replenishment — product-specific + generic fallback
    "[Z] Replenishment Reminder": "UXVWhK",  # generic fallback
    "[Z] Replenishment - Regaine":                    "SkCfgY",
    "[Z] Replenishment - Hayfexo Allergy":            "RyVVZV",
    "[Z] Replenishment - Oracoat":                    "STBhAz",
    "[Z] Replenishment - Optifast VLCD":              "RFAcvQ",
    "[Z] Replenishment - Vitamins and Supplements":   "UXVWhK",
}

FLOW_BUILDERS = [
    ("Flow 1 — Post-Purchase",   build_post_purchase,  []),
    ("Flow 2 — Flu Season",      build_flu_season,     []),
    ("Flow 3 — Win-Back",        build_winback,        []),
    ("Flow 4 — Back in Stock",   build_back_in_stock,  []),
    ("Flow 5 — Replenishment",   build_replenishment,  []),
]


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    # Delete all existing draft flows first
    print(f"Deleting {len(FLOWS_TO_DELETE)} existing draft flows...")
    for fid in FLOWS_TO_DELETE:
        print(f"  Deleting {fid}...", end=" ")
        try:
            delete_flow(fid)
            print("deleted")
        except Exception as e:
            print(f"failed (continuing): {e}")
    print()

    tpl_map: dict[str, str] = TPL_MAP

    results = []
    for label, builder, _ in FLOW_BUILDERS:
        print(f"─── {label} ───────────────────────────────")
        payload = builder(tpl_map)
        name = payload["data"]["attributes"]["name"]
        print(f"  Creating '{name}'…")
        try:
            flow_id = create_flow(payload)
            link = edit_link(flow_id)
            print(f"  ✓ Created → {flow_id}")
            print(f"  Edit:    {link}")
            results.append((label, flow_id, link, None))
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            results.append((label, None, None, str(e)))
        print()
        time.sleep(0.5)

    print("═" * 60)
    print("SUMMARY")
    print("═" * 60)
    for label, flow_id, link, err in results:
        if flow_id:
            print(f"✓ {label}")
            print(f"  ID:   {flow_id}")
            print(f"  Link: {link}")
        else:
            print(f"✗ {label}  →  {err}")
        print()


if __name__ == "__main__":
    main()
