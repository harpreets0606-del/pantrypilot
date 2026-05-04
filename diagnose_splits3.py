"""
Phase 3 diagnostic:

1. Probes the correct filter structure for profile-property conditions
   (the one valid type found so far).
2. Tries many more condition type values, including ones inferred from
   the ProfilePropertyCondition naming pattern.
3. Attempts PATCH on an existing flow-action to update split conditions.
4. Probes whether the trigger_filter on the trigger object can embed
   item-name conditions for Replenishment.

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py diagnose_splits3.py
"""

import os, sys, json, time, requests

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Content-Type": "application/json",
    "Accept": "application/json",
}

PLACED_ORDER   = "Sxnb5T"
REPLENISHMENT  = "UWP7cZ"
BACK_IN_STOCK  = "USbQRB"

# Back in Stock flow (Seu9Gy) split action id: 105625321
SPLIT_ACTION_ID = "105625321"

_counter = 0
def new_id():
    global _counter
    _counter += 1
    return str(_counter)
def reset_ids():
    global _counter
    _counter = 0


def minimal_flow(trigger_metric, pf):
    reset_ids()
    t1, t2 = new_id(), new_id()
    return {"data": {"type": "flow", "attributes": {"name": "__PROBE_DELETE_ME__",
        "definition": {
            "triggers": [{"type": "metric", "id": trigger_metric}],
            "profile_filter": None, "entry_action_id": t1,
            "actions": [
                {"temporary_id": t1, "type": "conditional-split",
                 "data": {"profile_filter": pf},
                 "links": {"next_if_true": None, "next_if_false": t2}},
                {"temporary_id": t2, "type": "send-email",
                 "data": {"message": {
                     "from_email": "hello@bargainchemist.co.nz", "from_label": "BC",
                     "reply_to_email": "orders@bargainchemist.co.nz",
                     "cc_email": None, "bcc_email": None, "subject_line": "probe",
                     "preview_text": "", "smart_sending_enabled": True,
                     "transactional": False, "add_tracking_params": True,
                     "custom_tracking_params": None, "additional_filters": None,
                     "name": "_probe"}, "status": "draft"},
                 "links": {"next": None}},
            ],
        }}}}


def probe(label, pf, trigger=PLACED_ORDER):
    r = requests.post(f"{BASE_URL}/flows", headers=HEADERS,
                      json=minimal_flow(trigger, pf), timeout=30)
    if r.ok:
        fid = r.json()["data"]["id"]
        print(f"  [ACCEPTED] {label} -> {fid}")
        requests.delete(f"{BASE_URL}/flows/{fid}", headers=HEADERS, timeout=15)
        time.sleep(0.3)
        return True
    else:
        print(f"  [REJECTED] {label}")
        try:
            for e in r.json().get("errors", []):
                d = e.get("detail", "")
                s = e.get("source", {})
                print(f"    detail: {d}")
                if s:
                    print(f"    source: {s}")
        except Exception:
            print(f"    raw: {r.text[:300]}")
        time.sleep(0.35)
        return False


def section(title):
    print(f"\n{'='*70}")
    print(title)
    print('='*70)
    print()


# ── Part 1: ProfilePropertyCondition filter structure ─────────────────────────

