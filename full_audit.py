"""
Deep audit of all 5 [Z] flows against Klaviyo best practices.

Checks every layer:
  - Flow structure & trigger
  - Time delays (values, units, weekday config)
  - Conditional splits (condition logic, branch routing)
  - Email actions (subject, preview text, from/reply-to, settings)
  - Template HTML (mobile, viewport, fonts, images, CTAs, unsubscribe)
  - Content quality (subject length, preview text, personalisation)

Usage:
    $env:KLAVIYO_API_KEY="pk_xxx"
    py full_audit.py
"""

import os, sys, re, requests, time

API_KEY  = os.environ.get("KLAVIYO_API_KEY", "")
REVISION = "2024-10-15.pre"
BASE_URL = "https://a.klaviyo.com/api"

HEADERS = {
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "revision": REVISION,
    "Accept": "application/json",
    "Content-Type": "application/json",
}

# Flow IDs are auto-discovered by name in main(); this is the name->config map.
# Replenishment has 16 products (added FLASH, Razene, Omeprazole).
EXPECTED_FLOW_CONFIG = {
    "[Z] Back in Stock": {
        "trigger_type": "metric",
        "expected_emails": 2,
        "expected_splits": 1,
        "expected_delays": 1,
        "delay_sequence": [("days", 1)],
    },
    "[Z] Post-Purchase Series": {
        "trigger_type": "metric",
        "expected_emails": 4,
        "expected_splits": 1,
        "expected_delays": 4,
        "delay_sequence": [("hours", 1), ("days", 3), ("days", 4), ("days", 7)],
    },
    "[Z] Replenishment - Reorder Reminders": {
        "trigger_type": "metric",
        "expected_emails": 16,
        "expected_splits": 16,
        "expected_delays": 16,
        "delay_sequence": None,
    },
    "[Z] Flu Season - Winter Wellness": {
        "trigger_type": "Added to List",
        "expected_emails": 2,
        "expected_splits": 0,
        "expected_delays": 1,
        "delay_sequence": [("days", 7)],
    },
    "[Z] Win-back - Lapsed Customers": {
        "trigger_type": "Added to List",
        "expected_emails": 3,
        "expected_splits": 0,
        "expected_delays": 2,
        "delay_sequence": [("days", 7), ("days", 7)],
    },
}

# Populated by main() after auto-discovering flow IDs
FLOWS: dict[str, str] = {}  # {id: name}

issues = []   # (flow_name, severity, category, detail)
passes = []   # (flow_name, category, detail)

def flag(flow, severity, category, detail):
    issues.append((flow, severity, category, detail))

def ok(flow, category, detail):
    passes.append((flow, category, detail))


# ── HTML audit helpers ─────────────────────────────────────────────────────────
VIEWPORT_RE    = re.compile(r'<meta[^>]+name=["\']viewport["\']', re.I)
MEDIA_RE       = re.compile(r'@media[^{]*max-width\s*:\s*(\d+)px', re.I)
UNSUB_RE       = re.compile(r'unsubscribe', re.I)
SMALL_FONT_RE  = re.compile(r'font-size\s*:\s*(\d+)px', re.I)
IMG_WIDTH_RE   = re.compile(r'<img[^>]+width=["\']?(\d+)["\']?', re.I)
OUTER_PX_RE    = re.compile(r'width=["\'](\d{3,4})["\']', re.I)
BUTTON_RE      = re.compile(r'(?:padding|height)\s*:\s*(\d+)px', re.I)
HREF_RE        = re.compile(r'href=["\']([^"\']+)["\']', re.I)
ALT_RE         = re.compile(r'<img(?![^>]*alt=)[^>]*>', re.I)
PLAINTEXT_RE   = re.compile(r'font-size\s*:\s*([0-9]+)px[^;]*;[^<]*', re.I)
STACK_RE       = re.compile(
    r'(?:\.col\w*\s*\{[^}]*display\s*:\s*block'
    r'|\.mobile-stack\s*\{[^}]*display\s*:\s*block'
    r'|td\[width=["\']?\d+%["\']?\][^{]*\{[^}]*display\s*:\s*block)',
    re.I | re.DOTALL)
