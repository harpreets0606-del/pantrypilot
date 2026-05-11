#!/usr/bin/env python3
"""Build Asana create_tasks payload — 100% fidelity from ClickUp.

Outputs:
- create-tasks-payload.json    : full payload split into 3 batches of 10
- zbr-order.json               : ordered list of ZBRs (or summary keys) for batch result mapping
- attachments-map.json         : per-ZBR list of CU attachment URLs to re-host
- skipped-assignees.json       : CU assignees that aren't in Asana workspace
"""
import json
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
STATE = ROOT / "state"
TMP = ROOT / "tmp" / "deploy"

PROJECT_GID = "1214475175808445"

# Sections
SEC_BACKLOG = "1214475175808453"
SEC_IN_PROGRESS = "1214512998624365"
SEC_PENDING_QA_REVIEW = "1214512998624367"
SEC_PENDING_CLIENT = "1214512998624369"
SEC_DONE = "1214512998624375"

# Custom fields
CF_NAME = "1209131474480020"          # text
CF_DETAILS = "1209131474480022"       # text
CF_MANAGER = "1209133766458986"       # people (single)
CF_PRIORITY = "1207253591034393"      # enum
CF_ESTIMATED_TIME = "1206060277023807"  # number (minutes)

# Priority enum option gids
PRI_HIGH = "1207253591034396"
PRI_MEDIUM = "1207253591034397"
PRI_LOW = "1207253591034398"

# Asana users we can resolve (email → gid)
ASANA_USERS = {
    "harpreetsingh@bargainchemist.co.nz": ("1214510558878078", "Harpreet Singh"),
    "gurdeep.singh@bargainchemist.co.nz": ("1214510558878075", "Gurdeep Singh"),
    "anna.vanderloo@bargainchemist.co.nz": ("1214510558878072", "Anna van der Loo"),
}

# CU users we know but cannot resolve (no Asana account)
CU_USER_DISPLAY_NAME = {
    "harpreetsingh@bargainchemist.co.nz": "Harpreet Singh",
    "gurdeep.singh@bargainchemist.co.nz": "Gurdeep Singh",
    "anna.vanderloo@bargainchemist.co.nz": "Anna van der Loo",
    "sam@zyber.co.nz": "Sam Edwards (Zyber)",
    "david@zyber.co.nz": "David Visser (Zyber)",
    "brenda@zyber.co.nz": "Brenda Walters (Zyber)",
    "saniya@zyber.co.nz": "Saniya (Zyber)",
    "yubin@zyber.co.nz": "Yubin (Zyber)",
    "jordan@zyber.co.nz": "Jordan Popovich (Zyber)",
    "amritwant@zyber.co.nz": "Amritwant (Zyber)",
    "tamara@zyber.co.nz": "Tamara Willmott (Zyber)",
    "ben@zyber.co.nz": "Ben Hammonds (Zyber)",
    "jericho@zyber.co.nz": "Jericho (Zyber)",
    "beverly@zyber.co.nz": "Beverly Di Mercurio (Zyber)",
}

# CU status → Asana section gid
STATUS_TO_SECTION = {
    "client review": SEC_PENDING_CLIENT,
    "owner review": SEC_PENDING_QA_REVIEW,
    "input required": SEC_PENDING_QA_REVIEW,
    "with external": SEC_PENDING_CLIENT,
    "tweaks": SEC_IN_PROGRESS,
    "working on it": SEC_IN_PROGRESS,
    "not started": SEC_BACKLOG,
    "on hold": SEC_BACKLOG,
    "done": SEC_DONE,
}

# CU priority → Asana priority option gid
PRIORITY_TO_OPTION = {
    "high": PRI_HIGH,
    "urgent": PRI_HIGH,
    "medium": PRI_MEDIUM,
    "normal": PRI_MEDIUM,
    "low": PRI_LOW,
}


def normalize_description(text: str) -> str:
    """Light normalization of CU description for plain-text Asana notes field.
    Preserves paragraph breaks and structure; no HTML/XML escaping needed.
    """
    if not text:
        return "(No description in ClickUp.)"
    return text.strip()


def pick_manager_gid(assignees: list) -> str | None:
    """Return the first Asana-resolvable user gid from the assignee list, else None."""
    for email in assignees or []:
        if email in ASANA_USERS:
            return ASANA_USERS[email][0]
    return None


