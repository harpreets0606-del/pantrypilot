"""Phase 1: Syntactic probe for Klaviyo conditional-split with metric_filters on $value.

Goal: verify Klaviyo's POST /api/flows endpoint accepts a 3-branch conditional-split
that filters on `Checkout Started where $value < N` AND preserves the metric_filters
field on round-trip GET. If syntax round-trips cleanly, runtime routing has a chance.

Test design:
  Build minimal test flow: trigger=metric VvcTue, profile_filter=marketability,
  one conditional-split with metric_filters on $value, two send-email branches.
  POST as draft. GET back. Compare written vs read metric_filters.

This validates SYNTAX but NOT runtime routing. Runtime is Phase 3.

Run: python klaviyo_probe_conditional_split.py
"""
import json
import sys
import time
from datetime import date
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/probe-condsplit"
OUT.mkdir(parents=True, exist_ok=True)
REVISION_CREATE = "2024-10-15.pre"
REVISION_GET = "2025-10-15"

# Need a working template id for the send-email actions (any owned template)
PLACEHOLDER_TEMPLATE_ID = "UH72Vm"


def load_key():
    text = ENV_FILE.read_text(encoding="utf-8-sig")
    for raw in text.splitlines():
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export "):].strip()
        if line.startswith("KLAVIYO_PRIVATE_KEY"):
            _, _, val = line.partition("=")
            val = val.strip().strip('"').strip("'")
            if val:
                return val
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing")


def hdrs(key, revision, content=False):
    h = {"Authorization": f"Klaviyo-API-Key {key}", "revision": revision,
         "Accept": "application/vnd.api+json"}
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, data):
    p = OUT / name
    p.write_text(
        json.dumps(data, indent=2) if isinstance(data, dict) else str(data),
        encoding="utf-8",
    )


def build_test_flow_definition():
    """A trigger=Checkout Started flow with one conditional-split branching on
    Checkout Started events with $value < 30 (since flow-start). If yes -> emailA,
    if no -> emailB. Tests metric_filters round-trip."""
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "PROBE - conditional-split metric_filters on $value",
                "definition": {
                    "triggers": [{"type": "metric", "id": "VvcTue"}],
                    "profile_filter": {
                        "condition_groups": [
                            {"conditions": [{
                                "type": "profile-marketing-consent",
                                "consent": {
                                    "channel": "email",
                                    "can_receive_marketing": True,
                                    "consent_status": {"subscription": "any", "filters": None},
                                },
                            }]}
                        ]
                    },
                    "entry_action_id": "split-1",
                    "actions": [
                        {
                            "temporary_id": "split-1",
                            "type": "conditional-split",
                            "data": {
                                "profile_filter": {
                                    "condition_groups": [
                                        {"conditions": [{
                                            "type": "profile-metric",
                                            "metric_id": "VvcTue",
                                            "measurement": "count",
                                            "measurement_filter": {
                                                "type": "numeric",
                                                "operator": "greater-than",
                                                "value": 0
                                            },
                                            "timeframe_filter": {
                                                "type": "date",
                                                "operator": "flow-start"
                                            },
                                            "metric_filters": [
                                                {
                                                    "property": "$value",
                                                    "filter": {
                                                        "type": "numeric",
                                                        "operator": "less-than",
                                                        "value": 30
                                                    }
                                                }
                                            ]
                                        }]}
                                    ]
                                }
                            },
                            "links": {
                                "next_if_true": "email-A",
                                "next_if_false": "email-B"
                            }
                        },
                        {
                            "temporary_id": "email-A",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "PROBE - Tier A (under $30)",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE A] Cart under $30",
                                    "preview_text": "probe",
                                    "template_id": PLACEHOLDER_TEMPLATE_ID,
                                    "smart_sending_enabled": True,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None,
                                },
                                "status": "draft"
                            },
                            "links": {"next": None}
                        },
                        {
                            "temporary_id": "email-B",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "PROBE - Tier B+C ($30+)",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE B] Cart $30+",
                                    "preview_text": "probe",
                                    "template_id": PLACEHOLDER_TEMPLATE_ID,
                                    "smart_sending_enabled": True,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None,
                                },
                                "status": "draft"
                            },
                            "links": {"next": None}
                        }
                    ]
                }
            }
        }
    }


