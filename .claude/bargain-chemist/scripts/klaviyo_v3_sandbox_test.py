"""Y84ruV-v3 sandbox — empirical test of Klaviyo conditional-split runtime routing
on metric_filters with $value across 9 boundary cases.

This is the proof-of-runtime test before we trust conditional-split for the real
Y84ruV redesign.

Phases (run in sequence with --phase flag):

  --phase=build     Create a sandbox test flow and audit list.
                    Flow triggers only for profiles with property is_test_profile=true.
                    3-branch conditional-split on Checkout Started $value:
                       <$30  -> Tier A email
                       <$79  -> Tier B email
                       else  -> Tier C email
                    Status starts DRAFT. Prints flow_id.

  --phase=inject    Sets flow live, then for each of 9 boundary $values:
                       1. Creates test profile harpreetsingh+cart-tier-{N}@bargainchemist.co.nz
                       2. Subscribes to email marketing
                       3. Sets is_test_profile=true on profile
                       4. Tracks synthetic Checkout Started event with $value=N
                       5. (Event triggers flow because metric matches)

  --phase=verify    Queries Received Email events for each test profile, identifies
                    which message_id was sent, compares vs expected tier.
                    Run AFTER waiting 8+ minutes (sandbox flow has 5min delay).

  --phase=cleanup   Sets flow back to DRAFT to stop firing.

User runs: build -> inject -> wait 8 min -> verify -> cleanup.

Boundary cases: $5, $20, $29, $30, $50, $78, $79, $80, $120
"""
import argparse
import json
import sys
import time
from datetime import date, datetime
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/v3-sandbox"
OUT.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUT / "state.json"

REVISION_CREATE = "2024-10-15.pre"
REVISION_GET = "2025-10-15"
TEMPLATE_ID = "UH72Vm"
TEST_EMAIL_BASE = "harpreetsingh+cart-tier"
TEST_EMAIL_DOMAIN = "bargainchemist.co.nz"

BOUNDARIES = [5, 20, 29, 30, 50, 78, 79, 80, 120]


def expected_tier(v):
    if v < 30: return "A"
    if v < 79: return "B"
    return "C"


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
    p.write_text(json.dumps(data, indent=2) if isinstance(data, dict) else str(data),
                 encoding="utf-8")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def write_state(d):
    STATE_FILE.write_text(json.dumps(d, indent=2))


# =================================================================
# PHASE 2: BUILD
# =================================================================