COL_RE         = re.compile(
    r'<td[^>]+width=["\'](?:3[0-9]|4[0-9]|5[0-9])%["\']'
    r'|width\s*:\s*(?:3[0-9]|4[0-9]|5[0-9])%', re.I)


def audit_html(flow_name, email_name, html):
    h = html or ""
    pf = f"{email_name}"

    # Viewport
    if not VIEWPORT_RE.search(h):
        flag(flow_name, "WARN", "Mobile", f"{pf}: missing viewport meta tag")
    else:
        ok(flow_name, "Mobile", f"{pf}: viewport meta present")

    # Media query
    mq = [int(x) for x in MEDIA_RE.findall(h)]
    if not mq:
        flag(flow_name, "WARN", "Mobile", f"{pf}: no @media max-width breakpoint")
    elif all(w > 620 for w in mq):
        flag(flow_name, "WARN", "Mobile", f"{pf}: @media breakpoints all > 620px: {mq}")
    else:
        ok(flow_name, "Mobile", f"{pf}: @media breakpoint present ({min(mq)}px)")

    # Column stacking
    if COL_RE.search(h) and not STACK_RE.search(h):
        flag(flow_name, "WARN", "Mobile", f"{pf}: multi-column layout but no stacking rule")
    elif COL_RE.search(h):
        ok(flow_name, "Mobile", f"{pf}: column stacking rule present")

    # Font sizes
    small = [int(s) for s in SMALL_FONT_RE.findall(h) if int(s) < 10]
    if small:
        flag(flow_name, "WARN", "Mobile", f"{pf}: font-size < 10px found: {sorted(set(small))}px")
    else:
        ok(flow_name, "Mobile", f"{pf}: no illegibly small font sizes")

    # Image widths
    wide_imgs = [int(w) for w in IMG_WIDTH_RE.findall(h) if int(w) > 600]
    if wide_imgs:
        flag(flow_name, "WARN", "Mobile", f"{pf}: img width > 600px: {wide_imgs}")

    # Outer container
    outer = [int(w) for w in OUTER_PX_RE.findall(h) if int(w) > 620]
    if outer:
        flag(flow_name, "WARN", "Mobile", f"{pf}: outer container width > 620px: {outer}")

    # Unsubscribe link
    if not UNSUB_RE.search(h):
        flag(flow_name, "ERROR", "Compliance", f"{pf}: no unsubscribe link found (CAN-SPAM/GDPR)")
    else:
        ok(flow_name, "Compliance", f"{pf}: unsubscribe link present")

    # Alt text on images
    missing_alt = ALT_RE.findall(h)
    # Filter out spacers (1x1 or tiny images) - only flag real content images
    real_missing = [t for t in missing_alt if 'width="1"' not in t and "spacer" not in t.lower()]
    if real_missing:
        flag(flow_name, "INFO", "Accessibility", f"{pf}: {len(real_missing)} img(s) missing alt text")

    # Broken / placeholder links
    hrefs = HREF_RE.findall(h)
    placeholder = [u for u in hrefs if "example.com" in u or "yoursite" in u or "INSERT" in u.upper()]
    if placeholder:
        flag(flow_name, "ERROR", "Content", f"{pf}: placeholder URLs found: {placeholder[:3]}")


def _rendered_len(subject: str) -> int:
    """Estimate rendered subject length by replacing Jinja tags with a 5-char name."""
    import re as _re
    rendered = _re.sub(r"\{\{[^}]+\}\}", "Alice", subject)
    return len(rendered)


