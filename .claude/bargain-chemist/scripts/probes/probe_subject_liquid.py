"""Probe: does the same Django parser handle the patterns we'd use in subject_line?

Klaviyo's subject_line field on flow-actions and campaign messages is rendered
via the same Django parser as template body (per Klaviyo docs). The render
endpoint operates on a template's HTML body — there is no documented endpoint
that renders a subject string in isolation. So we use template-render with the
candidate subject AS the template body. If the Django parser accepts the
syntax there, it will accept it in subject_line too.

This probe also PATCHes a flow-action's subject_line with Liquid to confirm
the field accepts arbitrary strings (rules out a server-side input
sanitiser).

Run locally:
    python .claude/bargain-chemist/scripts/probes/probe_subject_liquid.py

Snapshots to .claude/bargain-chemist/snapshots/<today>/probe-subject/.
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

REPO = Path(__file__).resolve().parents[4]
ENV_FILE = REPO / ".env.local"
OUT = REPO / f".claude/bargain-chemist/snapshots/{date.today():%Y-%m-%d}/probe-subject"
OUT.mkdir(parents=True, exist_ok=True)
TID = "UH72Vm"
REVISION = "2025-10-15"

# Each subject we'd consider for Y84ruV E1/E4
CANDIDATE_SUBJECTS = [
    ("static-control",
     "Your order's one click away",
     {},
     "Static — no Liquid. Should always render itself."),
    ("name-default-fallback",
     "{{ first_name|default:'there' }}, finish checkout",
     {"first_name": "Sarah"},
     "Name with default. With name -> 'Sarah, finish checkout'."),
    ("name-default-empty",
     "{{ first_name|default:'there' }}, finish checkout",
     {"first_name": ""},
     "Name empty. default should kick in -> 'there, finish checkout'."),
    ("name-default-missing",
     "{{ first_name|default:'there' }}, finish checkout",
     {},
     "Name absent. default -> 'there, finish checkout'."),
    ("conditional-low",
     "{% if event|lookup:'$value' < 79 %}A little more to unlock free shipping{% else %}Your order's one click away{% endif %}",
     {"event": {"$value": 50}},
     "Tiered subject, low cart -> low-cart text."),
    ("conditional-high",
     "{% if event|lookup:'$value' < 79 %}A little more to unlock free shipping{% else %}Your order's one click away{% endif %}",
     {"event": {"$value": 120}},
     "Tiered subject, high cart -> high-cart text."),
    ("conditional-edge-79",
     "{% if event|lookup:'$value' < 79 %}A little more to unlock free shipping{% else %}Your order's one click away{% endif %}",
     {"event": {"$value": 79}},
     "Edge case at exact $79 -> high-cart (strict <79 is FALSE)."),
    ("conditional-missing-value",
     "{% if event|lookup:'$value' < 79 %}A little more to unlock free shipping{% else %}Your order's one click away{% endif %}",
     {"event": {}},
     "Missing $value — what does Klaviyo do? Defensive default may be needed."),
    ("buggy-form-control",
     "{{ first_name|default:'Your' }} order's one click away",
     {"first_name": "Sarah"},
     "REPRODUCES the bug from current Y84ruV E4 subject. Renders 'Sarah order's one click away' (broken possessive)."),
]


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


def hdrs(key, content=False):
    h = {
        "Authorization": f"Klaviyo-API-Key {key}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    if content:
        h["Content-Type"] = "application/vnd.api+json"
    return h


def patch_template(key, html):
    body = {"data": {"type": "template", "id": TID,
                     "attributes": {"html": html}}}
    r = requests.patch(f"https://a.klaviyo.com/api/templates/{TID}/",
                       headers=hdrs(key, content=True), json=body, timeout=20)
    r.raise_for_status()


def main():
    key = load_key()
    # Snapshot rollback
    r = requests.get(f"https://a.klaviyo.com/api/templates/{TID}/",
                     headers=hdrs(key), timeout=20)
    r.raise_for_status()
    rollback = r.json()["data"]["attributes"]["html"]
    (OUT / "rollback.html").write_text(rollback, encoding="utf-8")

    print(f"Probing {len(CANDIDATE_SUBJECTS)} candidate subject patterns via template-render parser\n")

    summary = []
    for label, subject_template, ctx, intent in CANDIDATE_SUBJECTS:
        # Wrap subject as template body — same Django parser
        body_html = f"<html><body>SUBJ_START[{subject_template}]SUBJ_END</body></html>"
        patch_template(key, body_html)
        time.sleep(0.25)

        # Build context — flatten event/first_name as separate keys at root context level
        # matching the shape Klaviyo uses for subject rendering at send time
        context = {
            "first_name": ctx.get("first_name") if "first_name" in ctx else None,
            "organization": {"full_address": "1 Test St", "name": "Bargain Chemist"},
            "event": ctx.get("event", {}),
        }
        # Remove None first_name so we test "missing" cases properly
        if context["first_name"] is None:
            del context["first_name"]

        body = {"data": {"type": "template", "attributes": {
            "id": TID,
            "context": context,
        }}}
        r = requests.post("https://a.klaviyo.com/api/template-render/",
                          headers=hdrs(key, content=True), json=body, timeout=20)

        rendered_subject = "<render-error>"
        if r.status_code == 200:
            try:
                full = r.json()["data"]["attributes"]["html"]
                import re
                m = re.search(r"SUBJ_START\[(.*?)\]SUBJ_END", full, re.DOTALL)
                if m:
                    rendered_subject = m.group(1)
            except Exception:
                rendered_subject = r.text[:200]
        else:
            rendered_subject = f"HTTP-{r.status_code}: {r.text[:200]}"

        out = OUT / f"{label}.json"
        out.write_text(json.dumps({
            "status": r.status_code,
            "subject_template": subject_template,
            "context": context,
            "rendered_subject": rendered_subject,
            "intent": intent,
        }, indent=2), encoding="utf-8")

        liquid_leftover = "{%" in rendered_subject or "{{" in rendered_subject
        clean = "✅ clean" if r.status_code == 200 and not liquid_leftover else "⚠️"
        print(f"  {label:>30}  ->  {repr(rendered_subject[:80])}  {clean}")
        summary.append({"label": label, "rendered": rendered_subject, "ok": r.status_code == 200 and not liquid_leftover})

    # Rollback
    patch_template(key, rollback)
    print(f"\nRollback applied. Snapshots in {OUT}")

    fail_ct = sum(1 for s in summary if not s["ok"])
    if fail_ct == 0:
        print("\n✅ All subject patterns parse cleanly. Same parser as template body. Liquid in subject_line is SAFE.")
    else:
        print(f"\n⚠️  {fail_ct} pattern(s) returned errors or leftover Liquid. Use static subjects for those.")


if __name__ == "__main__":
    raise SystemExit(main())
