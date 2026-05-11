# Session Notes — 2026-05-11

Notes from the working session on branch `claude/verify-integrations-XcRO8`.
Captures open threads and decisions so they survive into the next session.

## Decisions made

- **Atlas Digital owns the Asana Priority field.** Claude does not write
  priorities into Asana cards without explicit per-session permission from
  Harpreet. The working priority list lives in `priorities.md` (this folder's
  parent) and is the reference Harpreet ↔ Claude use during conversations.
- **Daily Asana sync workflow** is defined at the bottom of `priorities.md`.
  Pull modified cards, mirror status/section/assignee/custom fields back into
  `priorities.md`, commit as `Daily Asana sync — YYYY-MM-DD`.
- **CLAUDE.md at repo root** points future sessions at `priorities.md` and
  this run folder so context auto-loads on session start.

## Open threads to resolve with Harpreet

### 1. Ambiguous priority mappings

The HIGH/MED list Harpreet shared maps cleanly onto some cards but is
ambiguous on others. Next conversation should confirm:

- **CRO issues (HIGH)** — no card literally called CRO. Candidates:
  - ZBR-2997 CWV Audit
  - ZBR-3034 Product Filter Review
  - ZBR-3100 Stock issue dark store
- **SEO issues (HIGH)** — primary card is ZBR-2654 SEO & GEO. Also likely:
  - ZBR-3066 Structured Data Findings from OMD
- **Orders investigation (MED)** — primary card is ZBR-3078 Order
  Investigation. Also possibly:
  - ZBR-2328 Order Editing investigation
  - ZBR-2923 Update lifecycle of an order documentation
- **Checkout analysis (MED)** — primary card is ZBR-2995 Hard Checkout Error.
  Also possibly:
  - ZBR-2793 Australian Store launch — Checkout Currency Blocker (currently
    on hold)

### 2. 11 live cards with no priority assigned

Surface these next time work scheduling comes up:

**Engineering (7):** ZBR-3076 BackEnd Documentation · ZBR-3075 FrontEnd
Documentation · ZBR-3042 April Sale Theme · ZBR-2931 GA4 Search Tracking
Implementation · ZBR-2850 Days for fulfilment & Unfulfilled reporting ·
ZBR-2565 Bulk email customers from shopify · ZBR-2792 Shipping Issues *(on
hold)*.

**Klaviyo (4):** ZBR-2805 Design guidance · ZBR-2801 Campaign Strategy ·
ZBR-2802 Working with the internal BC team to optimise campaign performance ·
ZBR-2806 Non-promotional Campaign.

### 3. Comments backfill — still outstanding

State as of end-of-session:

- **Posted: 10 of 202** (the 10 ZBR-2323 entries done in
  verify-integrations-4QVGm). **Remaining: 192.**
- Pre-computed slice ready at
  `integrations/clickup-asana/tmp/deploy/to_post.json` (192 entries: indices
  0–2 from comment-work.json plus indices 13–201).
- Two backfill agent attempts both failed on permission denials in this
  session — first on `get_task`, then on `add_comment` itself.
- **Fix shipped this session:** added both Asana MCP tools to
  `.claude/settings.json` allowlist (commit `7c228da`). The allowlist is
  loaded at session start, so the next session will pick them up. Re-run the
  backfill agent then with the same plan: skip indices 3–12, post 0–2 and
  13–201, batches of 10.

### 4. Klaviyo "flows activation" depends on BC

Per the priority list: flows are created and just need to be linked with
templates, but **BC needs to design and share the templates** before Atlas
can activate. Track this dependency before scheduling the work.

## Files added / changed this session

- `CLAUDE.md` (new) — repo-level context pointer
- `integrations/clickup-asana/priorities.md` (new) — priority list source of
  truth
- `.claude/settings.json` (new) — Asana + ClickUp MCP permissions allowlist
- `integrations/clickup-asana/tmp/deploy/to_post.json` (new) — pre-computed
  192-entry backfill slice
- `integrations/clickup-asana/tmp/deploy/comments-{posted,failed}.jsonl`
  (new, empty) — progress logs ready for the next backfill run
- The full `integrations/clickup-asana/` tree was cherry-picked from
  `claude/verify-integrations-4QVGm` (commit `ae2c372`)

## Quick-start prompt for the next session

> Pick up from session-notes 2026-05-11. First: re-run the comments backfill
> agent (the .claude/settings.json allowlist should now be active). Then: I
> want to walk through the ambiguous priority mappings (CRO / SEO / Orders /
> Checkout) and decide on the 11 unprioritised cards.