def build_sandbox_flow_definition():
    """Sandbox flow: trigger=Checkout Started, audience=is_test_profile=true,
    5min delay, 3-branch conditional-split, 3 simple email actions."""
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "PROBE - Y84ruV-v3 sandbox conditional-split runtime test",
                "definition": {
                    "triggers": [{"type": "metric", "id": "VvcTue"}],
                    "profile_filter": {
                        "condition_groups": [
                            # Audience: only test profiles
                            {"conditions": [{
                                "type": "profile-property",
                                "property": "properties['is_test_profile']",
                                "filter": {"type": "string", "operator": "equals", "value": "true"}
                            }]},
                            # Marketability
                            {"conditions": [{
                                "type": "profile-marketing-consent",
                                "consent": {
                                    "channel": "email",
                                    "can_receive_marketing": True,
                                    "consent_status": {"subscription": "any", "filters": None}
                                }
                            }]}
                        ]
                    },
                    "entry_action_id": "delay-1",
                    "actions": [
                        {
                            "temporary_id": "delay-1",
                            "type": "time-delay",
                            "data": {"unit": "minutes", "value": 5,
                                     "secondary_value": None, "timezone": "profile"},
                            "links": {"next": "split-A"}
                        },
                        # Split A: < $30 -> Tier A, else -> Split B
                        {
                            "temporary_id": "split-A",
                            "type": "conditional-split",
                            "data": {
                                "profile_filter": {
                                    "condition_groups": [{
                                        "conditions": [{
                                            "type": "profile-metric",
                                            "metric_id": "VvcTue",
                                            "measurement": "count",
                                            "measurement_filter": {
                                                "type": "numeric", "operator": "greater-than", "value": 0
                                            },
                                            "timeframe_filter": {
                                                "type": "date", "operator": "flow-start"
                                            },
                                            "metric_filters": [{
                                                "property": "$value",
                                                "filter": {"type": "numeric", "operator": "less-than", "value": 30}
                                            }]
                                        }]
                                    }]
                                }
                            },
                            "links": {"next_if_true": "email-A", "next_if_false": "split-B"}
                        },
                        # Split B: < $79 -> Tier B, else -> Tier C
                        {
                            "temporary_id": "split-B",
                            "type": "conditional-split",
                            "data": {
                                "profile_filter": {
                                    "condition_groups": [{
                                        "conditions": [{
                                            "type": "profile-metric",
                                            "metric_id": "VvcTue",
                                            "measurement": "count",
                                            "measurement_filter": {
                                                "type": "numeric", "operator": "greater-than", "value": 0
                                            },
                                            "timeframe_filter": {
                                                "type": "date", "operator": "flow-start"
                                            },
                                            "metric_filters": [{
                                                "property": "$value",
                                                "filter": {"type": "numeric", "operator": "less-than", "value": 79}
                                            }]
                                        }]
                                    }]
                                }
                            },
                            "links": {"next_if_true": "email-B", "next_if_false": "email-C"}
                        },
                        {
                            "temporary_id": "email-A",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "PROBE - Tier A",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE-A] Tier A: cart < $30",
                                    "preview_text": "tier A test",
                                    "template_id": TEMPLATE_ID,
                                    "smart_sending_enabled": False,
                                    "transactional": False, "add_tracking_params": True,
                                    "custom_tracking_params": None, "additional_filters": None
                                }, "status": "draft"
                            }, "links": {"next": None}
                        },
                        {
                            "temporary_id": "email-B",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "PROBE - Tier B",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE-B] Tier B: cart $30-78",
                                    "preview_text": "tier B test",
                                    "template_id": TEMPLATE_ID,
                                    "smart_sending_enabled": False,
                                    "transactional": False, "add_tracking_params": True,
                                    "custom_tracking_params": None, "additional_filters": None
                                }, "status": "draft"
                            }, "links": {"next": None}
                        },
                        {
                            "temporary_id": "email-C",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "PROBE - Tier C",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE-C] Tier C: cart >= $79",
                                    "preview_text": "tier C test",
                                    "template_id": TEMPLATE_ID,
                                    "smart_sending_enabled": False,
                                    "transactional": False, "add_tracking_params": True,
                                    "custom_tracking_params": None, "additional_filters": None
                                }, "status": "draft"
                            }, "links": {"next": None}
                        }
                    ]
                }
            }
        }
    }


def phase_build(key):
    print("Phase BUILD: POST sandbox flow as DRAFT")
    body = build_sandbox_flow_definition()
    save("posted-flow.json", body)
    r = requests.post("https://a.klaviyo.com/api/flows/",
                      headers=hdrs(key, REVISION_CREATE, content=True), json=body, timeout=60)
    save("post-response.json", r.json() if r.status_code < 400 else {"status": r.status_code, "body": r.text})
    if r.status_code not in (200, 201):
        print(f"  POST FAILED HTTP {r.status_code}: {r.text[:400]}")
        return 1
    flow_id = r.json()["data"]["id"]

    # Find the 3 send-email action ids and message ids from the response
    actions = r.json()["data"]["attributes"]["definition"]["actions"]
    tier_actions = {}
    for a in actions:
        if a.get("type") == "send-email":
            name = a["data"]["message"]["name"]
            tier = name.split("Tier ")[-1].strip()
            tier_actions[tier] = {
                "action_id": a["id"],
                "message_id": a["data"]["message"]["id"],
                "template_id": a["data"]["message"]["template_id"],
            }

    state = {"flow_id": flow_id, "tier_actions": tier_actions, "status": "draft"}
    write_state(state)
    print(f"  flow_id: {flow_id}")
    print(f"  tier_actions: {json.dumps(tier_actions, indent=4)}")
    print(f"  Status: DRAFT (won't fire). Run --phase=inject to activate + inject events.")
    return 0


