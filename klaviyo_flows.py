"""
Creates 5 Klaviyo email flows via the Klaviyo REST API (revision 2024-10-15).

Usage:
    KLAVIYO_API_KEY=pk_xxx python klaviyo_flows.py
    OR set KLAVIYO_KEY directly in the script below.
"""

import os
import sys
import json
import time
import requests

# ── Config ─────────────────────────────────────────────────────────────────────
API_KEY = os.environ.get("KLAVIYO_API_KEY", "YOUR_PRIVATE_KEY_HERE")
REVISION = "2024-10-15"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

# ── Helpers ────────────────────────────────────────────────────────────────────

def get_templates() -> dict[str, str]:
    """Return {template_name: template_id} for all templates in the account."""
    templates: dict[str, str] = {}
    url = f"{BASE_URL}/templates"
    params = {"page[size]": 10}
    page = 1
    while url:
        print(f"  Fetching page {page}…", flush=True)
        resp = requests.get(url, headers=HEADERS, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("data", []):
            templates[item["attributes"]["name"]] = item["id"]
        url = data.get("links", {}).get("next")
        params = {}
        page += 1
    return templates


def resolve_templates(names: list[str], catalog: dict[str, str]) -> dict[str, str]:
    """Map template names → IDs, printing a warning for any not found."""
    result: dict[str, str] = {}
    for name in names:
        tid = catalog.get(name)
        if tid:
            result[name] = tid
            print(f"  ✓ template '{name}' → {tid}")
        else:
            print(f"  ✗ template '{name}' NOT FOUND — will omit from flow")
    return result


def create_flow(payload: dict) -> str:
    """POST /api/flows and return the new flow ID."""
    resp = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload)
    if not resp.ok:
        print(f"  ERROR {resp.status_code}: {resp.text}")
        resp.raise_for_status()
    return resp.json()["data"]["id"]


def edit_link(flow_id: str) -> str:
    return f"https://www.klaviyo.com/flow/{flow_id}/edit"


# ── Node-building primitives ───────────────────────────────────────────────────

def email_node(name: str, subject: str, template_id: str | None) -> dict:
    content: dict = {
        "type": "send_email",
        "name": name,
        "settings": {
            "subject": subject,
            "from_email": "",   # Klaviyo fills from account default
            "from_name": "",
        },
    }
    if template_id:
        content["settings"]["template_id"] = template_id
    return content


def delay_node(hours: int | None = None, days: int | None = None) -> dict:
    if days is not None:
        hours = days * 24
    return {
        "type": "time_delay",
        "settings": {
            "delay": {
                "unit": "hours",
                "value": hours,
            }
        },
    }


def conditional_split_node(
    name: str,
    condition_group: dict,
) -> dict:
    return {
        "type": "conditional_split",
        "name": name,
        "settings": {
            "condition_groups": [condition_group],
        },
    }


# Klaviyo flow payload wrapper
def flow_payload(
    name: str,
    trigger: dict,
    action_nodes: list[dict],
) -> dict:
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": name,
                "trigger_type": trigger["type"],
                "trigger_id": trigger.get("id"),
                "status": "draft",
                "archived": False,
                "action_nodes": action_nodes,
            },
        }
    }


# ── Flow definitions ───────────────────────────────────────────────────────────

def build_winback(tpl: dict[str, str]) -> dict:
    """
    Flow 1: Win-back
    email1 → delay 7d → email2 → delay 7d → email3
    Trigger: segment Srd5Qr
    """
    nodes = [
        email_node(
            "[Z] Win-back Email 1",
            "We miss you, {{ person.first_name|default:'friend' }} 👋",
            tpl.get("[Z] Win-back Email 1"),
        ),
        delay_node(days=7),
        email_node(
            "[Z] Win-back Email 2",
            "Here's something for you, {{ person.first_name|default:'friend' }}",
            tpl.get("[Z] Win-back Email 2"),
        ),
        delay_node(days=7),
        email_node(
            "[Z] Win-back Email 3",
            "Last chance — we'd hate to say goodbye",
            tpl.get("[Z] Win-back Email 3"),
        ),
    ]
    return flow_payload(
        "[Z] Win-back - Lapsed Customers",
        {"type": "segment", "id": "Srd5Qr"},
        nodes,
    )


