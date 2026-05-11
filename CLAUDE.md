# PantryPilot — Project Context for Claude

## Bargain Chemist priority list

`integrations/clickup-asana/priorities.md` is the source of truth for the
Bargain Chemist work priorities (Engineering + Klaviyo). Read it at the start
of any session that involves discussing or scheduling BC work.

- Atlas Digital owns the Priority field inside Asana itself; do **not** write
  to Asana priorities without explicit per-session permission from Harpreet.
- This repo's `priorities.md` is the working reference for Harpreet ↔ Claude
  conversations and is updated daily via the Asana sync workflow described in
  that file.

## ClickUp → Asana migration state

State lives under `integrations/clickup-asana/`:

- `config/` — field/section/user mappings
- `state/` — snapshots of the source CU workspace (inventory, comments,
  custom fields)
- `runs/` — dated run notes; the most recent deploy-status doc records what
  was synced and what's outstanding
- `tmp/deploy/` — work lists used during the migration (created GIDs,
  comment-work, attachments-map, etc.)

Asana destination project: `1214475175808445` (Bargain Chemist).

## Working branch convention

Each task gets its own `claude/<short-slug>-<id>` branch. Develop, commit,
and push to the branch named in the session brief — never push to `main`
without explicit permission, and never open a PR unless asked.