def probe_profile_property_filters():
    section("PART 1: Correct filter structure for profile-property conditions")

    # Try different filter formats for profile-property
    base = lambda f: {"condition_groups": [{"conditions": [{
        "type": "profile-property",
        "property": "$email",
        "filter": f
    }]}]}

    probe("profile-property / filter=null", base(None))
    probe("profile-property / filter={}", base({}))
    probe("profile-property / filter with type=is-set", base({"type": "is-set"}))
    probe("profile-property / filter with type=IS_SET", base({"type": "IS_SET"}))
    probe("profile-property / filter with type=exists", base({"type": "exists"}))
    probe("profile-property / filter with type=string + operator=is-set",
          base({"type": "string", "operator": "is-set"}))
    probe("profile-property / filter with type=string + operator=equals + value",
          base({"type": "string", "operator": "equals", "value": "test@test.com"}))
    probe("profile-property / filter with operator=is-set (no type)",
          base({"operator": "is-set"}))
    probe("profile-property / filter with operator=equals + value (no type)",
          base({"operator": "equals", "value": "test@test.com"}))
    probe("profile-property / filter with type=numeric + operator=greater-than + value=0",
          base({"type": "numeric", "operator": "greater-than", "value": 0}))
    probe("profile-property / filter with type=number + operator=greater-than + value=0",
          base({"type": "number", "operator": "greater-than", "value": 0}))

    # $number_of_orders is a known Klaviyo profile property
    base2 = lambda f: {"condition_groups": [{"conditions": [{
        "type": "profile-property",
        "property": "$number_of_orders",
        "filter": f
    }]}]}
    probe("profile-property $number_of_orders / filter type=numeric, op=greater-than, val=1",
          base2({"type": "numeric", "operator": "greater-than", "value": 1}))
    probe("profile-property $number_of_orders / filter op=greater-than val=1",
          base2({"operator": "greater-than", "value": 1}))


# ── Part 2: More condition type variants ──────────────────────────────────────

def probe_more_types():
    section("PART 2: More condition type variants")

    # Infer types from ProfilePropertyCondition → profile-property
    # MetricActivityCondition → metric-activity?
    # HasDoneMetricCondition  → has-done-metric?
    candidates = [
        "profile-activity",
        "metric-activity",
        "has-done-metric",
        "has-done",
        "metric-count",
        "activity-count",
        "flow-activity",
        "flow-metric",
        "event-count",
        "event-activity",
        "trigger-property",
        "trigger-event",
        "order-activity",
        "purchase-activity",
        "catalog-item",
        "catalog-property",
        "predictive-analytics",
        "predictive-clv",
        "channel-subscription",
        "sms-subscription",
        "email-subscription",
        # Maybe it's completely different
        "data",
        "filter",
        "query",
        "expression",
    ]
    for t in candidates:
        probe(f"type={t!r}",
              {"condition_groups": [{"conditions": [{"type": t}]}]})


# ── Part 3: Attempt PATCH on existing split action ────────────────────────────

def probe_patch_action():
    section("PART 3: PATCH /api/flow-actions/{id} to update split condition")

    # Try patching the split action in Back in Stock (Seu9Gy)
    # split action id: 105625321
    url = f"{BASE_URL}/flow-actions/{SPLIT_ACTION_ID}"

    payloads = [
        ("PATCH data.profile_filter=empty", {
            "data": {"type": "flow-action", "id": SPLIT_ACTION_ID,
                     "attributes": {"settings": {"profile_filter": {"condition_groups": []}}}}
        }),
        ("PATCH attributes.settings direct", {
            "data": {"type": "flow-action", "id": SPLIT_ACTION_ID,
                     "attributes": {"settings": {"condition_groups": []}}}
        }),
        ("PATCH with data.profile_filter at top", {
            "data": {"type": "flow-action", "id": SPLIT_ACTION_ID,
                     "attributes": {"data": {"profile_filter": {"condition_groups": []}}}}
        }),
    ]

    for label, payload in payloads:
        r = requests.patch(url, headers=HEADERS, json=payload, timeout=15)
        print(f"  {label}")
        print(f"    status: {r.status_code}")
        if r.ok:
            print(f"    ACCEPTED! Response: {r.text[:300]}")
        else:
            try:
                for e in r.json().get("errors", []):
                    print(f"    detail: {e.get('detail')}")
                    print(f"    source: {e.get('source')}")
            except Exception:
                print(f"    raw: {r.text[:300]}")
        time.sleep(0.3)


# ── Part 4: Probe trigger_filter on the flow trigger ──────────────────────────

