# Decisions Log — Append-Only

> Every recommendation Claude makes goes here, with a falsifiable prediction. Future sessions read this to (a) know what's been tried and (b) check whether predictions came true.

## Format

```
## YYYY-MM-DD — <short title>
- **Context**: what was being analysed, what data
- **Recommendation**: what was proposed
- **Action taken**: <yes/no/partial — fill in next session>
- **Prediction**: if we do X, metric Y will move by Z within N days
- **Confidence**: Low / Medium / High
- **Outcome** (filled in later): what actually happened
- **Learning**: what this teaches us about Bargain Chemist
```

## Open predictions (awaiting outcome)

_None yet._

## Closed entries

_None yet — log starts when Phase 1 is complete._

---

## 2026-05-06 — Memory architecture initialised

- **Context**: User asked Claude to design persistent memory + integrations for Bargain Chemist analytics
- **Recommendation**: 3-layer architecture — repo files, Zapier Tables, hooks. Specialist subagents for parallel work. Phased rollout starting with file-based memory.
- **Action taken**: Created `.claude/bargain-chemist/` structure with CLAUDE.md, memory/, playbooks/, agents/. Awaiting Zapier + GA4 + Ads connection for Phase 2.
- **Prediction**: With this structure in place + Phase 2 integrations connected, weekly analysis time drops from "re-pull everything every session" to "diff against last week's snapshot." Untested.
- **Confidence**: Medium — structure is sound but value depends on user actually feeding the system.
- **Outcome**: TBD
- **Learning**: TBD

## 2026-05-06 — Sequencing + memory discipline confirmed

- **Sequencing decision (user)**: flows + campaigns first, UTM attribution fix deferred
- **Content access decision (user)**: expand Klaviyo MCP scope (templates:read + flow-actions:read) — user actioning on their end
- **Work order**: (1) Shopify-side analysis, (2) Welcome Series content draft once content access available, (3) Compliance gate slash command, (4) Deeper Klaviyo audit
- **Memory discipline (user)**: auto-log every confirmed fact + decision. From now on Claude appends to memory/decisions-log automatically without asking.
- **Confidence**: High. User clearly directed.
- **Action taken**: Logging this entry; starting Shopify-side analysis next.

## 2026-05-06 — Klaviyo audit completed; user confirmed key facts

- **Context**: Full audit pulled from Klaviyo MCP. 3 research agents synthesised best practices + benchmarks + brand voice corpus. Memory written: klaviyo-benchmarks.md, klaviyo-best-practices.md, brand-voice-design-template.md (DRAFT), account-audit-2026-05-06.md, gaps.md.
- **User confirmed (logged as facts)**:
  - Top 90-day priority: total revenue growth
  - SMS not in scope this round
  - `[Z]` is internal naming, not external agency — can use freely
  - Welcome Series Website draft status: investigate + activate
- **Top 4 critical gaps identified** (high confidence): C1 Welcome Series in draft, C2 Sender address mixed, C3 Order Confirmation 0% conversion (no marketing element), C4 Click rates universally below benchmark
- **Outstanding unknowns blocking 95% confidence**: template HTML inaccessible (MCP 401), DKIM/SPF/DMARC unverified, list/segment counts not pulled, Reputation Repair Audience origin
- **Action taken**: None yet — holding until further user answers on questions 5–20 in `gaps.md`
- **Prediction (untested)**: activating Welcome Series + fixing C2-C3 alone will lift email-attributed revenue ~10-20% within 60 days. Falsifiable: compare Welcome Series 60-day revenue post-activation vs the 537-recipient × $1.68 RPR = $902 baseline over 90 days.
- **Confidence**: Medium-High on findings, Low on prediction (no comparable baseline yet).
- **Outcome**: TBD
- **Learning**: TBD

---

## 2026-05-07 — Welcome Series 2026 (No Coupon) created via API

**What was deployed:**
- 4 email templates uploaded via `POST /api/templates/`:
  - `BC - Welcome Email 1 - Welcome to the Family` → ID `RjiNUy`
  - `BC - Welcome Email 2 - Best Sellers` → ID `SuHDNq`
  - `BC - Welcome Email 3 - Last Nudge` → ID `UPxjA8`
  - `BC - Cart Abandonment Email 3 - Last Chance (72h)` → ID `Sq6pt2`
