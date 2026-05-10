"""Session-start prelude check — read this FIRST before any Klaviyo task.

Per CLAUDE.md: "Read memory/klaviyo-mastery-index.md FIRST before planning
any Klaviyo task." This script enforces that by printing the most-relevant
memory items at session start, so I cannot plausibly claim "I forgot."

Prints:
  1. Last 5 entries from memory/decisions-log.md
  2. All ❌ entries from memory/klaviyo-mastery-index.md (broken capabilities)
  3. CLAUDE.md mandatory protocols (verbatim, top section)
  4. audit-rules.json version + key rule reminders
  5. Live status of the 8 LIVE flows + 1 paused + RtiVC5/XbQiKg/Sr3hxz
     (verified via klaviyo_get_flow today)
  6. Open audit items / predictions due for re-evaluation

Run locally:
    py .claude/bargain-chemist/scripts/prelude_check.py
"""
import json
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
MEMORY = REPO / ".claude/bargain-chemist/memory"
RULES = REPO / ".claude/bargain-chemist/audit-rules.json"
CLAUDE_MD = REPO / ".claude/bargain-chemist/CLAUDE.md"


def print_section(title):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def tail_decisions_log(n=5):
    print_section(f"1. Last {n} decisions (memory/decisions-log.md)")
    f = MEMORY / "decisions-log.md"
    if not f.exists():
        print("  (file missing)")
        return
    text = f.read_text(encoding="utf-8")
    # Match lines starting with "## " (date headers) — find last n
    sections = []
    cur = []
    for line in text.splitlines():
        if line.startswith("## "):
            if cur:
                sections.append("\n".join(cur))
                cur = []
            cur.append(line)
        elif cur is not None:
            cur.append(line)
    if cur:
        sections.append("\n".join(cur))
    for s in sections[-n:]:
        print(f"\n{s.rstrip()}\n")


def print_broken_capabilities():
    print_section("2. ❌ Broken capabilities you must design around")
    f = MEMORY / "klaviyo-mastery-index.md"
    if not f.exists():
        print("  (file missing)")
        return
    text = f.read_text(encoding="utf-8")
    rows = [
        line for line in text.splitlines()
        if "| ❌ |" in line or "❌ " in line[:20]
    ]
    for r in rows:
        if r.strip().startswith("|"):
            print(f"  {r.strip()}")


def print_mandatory_protocols():
    print_section("3. CLAUDE.md MANDATORY protocols (verbatim, must follow)")
    f = CLAUDE_MD
    if not f.exists():
        print("  (file missing)")
        return
    text = f.read_text(encoding="utf-8")
    # Pull the three "MANDATORY ..." sections — each is delimited by --- markers
    found = []
    in_block = False
    cur = []
    for line in text.splitlines():
        if line.strip().startswith("## ") and "MANDATORY" in line.upper():
            in_block = True
            cur = [line]
        elif line.strip().startswith("## ") and in_block:
            found.append("\n".join(cur))
            in_block = False
            cur = []
        elif line.strip() == "---" and in_block:
            found.append("\n".join(cur))
            in_block = False
            cur = []
        elif in_block:
            cur.append(line)
    if in_block and cur:
        found.append("\n".join(cur))
    for block in found:
        print(f"\n{block.rstrip()}\n")
    # Also check if NO UNVERIFIED FACTS RULE is present (top-level rule)
    if "NO UNVERIFIED FACTS RULE" in text:
        print("\n⚠️  NO UNVERIFIED FACTS RULE — ABSOLUTE")
        print("   Never assert or insert a factual claim without user-approved")
        print("   verification. Includes 'thousands of customers', '9/10 Kiwis',")
        print("   founding year, store count, awards, etc.")