def audit_subject(flow_name, email_name, subject):
    if not subject:
        flag(flow_name, "ERROR", "Subject", f"{email_name}: subject line is empty")
        return
    length = _rendered_len(subject)
    raw_length = len(subject)
    label = f"{length} chars rendered" + (f", {raw_length} raw" if raw_length != length else "")
    if length < 20:
        flag(flow_name, "WARN", "Subject", f"{email_name}: subject very short ({label}): {subject!r}")
    elif length > 60:
        flag(flow_name, "WARN", "Subject", f"{email_name}: subject long ({label}) - may truncate on mobile: {subject!r}")
    else:
        ok(flow_name, "Subject", f"{email_name}: subject length OK ({label})")

    # Spam trigger words
    spam_words = ["free", "buy now", "act now", "limited time", "click here", "!!!"]
    lower = subject.lower()
    found_spam = [w for w in spam_words if w in lower]
    if found_spam:
        flag(flow_name, "WARN", "Subject", f"{email_name}: possible spam words in subject: {found_spam}")
    else:
        ok(flow_name, "Subject", f"{email_name}: no spam trigger words")

    # Personalisation
    if "{{" in subject:
        ok(flow_name, "Subject", f"{email_name}: subject has personalisation token")


def audit_preview_text(flow_name, email_name, preview):
    if not preview or not preview.strip():
        flag(flow_name, "WARN", "Preview Text", f"{email_name}: preview text is empty — missing 40-130 chars of prime inbox real estate")
    elif len(preview) < 40:
        flag(flow_name, "INFO", "Preview Text", f"{email_name}: preview text short ({len(preview)} chars) — aim for 80-130: {preview!r}")
    elif len(preview) > 160:
        flag(flow_name, "WARN", "Preview Text", f"{email_name}: preview text long ({len(preview)} chars) — may show filler: {preview!r}")
    else:
        ok(flow_name, "Preview Text", f"{email_name}: preview text length OK ({len(preview)} chars)")


def audit_send_settings(flow_name, email_name, msg):
    if not msg.get("smart_sending_enabled"):
        flag(flow_name, "WARN", "Settings", f"{email_name}: smart sending DISABLED — risk of over-sending")
    else:
        ok(flow_name, "Settings", f"{email_name}: smart sending enabled")

    if msg.get("transactional"):
        flag(flow_name, "WARN", "Settings", f"{email_name}: marked transactional — marketing flows should be non-transactional")

    if not msg.get("from_email"):
        flag(flow_name, "ERROR", "Settings", f"{email_name}: no from_email set")

    if not msg.get("reply_to_email"):
        flag(flow_name, "WARN", "Settings", f"{email_name}: no reply_to_email set")

    if not msg.get("add_tracking_params"):
        flag(flow_name, "WARN", "Settings", f"{email_name}: UTM tracking params disabled")
    else:
        ok(flow_name, "Settings", f"{email_name}: UTM tracking enabled")


def audit_delay(flow_name, data, position):
    unit  = data.get("unit", "?")
    value = data.get("value", "?")
    tz    = data.get("timezone")
    days  = data.get("delay_until_weekdays", [])

    if unit == "days":
        if tz != "profile":
            flag(flow_name, "WARN", "Delay", f"Delay {position}: timezone should be 'profile' (is {tz!r})")
        if not days:
            flag(flow_name, "WARN", "Delay", f"Delay {position}: no weekday restriction set")
        else:
            ok(flow_name, "Delay", f"Delay {position}: {value}d, timezone=profile, all days")
    else:
        ok(flow_name, "Delay", f"Delay {position}: {value} {unit}")


def audit_split(flow_name, split_num, data, links):
    pf = data.get("profile_filter")
    yes_id = links.get("next_if_true")
    no_id  = links.get("next_if_false")

    if pf is None:
        flag(flow_name, "ERROR", "Split", f"Split {split_num}: profile_filter is NULL — unconfigured condition")
        return

    cgs = pf.get("condition_groups", [])
    if not cgs:
        flag(flow_name, "ERROR", "Split", f"Split {split_num}: condition_groups is empty — no condition set")
        return

    cond = cgs[0].get("conditions", [{}])[0]
    ctype     = cond.get("type", "?")
    metric_id = cond.get("metric_id", "?")
    mf_op     = cond.get("measurement_filter", {}).get("operator", "?")
    mf_val    = cond.get("measurement_filter", {}).get("value", "?")
    tf_op     = cond.get("timeframe_filter", {}).get("operator", "?")
    mfilters  = cond.get("metric_filters")

    if ctype != "profile-metric":
        flag(flow_name, "WARN", "Split", f"Split {split_num}: unexpected condition type {ctype!r}")
        return

    summary = f"type={ctype}, metric={metric_id}, count {mf_op} {mf_val}, timeframe={tf_op}"
    if mfilters:
        kw = mfilters[0].get("filter", {}).get("value", "?")
        prop = mfilters[0].get("property", "?")
        summary += f", filter: {prop} contains '{kw}'"

    ok(flow_name, "Split", f"Split {split_num}: condition set — {summary}")

    if yes_id is None and no_id is None:
        flag(flow_name, "WARN", "Split", f"Split {split_num}: both YES and NO branches lead nowhere")
    elif yes_id is None:
        ok(flow_name, "Split", f"Split {split_num}: YES=exit (correct for has-done check), NO -> action {no_id}")
    elif no_id is None:
        ok(flow_name, "Split", f"Split {split_num}: YES -> action {yes_id}, NO=exit")


