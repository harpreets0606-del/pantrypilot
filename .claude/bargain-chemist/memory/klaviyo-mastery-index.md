# Klaviyo Mastery Index

**Read this FIRST before planning any Klaviyo task.** Cite verification status before relying on a capability. Update this index after every empirical finding.

---

## ⚠️ TOP RULES — DO NOT VIOLATE (added 2026-05-08 after repeat failures)

These are the rules I have repeatedly violated within a single session, even though they were already documented elsewhere in this index. Read them every time before planning.

1. **Never PATCH a flow-cloned template directly.** `PATCH /api/templates/{cloned_id}/` returns HTTP 404 even when GET works. Cloned templates (those bound to flow-actions) are read-only via PATCH. **Workflow:** POST new owned global with patched HTML → PATCH `/api/flow-actions/{action_id}/` with new `template_id` → Klaviyo creates new clone → fresh GET to read new clone ID. Pattern verified 4× on 2026-05-08 (RtiVC5, XbQiKg E1+E2, Sr3hxz, V9XmEm E1).

2. **Klaviyo PATCH responses are eventually-consistent.** The `template_id` in a PATCH response on `/api/flow-actions/{id}` may show the OLD clone ID even when the PATCH succeeded. Always do a fresh GET ~2s later and read template_id from THAT response. See `patch_search_abandonment_fix.py:patch_action()` for the proven pattern.

3. **Never add a phrase to a banned-phrase list without checking primary data.** Specific marketing claims like "thousands of Kiwis" are NOT auto-fabricated. CLAUDE.md §"NO UNVERIFIED FACTS RULE" applies in BOTH directions — don't insert unverified facts AND don't reject claims as fabricated without verification. Pre-add check: query `klaviyo_query_metric_aggregates` on `Sxnb5T` (Placed Order, measurement=unique, weekly). If unique buyers ≥ 1000/week, claims like "thousands of Kiwis every week" are EMPIRICALLY VERIFIED.

4. **Compliance markers (legal/ASA) ≠ brand value props (creative).** Required on every email: `Always read the label`, `see your healthcare professional`, `{% unsubscribe %}`, `{{ organization.name }}`, `{{ organization.full_address }}`. Optional/creative-choice (do NOT flag absence as defect): `$79`, `Price Beat`, `30+ stores`. Different emails can lead with different value props. See `audit-rules.json` for canonical list.

5. **Different metrics use different field names.** `Viewed Product` (XQ2zfW): `event.Name`, `event.URL`, `event.ImageURL`, `event.Price`, `event.CompareAtPrice`, `event.ProductID`, `event.Categories`. `Boost Clicked Search Result` (Y2qHKK): `event.productName`, `event.productUrl`, `event.productCategory`, `event.productPrice`, `event.searchQuery`. `Added to Cart` (S4jKYD via Shopify): `event|lookup:'Product Name'`, `event|lookup:'URL'`, `event|lookup:'$value'`. See `audit-rules.json:klaviyo_field_name_map`.