def print_audit_rules_summary():
    print_section("4. audit-rules.json key reminders")
    if not RULES.exists():
        print("  (audit-rules.json missing — using inline lists in scripts)")
        return
    rules = json.loads(RULES.read_text(encoding="utf-8"))
    meta = rules.get("_meta", {})
    print(f"  Version:           {meta.get('version', '?')}")
    print(f"  Last updated:      {meta.get('last_updated', '?')}")
    print(f"  Review protocol:   {meta.get('review_protocol', '?')[:80]}")
    print(f"\n  Hard FAILS if missing (compliance_required_legal):")
    legal = rules.get("compliance_required_legal", {})
    for p in legal.get("phrases", []) + legal.get("liquid_macros", []):
        print(f"    - {p}")
    print(f"\n  Hard FAILS if present (banned_fear_strict + banned_coupons_strict):")
    for k in ("banned_fear_strict", "banned_coupons_strict"):
        for p in rules.get(k, {}).get("phrases", []):
            print(f"    - {p}")
    print(f"\n  ⚠️  CREATIVE CHOICE — do NOT flag absence as defect:")
    for p in rules.get("creative_choice_value_props", {}).get("phrases", []):
        print(f"    - {p}")
    print(f"\n  ⚠️  REQUIRES PRIMARY-DATA VERIFICATION before flagging:")
    for p in rules.get("specific_claims_require_verification", {}).get("phrases_to_check", []):
        print(f"    - {p}")
    proto = rules.get("specific_claims_require_verification", {}).get("verification_protocol", "")
    if proto:
        print(f"\n  How to verify: {proto}")


def print_live_flow_state():
    print_section("5. Last-known LIVE flow state (from snapshots/2026-05-08/)")
    print("  Re-verify via klaviyo_get_flow before any deploy decision.\n")
    flows = [
        ("RtiVC5", "live",   "Browse Abandonment              → WR3mRF"),
        ("XbQiKg", "live",   "Search Abandonment              → S3jZGb (E1) + RWGKkM (E2)"),
        ("Sr3hxz", "live",   "Abandoned Checkout v3            → Vtggdk (E1) + Yr6YBF (E4)"),
        ("RPQXaa", "live",   "Added to Cart Abandonment        → USNhYE (E1) + UCUwWu (E2)"),
        ("T7pmf6", "live",   "Win-back Lapsed Customers        → XRDX9U (E1) + RJhLMj (E2)"),
        ("Ua5LdS", "live",   "Replenishment Category-Based     → 6 category templates"),
        ("V9XmEm", "live",   "Flu Season Winter Wellness       → SNtytG (E1, just patched) + XmsJkZ (E2)"),
        ("YdejKf", "live",   "Welcome Series 2026              → VZASFD + WtmqBu + UvF2qd"),
        ("Ysj7sg", "manual", "Back in Stock — PAUSED (USbQRB dead since 2023-12-11)"),
    ]
    for fid, status, label in flows:
        marker = "✅" if status == "live" else "🟡"
        print(f"  {marker} {fid}  [{status}]  {label}")


def print_open_predictions():
    print_section("6. Open falsifiable predictions (re-evaluate by date)")
    f = MEMORY / "decisions-log.md"
    if not f.exists():
        print("  (decisions-log.md missing)")
        return
    text = f.read_text(encoding="utf-8")
    today = date.today().isoformat()
    in_pred = False
    found = 0
    for line in text.splitlines():
        if "prediction" in line.lower() and ("re-evaluate" in line.lower() or "score on" in line.lower() or "by 2026" in line.lower()):
            print(f"  {line.strip()}")
            found += 1
        if "2026-05-22" in line or "2026-05-15" in line:
            print(f"  {line.strip()}")
            found += 1
    if found == 0:
        print("  (no dated predictions found — search decisions-log.md manually)")
    print(f"\n  Today: {today}")


def main():
    print(f"=== Bargain Chemist session prelude — {date.today().isoformat()} ===")
    print("This is what you must consult BEFORE planning any Klaviyo task.\n")
    print("Per CLAUDE.md: skipping any of these reads = task incomplete.")

    tail_decisions_log(n=5)
    print_broken_capabilities()
    print_mandatory_protocols()
    print_audit_rules_summary()
    print_live_flow_state()
    print_open_predictions()

    print_section("✅ Prelude complete")
    print("Now you can plan with full context. Cite mastery-index status for")
    print("every capability you touch. State verification line in every audit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