def main():
    key = load_key()
    body = build_test_flow_definition()
    save("posted-flow.json", body)

    # POST as draft
    print("Phase 1.1: POST /api/flows with conditional-split using metric_filters on $value...")
    r = requests.post(
        "https://a.klaviyo.com/api/flows/",
        headers=hdrs(key, REVISION_CREATE, content=True), json=body, timeout=60,
    )
    save("post-response.json",
         r.json() if r.status_code < 400 else {"status": r.status_code, "body": r.text})
    if r.status_code not in (200, 201):
        print(f"  POST FAILED HTTP {r.status_code}: {r.text[:400]}")
        return 1
    flow_id = r.json()["data"]["id"]
    print(f"  POST OK. flow_id={flow_id}")

    # GET back with full definition
    print(f"\nPhase 1.2: GET /api/flows/{flow_id}/?additional-fields[flow]=definition")
    r = requests.get(
        f"https://a.klaviyo.com/api/flows/{flow_id}/?additional-fields%5Bflow%5D=definition",
        headers=hdrs(key, REVISION_GET), timeout=30,
    )
    save("get-response.json", r.json() if r.status_code < 400 else {"status": r.status_code, "body": r.text})
    if r.status_code != 200:
        print(f"  GET FAILED: {r.status_code}")
        return 1

    # Inspect the conditional-split's metric_filters
    defn = r.json()["data"]["attributes"]["definition"]
    actions = defn.get("actions", [])
    split = next((a for a in actions if a.get("type") == "conditional-split"), None)
    if not split:
        print("  GET response has no conditional-split action!")
        return 1

    pf = split.get("data", {}).get("profile_filter", {})
    cgs = pf.get("condition_groups", [])
    if not cgs:
        print("  conditional-split has no condition_groups!")
        return 1

    cond = cgs[0].get("conditions", [{}])[0]
    print(f"\n  conditional-split GET-back inspection:")
    print(f"    type:                 {cond.get('type')}")
    print(f"    metric_id:            {cond.get('metric_id')}")
    print(f"    measurement:          {cond.get('measurement')}")
    print(f"    measurement_filter:   {cond.get('measurement_filter')}")
    print(f"    timeframe_filter:     {cond.get('timeframe_filter')}")
    print(f"    metric_filters:       {json.dumps(cond.get('metric_filters'))}")

    # Compare to what we POSTed
    if cond.get("metric_filters"):
        mf = cond["metric_filters"][0]
        prop_ok = mf.get("property") == "$value"
        op_ok = mf.get("filter", {}).get("operator") == "less-than"
        val_ok = mf.get("filter", {}).get("value") == 30
        print(f"\n  Round-trip check:")
        print(f"    property == '$value':       {prop_ok}")
        print(f"    operator == 'less-than':    {op_ok}")
        print(f"    value == 30:                {val_ok}")
        if prop_ok and op_ok and val_ok:
            print(f"\n  PHASE 1 PASS: Klaviyo accepted + round-tripped metric_filters with $value")
            print(f"\n  Next: examine flow_id={flow_id} in Klaviyo UI to see canvas representation,")
            print(f"  then proceed to Phase 2 (build sandbox v3) and Phase 3 (synthetic event tests).")
            return 0
        else:
            print(f"\n  PHASE 1 FAIL: round-trip lost or mutated metric_filters")
            return 1
    else:
        print(f"\n  PHASE 1 FAIL: GET-back has metric_filters=null. Klaviyo silently dropped it.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