6. **Klaviyo cloned templates are not visible in the UI Templates list.** Searching the [Templates page](https://www.klaviyo.com/templates) for a cloned template ID will return nothing. They live attached to flow-action message slots, accessible only via API. To view visually: open the flow URL → click into the email → template editor opens. Direct URL: `https://www.klaviyo.com/flow/{flow_id}/edit`.

7. **Trust but verify subagent reports.** Audit subagents may pull from snapshots that are stale. Always spot-check at least 3 key claims from any subagent audit by direct MCP fetch before propagating findings. The agent's report describes its INTENT, not verified ground truth.

8. **Run `prelude_check.py` at session start.** It prints last 5 decisions, all ❌ broken capabilities, mandatory protocols, audit-rules.json reminders, current flow state, and open predictions. Skipping it = forgetting prior session context.

---

## How to use this file

1. **Find the capability your task touches** in the table below.
2. **Read the Status column.** ✅ = safe to rely on. 🟡 = documented but unverified — flag the assumption to the user before depending on it. ❌ = known broken, design around it. ❓ = unknown — run a probe before designing.
3. **Cite the Source** — link to the deep-dive file or probe result that backs the status.
4. **At task end, update this file**: bump `Last verified`, add new gotchas, escalate 🟡 → ✅ when probed.

## Verification legend

| Symbol | Meaning |
|---|---|
| ✅ | Empirically verified via probe or live deploy. Cite the snapshot file. |
| 🟡 | Documented in Klaviyo official docs and/or used in production by us, but not directly probed in our test suite. Trust at lower confidence. |
| ❌ | Known broken or not supported. Must design around. |
| ❓ | Unknown / not yet investigated. Probe before relying on. |

## Probe directory

All empirical probes live in `.claude/bargain-chemist/scripts/probes/`. Probe results snapshot to `.claude/bargain-chemist/snapshots/<date>/probe-<name>/`.

When a 🟡 or ❓ entry blocks a task, write a probe (one capability per probe), run it, snapshot results, and bump this index.

---

## A. Authentication & scopes

| Capability | Status | Endpoint / mechanism | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Private API key (server-side) | ✅ | `Authorization: Klaviyo-API-Key <key>` header | `klaviyo-api-capabilities.md`, `.env.local` | 2026-05-08 | Per-key scopes set at Klaviyo Account → API keys. Wide-scope keys preferred for dev box. |
| Public API key (client-side) | 🟡 | URL param / Klaviyo.js | Klaviyo docs | — | Read-only; for tracking events from web/app, not scripts. |
| `templates:read` scope | ❌ | MCP token lacks this scope (verified 2026-05-07: MCP `klaviyo_get_email_template` returns 401 on flow-cloned templates) | `decisions-log.md` 2026-05-07 entries | 2026-05-07 | The user's `.env.local` PowerShell key has it; MCP key doesn't. |
| `flows:write` scope | ✅ | Required for POST/PATCH /api/flows and PATCH /api/flow-actions | `klaviyo-api-capabilities.md` line 178 | 2026-05-07 | |
| Revision header conventions | ✅ | `revision: YYYY-MM-DD` for stable, `YYYY-MM-DD.pre` for beta (e.g. `2024-10-15.pre`) | `klaviyo-api-capabilities.md` line 178 | 2026-05-07 | New endpoints often live behind a beta revision for ~1 quarter before going GA. |

## B. Flows

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List flows | ✅ | `GET /api/flows/` | live use, MCP `klaviyo_get_flows` | 2026-05-08 | Page size cap is 50 (not 100). |
| Get flow with full definition | ✅ | `GET /api/flows/{id}/?additional-fields[flow]=definition` | snapshots/2026-05-07/audit/ | 2026-05-07 | Returns `included` array with all flow-actions when `include=flow-actions` added. |
| Create flow with full definition | 🟡 (Beta) | `POST /api/flows/` revision `2024-10-15.pre` | `klaviyo-api-capabilities.md` lines 169-186 | 2026-05-07 | Beta ≠ unsuitable for one-shot creation. Daily limit 100/day, 15/min steady, 1/s burst. |
| Update flow status (live↔draft↔manual) | ✅ | `PATCH /api/flows/{id}/` body `{"status":"manual"}` | cleanup script run 2026-05-08 | 2026-05-08 | `paused` is NOT a valid status; maps to `manual` internally. |
| Update flow definition (steps/branches/triggers) | ❌ | n/a | `klaviyo-api-capabilities.md` line 171 | 2026-05-07 | Only `status` is patchable. To restructure: DELETE + recreate via POST. |
| Update audience / profile filter | ❌ | n/a | `klaviyo-api-capabilities.md` line 172 | 2026-05-07 | Returns "definition is not a valid field for the resource flow". UI only. |
| Archive a flow | ❌ | n/a | `decisions-log.md` 2026-05-08 | 2026-05-08 | `archived` is NOT a patchable field. `POST /api/flows/{id}/archive/` returns 404. **Workarounds:** DELETE for disposable; UI for retain-archived. |
| Delete flow | ✅ | `DELETE /api/flows/{id}/` | cleanup script 2026-05-08, 7 deletes HTTP 204 | 2026-05-08 | Cloned message templates orphan but stay in template list. Local snapshots unaffected. |
| Delete a single flow-action | ❌ | n/a | `probe_flow_action_delete.py` 2026-05-08 | 2026-05-08 | `DELETE /api/flow-actions/{id}` returns HTTP 405 Method Not Allowed. Nested form `DELETE /api/flows/{flow_id}/flow-actions/{action_id}` returns 404. Must DELETE+recreate the entire flow (Path B). |

## C. Flow actions

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List flow-actions for a flow | ✅ | `GET /api/flows/{id}/flow-actions/` | snapshots/2026-05-07/audit/ | 2026-05-07 | |
| `send-email` action schema | ✅ | POST/PATCH | `klaviyo-api-capabilities.md` lines 222-249 | 2026-05-07 | Use `subject_line` (NOT `subject`), `smart_sending_enabled` (NOT `smart_sending`). |
| `time-delay` action schema | ✅ | POST | `klaviyo-api-capabilities.md` lines 200-215 | 2026-05-07 | `delay_until_weekdays` and `delay_until_time` ONLY valid when `unit=days`. Otherwise omit. |
| `trigger-split` action (UI-built) | 🟡 | n/a | `decisions-log.md` Y84ruV audit | — | Live in Y84ruV (98627485). Routing accuracy untested empirically; same family as broken conditional-split. |
| `conditional-split` action with `metric_filters` on `$value` (runtime) | ❌ | POST schema accepted, runtime broken | `decisions-log.md` 2026-05-08 v3 sandbox; `snapshots/2026-05-08/v3-sandbox-v2/verify-results.json` | 2026-05-08 | 2/2 routable profiles routed wrong (always falls to `else`). **Workaround: in-template Liquid.** |
| `conditional-split` action with profile-property filters | ❓ | POST schema | — | — | Unknown if profile-property splits work where metric-property splits fail. Probe before relying on. |
| `profile-filter` action | 🟡 | POST schema partial | `klaviyo-api-capabilities.md` line 251 | — | Known: `data.profile_filter` required (object), `data.condition_groups` invalid, links use `next_if_true`/`next_if_false`. Full schema not yet probed. |
| Update flow-action (swap template, edit subject, etc.) | ✅ | `PATCH /api/flow-actions/{id}/` revision `2025-10-15` | `decisions-log.md` 13 deploys 2026-05-07; `klaviyo_apply_3_fixes.py` | 2026-05-07 | Full `definition` body required. Updates clone-on-assign — re-PATCH forces re-clone. |
| A/B test action via API | ❌ | n/a | `klaviyo-api-capabilities.md` line 182 | 2026-05-07 | Not supported via API; UI only. |
| Once-created flow definition immutable via API | ✅ (constraint) | n/a | `klaviyo-api-capabilities.md` line 183 | 2026-05-07 | Recommended workflow: build reference flow in UI → GET definition → mutate → POST as new flow. |

## D. Templates & email rendering

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Create email template (HTML / CODE) | ✅ | `POST /api/templates/` | `klaviyo-api-capabilities.md` line 78 | 2026-05-07 | Set `editor_type: CODE` explicitly; default may be SYSTEM_DRAGGABLE. |
| Get template (global) | ✅ | `GET /api/templates/{id}/` | live use | 2026-05-07 | Returns 200 for both global and flow-cloned IDs. |
| PATCH global template HTML | ✅ | `PATCH /api/templates/{id}/` | render-probe scripts | 2026-05-08 | Works on owned globals. |
| PATCH flow-cloned template HTML | ❌ | `PATCH /api/templates/{cloned_id}/` returns 404 | `klaviyo-api-capabilities.md` lines 134-144 | 2026-05-07 | Klaviyo platform bug. **Workaround:** PATCH owned global, then PATCH flow-action to re-assign (forces re-clone). |
| Delete template | ✅ | `DELETE /api/templates/{id}/` | `klaviyo-api-capabilities.md` line 81 | 2026-05-07 | Cloned templates from deleted flows orphan — harmless but cluttered. |
| Render template | ✅ | `POST /api/template-render/` revision `2025-10-15` | render-probe + probe-elif | 2026-05-08 | Does NOT accept inline html — requires existing `template_id`. Workflow: PATCH owned template → render → restore. |
| Clone template | ✅ | `POST /api/template-clone/` | `klaviyo-api-capabilities.md` line 82 | 2026-05-07 | |
| Get template for a flow message | ✅ | `GET /api/flow-messages/{id}/template/` | `klaviyo-api-capabilities.md` line 83 | 2026-05-07 | |
| Editor types: CODE / USER_DRAGGABLE / SYSTEM_DRAGGABLE | ✅ | n/a | `klaviyo-api-capabilities.md` lines 67-75 | 2026-05-07 | API-created templates are CODE. Flow editor produces SYSTEM_DRAGGABLE. PATCH HTML on SYSTEM_DRAGGABLE updates `definition` only, not raw HTML. |
| Header Block "links" layout + logo subblock | ❌ | n/a | TUbBRk MCP fetch 2026-05-07 | 2026-05-07 | MCP `klaviyo_get_email_template` returns 500 on TUbBRk: *"Header blocks with 'links' desktop layout must not include a logo subblock"*. Side-effect on send pipeline unverified. **Mitigation:** rebuild as CODE editor_type. |

## E. Liquid syntax (Klaviyo Django)

See `klaviyo-template-syntax-verified.md` for full details + render-probe evidence.

| Capability | Status | Source | Last verified | Notes |
|---|---|---|---|---|
| `{{ first_name }}` direct profile field | ✅ | render-probe 02 | 2026-05-08 | |
| `{{ first_name\|default:'there' }}` default filter | ✅ | render-probe 03 | 2026-05-08 | |
| `{{ event\|lookup:'$value' }}` `$`-prefixed event property | ✅ | render-probe 06 | 2026-05-08 | Required for any `$`-prefixed key. |
| `{{ event.$value }}` direct dotted access | ❌ | render-probe 07 | 2026-05-08 | Django parser breaks on `$` in identifier. Returns 400. |
| `{% if event\|lookup:'$value' < 79 %}` numeric compare | ✅ | render-probe + probe-elif | 2026-05-08 | |
| `{% if %}{% elif %}{% else %}` | ✅ | probe-elif at $value=20/50/120 | 2026-05-08 | 3/3 PASS standalone + 3/3 PASS embedded in 50KB chrome (`email1-3tier/`). |
| `{% if %}{% elif %}{% else %}` boundary edges ($0/$29/$29.99/$30/$30.01/$78.99/$79/$79.01/$120) | ✅ | `probe_elif_boundaries.py` 2026-05-08 | 2026-05-08 | 9/9 numeric cases PASS, both bare and defensive `{% with %}+default:0` patterns. Strict `<30` excludes 30 (→B); strict `<79` excludes 79 (→C). Matches free-ship policy. |
| `{% with v=… %}…{% endwith %}` | ✅ | `klaviyo-template-syntax-verified.md` line 20 | 2026-05-08 | |
| Empty / null / missing `event\|lookup:'$missing'` | ✅ | `probe_null_value_handling.py` 2026-05-08 | 2026-05-08 | Missing key renders as literal `'None'` (visible to recipient). `\|default:0` catches both missing AND explicit null. Conditional `{% if missing < 79 %}` evaluates TRUE (None < num is True in Django). String `$value` does NOT coerce to numeric in `<` compare; falls to `else`. |
| `\|float`, `\|round(2)` | ❌ | klaviyo-template-syntax-verified.md line 33 | 2026-05-08 | Jinja2-only. Falls through as literal text. |
| `\|floatformat:2`, `\|add:-N` | ✅ | klaviyo-template-syntax-verified.md line 34 | 2026-05-08 | Django-native. |
| `{% currency_format %}` | ✅ | live TuHa4f cart loop | 2026-05-08 | |
| `{% unsubscribe 'Click here' %}` Klaviyo tag | ✅ | live use, klaviyo-template-syntax-verified.md line 22 | 2026-05-08 | |
| Chained `\|replace:'a','b'\|other_filter` | ❌ | klaviyo-api-capabilities.md lines 5-9 | 2026-05-07 | Parser tokenizes comma as filter delimiter. Drop replace; rely on Shopify 301 redirect. |
| Liquid in `subject_line` field (parses same as body) | ✅ | `probe_subject_liquid.py` 2026-05-08 | 2026-05-08 | 9/9 candidate patterns parse cleanly via `/api/template-render` (same Django parser). `{{ first_name\|default:'…' }}` and `{% if event\|lookup:'$value' < 79 %}…{% else %}…{% endif %}` both safe in subject. **Regression evidence**: confirmed the buggy `{{ first_name\|default:'Your' }} order's…` form renders as `"Sarah order's…"` (broken possessive). Recommendation: prefer static subjects when name doesn't fit grammatically. |
| Arithmetic in templates (`{{ 79 - x }}`) | ❌ | klaviyo-template-syntax-verified.md line 35 | 2026-05-08 | Django doesn't support expression syntax. Use `\|add:-N` or compute server-side. |

## F. Events & metrics

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List metrics | ✅ | `GET /api/metrics/` | live use | 2026-05-07 | |
| Get metric | ✅ | `GET /api/metrics/{id}/` | live use | 2026-05-07 | |
| List events filtered by metric_id | ✅ | `GET /api/events/?filter=equals(metric_id,"X")` | klaviyo-api-capabilities.md, MCP | 2026-05-07 | |
| Create event (write) | ✅ | `POST /api/events/` | v3 sandbox reinject 2026-05-08 | 2026-05-08 | HTTP 202 on success. Used to fire synthetic events for runtime tests. |
| Query metric aggregates | ✅ | `POST /api/metric-aggregates/` (or via MCP) | live use | 2026-05-07 | |
| Verified Shopify "Checkout Started" payload shape | ✅ | klaviyo-template-syntax-verified.md (3 real events sampled 2026-05-08) | 2026-05-08 | `$value` numeric. `$extra.line_items` = full cart. **For "Return to checkout" CTA: use `event.extra.checkout_url` (cart recovery URL). DO NOT use `event.extra.full_landing_site` — that's the product page customer was on before checkout.** Trap: `full_landing_site` SOUNDS right but always points to `/products/<handle>`, not the cart. Discovered via Y84ruV v3 test sends 2026-05-08. |
| **Preview-vs-production divergence trap** | ⚠️ | decisions-log 2026-05-08 Y84ruV v3 URL fix | 2026-05-08 | Klaviyo's UI preview can substitute placeholder context that masks bugs. Real test sends use the actual production renderer + real event payloads. Always pair render-tests with at least one real test send + manual link-click before declaring a deploy ready. |
| **PATCH /api/flow-actions response is eventually-consistent** | ⚠️ | decisions-log 2026-05-08 XbQiKg E1 deploy | 2026-05-08 | PATCH HTTP 200 response can return the OLD cloned `template_id` even when the PATCH actually applied. Fresh GET ~2 seconds later shows the new clone. **Always verify post-PATCH state via a fresh GET, not by reading the PATCH response.** Pattern in `patch_search_abandonment_fix.py:patch_action()` (commit `d7e8531`). |
| Verified Shopify "Added to Cart" payload | ✅ | klaviyo-api-capabilities.md lines 25-43 | 2026-05-07 | `ImageURL` is one word camelCase (not `Image URL` with space). Common trap. |
| Custom metric for sandbox testing (XyMJz4 in v3) | ✅ | manual creation via UI / API events | snapshots/2026-05-08/v3-sandbox-v2/state.json | 2026-05-08 | Decoupled from real Shopify metrics so probes don't affect production analytics. |

## G. Profiles & subscriptions

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Get profile by ID | ✅ | `GET /api/profiles/{id}/` (or MCP) | live use | 2026-05-07 | |
| List profiles with filters | ✅ | `GET /api/profiles/?filter=…` | live use | 2026-05-07 | |
| Create profile | ✅ | `POST /api/profiles/` | v3 sandbox 2026-05-08 | 2026-05-08 | |
| Update profile | ✅ | `PATCH /api/profiles/{id}/` | live use | 2026-05-07 | |
| Subscribe profile to marketing (consent capture) | ✅ | `POST /api/profile-subscription-bulk-create-jobs/` (or MCP `klaviyo_subscribe_profile_to_marketing`) | v3 sandbox 2026-05-08 | 2026-05-08 | Subscription is async; ~120s propagation lag observed in v3 sandbox. |
| Unsubscribe / suppress | ✅ | bulk job pattern | klaviyo-api-capabilities.md line 273 | 2026-05-07 | |
| Bot-protection suppression edge case | ✅ (workaround) | re-inject via state.json upsert | git commit `9173254` ("reinject upserts profiles into state.json so verify can find them") | 2026-05-08 | Klaviyo's bot-protection sometimes suppresses test profiles; reinject phase recreates them. |
| Profile property paths in Liquid | ✅ | `{{ properties.name }}` form | git commit `270f91c` ("Use Klaviyo's properties['name'] form") | 2026-05-07 | Use `properties[…]` not `profile.properties.…` in Klaviyo Django context. |

## H. Lists & segments

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List all lists | ✅ | `GET /api/lists/` | live use, MCP | 2026-05-07 | |
| Create list | ✅ | `POST /api/lists/` | klaviyo-api-capabilities.md line 270 | 2026-05-07 | |
| Add profile to list | ✅ | `POST /api/list-relationships/profiles/` | klaviyo-api-capabilities.md line 270 | 2026-05-07 | |
| List segments | ✅ | `GET /api/segments/` | live use | 2026-05-07 | |
| Create segment | ✅ | `POST /api/segments/` | klaviyo-api-capabilities.md line 271 | 2026-05-07 | Definition uses condition-group JSON. |
| Edit segment definition | 🟡 | PATCH | klaviyo-api-capabilities.md line 271 | — | "Definitions are also editable" per docs; not directly probed by us. |
| Segment member count freshness lag | ❓ | — | — | Anecdotal: Klaviyo segment membership refreshes asynchronously; counts can lag triggering events by minutes. Not measured. |
| Delete segment | ✅ | `DELETE /api/segments/{id}/` | klaviyo-api-capabilities.md | 2026-05-07 | |

## I. Campaigns

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List campaigns | ✅ | `GET /api/campaigns/` | live use, MCP `klaviyo_get_campaigns` | 2026-05-07 | |
| Get campaign | ✅ | `GET /api/campaigns/{id}/` | live use | 2026-05-07 | |
| Get campaign report | ✅ | `POST /api/campaign-values-reports/` (MCP `klaviyo_get_campaign_report`) | live use | 2026-05-07 | |
| Create campaign (draft) | ✅ | `POST /api/campaigns/` (MCP `klaviyo_create_campaign`) | klaviyo-api-capabilities.md line 272 | 2026-05-07 | |
| Send strategies (immediate / static / smart_send_time / throttled) | 🟡 | MCP campaign-creation schema | MCP tool schema | — | Schema seen in MCP tool def. Not directly probed. |
| Throttle percentages | 🟡 | enum: 10/11/13/14/17/20/25/33/50 | MCP tool schema | — | Per Klaviyo docs. |
| Assign template to campaign-message | ✅ | `POST /api/campaign-message-assign-template/` (MCP `klaviyo_assign_template_to_campaign_message`) | live use | 2026-05-07 | Required step after creating campaign + template separately. |
| UTM tracking config | ✅ | Account → Tracking → UTM Tracking (UI) | decisions-log.md 2026-05-07 UTM entry | 2026-05-07 | utm_source = "Klaviyo" (capitalized, Klaviyo's preset has no lowercase). utm_medium = "email" critical for GA4. |

## J. Universal Content blocks

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Create universal content block | 🟡 | `POST /api/universal-content/` | klaviyo-api-capabilities.md lines 52-62 | 2026-05-07 | Documented stable; not yet probed by us. |
| PATCH propagation to all consumers | 🟡 | `PATCH /api/universal-content/{id}/` | klaviyo-api-capabilities.md lines 56-62 | 2026-05-07 | **Critical primitive for compliance footer.** Single PATCH propagates to every template using `<div data-klaviyo-universal-block="block_id">`. Worth probing before relying on for footer rollouts. |
| Block types | ✅ | enum: button, drop_shadow, horizontal_rule, html, image, spacer, text | klaviyo-api-capabilities.md line 63 | 2026-05-07 | |

## K. Webhooks

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List webhooks / configure | ❓ | TBD | Klaviyo docs (not yet read) | — | Not used by Bargain Chemist yet. Phase 2 deep-dive. |
| Webhook signing / replay protection | ❓ | — | — | — | Not investigated. |

## L. Translations / multi-locale

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Create translation collection | 🟡 | `POST /api/translations/` (MCP `klaviyo_create_translation`) | MCP tool schema | — | Channel ↔ relationship-type matrix per MCP schema. NZ-only currently; not in scope. |

## M. Coupons

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Coupons CRUD | ✅ (capability), ❌ (policy) | `POST /api/coupons/` etc. | klaviyo-api-capabilities.md line 274 | 2026-05-07 | **BANNED for Bargain Chemist.** EDLP strategy + Price Beat Guarantee — never recommend, draft, or build coupon-based copy. See `no-coupon-strategy.md`. |

## N. Forms

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List forms | ✅ | `GET /api/forms/` | klaviyo-api-capabilities.md line 277 | 2026-05-07 | Read-only via API. |
| Create / update form | ❌ | n/a | klaviyo-api-capabilities.md line 277 | 2026-05-07 | UI only. |

## O. Reviews (Klaviyo Reviews product)

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| List public reviews | 🟡 | TBD | Klaviyo docs | — | Not used yet. |

## P. Reporting & analytics

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Flow values report | ✅ | `POST /api/flow-values-reports/` (MCP `klaviyo_get_flow_report`) | live use | 2026-05-07 | Group by flow_id, send_channel, flow_message_id. |
| Campaign values report | ✅ | `POST /api/campaign-values-reports/` (MCP `klaviyo_get_campaign_report`) | live use | 2026-05-07 | |
| Metric aggregates | ✅ | MCP `klaviyo_query_metric_aggregates` | live use | 2026-05-07 | |
| Conversion metric ID for reports | ✅ | MCP requires `conversionMetricId` param | MCP tool schema | 2026-05-07 | Default: "Placed Order" metric ID. |
| Statistics enum (open_rate, click_rate, conversion_rate, etc.) | ✅ | MCP tool schema | MCP enum list | 2026-05-07 | Full list in MCP `get_flow_report` schema. |

## Q. Catalogs (product feed)

| Capability | Status | Endpoint | Source | Last verified | Gotchas |
|---|---|---|---|---|---|
| Catalogs CRUD | ✅ | klaviyo-api-capabilities.md line 276 | 2026-05-07 | | Not actively maintained by us; Shopify integration auto-syncs. |
| Get catalog items | ✅ | MCP `klaviyo_get_catalog_items` | MCP tool | 2026-05-07 | |

## R. Rate limits & job-based bulk ops

| Capability | Status | Notes | Source | Last verified |
|---|---|---|---|---|
| Per-endpoint rate limits | 🟡 | Documented per-endpoint in Klaviyo dev portal | — | — |
| POST /api/flows/ daily limit | ✅ | 100/day, 15/min steady, 1/s burst | klaviyo-api-capabilities.md line 180 | 2026-05-07 |
| Bulk profile subscription job | ✅ | `POST /api/profile-subscription-bulk-create-jobs/` | v3 sandbox use | 2026-05-08 |
| 429 retry pattern | 🟡 | Exponential backoff | git commit `1571f7b` ("verify-flows: retry flow-values-reports on 429 with backoff") | 2026-05-07 |
| Asynchronous job polling | ❓ | — | — | — |

## S. Smart sending & deduplication

| Capability | Status | Notes | Source | Last verified |
|---|---|---|---|---|
| `smart_sending_enabled` field | ✅ | Per flow-action message | All live flow-action audits | 2026-05-07 |
| Smart sending dedupe window | 🟡 | Default 16 hours per Klaviyo docs (not directly probed) | — | — |
| Transactional flag bypasses smart sending | 🟡 | `transactional: true` exempts | klaviyo-api-capabilities.md line 245 | 2026-05-07 |
| Order of evaluation: trigger → flow filter → conditional split → action filter | ❓ | — | — | — |
| Flow re-entry rules | ❓ | "Has not been in this flow in last N days" filter behavior | — | — |

## T. Cross-cutting concerns

| Concern | Status | Notes |
|---|---|---|
| **Verification protocol** | ✅ | See top of `CLAUDE.md`. Pull live data; compare timestamps to snapshots; emit verification line in output. |
| **No unverified facts** | ✅ | See `CLAUDE.md`. Approved claims register in `no-coupon-strategy.md`. |
| **Brand voice** | ✅ | See `brand-voice-design-template.md`. Warm, descriptive, wellness-coded. ~43-char subjects. |
| **NZ ASA Therapeutic Code** | ✅ | No fear-based language. Footer must include address + "Always read the label". See compliance scan 2026-05-06. |
| **Pharmacy-only products disclaimer** | ✅ | Required regulatory text in templates touching restricted SKUs. User confirmed: keep as-is. |
| **`$79` free shipping threshold** | ✅ | Set via Zyber Shipping Rate Provider app (NOT Shopify-native). Not queryable directly. |
| **Sender authentication (DKIM/SPF/DMARC)** | ❓ | Not verified. Phase 2 priority for deliverability. |

---

## Open probes queued

| Probe | Capability gap | Priority |
|---|---|---|
| `probe_elif_boundaries.py` | Boundary cart values $29/$30/$78/$79 + null/string $value | Y84ruV deploy gate |
| `probe_null_value_handling.py` | `event\|lookup:'$missing'` behavior | Y84ruV deploy gate |
| `probe_subject_liquid.py` | Liquid in subject_line — parser parity with template body | Y84ruV deploy gate |
| `probe_flow_action_delete.py` | Can a single flow-action be deleted via API | Y84ruV deploy gate |
| `probe_universal_content_propagation.py` | PATCH on universal content propagates to all consumers | Phase 2 — compliance footer rollouts |
| `probe_smart_sending_window.py` | Empirical 16-hour dedupe window | Phase 2 — campaign cadence |
| `probe_segment_count_lag.py` | Segment membership refresh latency | Phase 2 — flow trigger timing |
| `probe_conditional_split_profile_property.py` | Whether conditional-split works for profile-property filters where it's broken for metric-property | Phase 2 — flow architecture |
| `probe_flow_filter_eval_order.py` | Order of trigger filter / flow filter / conditional split / action filter evaluation | Phase 2 — flow architecture |

When a probe runs and resolves a 🟡 or ❓ entry, **edit this file** to ✅ and bump `Last verified`.

## Mastery index changelog

- **2026-05-08**: Initial version. Rolled up findings from `klaviyo-api-capabilities.md`, `klaviyo-template-syntax-verified.md`, `decisions-log.md` (entries 2026-05-06 through 2026-05-08), and v3 sandbox + cleanup runs.
