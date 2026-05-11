# Bargain Chemist — Priority List

Source of truth for what's HIGH / MED across the migrated Asana project
`1214475175808445`. Atlas Digital owns assigning the Priority field inside
Asana itself; this file is the working reference for conversations between
Harpreet and Claude. Update by editing this file and committing on the
current working branch.

Last updated: 2026-05-11

## Engineering (Eng list)

| Priority | Item | Card |
|---|---|---|
| HIGH | Inventory sync by location | ZBR-3003 |
| HIGH | Doordash implementation | ZBR-2323 |
| HIGH | Toniq stock sync processes | ZBR-2846 |
| HIGH | CRO issues | unmapped — confirm which cards (candidates: ZBR-2997 CWV Audit, ZBR-3034 Product Filter Review, ZBR-3100 Stock issue dark store) |
| HIGH | SEO issues | ZBR-2654 SEO & GEO (likely also ZBR-3066 Structured Data Findings from OMD) |
| MED | Orders investigation | ZBR-3078 Order Investigation (also possibly ZBR-2328 Order Editing investigation, ZBR-2923 Update lifecycle of an order documentation) |
| MED | Checkout analysis | ZBR-2995 Hard Checkout Error (also possibly ZBR-2793 AU Checkout Currency Blocker — on hold) |

## Klaviyo (Klaviyo list)

| Priority | Item | Card |
|---|---|---|
| HIGH | Pop up activated | ZBR-3083 Pop Up Sign Up Form |
| HIGH | Investigate flows + identify gaps | ZBR-2812 Flow expansion |
| HIGH | Flows activation (link templates — BC to design and share) | ZBR-2814 Replenishment Flows |
| MED | Segmentation conversation continued | ZBR-2803 Segmentation use |

## Live cards NOT yet prioritised

These are in the Asana Backlog but Harpreet hasn't assigned a priority.
Surface them next time we discuss work.

**Engineering:**
- ZBR-3076 BackEnd Documentation
- ZBR-3075 FrontEnd Documentation
- ZBR-3042 April Sale Theme
- ZBR-2931 GA4 Search Tracking Implementation
- ZBR-2850 Days for fulfilment & Unfulfilled reporting
- ZBR-2565 Bulk email customers from shopify
- ZBR-2792 Shipping Issues *(on hold)*

**Klaviyo:**
- ZBR-2805 Design guidance
- ZBR-2801 Campaign Strategy
- ZBR-2802 Working with the internal BC team to optimise campaign performance
- ZBR-2806 Non-promotional Campaign

## Daily sync workflow

Atlas Digital will edit Asana directly; Claude does not write to the Priority
field. To keep this file in sync each day:

1. Pull task data via Asana MCP (`search_tasks` / `get_tasks` against project
   `1214475175808445`), focusing on cards that have changed since the prior
   sync (use `modified_since` filter).
2. For each card, check status, section, assignee, and any custom field
   changes (especially Priority once Atlas adds the field, plus Estimate /
   Time remaining).
3. Update the tables above to mirror what's in Asana. Move newly-DONE cards
   into a "Recently completed" section at the bottom, then drop them after
   ~14 days.
4. Commit with message `Daily Asana sync — YYYY-MM-DD` on the active working
   branch.

If Asana access is denied for any tool, surface the block to Harpreet rather
than silently skipping. Never write to Asana cards on Atlas's behalf
without explicit permission for that session.