def build_live_card(card: dict) -> tuple[dict, list[str]]:
    """Returns (task_payload, unresolved_emails_list)."""
    zbr = card["zbr"]
    name = card["name"]
    status = card["status"]
    task_type = card.get("task_type") or ""
    priority = card.get("priority_cu") or ""
    assignees = card.get("assignees") or []
    parent = card.get("parent")
    cu_url = card.get("cu_url") or ""
    cu_desc = card.get("cu_description") or ""
    time_estimate_ms = card.get("time_estimate_ms")

    assignee_names = [CU_USER_DISPLAY_NAME.get(a, a) for a in assignees]
    assignee_display = ", ".join(assignee_names) if assignee_names else "—"

    parent_line = f"Parent task: {parent} (subtask in ClickUp)\n" if parent else ""
    type_segment = f" · Type: {task_type}" if task_type else ""
    priority_segment = f" · Priority (CU): {priority}" if priority else ""

    notes = (
        f"ZBR ID: {zbr} · Workstream: {card['list']} · Status (CU): {status}"
        f"{type_segment}{priority_segment}\n"
        f"Assignees (CU): {assignee_display}\n"
        f"{parent_line}"
        f"Source: {cu_url}\n"
        f"\n"
        f"———————————————\n"
        f"\n"
        f"Brief / Description:\n"
        f"\n"
        f"{normalize_description(cu_desc)}"
    )

    details_value = f"{card['list']} · {status}"
    if parent:
        details_value += f" · subtask of {parent}"

    cf_dict = {
        CF_NAME: zbr,
        CF_DETAILS: details_value,
    }

    # Priority mapping
    if priority and priority.lower() in PRIORITY_TO_OPTION:
        cf_dict[CF_PRIORITY] = PRIORITY_TO_OPTION[priority.lower()]

    # Manager mapping (single user)
    manager_gid = pick_manager_gid(assignees)
    if manager_gid:
        cf_dict[CF_MANAGER] = manager_gid

    # Estimated time (CU ms → Asana minutes; only if meaningful)
    if time_estimate_ms and time_estimate_ms > 0:
        minutes = round(time_estimate_ms / 60000)
        if minutes > 0:
            cf_dict[CF_ESTIMATED_TIME] = minutes

    # Section assignment based on CU status
    section_id = STATUS_TO_SECTION.get(status, SEC_BACKLOG)

    task = {
        "name": f"{zbr} — {name}",
        "section_id": section_id,
        "notes": notes,
        "custom_fields": json.dumps(cf_dict, ensure_ascii=False),
    }

    # Set Asana assignee (the task's primary assignee) to the resolved manager too,
    # if we have one. This makes the card actionable for BC team out of the gate.
    if manager_gid:
        task["assignee"] = manager_gid

    unresolved = [a for a in assignees if a not in ASANA_USERS]
    return task, unresolved


def build_summary_card(workstream_key: str, summary: dict) -> dict:
    name = summary["name"]
    desc = summary["description"]

    cf_name_value = "BC-DONE-ENG" if workstream_key == "engineering" else "BC-DONE-KLAVIYO"
    details = (
        "Engineering · Completed work history"
        if workstream_key == "engineering"
        else "Klaviyo · Completed work history"
    )
    cf_dict = {CF_NAME: cf_name_value, CF_DETAILS: details}

    return {
        "name": name,
        "section_id": SEC_DONE,
        "notes": desc.strip(),
        "custom_fields": json.dumps(cf_dict, ensure_ascii=False),
        "completed": True,
    }


def main():
    live_cards = json.loads((TMP / "card-payloads.json").read_text())
    summaries = json.loads((STATE / "done-summary-tasks.json").read_text())

    tasks_payload = []
    zbr_order = []
    all_unresolved = set()

    for card in live_cards:
        task, unresolved = build_live_card(card)
        tasks_payload.append(task)
        zbr_order.append(card["zbr"])
        all_unresolved.update(unresolved)

    tasks_payload.append(build_summary_card("engineering", summaries["engineering"]))
    zbr_order.append("BC-DONE-ENG")
    tasks_payload.append(build_summary_card("klaviyo", summaries["klaviyo"]))
    zbr_order.append("BC-DONE-KLAVIYO")

    output = {
        "default_project": PROJECT_GID,
        "tasks": tasks_payload,
    }

    # Split into 3 batches of 10 for manageable tool-call sizes
    batches = []
    for i in range(0, len(tasks_payload), 10):
        batches.append({
            "default_project": PROJECT_GID,
            "tasks": tasks_payload[i:i + 10],
        })
        (TMP / f"batch-{i // 10 + 1}.json").write_text(
            json.dumps({
                "default_project": PROJECT_GID,
                "tasks": tasks_payload[i:i + 10],
            }, ensure_ascii=False, indent=2)
        )

    (TMP / "create-tasks-payload.json").write_text(json.dumps(output, ensure_ascii=False, indent=2))
    (TMP / "zbr-order.json").write_text(json.dumps(zbr_order, indent=2))

    # Per-card attachment map
    attachments_map = {}
    for card in live_cards:
        atts = card.get("attachments") or []
        if atts:
            attachments_map[card["zbr"]] = atts
    (TMP / "attachments-map.json").write_text(json.dumps(attachments_map, ensure_ascii=False, indent=2))

    # Unresolved assignees report
    (TMP / "skipped-assignees.json").write_text(
        json.dumps(sorted(all_unresolved), indent=2)
    )

    print(f"Wrote create-tasks-payload.json with {len(tasks_payload)} tasks ({len(live_cards)} live + 2 summary)")
    print(f"Wrote {len(batches)} batches: batch-1.json, batch-2.json, batch-3.json")
    print(f"Wrote zbr-order.json")
    print(f"Wrote attachments-map.json ({len(attachments_map)} cards, {sum(len(v) for v in attachments_map.values())} attachments)")
    print(f"Wrote skipped-assignees.json ({len(all_unresolved)} CU users not in Asana)")
    print("")
    print("=== Sample task (first live card) ===")
    print(json.dumps(tasks_payload[0], ensure_ascii=False, indent=2)[:1500])


if __name__ == "__main__":
    main()
