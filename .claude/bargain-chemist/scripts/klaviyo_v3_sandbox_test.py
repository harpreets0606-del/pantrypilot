"""Y84ruV-v3 sandbox — empirical test of Klaviyo conditional-split runtime routing
on metric_filters with $value across 9 boundary cases.

v2 — fixes 3 root-cause bugs from v1:
  BUG 1 WRONG METRIC: Synthetic API events create metric XyMJz4 (API integration),
        not VvcTue (Shopify integration). Flow triggered on VvcTue — profiles never
        entered. Fix: use XyMJz4 in both trigger AND split conditions.
  BUG 2 SUBSCRIPTION LAG: Checkout Started fired 68s before subscription completed.
        Marketability filter blocked entry. Fix: subscribe all 9 profiles, wait 120s,
        THEN fire all events in a batch.
  BUG 3 DRAFT MESSAGES: send-email actions with status="draft" — Klaviyo queues but
        never sends. "Received Email" events never fire. Fix: PATCH all send-email
        actions to status="live" after building flow.

Phases (run in sequence):

  --phase=build     Create sandbox test flow (DRAFT). Trigger = XyMJz4 (API metric).
                    3-branch conditional-split on Checkout Started XyMJz4 $value:
                       <$30  -> Tier A email
                       <$79  -> Tier B email
                       else  -> Tier C email
                    Audience: is_test_profile=true (blocks real customers).
                    After POST, PATCHes all 3 send-email actions to status=live
                    so emails actually send and produce Received Email events.

  --phase=inject    Sets flow live. Subscribes all 9 profiles. Waits 120s for
                    subscription propagation. Then fires all 9 Checkout Started events.
                    Boundary values: 5, 20, 29, 30, 50, 78, 79, 80, 120.

  --phase=verify    Queries Received Email events per profile, maps message_id -> tier.
                    Run AFTER waiting 8+ minutes (5min flow delay + execution buffer).

  --phase=cleanup   Sets flow back to DRAFT to stop firing.

User runs: build -> inject -> wait 8 min -> verify -> (review results) -> cleanup
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
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/v3-sandbox-v2"
OUT.mkdir(parents=True, exist_ok=True)
STATE_FILE = OUT / "state.json"

REVISION_CREATE = "2024-10-15.pre"
REVISION_GET = "2025-10-15"
TEMPLATE_ID = "UH72Vm"
TEST_EMAIL_BASE = "harpreetsingh+cart-tier"
TEST_EMAIL_DOMAIN = "bargainchemist.co.nz"

# XyMJz4 = API-tracked "Checkout Started" created by our synthetic events.
# We use this instead of VvcTue (Shopify) because API events cannot fire Shopify metrics.
API_CHECKOUT_METRIC_ID = "XyMJz4"

BOUNDARIES = [5, 20, 29, 30, 50, 78, 79, 80, 120]

# Subscription propagation wait. Klaviyo subscription bulk-create jobs are async;
# in testing the job took ~68 seconds to process. 120s provides safe headroom.
SUBSCRIPTION_WAIT_SECONDS = 120


def expected_tier(v):
    if v < 30:
        return "A"
    if v < 79:
        return "B"
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
    sys.exit("ERROR: KLAVIYO_PRIVATE_KEY missing in .env.local")


def hdrs(key, revision, content=False):
    h = {"Authorization": f"Klaviyo-API-Key {key}", "revision": revision,
         "Accept": "application/vnd.api+json"}
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def save(name, data):
    p = OUT / name
    p.write_text(json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data),
                 encoding="utf-8")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {}


def write_state(d):
    STATE_FILE.write_text(json.dumps(d, indent=2))


# =================================================================
# PHASE: BUILD
# =================================================================

def build_sandbox_flow_definition():
    """Sandbox flow using XyMJz4 (API metric) so synthetic events trigger it.
    5-min delay then 2 chained conditional-splits for 3-branch routing."""
    return {
        "data": {
            "type": "flow",
            "attributes": {
                "name": "PROBE-v2 - Y84ruV-v3 sandbox conditional-split runtime test",
                "definition": {
                    "triggers": [{"type": "metric", "id": API_CHECKOUT_METRIC_ID}],
                    "profile_filter": {
                        "condition_groups": [
                            # Audience: only test profiles (blocks real customers)
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
                        # Split A: Checkout Started (XyMJz4) where $value < 30 -> Tier A
                        {
                            "temporary_id": "split-A",
                            "type": "conditional-split",
                            "data": {
                                "profile_filter": {
                                    "condition_groups": [{
                                        "conditions": [{
                                            "type": "profile-metric",
                                            "metric_id": API_CHECKOUT_METRIC_ID,
                                            "measurement": "count",
                                            "measurement_filter": {
                                                "type": "numeric", "operator": "greater-than", "value": 0
                                            },
                                            "timeframe_filter": {
                                                "type": "date", "operator": "flow-start"
                                            },
                                            "metric_filters": [{
                                                "property": "$value",
                                                "filter": {
                                                    "type": "numeric",
                                                    "operator": "less-than",
                                                    "value": 30
                                                }
                                            }]
                                        }]
                                    }]
                                }
                            },
                            "links": {"next_if_true": "email-A", "next_if_false": "split-B"}
                        },
                        # Split B: Checkout Started (XyMJz4) where $value < 79 -> Tier B
                        {
                            "temporary_id": "split-B",
                            "type": "conditional-split",
                            "data": {
                                "profile_filter": {
                                    "condition_groups": [{
                                        "conditions": [{
                                            "type": "profile-metric",
                                            "metric_id": API_CHECKOUT_METRIC_ID,
                                            "measurement": "count",
                                            "measurement_filter": {
                                                "type": "numeric", "operator": "greater-than", "value": 0
                                            },
                                            "timeframe_filter": {
                                                "type": "date", "operator": "flow-start"
                                            },
                                            "metric_filters": [{
                                                "property": "$value",
                                                "filter": {
                                                    "type": "numeric",
                                                    "operator": "less-than",
                                                    "value": 79
                                                }
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
                                    "name": "PROBE-v2 Tier A (<$30)",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE-A] Tier A: cart under $30",
                                    "preview_text": "probe tier A",
                                    "template_id": TEMPLATE_ID,
                                    "smart_sending_enabled": False,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None
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
                                    "name": "PROBE-v2 Tier B ($30-$78)",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE-B] Tier B: cart $30-$78",
                                    "preview_text": "probe tier B",
                                    "template_id": TEMPLATE_ID,
                                    "smart_sending_enabled": False,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None
                                },
                                "status": "draft"
                            },
                            "links": {"next": None}
                        },
                        {
                            "temporary_id": "email-C",
                            "type": "send-email",
                            "data": {
                                "message": {
                                    "name": "PROBE-v2 Tier C ($79+)",
                                    "from_email": "hello@bargainchemist.co.nz",
                                    "from_label": "Bargain Chemist",
                                    "subject_line": "[PROBE-C] Tier C: cart $79+",
                                    "preview_text": "probe tier C",
                                    "template_id": TEMPLATE_ID,
                                    "smart_sending_enabled": False,
                                    "transactional": False,
                                    "add_tracking_params": True,
                                    "custom_tracking_params": None,
                                    "additional_filters": None
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


def patch_flow_action_live(action_id, key):
    """PATCH a send-email flow action to status=live so emails actually send."""
    body = {
        "data": {
            "type": "flow-action",
            "id": action_id,
            "attributes": {"status": "live"}
        }
    }
    r = requests.patch(
        f"https://a.klaviyo.com/api/flow-actions/{action_id}/",
        headers=hdrs(key, REVISION_GET, content=True),
        json=body,
        timeout=20
    )
    return r.status_code, r.text[:200]


def phase_build(key):
    print("Phase BUILD: POST sandbox flow (trigger=XyMJz4 API metric) as DRAFT")
    body = build_sandbox_flow_definition()
    save("posted-flow.json", body)

    r = requests.post(
        "https://a.klaviyo.com/api/flows/",
        headers=hdrs(key, REVISION_CREATE, content=True),
        json=body,
        timeout=60
    )
    resp_data = r.json() if r.status_code < 500 else {"status": r.status_code, "body": r.text}
    save("post-response.json", resp_data)

    if r.status_code not in (200, 201):
        print(f"  POST FAILED HTTP {r.status_code}: {r.text[:600]}")
        return 1

    flow_id = r.json()["data"]["id"]
    actions = r.json()["data"]["attributes"]["definition"]["actions"]

    tier_actions = {}
    for a in actions:
        if a.get("type") == "send-email":
            name = a["data"]["message"]["name"]
            if "Tier A" in name:
                tier = "A"
            elif "Tier B" in name:
                tier = "B"
            elif "Tier C" in name:
                tier = "C"
            else:
                continue
            tier_actions[tier] = {
                "action_id": a["id"],
                "message_id": a["data"]["message"]["id"],
            }

    print(f"  flow_id: {flow_id}")
    print(f"  tier_actions: {json.dumps(tier_actions, indent=4)}")

    # PATCH all send-email actions to status=live (fix BUG 3)
    print(f"\n  PATCHing send-email actions to status=live (so emails actually send)...")
    all_live = True
    for tier, info in tier_actions.items():
        code, body_txt = patch_flow_action_live(info["action_id"], key)
        ok = code == 200
        print(f"    Tier {tier} action {info['action_id']}: HTTP {code} {'OK' if ok else 'FAIL: ' + body_txt}")
        all_live = all_live and ok

    if not all_live:
        print("  WARNING: some actions failed to go live — emails may not send")

    state = {
        "flow_id": flow_id,
        "tier_actions": tier_actions,
        "status": "draft",
        "api_metric_id": API_CHECKOUT_METRIC_ID,
        "built_at": datetime.utcnow().isoformat() + "Z"
    }
    write_state(state)
    print(f"\n  State saved to {STATE_FILE}")
    print(f"  Flow is DRAFT. Run --phase=inject to activate + inject events.")
    return 0


# =================================================================
# PHASE: INJECT
# =================================================================

def upsert_profile(email, key):
    """Create or find profile. Returns profile_id."""
    body = {
        "data": {
            "type": "profile",
            "attributes": {
                "email": email,
                "properties": {"is_test_profile": "true"}
            }
        }
    }
    r = requests.post(
        "https://a.klaviyo.com/api/profiles/",
        headers=hdrs(key, REVISION_GET, content=True),
        json=body,
        timeout=20
    )
    if r.status_code == 201:
        return r.json()["data"]["id"]
    if r.status_code == 409:
        err = r.json().get("errors", [{}])[0]
        existing_id = err.get("meta", {}).get("duplicate_profile_id")
        if existing_id:
            # Ensure is_test_profile is set
            patch = {
                "data": {
                    "type": "profile", "id": existing_id,
                    "attributes": {"properties": {"is_test_profile": "true"}}
                }
            }
            requests.patch(
                f"https://a.klaviyo.com/api/profiles/{existing_id}/",
                headers=hdrs(key, REVISION_GET, content=True),
                json=patch,
                timeout=20
            )
            return existing_id
    raise RuntimeError(f"upsert_profile {email}: HTTP {r.status_code} {r.text[:200]}")


def subscribe_marketing(email, key):
    """Submit async subscription job. Returns HTTP status code."""
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
    r = requests.post(
        "https://a.klaviyo.com/api/profile-subscription-bulk-create-jobs/",
        headers=hdrs(key, REVISION_GET, content=True),
        json=body,
        timeout=20
    )
    return r.status_code


def track_checkout_started(email, value, key):
    """Track synthetic Checkout Started event. Must match XyMJz4 (API metric)
    by using metric name 'Checkout Started' — Klaviyo will resolve to XyMJz4."""
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
                    "data": {
                        "type": "metric",
                        "attributes": {"name": "Checkout Started"}
                    }
                },
                "profile": {
                    "data": {
                        "type": "profile",
                        "attributes": {"email": email}
                    }
                },
                "value": value
            }
        }
    }
    r = requests.post(
        "https://a.klaviyo.com/api/events/",
        headers=hdrs(key, REVISION_GET, content=True),
        json=body,
        timeout=20
    )
    return r.status_code, r.text[:200]


def set_flow_status(flow_id, status, key):
    body = {"data": {"type": "flow", "id": flow_id, "attributes": {"status": status}}}
    r = requests.patch(
        f"https://a.klaviyo.com/api/flows/{flow_id}/",
        headers=hdrs(key, REVISION_GET, content=True),
        json=body,
        timeout=30
    )
    return r.status_code, r.text[:300]


def phase_inject(key):
    state = load_state()
    if not state.get("flow_id"):
        print("ERROR: no flow_id in state — run --phase=build first")
        return 1
    flow_id = state["flow_id"]

    # Activate flow
    print(f"Phase INJECT: setting flow {flow_id} to live")
    code, body = set_flow_status(flow_id, "live", key)
    if code != 200:
        print(f"  FAILED HTTP {code}: {body}")
        return 1
    state["status"] = "live"
    write_state(state)
    print(f"  Flow is live\n")

    # Step 1: create/update all 9 profiles and submit subscription jobs
    profiles = {}
    print(f"  Step 1: upsert + subscribe all {len(BOUNDARIES)} profiles")
    for v in BOUNDARIES:
        email = f"{TEST_EMAIL_BASE}-{v}@{TEST_EMAIL_DOMAIN}"
        try:
            pid = upsert_profile(email, key)
        except Exception as e:
            print(f"    v={v} upsert FAILED: {e}")
            continue
        sub_code = subscribe_marketing(email, key)
        print(f"    v={v:>4}  pid={pid}  subscribe HTTP {sub_code}")
        profiles[v] = {
            "email": email,
            "profile_id": pid,
            "expected_tier": expected_tier(v)
        }
        time.sleep(0.3)

    state["profiles"] = {str(k): v for k, v in profiles.items()}
    state["subscribed_at"] = datetime.utcnow().isoformat() + "Z"
    write_state(state)

    # Step 2: wait for async subscription jobs to process (BUG 2 fix)
    print(f"\n  Step 2: waiting {SUBSCRIPTION_WAIT_SECONDS}s for subscription jobs to process...")
    for remaining in range(SUBSCRIPTION_WAIT_SECONDS, 0, -10):
        print(f"    {remaining}s remaining...", flush=True)
        time.sleep(10)
    print(f"  Subscription wait complete.\n")

    # Step 3: fire all Checkout Started events
    print(f"  Step 3: tracking Checkout Started events for all {len(profiles)} profiles")
    for v, info in sorted(profiles.items()):
        code, body = track_checkout_started(info["email"], v, key)
        ok = "OK" if code in (200, 202) else f"FAIL: {body}"
        print(f"    v={v:>4}  HTTP {code}  {ok}")
        time.sleep(0.3)

    state["events_fired_at"] = datetime.utcnow().isoformat() + "Z"
    write_state(state)
    print(f"\n  All events fired. Wait 8+ minutes for flow delay + execution, then run --phase=verify")
    return 0


# =================================================================
# PHASE: ENSURE-LIVE
# =================================================================

def phase_ensure_live(key):
    """Force all 3 send-email actions to status=live.
    Run this if emails aren't sending — messages may be stuck in draft.
    Profiles queued at a draft action will be released and sent immediately."""
    state = load_state()
    if not state.get("tier_actions"):
        print("ERROR: no tier_actions in state — run --phase=build first")
        return 1
    tier_actions = state["tier_actions"]

    print(f"Phase ENSURE-LIVE: PATCHing all send-email actions to status=live")
    all_ok = True
    for tier in ["A", "B", "C"]:
        info = tier_actions.get(tier, {})
        action_id = info.get("action_id")
        if not action_id:
            print(f"  Tier {tier}: no action_id in state")
            all_ok = False
            continue
        code, body = patch_flow_action_live(action_id, key)
        ok = code == 200
        print(f"  Tier {tier}  action_id={action_id}  HTTP {code}  {'OK — now live' if ok else 'FAIL: ' + body}")
        all_ok = all_ok and ok

    if all_ok:
        print("\n  All actions live. Queued profiles will send within 1-2 minutes.")
        print("  Run --phase=verify in 3 minutes.")
    else:
        print("\n  Some actions failed. Check action IDs in state.json.")
    return 0 if all_ok else 1


# =================================================================
# PHASE: VERIFY
# =================================================================

def phase_verify(key):
    state = load_state()
    if not state.get("profiles"):
        print("ERROR: no injected profiles in state — run --phase=inject first")
        return 1

    flow_id = state["flow_id"]
    tier_actions = state["tier_actions"]
    profiles = state["profiles"]
    events_fired = state.get("events_fired_at", "unknown")

    # message_id -> tier reverse lookup
    msg_to_tier = {info["message_id"]: tier for tier, info in tier_actions.items()}
    print(f"Phase VERIFY: checking routing for {len(profiles)} profiles")
    print(f"  flow_id: {flow_id}")
    print(f"  Events fired at: {events_fired}")
    print(f"  message_id -> tier: {msg_to_tier}\n")

    results = []
    for v_str, info in sorted(profiles.items(), key=lambda kv: float(kv[0])):
        v = float(v_str)
        email = info["email"]
        pid = info["profile_id"]
        expected = info["expected_tier"]

        # Query all events for this profile, look for Received Email from our test flow
        url = (f"https://a.klaviyo.com/api/events/"
               f"?filter=equals(profile_id,\"{pid}\")"
               f"&page%5Bsize%5D=50")
        r = requests.get(url, headers=hdrs(key, REVISION_GET), timeout=20)
        if r.status_code != 200:
            print(f"  v={v}: GET events failed HTTP {r.status_code}")
            results.append({"value": v, "email": email, "expected": expected,
                            "actual": "GET_FAIL", "match": False, "events_found": []})
            continue

        events = r.json().get("data", [])
        actual_tier = None
        received_emails = []

        for ev in events:
            props = ev.get("attributes", {}).get("event_properties", {})
            # Check if this is a Received Email event tied to our test messages
            msg_id = props.get("$message")
            subject = props.get("Subject", "")
            if msg_id and msg_id in msg_to_tier:
                actual_tier = msg_to_tier[msg_id]
                received_emails.append({"message_id": msg_id, "subject": subject})

        match = (actual_tier == expected)
        status = "PASS" if match else ("no-email-yet" if not actual_tier else "WRONG-TIER")
        results.append({
            "value": v,
            "email": email,
            "expected": expected,
            "actual": actual_tier or "no-email-yet",
            "match": match,
            "received_emails": received_emails
        })

    # Print table
    print(f"{'$value':>7}  {'expected':>8}  {'actual':>14}  result")
    print("-" * 55)
    all_pass = True
    no_email_count = 0
    for r in results:
        v = r["value"]
        exp = r["expected"]
        act = r["actual"]
        match = r["match"]
        ok = "PASS" if match else ("⏳ no-email-yet" if act == "no-email-yet" else "❌ WRONG-TIER")
        if act == "no-email-yet":
            no_email_count += 1
        if not match:
            all_pass = False
        print(f"  ${v:>5.0f}     {exp:>8}  {act:>14}  {ok}")

    save("verify-results.json", results)

    print(f"\n  Results saved to {OUT}/verify-results.json")
    if no_email_count == len(results):
        print(f"\n  ⏳ All {len(results)} profiles: no email yet.")
        print(f"  Possible causes:")
        print(f"    a) Flow hasn't executed yet — wait longer and re-run verify")
        print(f"    b) Profiles failed audience filter (is_test_profile or marketability)")
        print(f"    c) Conditional-split silently failed")
        elapsed = ""
        if events_fired != "unknown":
            try:
                fired_dt = datetime.fromisoformat(events_fired.rstrip("Z"))
                elapsed_min = (datetime.utcnow() - fired_dt).total_seconds() / 60
                elapsed = f"  Time since events fired: {elapsed_min:.1f} minutes"
                print(elapsed)
            except Exception:
                pass
    elif all_pass:
        print(f"\n  ✅ ALL {len(results)} BOUNDARY CASES ROUTED CORRECTLY")
        print(f"  Conditional-split with metric_filters on $value works at runtime.")
        print(f"  NEXT: build Y84ruV-v3 production flow with 3-branch conditional-split.")
    else:
        wrong = [r for r in results if r["actual"] not in ("no-email-yet", "GET_FAIL") and not r["match"]]
        print(f"\n  ❌ ROUTING FAILURES: {len(wrong)} profiles routed to wrong tier")
        for r in wrong:
            print(f"    ${r['value']}: expected {r['expected']}, got {r['actual']}")
        print(f"  Runtime conditional-split with metric_filters has routing bugs.")

    return 0 if all_pass else 1


# =================================================================
# PHASE: CLEANUP
# =================================================================

def phase_reinject(key):
    """Fire fresh Checkout Started events for profiles that were BOT_PROTECTION suppressed
    during the original inject. Call this AFTER manually re-subscribing those profiles.
    Fires events only for profiles whose $value maps to boundaries given via --values."""
    import argparse as _ap
    # Parse --values from remaining argv
    import sys as _sys
    vals_raw = []
    for i, a in enumerate(_sys.argv):
        if a == "--values" and i + 1 < len(_sys.argv):
            vals_raw = _sys.argv[i + 1].split(",")
            break
    if not vals_raw:
        # Default: all Tier C + boundary v=78
        vals_raw = ["78", "79", "80", "120"]
    try:
        target_vals = [int(v.strip()) for v in vals_raw]
    except ValueError:
        print("ERROR: --values must be comma-separated integers e.g. --values=78,79,80,120")
        return 1

    state = load_state()
    if not state.get("flow_id"):
        print("ERROR: no flow_id in state — run --phase=build first")
        return 1

    print(f"Phase REINJECT: firing fresh events for {target_vals}")
    print(f"  (Profiles must be re-subscribed BEFORE running this)")

    for v in target_vals:
        email = f"{TEST_EMAIL_BASE}-{v}@{TEST_EMAIL_DOMAIN}"
        code, body = track_checkout_started(email, v, key)
        ok = "OK" if code in (200, 202) else f"FAIL: {body}"
        print(f"    v={v:>4}  HTTP {code}  {ok}")
        time.sleep(0.5)

    state["reinject_at"] = datetime.utcnow().isoformat() + "Z"
    state["reinject_vals"] = target_vals
    write_state(state)
    print(f"\n  Done. Wait 8+ minutes then run --phase=verify")
    return 0


def phase_cleanup(key):
    state = load_state()
    if not state.get("flow_id"):
        print("ERROR: no flow_id in state")
        return 1
    flow_id = state["flow_id"]
    code, body = set_flow_status(flow_id, "draft", key)
    print(f"Phase CLEANUP: flow {flow_id} -> draft  (HTTP {code})")
    if code == 200:
        state["status"] = "draft"
        write_state(state)
    else:
        print(f"  FAILED: {body}")
    return 0 if code == 200 else 1


def main():
    ap = argparse.ArgumentParser(description="Y84ruV-v3 conditional-split sandbox test v2")
    ap.add_argument("--phase", choices=["build", "inject", "reinject", "ensure-live", "verify", "cleanup"], required=True)
    ap.add_argument("--values", help="Comma-separated $values to reinject e.g. 78,79,80,120", default="")
    args = ap.parse_args()
    key = load_key()

    if args.phase == "build":
        return phase_build(key)
    if args.phase == "inject":
        return phase_inject(key)
    if args.phase == "reinject":
        return phase_reinject(key)
    if args.phase == "ensure-live":
        return phase_ensure_live(key)
    if args.phase == "verify":
        return phase_verify(key)
    if args.phase == "cleanup":
        return phase_cleanup(key)


if __name__ == "__main__":
    raise SystemExit(main())
