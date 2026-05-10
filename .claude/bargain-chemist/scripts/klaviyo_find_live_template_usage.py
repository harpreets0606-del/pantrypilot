"""Identify which fix-file template IDs are referenced by any LIVE flow definition.

Output:
  ID  -> [flow1, flow2, ...]   (templates we MUST UI-paste)
  ID  -> NOT in any live flow  (skip — orphaned in archived/draft flows)
"""
import glob
import json
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
FLOWS_DIR = REPO / ".claude/bargain-chemist/snapshots/2026-05-07/all-flows"
FIXES_DIR = REPO / ".claude/bargain-chemist/templates/fixes"


def main() -> int:
    fix_ids = sorted(p.stem for p in FIXES_DIR.glob("*.html"))
    in_use: dict[str, list[str]] = {}

    def process_flow(flow_obj, fallback_fid):
        attrs = (flow_obj.get("attributes") or {}) if isinstance(flow_obj, dict) else {}
        if attrs.get("status") != "live":
            return
        fid = flow_obj.get("id", fallback_fid)
        name = attrs.get("name", "?")
        blob = json.dumps(flow_obj)
        for tid in fix_ids:
            if f'"{tid}"' in blob:
                in_use.setdefault(tid, []).append(f"{fid} ({name})")

    for fp in sorted(FLOWS_DIR.glob("*.json")):
        fid = fp.stem
        try:
            d = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            continue
        data = d.get("data") if isinstance(d, dict) else d
        if isinstance(data, list):
            for item in data:
                process_flow(item, fid)
        elif isinstance(data, dict):
            process_flow(data, fid)

    print("Templates that ARE in a live flow (must UI-paste):")
    for tid in fix_ids:
        if tid in in_use:
            print(f"  {tid:<8} -> {', '.join(in_use[tid])}")
    print("\nTemplates NOT in any live flow (safe to skip):")
    for tid in fix_ids:
        if tid not in in_use:
            print(f"  {tid}")
    print(f"\nSummary: {len(in_use)} need UI paste, {len(fix_ids)-len(in_use)} can skip")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