# ── Main audit ─────────────────────────────────────────────────────────────────

def fetch_template_html(tpl_id):
    r = requests.get(f"{BASE_URL}/templates/{tpl_id}", headers=HEADERS,
                     params={"fields[template]": "html"}, timeout=15)
    if r.ok:
        return r.json()["data"]["attributes"].get("html", "")
    return ""


def audit_flow(flow_id, flow_name):
    r = requests.get(f"{BASE_URL}/flows/{flow_id}", headers=HEADERS,
                     params={"additional-fields[flow]": "definition"}, timeout=15)
    if not r.ok:
        flag(flow_name, "ERROR", "API", f"Could not fetch flow: {r.status_code}")
        return

    attrs  = r.json()["data"]["attributes"]
    status = attrs.get("status", "?")
    defn   = attrs.get("definition", {})
    actions = defn.get("actions", [])
    triggers = defn.get("triggers", [])

    emails  = [a for a in actions if a.get("type") == "send-email"]
    splits  = [a for a in actions if a.get("type") == "conditional-split"]
    delays  = [a for a in actions if a.get("type") == "time-delay"]

    cfg = EXPECTED_FLOW_CONFIG.get(flow_name, {})

    # Status
    if status == "draft":
        ok(flow_name, "Status", f"Flow is draft (ready for review before activation)")
    else:
        flag(flow_name, "INFO", "Status", f"Flow status: {status}")

    # Trigger
    if triggers:
        t = triggers[0]
        ok(flow_name, "Trigger", f"Trigger type: {t.get('type')}, id: {t.get('id')}")
    else:
        flag(flow_name, "ERROR", "Trigger", "No trigger configured")

    # Action counts
    exp_e = cfg.get("expected_emails", 0)
    exp_s = cfg.get("expected_splits", 0)
    exp_d = cfg.get("expected_delays", 0)

    if len(emails) == exp_e:
        ok(flow_name, "Structure", f"Email count correct: {len(emails)}")
    else:
        flag(flow_name, "ERROR", "Structure", f"Email count: got {len(emails)}, expected {exp_e}")

    if len(splits) == exp_s:
        ok(flow_name, "Structure", f"Split count correct: {len(splits)}")
    else:
        flag(flow_name, "ERROR", "Structure", f"Split count: got {len(splits)}, expected {exp_s}")

    if len(delays) == exp_d:
        ok(flow_name, "Structure", f"Delay count correct: {len(delays)}")
    else:
        flag(flow_name, "WARN", "Structure", f"Delay count: got {len(delays)}, expected {exp_d}")

    # Audit delays
    delay_seq = cfg.get("delay_sequence")
    for i, a in enumerate(delays):
        data = a.get("data", {})
        if delay_seq and i < len(delay_seq):
            exp_unit, exp_val = delay_seq[i]
            if data.get("unit") != exp_unit or data.get("value") != exp_val:
                flag(flow_name, "WARN", "Delay",
                     f"Delay {i+1}: expected {exp_val} {exp_unit}, got {data.get('value')} {data.get('unit')}")
        audit_delay(flow_name, data, i + 1)

    # Audit splits
    for i, a in enumerate(splits):
        audit_split(flow_name, i + 1, a.get("data", {}), a.get("links", {}))

    # Audit emails
    for i, a in enumerate(emails):
        msg      = a.get("data", {}).get("message", {})
        name     = msg.get("name", f"Email {i+1}")
        subject  = msg.get("subject_line", "")
        preview  = msg.get("preview_text", "")
        tpl_id   = msg.get("template_id")

        audit_subject(flow_name, name, subject)
        audit_preview_text(flow_name, name, preview)
        audit_send_settings(flow_name, name, msg)

        if tpl_id:
            html = fetch_template_html(tpl_id)
            time.sleep(0.15)
            if html:
                audit_html(flow_name, name, html)
            else:
                flag(flow_name, "ERROR", "Template", f"{name}: template {tpl_id} has no HTML")
        else:
            flag(flow_name, "ERROR", "Template", f"{name}: no template_id assigned")

    time.sleep(0.2)


