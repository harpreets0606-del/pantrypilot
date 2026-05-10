"""Extract rendered HTML previews from build_y84ruv_templates.py snapshots.

Defensive: tries multiple parsing strategies (full JSON, regex fallback) so
it works even when the snapshot's body field was truncated mid-JSON.

Reads:  .claude/bargain-chemist/snapshots/<today>/build-y84ruv/*-render-v*.json
        (or the latest build-y84ruv dir if today's doesn't exist)
Writes: ./previews/<basename>.html  (cwd-relative for easy `start` access)

Run locally:
    python .claude/bargain-chemist/scripts/extract_y84ruv_previews.py

Then open any:
    start previews\cart-recover-e1-w2sbja-render-v50.html
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]


def find_snapshots_dir():
    """Use today's build-y84ruv dir if it exists, else fall back to most recent."""
    today_dir = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/build-y84ruv"
    if today_dir.exists():
        return today_dir
    candidates = sorted((REPO/".claude/bargain-chemist/snapshots").glob("*/build-y84ruv"))
    if not candidates:
        sys.exit("❌ No build-y84ruv snapshot dirs found. Run build_y84ruv_templates.py first.")
    return candidates[-1]


def extract_html(file_text):
    """Try multiple strategies to extract the rendered HTML from snapshot JSON."""
    # Strategy 1: parse outer JSON, then inner body JSON
    try:
        outer = json.loads(file_text)
        body = outer.get("body", "")
        if body:
            try:
                inner = json.loads(body)
                html = inner.get("data", {}).get("attributes", {}).get("html")
                if html:
                    return html, "strategy-1-full-json"
            except json.JSONDecodeError:
                # Body was truncated. Fall through to regex on the body string.
                pass
            # Strategy 2: regex on body string (handles truncated body)
            m = re.search(r'"html"\s*:\s*"((?:[^"\\]|\\.)*)"', body)
            if m:
                try:
                    decoded = json.loads(f'"{m.group(1)}"')
                    return decoded, "strategy-2-regex-on-body"
                except json.JSONDecodeError:
                    pass
    except json.JSONDecodeError:
        # Outer JSON itself is malformed. Try regex on whole file.
        pass

    # Strategy 3: regex on the entire file text
    m = re.search(r'"html"\s*:\s*"((?:[^"\\]|\\.)*)"', file_text)
    if m:
        try:
            decoded = json.loads(f'"{m.group(1)}"')
            return decoded, "strategy-3-regex-on-file"
        except json.JSONDecodeError:
            return m.group(1), "strategy-3-regex-raw"

    return None, "no-strategy-worked"


def main():
    snapshots_dir = find_snapshots_dir()
    print(f"Reading from: {snapshots_dir}")

    previews_dir = Path.cwd() / "previews"
    previews_dir.mkdir(exist_ok=True)

    files = sorted(snapshots_dir.glob("*-render-v*.json"))
    if not files:
        sys.exit(f"❌ No render snapshots in {snapshots_dir}")

    print(f"Found {len(files)} snapshot(s)\n")
    written = 0
    failed = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = f.read_text(encoding="utf-8", errors="replace")

        html, strategy = extract_html(text)
        if not html:
            print(f"  ❌ {f.name}: extraction failed ({strategy})")
            failed += 1
            continue

        out = previews_dir / (f.stem + ".html")
        out.write_text(html, encoding="utf-8")
        print(f"  ✅ {f.stem}.html  ({len(html)} bytes)  via {strategy}")
        written += 1

    print(f"\n=== Done: {written} extracted, {failed} failed ===")
    print(f"Previews dir: {previews_dir}\n")
    if written > 0:
        print("Open one in browser:")
        first = sorted(previews_dir.glob("*.html"))[0]
        # Cross-platform-ish hint:
        print(f"  Windows:   start {first.relative_to(Path.cwd())}")
        print(f"  PowerShell:Invoke-Item {first.relative_to(Path.cwd())}")


if __name__ == "__main__":
    raise SystemExit(main())
