"""
Rebuilds the Replenishment flow with:
  - Corrected timing: Magnesium 100d->30d, Oracoat 10d->30d, Optifast 9d->21d
  - New product: Wegovy (28 days)

Approach: DELETE existing flow XRUj2w, then POST a fresh one.
People mid-flow will exit - acceptable since the flow is short.

Usage:
    py scripts/fix-replenishment-flow.py
"""

import os, sys, time, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

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

# Metric ID for the replenishment trigger (Placed Order for BC)
REPLENISHMENT_METRIC_ID = "UWP7cZ"

# Template IDs
TPL_DEFAULT    = "UXVWhK"
TPL_REGAINE    = "SkCfgY"
TPL_HAYFEXO    = "RyVVZV"
TPL_ORACOAT    = "STBhAz"
TPL_OPTIFAST   = "RFAcvQ"

TPL_MAP = {
    "Regaine":   TPL_REGAINE,
    "Hayfexo":   TPL_HAYFEXO,
    "Oracoat":   TPL_ORACOAT,
    "Optifast":  TPL_OPTIFAST,
    "Optislim":  TPL_OPTIFAST,
}

# All products with corrected timing + new Wegovy entry
PRODUCTS = [
    ("Regaine",    110),
    ("Magnesium",   30),  # fixed: was 100
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
    ("Oracoat",     30),  # fixed: was 10
    ("Optislim",    15),
    ("Optifast",    21),  # fixed: was 9
    ("Wegovy",      28),  # NEW
]

# ── ID counter ─────────────────────────────────────────────────────────────────
_counter = 0

def new_id():
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0

# ── Action builders ────────────────────────────────────────────────────────────

def email_action(subject, template_id, name):
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


def delay_action(value, unit="days"):
    data = {"unit": unit, "value": value, "secondary_value": None}
    if unit == "days":
        data["timezone"] = "profile"
        data["delay_until_weekdays"] = ALL_DAYS
    return {"type": "time-delay", "data": data}


def split_action(profile_filter, yes_branch, no_branch):
    return {
        "type": "conditional-split",
        "data": {"profile_filter": profile_filter},
        "_yes": yes_branch,
        "_no": no_branch,
    }


def replenishment_filter(keyword):
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


# ── Definition builder ─────────────────────────────────────────────────────────

def build_definition(trigger, node_list):
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


def build_replenishment():
    reset_ids()
    subject = "{{ person.first_name|default:'friend' }}, time to restock?"

    def branch(keyword, days):
        tpl_id = TPL_MAP.get(keyword, TPL_DEFAULT)
        return [
            delay_action(days),
            email_action(subject, tpl_id, f"[Z] Replenishment Reminder ({keyword})"),
        ]

    no_branch = []
    for keyword, days in reversed(PRODUCTS):
        no_branch = [
            split_action(
                profile_filter=replenishment_filter(keyword),
                yes_branch=branch(keyword, days),
                no_branch=no_branch,
            )
        ]

    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "[Z] Replenishment - Reorder Reminders",
                "definition": build_definition(
                    {"type": "metric", "id": REPLENISHMENT_METRIC_ID},
                    no_branch,
                ),
            },
        }
    }


# ── API helpers ────────────────────────────────────────────────────────────────

def delete_flow(flow_id):
    r = requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        print(f"  Warning: delete returned {r.status_code}: {r.text[:200]}")


def create_flow(payload):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:500]}"


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    print("Replenishment Flow Rebuild")
    print("-" * 50)
    print(f"Products: {len(PRODUCTS)} (including Wegovy)")
    print()

    print("Building flow definition...")
    payload = build_replenishment()
    action_count = len(payload["data"]["attributes"]["definition"]["actions"])
    print(f"  Definition built: {action_count} actions")
    print()

    print("Deleting existing flow XRUj2w...")
    delete_flow("XRUj2w")
    print("  Deleted")
    time.sleep(1)

    print("Creating new flow...")
    fid, err = create_flow(payload)
    if fid:
        print(f"  Created: {fid}")
        print(f"  Edit: https://www.klaviyo.com/flow/{fid}/edit")
        print()
        print("Timing fixes applied:")
        print("  Magnesium: 100 days -> 30 days")
        print("  Oracoat:    10 days -> 30 days")
        print("  Optifast:    9 days -> 21 days")
        print("  Wegovy:     NEW     -> 28 days")
        print()
        print("IMPORTANT: Update the flow ID in any scripts that reference XRUj2w ->", fid)
    else:
        print(f"  FAILED: {err}")
        sys.exit(1)


if __name__ == "__main__":
    main()