def discover_flow_ids() -> dict:
    """Returns {name: id} for all [Z] flows in the account."""
    found = {}
    url = f"{BASE_URL}/flows"
    params = {"fields[flow]": "name", "page[size]": 100}
    while url:
        r = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if not r.ok:
            print(f"WARNING: could not list flows: {r.status_code}")
            break
        data = r.json()
        for item in data.get("data", []):
            name = item["attributes"]["name"]
            if name.startswith("[Z]"):
                found[name] = item["id"]
        url = data.get("links", {}).get("next")
        params = {}
        time.sleep(0.2)
    return found


def main():
    if not API_KEY:
        print("ERROR: Set KLAVIYO_API_KEY env var.")
        sys.exit(1)

    print("Discovering [Z] flow IDs...")
    name_to_id = discover_flow_ids()
    target_names = set(EXPECTED_FLOW_CONFIG.keys())
    for name in target_names:
        if name in name_to_id:
            FLOWS[name_to_id[name]] = name
            print(f"  {name_to_id[name]}  {name}")
        else:
            print(f"  NOT FOUND: {name}")

    missing = target_names - set(name_to_id.keys())
    if missing:
        print(f"\nWARNING: {len(missing)} flow(s) not found in account:")
        for m in missing:
            print(f"  - {m}")

    print()
    print("Running deep audit of all 5 flows...")
    total_emails = sum(EXPECTED_FLOW_CONFIG[n]["expected_emails"]
                       for n in EXPECTED_FLOW_CONFIG)
    print(f"(Fetches each flow definition + all {total_emails} template HTMLs — takes ~90s)\n")

    for flow_id, flow_name in FLOWS.items():
        print(f"  Auditing {flow_name}...")
        audit_flow(flow_id, flow_name)

    # ── Report ─────────────────────────────────────────────────────────────────
    errors = [(f,c,d) for f,s,c,d in issues if s == "ERROR"]
    warns  = [(f,c,d) for f,s,c,d in issues if s == "WARN"]
    infos  = [(f,c,d) for f,s,c,d in issues if s == "INFO"]

    print()
    print("=" * 70)
    print("DEEP AUDIT RESULTS")
    print("=" * 70)
    print(f"  Checks passed : {len(passes)}")
    print(f"  Errors        : {len(errors)}")
    print(f"  Warnings      : {len(warns)}")
    print(f"  Info          : {len(infos)}")

    if errors:
        print()
        print("-- ERRORS (must fix before activating) " + "-"*31)
        for flow, cat, detail in errors:
            print(f"  [{flow}] [{cat}] {detail}")

    if warns:
        print()
        print("-- WARNINGS (best practice violations) " + "-"*31)
        for flow, cat, detail in warns:
            print(f"  [{flow}] [{cat}] {detail}")

    if infos:
        print()
        print("-- INFO (minor / nice to have) " + "-"*39)
        for flow, cat, detail in infos:
            print(f"  [{flow}] [{cat}] {detail}")

    print()
    if not errors and not warns:
        print("PASS - All flows meet Klaviyo best practices.")
    elif not errors:
        print("PASS WITH WARNINGS - No blocking issues; warnings above are best-practice improvements.")
    else:
        print("FAIL - Errors above must be resolved before activating flows.")


if __name__ == "__main__":
    main()