- New flow created via beta `POST /api/flows/` → ID `YdejKf`
- Flow shape (linear, no splits yet): Trigger (list `SxBenU`) → 5min → E1 → 1d → E2 → 2d → E3 → end
- Templates: Family B design, canonical brand voice, no coupons (per locked strategy)
- Existing `SehWRt` left untouched in DRAFT

**Pending UI work (user):**
- Add 2× "Placed Order? → exit" conditional splits between delays + emails (API schema for splits not yet verified — couldn't auto-create)
- Add flow filter "has not been in this flow in last 30 days"
- Preview each email with test profile
- Flip from DRAFT → LIVE
- Optionally archive SehWRt

**Falsifiable prediction:**
Within 14 days of LIVE activation:
- Welcome Series 2026 should hit ≥40% open rate on Email 1 (current SehWRt baseline is irrelevant — it never went live)
- Email 1 → placed-order rate ≥2.0% (Klaviyo benchmark for welcome 1st email)
- Combined 3-email RPR ≥$2.50/recipient (lower bound; benchmark $3.34)

**Confidence:** Medium — content quality is strong, brand voice locked, footer matches existing templates. Risk: feed name (`Best_Selling_No_Clearance`) may need a name fix in Klaviyo if the feed has been renamed.

**How we'll know:**
- Pull Klaviyo flow report for `YdejKf` 14 days after activation
- Compare to benchmark + to TsC8GZ (current LIVE no-coupon series)

**Related files:**
- Templates: `.claude/bargain-chemist/templates/welcome-email-{1,2,3}.html`
- Build spec: `.claude/bargain-chemist/templates/welcome-flow-build-spec.md`
- API capabilities: `.claude/bargain-chemist/memory/klaviyo-api-capabilities.md`

---

## 2026-05-07 — Flu Season E2 (YtcgUa) rebuilt from master template

**What was deployed:**
- YtcgUa template rebuilt from scratch using master template structure (matches VMMpC9 welcome series)
- File: `.claude/bargain-chemist/templates/flu-recovery-e2.html` (20,435 bytes)
- Key fixes: $79 free shipping (was $49), emoji HTML entities replacing 6 broken CDN icons, full brand footer with ASA language, correct Django syntax `{{ first_name|default:'there' }}` (was Jinja2 parentheses)
- User pasted into Klaviyo via Source view → confirmed "looks good"
- PATCH API returns 404 for flow-attached templates (named `[COMPLIANCE] msg_*`) — this is expected, manual paste is the only route

**Known remaining issue (NOT yet fixed):**
- V9XmEm E2 subject is "Have you booked your flu vaccine yet?" — this does NOT match the YtcgUa template body (which is about flu recovery products). Must update subject to "Already under the weather, {{ first_name|default:'there' }}?" and preview to "Pharmacist-backed recovery picks — feel like yourself again sooner. Free shipping over $79."

**Prediction:** After subject fix, E2 open→click rate should improve meaningfully vs current mismatch state. Unquantified — no prior valid E2 baseline.
**Confidence:** High on the diagnosis (mismatch confirmed from live data), Medium on magnitude of improvement.

---

## 2026-05-07 — Complete flow + email audit (all 17 flows)

**Scope:** All 17 flows, all email subjects/previews/smart-sending/template assignments pulled from live snapshots in `.claude/bargain-chemist/snapshots/2026-05-07/all-flows/`. Template HTML content NOT audited (Klaviyo MCP `templates:read` scope missing — 401 on all template GET calls despite valid account credentials).

**CONFIRMED LIVE ASA VIOLATIONS (fix immediately):**
1. **Ysj7sg E1 preview:** "Grab yours before it sells out again" → Rule 1(b) scarcity
2. **Ysj7sg E2 subject:** "Still available - but selling fast" → Rule 1(b)
3. **Ysj7sg E2 preview:** "Limited stock remaining. Don't miss your chance to grab one." → Rule 1(b) x2
4. **RPQXaa E2 preview:** "Items selling fast - protected by Price Beat Guarantee." → Rule 1(b)

**Other live flow issues confirmed:**
- V9XmEm E2: subject/preview mismatch with template body (vaccine vs recovery)
- Y84ruV E2+E3: identical subject + preview + smart_sending=False on both
- V4cZMd E1+E17: empty preview text + likely accidental duplicate email
- YdejKf E2: "flying off our shelves" — borderline urgency (grey area, not hard violation)

**Draft flow flags:**
- VMKAyS E3: "$5 off to complete your checkout" — explicit coupon, violates EDLP strategy. Do NOT activate.
- SehWRt: Placeholder subject, no template. Archive or build.
- TsC8GZ: All 3 emails have empty previews. Consider archiving (YdejKf is the active welcome series).
- XbQiKg E2: Placeholder subject, no template.
- VJui9n (Order Confirmation): In DRAFT — not sending. Low risk to activate after HTML check.
- RDJQYM (Post-Purchase): Manually paused. Needs activation decision.

**Unresolved (need template HTML):**
- $79 threshold correct in all live templates? (can't verify — MCP 401 on templates:read)
- All live templates have correct footer (ASA language, unsubscribe, address)?
- V4cZMd's 17 templates — images broken? Brand consistent?

**Fix to unblock HTML audit:**
Add `templates:read` scope to Klaviyo MCP API key at https://www.klaviyo.com/settings/api-keys

**Recommended fix order (live flow issues only):**
1. Ysj7sg E1 preview + E2 subject + E2 preview (3 ASA violations, highest risk)
2. RPQXaa E2 preview (1 ASA violation)
3. V9XmEm E2 subject + preview (mismatch)
4. Y84ruV E2+E3 subject + preview differentiation + smart sending ON
5. V4cZMd E1+E17 add preview text + confirm E17 is not a duplicate

**Falsifiable prediction:** Fixing Ysj7sg E2 subject from "Still available - but selling fast" to "{{ event.ProductName }} is still available" will improve E2 open rate. Baseline to pull: Ysj7sg flow report before fix.
**Confidence:** High on ASA violations (explicit rule breaches). Medium on conversion impact of fixes.
**Action taken:** Fixes not yet applied — user to implement or instruct Claude to action.

## 2026-05-07 — "Since 1984" fabricated founding-year claim removed + new no-unverified-facts rule

- **Context**: User flagged the trust-block line "Trusted by thousands of Kiwis since 1984. 30+ stores nationwide." in a template. Investigation showed "since 1984" was never verified against any primary source — it originated in `memory/no-coupon-strategy.md` (written in a prior session) and propagated through 16 LIVE Klaviyo templates plus 12 local draft files, the activation guide, the welcome flow build spec, and a deploy script.
- **User decisions** (this session):
  - **Founding-year claim**: REMOVE ENTIRELY from every template and memory/guide file. Do not replace with a different year.
  - **"30+ stores nationwide"**: APPROVED — keep as-is.
  - **"Trusted by thousands of Kiwis"**: APPROVED — keep as-is.
- **Action taken**:
  1. Stripped "since 1984" + the fabricated "Bargain Chemist has been serving New Zealanders since 1984 — that's over 40 years..." paragraph from all 16 affected live templates (HTML written to `.claude/bargain-chemist/templates/fixes/<id>.html` ready to apply).
  2. Cleaned 12 local files (cart-abandon-email-1/2/3, welcome-email-1/2/3, flu-recovery-e2, replenishment-master, ACTIVATION-GUIDE.md, welcome-flow-build-spec.md, klaviyo-create-welcome-flow.ps1, no-coupon-strategy.md).
  3. Live Klaviyo PATCH still pending — to be applied via UI Source paste or working API path.
  4. Added permanent **NO UNVERIFIED FACTS RULE** to `.claude/bargain-chemist/CLAUDE.md` — prohibits inserting any factual claim (founding year, store count, customer count, awards, statistics, partnerships, etc.) into copy or memory without explicit user verification + approval.
- **User-approved factual claims register** (only items in this list may be used in copy):
  - Free shipping threshold: **$79 NZD**
  - **Price Beat 10% Guarantee**
  - **30+ stores nationwide**
  - **Trusted by thousands of Kiwis** (generic, no number)
  - Standard NZ pharmacy regulatory phrasing: *"Always read the label and use as directed. If symptoms persist, see your healthcare professional."*
  - Trading name: **Bargain Chemist** / domain `bargainchemist.co.nz`
- **Anything else requires explicit user approval before use.**
- **Prediction**: removing the year claim has no measurable impact on conversion (trust line still present); this is a compliance + accuracy fix, not a performance lever.
- **Confidence**: High that the rule prevents recurrence. The 1984 error is now traceable to a single root cause (unverified copy in `no-coupon-strategy.md`) — fixed.
- **Learning**: Any factual specific in user-facing copy must trace to a user-approved source. Memory files written in prior sessions are NOT a source of truth for facts unless those facts have an explicit "user approved" line in this decisions log.

## 2026-05-07 — DEPLOYED: 1984 + ASA fear-phrase fixes to 13 live flow emails

- **Context**: Following the 1984 fabrication discovery, applied surgical HTML fixes to every live flow email containing the bad copy. Klaviyo's legacy `PATCH /api/templates/{id}/` returns 404 for flow-cloned templates, so used the working `PATCH /api/flow-actions/{id}/` (revision 2025-10-15) re-assignment workflow.
- **Workflow** (now codified as `scripts/klaviyo_deploy_compliance_fixes.py`):
  1. POST /api/templates with fixed HTML → owned global template (named `BC OWNED - <oldId> - 1984 fix YYYY-MM-DD`)
  2. PATCH /api/flow-actions/{action_id} swapping `definition.data.message.template_id` to the owned global ID
  3. Klaviyo internally clones the owned template into a fresh cloned ID, which becomes the live template for the flow message
- **13 actions deployed (flow → action → old-clone → new-clone)**:
  - YdejKf 105917207  UpdhCT → VZASFD  (Welcome E1)
  - YdejKf 105917209  UVB5U8 → WtmqBu  (Welcome E2)
  - YdejKf 105917211  XgqKFQ → UvF2qd  (Welcome E3)
  - RPQXaa 98627502   TgFsGf → USNhYE  (Cart E1)
  - RPQXaa 98628345   QRewz9 → UCUwWu  (Cart E2)
  - Ua5LdS 105926049  VjuB7J → Wg5TLb  (Replenishment E1 Vitamins)
  - Ua5LdS 105926052  WuTrZA → UdLfdw  (Replenishment E2 Skincare)
  - Ua5LdS 105926055  U5svSu → YbKhNV  (Replenishment E3 Hair Care)
  - Ua5LdS 105926058  RDZzKn → RixM24  (Replenishment E4 Oral Care)
  - Ua5LdS 105926061  X3hegP → UbKf4Z  (Replenishment E5 Baby & Family)
  - Ua5LdS 105926062  SPqqDe → XBkvpb  (Replenishment E6 Fallback)
  - V9XmEm 105627868  YtcgUa → XmsJkZ  (Flu E2)
  - Ysj7sg 105627854  W2Sbja → XccdEd  (Back in Stock E1)
- **Verified post-deploy** (GET /api/templates/{newCloneId} → check `data.attributes.html`):
  - All 13 confirmed: `1984=no, fear-hits=0` (live HTML clean).
  - Old cloned IDs are now orphaned but still exist in templates list.
- **Note on subscribers mid-flow**: Klaviyo holds an inflight subscriber on the previous clone reference, so people already in the flow continue with the previous (un-fixed) HTML; new entrants get the fixed clone. For the 5-day-old flows (V9XmEm, Ysj7sg) the inflight cohort is small. For YdejKf/RPQXaa/Ua5LdS (1-2 days old), even smaller.
- **Prediction**: zero measurable impact on engagement metrics (open/click/CTR). This was a compliance + accuracy fix, not a creative test.
- **Confidence**: High on the deployment itself. Medium on the inflight-cohort behaviour assumption (Klaviyo docs confirm clone reference is captured at flow-entry time, but worth re-checking next session via campaign report).
- **Action taken**: Deployed via Python script. Snapshots of every POST/GET/PATCH/verify response saved to `.claude/bargain-chemist/snapshots/2026-05-07/deploy/`.
- **Rollback path**: each old cloned ID still exists. To revert any one message: `PATCH /api/flow-actions/{action_id}` setting `template_id` back to the original cloned ID listed above.