# =================================================================
# PHASE 3: INJECT
# =================================================================

def upsert_profile(email, key):
    """Create profile or fetch existing. Sets is_test_profile=true."""
    body = {
        "data": {
            "type": "profile",
            "attributes": {
                "email": email,
                "properties": {"is_test_profile": "true"}
            }
        }
    }
    r = requests.post("https://a.klaviyo.com/api/profiles/",
                      headers=hdrs(key, REVISION_GET, content=True), json=body, timeout=20)
    if r.status_code == 201:
        return r.json()["data"]["id"]
    if r.status_code == 409:
        # Already exists — extract id from error and PATCH the property
        err = r.json().get("errors", [{}])[0]
        existing_id = (err.get("meta", {}).get("duplicate_profile_id"))
        if not existing_id:
            return None
        # PATCH to ensure is_test_profile is set
        patch_body = {
            "data": {
                "type": "profile", "id": existing_id,
                "attributes": {"properties": {"is_test_profile": "true"}}
            }
        }
        requests.patch(f"https://a.klaviyo.com/api/profiles/{existing_id}/",
                       headers=hdrs(key, REVISION_GET, content=True), json=patch_body, timeout=20)
        return existing_id
    raise RuntimeError(f"upsert_profile {email} HTTP {r.status_code}: {r.text[:200]}")


def subscribe_marketing(email, key):
    body = {
        "data": {
            "type": "profile-subscription-bulk-create-job",
            "attributes": {
                "profiles": {
                    "data": [{
                        "type": "profile",
                        "attributes": {
                            "email": email,
                            "subscriptions": {
                                "email": {"marketing": {"consent": "SUBSCRIBED"}}
                            }
                        }
                    }]
                }
            }
        }
    }
    r = requests.post("https://a.klaviyo.com/api/profile-subscription-bulk-create-jobs/",
                      headers=hdrs(key, REVISION_GET, content=True), json=body, timeout=20)
    return r.status_code in (200, 202)


def track_checkout_started(email, value, key):
    """Use Klaviyo Track API to fire a synthetic Checkout Started event."""
    body = {
        "data": {
            "type": "event",
            "attributes": {
                "properties": {
                    "$value": value,
                    "$extra": {"test_profile": True, "boundary_test_value": value},
                    "Item Count": 1,
                    "Source Name": "test"
                },
                "metric": {
                    "data": {"type": "metric", "attributes": {"name": "Checkout Started"}}
                },
                "profile": {
                    "data": {"type": "profile", "attributes": {"email": email}}
                },
                "value": value
            }
        }
    }
    r = requests.post("https://a.klaviyo.com/api/events/",
                      headers=hdrs(key, REVISION_GET, content=True), json=body, timeout=20)
    return r.status_code, r.text[:200]


def set_flow_status(flow_id, status, key):
    """PATCH flow status (live | draft | manual)."""
    body = {"data": {"type": "flow", "id": flow_id, "attributes": {"status": status}}}
    r = requests.patch(f"https://a.klaviyo.com/api/flows/{flow_id}/",
                       headers=hdrs(key, REVISION_GET, content=True), json=body, timeout=30)
    return r.status_code, r.text[:300]


def phase_inject(key):
    state = load_state()
    if not state.get("flow_id"):
        print("ERROR: state has no flow_id — run --phase=build first")
        return 1
    flow_id = state["flow_id"]

    print(f"Phase INJECT: activate flow {flow_id} + inject {len(BOUNDARIES)} events")
    code, body = set_flow_status(flow_id, "live", key)
    if code != 200:
        print(f"  set_flow_status FAILED HTTP {code}: {body}")
        return 1
    state["status"] = "live"
    write_state(state)
    print(f"  Flow status: live")

    profiles = {}
    for v in BOUNDARIES:
        email = f"{TEST_EMAIL_BASE}-{v}@{TEST_EMAIL_DOMAIN}"
        print(f"\n  v={v} ({email})")
        try:
            pid = upsert_profile(email, key)
            print(f"    profile_id: {pid}")
        except Exception as e:
            print(f"    upsert FAILED: {e}")
            continue
        sub_ok = subscribe_marketing(email, key)
        print(f"    subscribed: {sub_ok}")
        time.sleep(0.5)
        code, body = track_checkout_started(email, v, key)
        print(f"    track Checkout Started ($value={v}): HTTP {code}")
        if code not in (200, 202):
            print(f"    track FAIL body: {body}")
        profiles[v] = {"email": email, "profile_id": pid, "expected_tier": expected_tier(v)}
        time.sleep(0.5)

    state["profiles"] = profiles
    state["injected_at"] = datetime.utcnow().isoformat() + "Z"
    write_state(state)
    print(f"\n  All {len(profiles)} profiles injected.")
    print(f"  Wait 8+ minutes (5min flow delay + buffer), then run --phase=verify")
    return 0


