"""Quick diagnostic: GET XbQiKg E1 action 105487706 fresh and report current state.

Helps differentiate two scenarios for the failed PATCH verification:
  A) PATCH succeeded but verification fetched stale data
     -> updated timestamp is recent, template_id is the new owned global
  B) PATCH genuinely no-op'd
     -> updated timestamp is old, template_id is still the original

Run locally:
    python .claude/bargain-chemist/scripts/diagnose_xbqikg_e1.py
"""
import sys
from pathlib import Path

try:
    import requests
except ImportError:
    sys.exit("ERROR: pip install requests")

REPO = Path(__file__).resolve().parents[3]
ENV_FILE = REPO / ".env.local"


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


def main():
    key = load_key()
    h = {"Authorization": f"Klaviyo-API-Key {key}",
         "revision": "2025-10-15",
         "Accept": "application/vnd.api+json"}

    print("=== Fresh GET on XbQiKg E1 (action 105487706) ===\n")
    r = requests.get("https://a.klaviyo.com/api/flow-actions/105487706/",
                     headers=h, timeout=30)
    print(f"HTTP {r.status_code}")
    if r.status_code != 200:
        print(r.text[:500])
        return 1

    attrs = r.json()["data"]["attributes"]
    msg = attrs["definition"]["data"]["message"]
    print(f"action.updated:  {attrs.get('updated')}")
    print(f"template_id:     {msg.get('template_id')}")
    print(f"subject_line:    {msg.get('subject_line')[:120]}")
    print(f"preview_text:    {msg.get('preview_text')[:120]}")
    print()

    # Is this the new owned global Thn6Vr or the old clone RPZh8V?
    expected_new = "Thn6Vr"
    if msg.get("template_id") == expected_new:
        print(f"✅ PATCH SUCCEEDED — template_id is the new owned global ({expected_new}).")
        print(f"   Verification step in patch_search was reading stale data.")
        print(f"   Live clone will be regenerated on next send / re-PATCH.")
    elif msg.get("template_id") == "RPZh8V":
        print(f"❌ PATCH NO-OP — template_id is still the original RPZh8V.")
        print(f"   Klaviyo silently rejected the PATCH. Need a different approach.")
    else:
        print(f"❓ Unexpected template_id — neither old nor new owned global.")
        print(f"   Got: {msg.get('template_id')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
