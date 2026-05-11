# ClickUp → Asana Migration — Deploy Status (2026-05-11)

## Outcome summary

| Phase | Done | Remaining |
|---|---|---|
| **Cards created** | ✅ 30/30 in Asana | — |
| **Section assignment** | ✅ 28 live cards in Backlog, 2 done summaries in Done | — |
| **Custom fields** | ✅ Name, Details, Manager, Priority, Estimated time mapped for every card | — |
| **Asana assignee** | ✅ Set to BC team member (Harpreet/Gurdeep) where CU assignee resolvable | Zyber users not in Asana — captured in description text only |
| **Attachments re-hosted (Zapier)** | ✅ 36 of 38 | 2 skipped (truncated URLs in source) |
| **Comments backfilled** | 🟡 10 of 202 (ZBR-2323 partial) | 192 remaining |
| **Read-back hash verify** | — | After comments complete |

## Asana project
- **Project:** Bargain Chemist (`1214475175808445`)
- **Live cards:** 28 in `Backlog` (`1214475175808453`) — Atlas to estimate
- **Done summaries:** 2 in `Done` (`1214512998624375`)

## Saved state (in `integrations/clickup-asana/tmp/deploy/`)
- `created-gids.json` — ZBR → Asana task GID map for all 30 cards
- `attach-work.json` — per-attachment re-host work list (used)
- `comment-work.json` — per-comment backfill work list (202 entries, 10 done)
- `build_payload.py` — payload generator script
- `batch-1.json` / `batch-2.json` / `batch-3.json` — card creation payloads
- `attachments-map.json` — ZBR → attachment URLs map
- `skipped-assignees.json` — 5 Zyber emails not in Asana workspace

## Issues found and resolved this session

| Issue | Resolution |
|---|---|
| Asana MCP has no `create_attachment` tool | Workaround via Zapier `attach_file` (verified end-to-end) |
| User can't generate Asana PAT (admin-locked) | OAuth route via Zapier (different permission, worked) |
| CU attachment URLs need no auth | Confirmed — Zapier fetches directly from CU CDN |
| `html_notes` rejected `<p>` tag (silent restriction in MCP schema) | Switched to plain-text `notes` field — preserves 100% CU content |
| `<hr/>` and `&middot;` initially caused XML invalid errors | Used plain text instead of XML markup |
| Asana GID overflows int32 in Zapier | Pass GIDs as strings, not numbers |
| Zyber team users not in Asana workspace | Preserved in description ("Assignees (CU): ..."), Asana assignee left null for Zyber-only cards |
| 2 Korean-filename attachments truncated in source export | Skipped; agency can re-take if needed |

## Outstanding for follow-up session

**Comments backfill — 192 remaining.** Work list pre-computed in `tmp/deploy/comment-work.json`. To resume:
1. Read the work list, skip first 10 entries (already done in ZBR-2323).
2. For each entry, call `mcp__0d1c5c0f-718c-4905-9c72-ee342d312ed8__add_comment` with `task_id = .asana_gid` and `text = .text`.
3. Batches of ~10 parallel calls per turn work well.

**Heaviest remaining threads:**
- ZBR-2323 (Doordash): 48 more (first 10 done)
- ZBR-3003 (Inventory sync by locations): 33
- ZBR-2792 (Shipping Issues): 19
- ZBR-2565 (Bulk email): 13
- ZBR-2995 (Hard Checkout Error): 13
- ZBR-2654 (SEO & GEO): 12
- ZBR-2846 (Toniq Stock Sync): 8
- 19 others with 1–5 each

## How to verify in Asana

1. Open project: https://app.asana.com/1/1205781270518547/project/1214475175808445
2. Sort/filter by **Details** custom field to see CU statuses (e.g., "Eng · client review")
3. Open any card to see: full CU description, ZBR ID in title, Manager + Asana assignee, Priority + Estimated time custom fields, re-hosted attachments
4. ZBR-2323 (Doordash) has the first 10 comments backfilled — preview of what the rest will look like once finished

## Cleanup once everything is verified
- Disable Zapier Asana integration: tell Claude "disable the Zapier Asana action" or do it in the Zapier UI
- (Optional) Revoke Zapier's Asana OAuth from your Asana settings if you no longer need the integration