def build_back_in_stock(tpl: dict[str, str]) -> dict:
    """
    Flow 2: Back in Stock
    email1 → delay 24h → conditional_split → YES=end / NO=email2
    Trigger: metric USbQRB
    """
    placed_order_condition = {
        "conditions": [
            {
                "type": "metric",
                "metric_id": "Sxnb5T",  # Placed Order
                "operator": "has_done",
                "timeframe": {"type": "relative", "quantity": 1, "unit": "day"},
                "filters": [
                    {
                        "property": "ProductName",
                        "operator": "equals",
                        "value": "{{ event.ProductName }}",
                    }
                ],
            }
        ]
    }

    nodes = [
        email_node(
            "[Z] Back in Stock Email 1",
            "{{ event.ProductName }} is back! 🎉",
            tpl.get("[Z] Back in Stock Email 1"),
        ),
        delay_node(hours=24),
        {
            "type": "conditional_split",
            "name": "Placed order for same product in last 1 day?",
            "settings": {"condition_groups": [placed_order_condition]},
            "yes_branch": [],  # end
            "no_branch": [
                email_node(
                    "[Z] Back in Stock Email 2",
                    "Still available — but selling fast",
                    tpl.get("[Z] Back in Stock Email 2"),
                )
            ],
        },
    ]
    return flow_payload(
        "[Z] Back in Stock",
        {"type": "metric", "id": "USbQRB"},
        nodes,
    )


def build_post_purchase(tpl: dict[str, str]) -> dict:
    """
    Flow 3: Post-Purchase
    delay 1h → email1 → delay 3d → email2 → delay 4d → email3 →
    delay 7d → conditional_split → YES=end / NO=email4
    Trigger: metric Sxnb5T
    """
    placed_order_14d = {
        "conditions": [
            {
                "type": "metric",
                "metric_id": "Sxnb5T",
                "operator": "has_done",
                "timeframe": {"type": "relative", "quantity": 14, "unit": "day"},
            }
        ]
    }

    nodes = [
        delay_node(hours=1),
        email_node(
            "[Z] Post-Purchase Email 1",
            "Thank you {{ person.first_name|default:'friend' }} — your order is confirmed 🙌",
            tpl.get("[Z] Post-Purchase Email 1"),
        ),
        delay_node(days=3),
        email_node(
            "[Z] Post-Purchase Email 2",
            "Getting the most from your order",
            tpl.get("[Z] Post-Purchase Email 2"),
        ),
        delay_node(days=4),
        email_node(
            "[Z] Post-Purchase Email 3",
            "{{ person.first_name|default:'friend' }}, customers also loved these",
            tpl.get("[Z] Post-Purchase Email 3"),
        ),
        delay_node(days=7),
        {
            "type": "conditional_split",
            "name": "Placed order in last 14 days?",
            "settings": {"condition_groups": [placed_order_14d]},
            "yes_branch": [],  # end
            "no_branch": [
                email_node(
                    "[Z] Post-Purchase Email 4",
                    "How did we do, {{ person.first_name|default:'friend' }}?",
                    tpl.get("[Z] Post-Purchase Email 4"),
                )
            ],
        },
    ]
    return flow_payload(
        "[Z] Post-Purchase Series",
        {"type": "metric", "id": "Sxnb5T"},
        nodes,
    )


def build_flu_season(tpl: dict[str, str]) -> dict:
    """
    Flow 4: Flu Season
    email1 → delay 7d → email2
    Trigger: segment VGQby3
    """
    nodes = [
        email_node(
            "[Z] Flu Season Email 1",
            "Stay well this winter, {{ person.first_name|default:'friend' }} 🛡️",
            tpl.get("[Z] Flu Season Email 1"),
        ),
        delay_node(days=7),
        email_node(
            "[Z] Flu Season Email 2",
            "Have you booked your flu vaccine yet?",
            tpl.get("[Z] Flu Season Email 2"),
        ),
    ]
    return flow_payload(
        "[Z] Flu Season - Winter Wellness",
        {"type": "segment", "id": "VGQby3"},
        nodes,
    )