def probe_trigger_filter():
    section("PART 4: trigger_filter on the flow trigger object")
    # Can we embed the item-name condition in the TRIGGER's filter
    # instead of the split? This would restrict the whole flow to only
    # fire for orders containing the keyword.

    def flow_with_trigger_filter(tf):
        reset_ids()
        t1 = new_id()
        return {"data": {"type": "flow", "attributes": {"name": "__PROBE_DELETE_ME__",
            "definition": {
                "triggers": [{"type": "metric", "id": REPLENISHMENT, "trigger_filter": tf}],
                "profile_filter": None, "entry_action_id": t1,
                "actions": [
                    {"temporary_id": t1, "type": "send-email",
                     "data": {"message": {
                         "from_email": "hello@bargainchemist.co.nz", "from_label": "BC",
                         "reply_to_email": "orders@bargainchemist.co.nz",
                         "cc_email": None, "bcc_email": None, "subject_line": "probe",
                         "preview_text": "", "smart_sending_enabled": True,
                         "transactional": False, "add_tracking_params": True,
                         "custom_tracking_params": None, "additional_filters": None,
                         "name": "_probe"}, "status": "draft"},
                     "links": {"next": None}},
                ],
            }}}}

    def try_trigger(label, tf):
        r = requests.post(f"{BASE_URL}/flows", headers=HEADERS,
                          json=flow_with_trigger_filter(tf), timeout=30)
        if r.ok:
            fid = r.json()["data"]["id"]
            print(f"  [ACCEPTED] {label} -> {fid}")
            requests.delete(f"{BASE_URL}/flows/{fid}", headers=HEADERS, timeout=15)
            time.sleep(0.3)
        else:
            print(f"  [REJECTED] {label}")
            try:
                for e in r.json().get("errors", []):
                    print(f"    detail: {e.get('detail')}")
                    print(f"    source: {e.get('source')}")
            except Exception:
                print(f"    raw: {r.text[:300]}")
            time.sleep(0.35)

    try_trigger("trigger_filter=null (baseline)", None)
    try_trigger("trigger_filter={condition_groups:[]}",
                {"condition_groups": []})
    try_trigger("trigger_filter with profile-property (email is set)",
                {"condition_groups": [{"conditions": [{
                    "type": "profile-property",
                    "property": "$email",
                    "filter": {"type": "string", "operator": "is-set"}
                }]}]})


# ── Part 5: Read full definition of a known-configured external flow ──────────

def read_external_flow_definitions():
    section("PART 5: Read definitions of all flows looking for non-null profile_filter")
    flows_resp = requests.get(f"{BASE_URL}/flows",
                              headers=HEADERS,
                              params={"fields[flow]": "name,status", "page[size]": 50},
                              timeout=15)
    flows_resp.raise_for_status()
    flows = flows_resp.json().get("data", [])

    for flow in flows:
        fid = flow["id"]
        fname = flow["attributes"]["name"]
        r = requests.get(f"{BASE_URL}/flows/{fid}",
                         headers=HEADERS,
                         params={"additional-fields[flow]": "definition"},
                         timeout=15)
        if not r.ok:
            continue
        defn = r.json()["data"]["attributes"].get("definition", {})
        if not defn:
            continue
        # Look for any action with non-null profile_filter
        for action in defn.get("actions", []):
            if action.get("type") == "conditional-split":
                pf = action.get("data", {}).get("profile_filter")
                if pf is not None:
                    print(f"\nFOUND non-null profile_filter in '{fname}' ({fid})!")
                    print(f"  Action id: {action['id']}")
                    print(f"  profile_filter: {json.dumps(pf, indent=4)}")
        time.sleep(0.15)

    print("\n(Scan complete)")


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    probe_profile_property_filters()
    probe_more_types()
    probe_patch_action()
    probe_trigger_filter()
    read_external_flow_definitions()

    print("\n\nDone.")


if __name__ == "__main__":
    main()
