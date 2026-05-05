"""
Rebuilds the Win-back flow with correct metric trigger.

Deletes WRKYPs (broken "Added to List" trigger, no lapsed list exists).
Creates new flow triggered on Placed Order metric:
  Wait 90 days
  Split: placed order since flow start?
    YES -> exit (came back on their own)
    NO  -> Email 1 (We Miss You)
         -> Wait 14 days
         -> Split: placed order since?
              YES -> exit
              NO  -> Email 2 (Still Here For You)

Templates:
  XxBbRK  Win-back Email 1 - We Miss You
  THsTQX  Win-back Email 2 - Still Here For You

Metric IDs:
  Sxnb5T  Placed Order

Usage:
    py scripts/rebuild-winback-flow.py
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

OLD_FLOW_ID     = "WRKYPs"
PLACED_ORDER_ID = "Sxnb5T"

TPL_MISS_YOU = "XxBbRK"
TPL_STILL_HERE = "THsTQX"

_counter = 0

def new_id():
    global _counter
    _counter += 1
    return str(_counter)

def reset_ids():
    global _counter
    _counter = 0

def email_action(subject, template_id, name):
    return {
        "type": "send-email",
        "data": {
            "message": {
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
                "template_id": template_id,
            },
            "status": "draft",
        },
    }

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

def repurchased_filter():
    """Has placed another Placed Order since entering this flow."""
    return {
        "condition_groups": [{
            "conditions": [{
                "type": "profile-metric",
                "metric_id": PLACED_ORDER_ID,
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
            }]
        }]
    }

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

def build_winback():
    reset_ids()

    second_chance = [
        split_action(
            profile_filter=repurchased_filter(),
            yes_branch=[],   # came back, exit
            no_branch=[
                email_action(
                    "We're still here for you, {{ first_name|default:'there' }}",
                    TPL_STILL_HERE,
                    "[Z] Win-back - Email 2 - Still Here",
                ),
            ],
        )
    ]

    nodes = [
        delay_action(90),
        split_action(
            profile_filter=repurchased_filter(),
            yes_branch=[],   # repurchased on their own, exit
            no_branch=[
                email_action(
                    "We've missed you, {{ first_name|default:'there' }}",
                    TPL_MISS_YOU,
                    "[Z] Win-back - Email 1 - We Miss You",
                ),
                delay_action(14),
            ] + second_chance,
        ),
    ]

    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "[Z] Win-back - Lapsed Customers",
                "definition": build_definition(
                    {"type": "metric", "id": PLACED_ORDER_ID},
                    nodes,
                ),
            },
        }
    }

def delete_flow(flow_id):
    r = requests.delete(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS, timeout=15)
    if not r.ok and r.status_code != 404:
        print(f"  Warning: delete returned {r.status_code}: {r.text[:200]}")

def create_flow(payload):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS, json=payload, timeout=30)
    if r.ok:
        return r.json()["data"]["id"], None
    return None, f"HTTP {r.status_code}: {r.text[:500]}"

def set_flow_live(flow_id):
    body = {"data": {"type": "flow", "id": flow_id, "attributes": {"status": "live"}}}
    r = requests.patch(f"{BASE_URL}/flows/{flow_id}/", headers=HEADERS, json=body, timeout=15)
    return r.ok

def main():
    print("Win-back Flow Rebuild")
    print("-" * 50)
    print(f"Trigger: Placed Order metric ({PLACED_ORDER_ID})")
    print(f"Logic: 90d delay -> check repurchased -> if not, Email 1 -> 14d -> check again -> Email 2")
    print()

    print("Building flow definition...")
    payload = build_winback()
    action_count = len(payload["data"]["attributes"]["definition"]["actions"])
    print(f"  Definition built: {action_count} actions")
    print()

    print(f"Deleting old flow {OLD_FLOW_ID}...")
    delete_flow(OLD_FLOW_ID)
    print("  Deleted")
    time.sleep(1)

    print("Creating new flow...")
    fid, err = create_flow(payload)
    if err:
        print(f"  FAILED: {err}")
        sys.exit(1)

    print(f"  Created: {fid}")

    print("Setting flow to live...")
    if set_flow_live(fid):
        print("  Flow is live")
    else:
        print("  Could not set live — set manually in Klaviyo UI")

    print()
    print("Flow structure:")
    print("  Trigger: Placed Order")
    print("  90-day delay")
    print("  Split: repurchased since flow start?")
    print("    YES -> exit (no action needed)")
    print("    NO  -> Email 1: We Miss You")
    print("           14-day delay")
    print("           Split: repurchased?")
    print("             YES -> exit")
    print("             NO  -> Email 2: Still Here For You")
    print()
    print(f"Edit: https://www.klaviyo.com/flow/{fid}/edit")
    print()
    print(f"IMPORTANT: Update any references to old flow {OLD_FLOW_ID} -> {fid}")

if __name__ == "__main__":
    main()