# =================================================================
# PHASE 3 verify: query routing
# =================================================================

def phase_verify(key):
    state = load_state()
    if not state.get("profiles"):
        print("ERROR: no injected profiles in state")
        return 1
    flow_id = state["flow_id"]
    tier_actions = state["tier_actions"]
    profiles = state["profiles"]

    # Build a reverse lookup: message_id -> tier
    msg_to_tier = {info["message_id"]: tier for tier, info in tier_actions.items()}
    print(f"Phase VERIFY: query Received Email events for {len(profiles)} test profiles\n")
    print(f"  flow_id: {flow_id}")
    print(f"  message_id -> tier mapping: {msg_to_tier}\n")

    # For each profile, query its recent events
    results = []
    for v_str, info in sorted(profiles.items(), key=lambda kv: float(kv[0])):
        v = float(v_str)
        email = info["email"]
        pid = info["profile_id"]
        expected = info["expected_tier"]

        # Get events for this profile, look for Received Email from our test flow
        url = (f"https://a.klaviyo.com/api/events/?filter=equals(profile_id,\"{pid}\")"
               "&include=metric&page%5Bsize%5D=50")
        r = requests.get(url, headers=hdrs(key, REVISION_GET), timeout=20)
        if r.status_code != 200:
            results.append((v, email, expected, "GET_FAIL", "", False))
            continue

        events = r.json().get("data", [])
        # Find Received Email events whose attributed message_id is in our tier set
        actual_tier = None
        for ev in events:
            mid = ev.get("attributes", {}).get("event_properties", {}).get("$message")
            if mid in msg_to_tier:
                actual_tier = msg_to_tier[mid]
                break
        match = (actual_tier == expected) if actual_tier else False
        results.append((v, email, expected, actual_tier or "no-event-yet", "", match))

    print(f"\n{'value':>6} {'email':<60} expect actual match")
    print("-" * 100)
    all_pass = True
    for v, email, exp, act, _, match in results:
        ok = "PASS" if match else "FAIL"
        all_pass = all_pass and match
        print(f"  ${v:>5.0f} {email:<60} {exp:<6} {act:<6} {ok}")

    save("verify-results.json", [{"value": v, "email": e, "expected_tier": exp,
                                  "actual_tier": a, "match": m}
                                 for v, e, exp, a, _, m in results])

    if all_pass:
        print(f"\n  ALL {len(results)} BOUNDARY CASES ROUTED CORRECTLY")
    else:
        print(f"\n  ROUTING INCONSISTENCIES — runtime conditional-split with metric_filters has bugs")
    return 0 if all_pass else 1


def phase_cleanup(key):
    state = load_state()
    if not state.get("flow_id"):
        return 1
    flow_id = state["flow_id"]
    code, body = set_flow_status(flow_id, "draft", key)
    print(f"Phase CLEANUP: flow {flow_id} -> draft  (HTTP {code})")
    return 0 if code == 200 else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", choices=["build", "inject", "verify", "cleanup"], required=True)
    args = ap.parse_args()
    key = load_key()
    if args.phase == "build":  return phase_build(key)
    if args.phase == "inject": return phase_inject(key)
    if args.phase == "verify": return phase_verify(key)
    if args.phase == "cleanup":return phase_cleanup(key)


if __name__ == "__main__":
    raise SystemExit(main())