def _repl_branch(keyword: str, delay_days: int, tpl_id: str | None) -> list[dict]:
    """One branch of the replenishment conditional split."""
    return [
        delay_node(days=delay_days),
        email_node(
            f"[Z] Replenishment Reminder ({keyword})",
            "{{ person.first_name|default:'friend' }}, time to restock?",
            tpl_id,
        ),
    ]


def build_replenishment(tpl: dict[str, str]) -> dict:
    """
    Flow 5: Replenishment
    Nested conditional splits on Product Title, each branch:
      contains X → delay N days → email
    Falls through to end on no match.
    Trigger: metric UWP7cZ
    """
    rpl_tpl = tpl.get("[Z] Replenishment Reminder")

    products = [
        ("Optislim",  5),
        ("LIVON",     22),
        ("Clinicians",22),
        ("Magnesium", 100),
        ("Regaine",   110),
        ("Elevit",    80),
        ("Hayfexo",   55),
        ("Ensure",    12),
    ]

    def contains_condition(keyword: str) -> dict:
        return {
            "conditions": [
                {
                    "type": "property",
                    "property": "Product Title",
                    "operator": "contains",
                    "value": keyword,
                }
            ]
        }

    # Build from the innermost (last) product outward so each split's
    # no_branch contains the next split (or ends for the final else).
    current_no_branch: list[dict] = []  # final else → end

    for keyword, delay_days in reversed(products):
        split = {
            "type": "conditional_split",
            "name": f"Product contains '{keyword}'?",
            "settings": {"condition_groups": [contains_condition(keyword)]},
            "yes_branch": _repl_branch(keyword, delay_days, rpl_tpl),
            "no_branch": current_no_branch,
        }
        current_no_branch = [split]

    # The outermost split is the single top-level action node
    nodes = current_no_branch

    return flow_payload(
        "[Z] Replenishment - Reorder Reminders",
        {"type": "metric", "id": "UWP7cZ"},
        nodes,
    )


# ── Main ───────────────────────────────────────────────────────────────────────

FLOW_BUILDERS = [
    (
        "Flow 1 — Win-back",
        build_winback,
        ["[Z] Win-back Email 1", "[Z] Win-back Email 2", "[Z] Win-back Email 3"],
    ),
    (
        "Flow 2 — Back in Stock",
        build_back_in_stock,
        ["[Z] Back in Stock Email 1", "[Z] Back in Stock Email 2"],
    ),
    (
        "Flow 3 — Post-Purchase",
        build_post_purchase,
        [
            "[Z] Post-Purchase Email 1",
            "[Z] Post-Purchase Email 2",
            "[Z] Post-Purchase Email 3",
            "[Z] Post-Purchase Email 4",
        ],
    ),
    (
        "Flow 4 — Flu Season",
        build_flu_season,
        ["[Z] Flu Season Email 1", "[Z] Flu Season Email 2"],
    ),
    (
        "Flow 5 — Replenishment",
        build_replenishment,
        ["[Z] Replenishment Reminder"],
    ),
]


def main():
    if API_KEY == "YOUR_PRIVATE_KEY_HERE":
        print("ERROR: Set your Klaviyo API key via the KLAVIYO_API_KEY env var or edit API_KEY in this script.")
        sys.exit(1)

    print("Fetching templates from Klaviyo…")
    try:
        template_catalog = get_templates()
    except requests.HTTPError as exc:
        print(f"Failed to fetch templates: {exc}\n{exc.response.text}")
        sys.exit(1)

    print(f"Found {len(template_catalog)} templates.\n")

    results = []

    for label, builder, needed_tpl_names in FLOW_BUILDERS:
        print(f"─── {label} ───────────────────────────────")
        tpl_map = resolve_templates(needed_tpl_names, template_catalog)
        payload = builder(tpl_map)
        print(f"  Creating flow '{payload['data']['attributes']['name']}'…")
        try:
            flow_id = create_flow(payload)
            link = edit_link(flow_id)
            print(f"  ✓ Created → {flow_id}")
            print(f"  Edit:    {link}")
            results.append((label, flow_id, link, None))
        except Exception as exc:
            print(f"  ✗ FAILED: {exc}")
            results.append((label, None, None, str(exc)))
        print()
        time.sleep(0.5)  # gentle rate-limit courtesy

    # ── Summary ──
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
