# Flows Deep-Dive — Bargain Chemist Klaviyo

**Date**: 2026-05-06
**Constraint**: Klaviyo MCP currently does NOT expose flow message HTML, message-level conditions, profile filters, conditional splits, delays, or template content. `klaviyo_get_email_template` returns 401. So this deep-dive is built from API metadata + message-level performance + flow_report data.

> What I CAN see: flow ID, name, status, trigger type, created/updated dates, message-level (per email step) performance, flow message names.
> 
> What I CANNOT see (without user help): full flow structure (delays, splits, filters), email subject lines, email body HTML/copy, sender configuration per message, exit criteria, A/B variants within messages.

---

## 0. SUMMARY

**15 flows total** (7 live, 7 draft, 1 manual). Most created end-Jan to early-May 2026 — **the account is in active rebuild**.

| ID | Name | Status | Trigger | Created | Updated | 90d recipients | 90d revenue |
|----|------|--------|---------|---------|---------|----------------|-------------|
| RPQXaa | [Z] Added to Cart Abandonment | **live** | Metric | 2026-01-30 | 2026-03-30 | 8,743 | $20,144 |
| Y84ruV | [Z] Abandoned Checkout | **live** | Metric | 2026-01-30 | 2026-05-06 | 9,792 | $17,614 |
| T7pmf6 | [Z] Win-back - Lapsed Customers | **live** | Metric | 2026-05-05 | 2026-05-05 | 0 (new) | $0 |
| TsC8GZ | [Z] Welcome Series - No Coupon | **live** | Added to List | 2026-05-05 | 2026-05-05 | 8 | $0 |
| V4cZMd | [Z] Replenishment - Reorder Reminders | **live** | Metric | 2026-05-05 | 2026-05-05 | 0 (new) | $0 |
| V9XmEm | [Z] Flu Season - Winter Wellness | **live** | Added to List | 2026-05-04 | 2026-05-04 | 22 | $0 |
| Ysj7sg | [Z] Back in Stock | **live** | Metric | 2026-05-04 | 2026-05-04 | 0 (new) | $0 |
| RDJQYM | [Z] Post-Purchase Series | **manual** ⚠️ | Metric | 2026-05-04 | 2026-05-04 | 0 | $0 |
| SehWRt | [Z] Welcome Series - Website | **draft** ⚠️ | Added to List | 2026-03-03 | 2026-05-04 | 537 | $902 |
| RtiVC5 | [Z] Browse Abandonment | **draft** | Metric | 2026-01-30 | 2026-03-30 | 1,376 | $676 |
| RSnNak | [Z] Browse Abandonment - Triple Pixel | **draft** ⚠️ | Metric | 2026-03-30 | 2026-03-30 | 8,175 | $2,938 |
| SnakeG | [Z] Added to Cart Abandonment - Triple Pixel | **draft** | Metric | 2026-03-30 | 2026-03-30 | 1,888 | $3,388 |
| VMKAyS | [Z] Abandoned Checkout - Triple Pixel | **draft** | Metric | 2026-03-30 | 2026-03-30 | 845 | $1,220 |
| VJui9n | [Z] Order Confirmation | **draft** ⚠️ | Metric | 2026-05-05 | 2026-05-05 | 136 (via Smp9WN) | $0 |
| XbQiKg | [B] Search Abandonment V4 - Clicked Search Result | **draft** | Metric | 2026-05-01 | 2026-05-06 | 27 | $0 |

⚠️ = critical attention needed

> **Note**: Some flow IDs in performance data (RbbNUc, SNmbHT, Smp9WN, WJFkKx, SLJg3V, WRKYPs) don't appear in the live flows list — these are likely **archived or older versions of flows** that ran in the period. Flow performance still attributes to these legacy IDs.

---

## 1. LIVE FLOWS (deep-dive)

### 1.1 [Z] Added to Cart Abandonment (RPQXaa) ⭐ best performer
- **Status**: live
- **Trigger**: Metric (likely "Added to Cart" event)
- **Created**: 2026-01-30; updated 2026-03-30
- **Message structure observed** (from message-level reports):
  - **Email #1**: "Added to Cart Abandonment Email #1" (TCgQED) — 4,339 recipients, 41.1% open, 5.3% click, 2.87% conv, $2.82 RPR ✓ best message
  - **Email #2**: "Email #2" (TpkzDd) — 4,404 recipients, 41.2% open, 6.9% click, 2.10% conv, $1.81 RPR
- **Aggregate 90d**: 8,743 recipients, 41.18% open, 6.10% click, 2.48% conv, **$2.31 RPR**, $20,144 revenue
- **vs benchmark**: Open rate -9pp (50.5% benchmark), conv -0.85pp (3.33% benchmark), RPR ~$2.31 vs $3.65 H&B benchmark = below
- **Critical observations**:
  - Two-message sequence — benchmark says 3 emails produces 6.5× revenue of 1-email. Adding email 3 should lift revenue ~50%.
  - Email #2 has best click rate (6.9%) but lower conversion than Email #1 — possible incentive structure issue
  - Triple Pixel duplicate exists in DRAFT (SnakeG) — running parallel?
- **What I CANNOT see**: timing between emails, content, incentive structure, exit conditions, sender address
- **Hypotheses to test (with user)**:
  - H1: Adding Email 3 (last-chance + escalated incentive) lifts 90d revenue from $20k to $30k
  - H2: Aligning send time to 1h after trigger (not 2h+) lifts conversion 15-25%

### 1.2 [Z] Abandoned Checkout (Y84ruV)
- **Status**: live
- **Trigger**: Metric (Checkout Started)
- **Created**: 2026-01-30; updated 2026-05-06 (modified TODAY!)
- **Messages observed**:
  - **Email #1** (S7KJkR) — 5,065 recipients, 45.6% open, 5.95% click, 2.76% conv, $2.18 RPR
  - **Email #4** (TcxiTj) — 4,632 recipients, 44.0% open, 6.42% click, 2.06% conv, $1.17 RPR
  - **Email #4** (SE9wC6) — 45 recipients (small sample) — 46.7% open, 6.7% click, 6.67% conv, $24.47 RPR (high outlier — small sample)
  - **Email #4** (VBYf2r) — 50 recipients, 48% open, 10% click, 2% conv, $4.71 RPR
- **Aggregate**: 9,792 recipients, 44.86% open, 6.20% click, 2.44% conv, **$1.81 RPR**, $17,614 revenue
- **Critical observations**:
  - Multiple "Email #4" entries with different IDs — **A/B variants in the flow** but with very different performance
  - Updated TODAY (2026-05-06) — what changed?
  - Conv 2.44% vs 3.5–5% benchmark (checkout abandonment converts 3.5× cart) = significantly below
  - RPR $1.81 vs $4.50–$8.00 benchmark = far below
- **What I CANNOT see**: Email #2, #3 (only #1 and #4 appear in reports — flow may skip 2/3 or they renamed)
- **Hypotheses to test**:
  - H1: The 6,890 "checkout-abandoned-but-not-emailed" people (16,890 events − 9,792 reached) have email capture issue — investigate checkout email capture timing
  - H2: Variants of Email #4 are being run without statistical declaration of winner; pick winner

### 1.3 [Z] Welcome Series - No Coupon (TsC8GZ)
- **Status**: live (since 2026-05-05 — brand new, 1 day old)
- **Trigger**: Added to List
- **Messages observed**: Only 8 recipients in 90d
  - Email 1 "Welcome - Email 1 - Welcome" (UC2XAR) — 8 recipients, 50% open, 12.5% click, 0% conv
- **Critical observations**:
  - Brand new — too small a sample to evaluate
  - "No Coupon" naming suggests this is the no-incentive variant — paired with another welcome flow (the DRAFT Website Welcome) that does have a coupon?
  - Need to understand: is this flow firing because user uses incentive separately, or is it the only welcome flow currently active?

### 1.4 [Z] Win-back - Lapsed Customers (T7pmf6)
- **Status**: live (since 2026-05-05 — brand new)
- **Trigger**: Metric (probably "no order in X days")
- **0 recipients in 90d** — flow may not have triggered yet, or filter is too strict
- **Critical**: investigate trigger configuration — is it set to "no order in X days where X is achievable"?
- **Hypothesis**: trigger is set too far back (e.g. 365d+) or filter excludes most lapsed users

### 1.5 [Z] Replenishment - Reorder Reminders (V4cZMd)
- **Status**: live (since 2026-05-05 — brand new)
- **Trigger**: Metric (probably "Placed Order" + delay)
- **0 recipients in 90d** — too new to have processed orders + delay
- **Critical for revenue**: replenishment in H&B = 35–50% of flow revenue. **Configure correctly = $20k+/quarter potential.**
- **What I'd want to verify**: trigger logic uses replenishment-eligible product property (custom tag or category filter), delay matches product cycle (vitamins ~30d, oral care ~60d, fragrance ~90d)

### 1.6 [Z] Flu Season - Winter Wellness (V9XmEm)
- **Status**: live (since 2026-05-04)
- **Trigger**: Added to List
- **22 recipients in 90d**, 36.4% open, 0% click, **0 conversions**
- **Critical observations**:
  - Seasonal flow — autumn 2026 NZ (heading into winter). Right time of year.
  - 0% click rate is concerning — content may not be resonating OR sample too small to judge
  - Compliance risk: winter wellness category includes pharmacy-only medicines (Codral, Sudafed) — if flow content names these, same compliance issue as Codral campaign
- **Recommend**: review content urgently before more recipients hit it

### 1.7 [Z] Back in Stock (Ysj7sg)
- **Status**: live (since 2026-05-04 — brand new)
- **Trigger**: Metric (likely "Back in Stock subscription" + product back in stock)
- **0 recipients in 90d** — too new + depends on stock events
- **Benchmark for this flow type**: 6–24% conversion (highest of any flow) — high-leverage when running

---

## 2. DRAFT FLOWS (deep-dive — these are receiving recipients)

### 2.1 [Z] Welcome Series - Website (SehWRt) ⚠️ TOP PRIORITY
- **Status**: DRAFT but receiving recipients (537 in 90d!)
- **Trigger**: Added to List
- **Created**: 2026-03-03; updated 2026-05-04
- **Messages observed** (5 of likely 6+):
  - Email 1 (U2HQmW) — 220 recipients, **54.8% open, 15.07% click, 3.65% conv, $3.30 RPR** ← strong performer
  - Email 2 (QYfRCd) — 165 recipients, 44.2% open, 9.7% click, 0.6% conv, $0.50 RPR
  - Email 6 (VJwtx3) — 152 recipients, 42.8% open, 4.6% click, 1.32% conv, $0.64 RPR
- **Aggregate**: 537 recipients, 48.13% open, 10.45% click, 2.05% conv, **$1.68 RPR**, $902 revenue
- **vs benchmark**:
  - Open rate 48% (benchmark 45–50%) ✓
  - Click rate 10.45% (top performers 15%) — close to top
  - Conversion 2.05% — below benchmark of 8–12%. **Big gap.**
  - RPR $1.68 vs $3.34 H&B benchmark = half
- **Critical observations**:
  - Email 1 performs near top quartile open + click — **content is working at the top**
  - **Conversion drops sharply by Email 2** — 3.65% → 0.6% conversion, $3.30 → $0.50 RPR
  - 6+ emails in series — possibly too long (best practice 3–4)
  - **Why is this DRAFT?** — User says "investigate + activate" so I have permission to dig
- **Hypotheses to investigate before activating**:
  - H1: Email 1 is fine; Emails 2–6 need rewrite around confirmed positioning (Kiwi-owned, 10% price beat, $79 free ship)
  - H2: Sequence is too long; consolidate to 3 emails
  - H3: There's an incomplete edit blocking activation — look for an "unsaved" or "missing content" Email 3, 4, 5
- **Estimate of unlocked revenue**: 537 recipients/90d × ($3.34 benchmark RPR − $1.68 actual RPR) = **+$890 / 90d** if we just hit benchmark = ~$3.6k/yr from this flow alone. Higher if email-capture rate from forms is improved.

### 2.2 [Z] Browse Abandonment (RtiVC5)
- **Status**: DRAFT, receiving 1,376 recipients in 90d
- **Trigger**: Metric (Viewed Product / Active on Site)
- **Messages**: Email #1 (V4aGD3) — 1,376 recipients, 44.9% open, 4.89% click, 0.73% conv, **$0.49 RPR**
- **vs benchmark**: open 44.9% (vs 42.16% bench) ✓; conv 0.73% (vs 0.59% bench) slightly above; RPR $0.49 (vs $0.50–$1.50 bench) below
- **Critical**: only 1 email — best practice 1–3. Worth testing if email 2 lifts incremental revenue.

### 2.3 [Z] Browse Abandonment - Triple Pixel (RSnNak) ⚠️
- **Status**: DRAFT, receiving 8,175 recipients in 90d (largest by recipients!)
- **Trigger**: Metric (Triple Whale "Viewed Product - Triple Pixel")
- **Messages**: Email #1 (Vtezbi) — 8,175 recipients, **22.7% open, 1.5% click, 0.45% conv, $0.36 RPR**
- **CRITICAL**: this flow is sending to far more people than the standard browse abandonment (8,175 vs 1,376) but performing WORSE on every metric. Open rate half of benchmark (22.7% vs 42.16%).
- **Hypothesis**: Triple Pixel events fire much more aggressively than standard "Viewed Product" → flow is over-firing to low-intent traffic, hurting open rates → poor reputation impact + low revenue
- **Recommendation**: investigate trigger threshold, OR turn off Triple Pixel version and use only standard browse abandonment

### 2.4 [Z] Added to Cart Abandonment - Triple Pixel (SnakeG)
- **Status**: DRAFT, 1,888 recipients, 28.25% open, 4.01% click, 1.82% conv, $1.81 RPR
- **Same Triple Pixel duplication concern** — running parallel to live RPQXaa
- **Hypothesis**: pick one. Either standard or Triple Pixel — running both = audience overlap + send fatigue

### 2.5 [Z] Abandoned Checkout - Triple Pixel (VMKAyS)
- **Status**: DRAFT, 845 recipients, 31.64% open, 5.21% click, 1.33% conv, $1.48 RPR
- **Same concern** — duplicates live Y84ruV

### 2.6 [Z] Order Confirmation (VJui9n) — flow ID Smp9WN in reports ⚠️
- **Status**: DRAFT
- **Messages**: "[Z] Post-Purchase Email 1" (XJENuf) — 136 recipients, **57.4% open, 0.74% click, 0% conversion**
- **Critical finding**: 0 conversions despite high open rate. Industry says +2200% conversion lift from adding ONE marketing element to order confirmation.
- **What likely current state is**: pure transactional confirmation with no upsell / cross-sell / review request / refer-a-friend
- **Easiest high-impact fix**: add 1 product-recommendation block + activate

### 2.7 [B] Search Abandonment V4 - Clicked Search Result (XbQiKg)
- **Status**: DRAFT
- **27 recipients**, 59.3% open (excellent!), 25.9% click (very high!), 0% conversion
- **Critical**: high engagement but no conversions. Either flow short-circuits before purchase, or sample too small (n=27)
- Note: `[B]` prefix here — only flow not labelled `[Z]`; possibly Boost recommendations engine integration

### 2.8 Legacy / unlinked flow IDs from reports
These flow IDs appear in 90d performance data but NOT in the active flow list — likely archived or older versions:
- **RbbNUc** — Added to Cart Abandonment Triple Pixel (older version) — 317 recipients
- **SNmbHT** — Abandoned Checkout Triple Pixel (older version) — 150 recipients
- **WJFkKx** — Search Abandonment V3 (Zyber Version) — 294 recipients, **0% conversion** despite 44.9% open
- **SLJg3V** — Search Abandonment Zyber (Boost Test) — 131 recipients, 56.5% open, 9.2% click, **4.6% conv, $3.54 RPR** ← this small test was a top performer
- **WRKYPs** — Win-back Lapsed (older version) — 1 recipient

> The "Zyber" labels suggest there WAS an agency at some point — contradicts the user's "internal naming" answer. Worth a follow-up question.

---

## 3. MANUAL FLOWS

### 3.1 [Z] Post-Purchase Series (RDJQYM)
- **Status**: MANUAL — meaning paused / requires manual action
- **Trigger**: Metric
- **Created**: 2026-05-04
- **0 recipients in 90d** — confirmed paused
- **Hypothesis**: this is one of the user's "paused for compliance" flows. Manual status in Klaviyo means the flow won't auto-fire.

---

## 4. STRUCTURAL OBSERVATIONS

### Triple Pixel duplication strategy
The pattern of having `[Z] X` (live) + `[Z] X - Triple Pixel` (draft) for the same flow type appears to be testing alternative triggers (Klaviyo standard event vs Triple Whale event). The Triple Pixel versions consistently underperform — suggests Triple Whale events are noisier / lower intent.

**Recommendation**: pick winners and retire losers. Don't run both indefinitely.

### Naming inconsistency
- 14 of 15 flows use `[Z]` prefix
- 1 uses `[B]` (Search Abandonment V4) — suggests another category/agency/initiative
- "Welcome Series - No Coupon" (live) + "Welcome Series - Website" (draft) — two welcome flows; relationship unclear

### Recent rebuild
- 7 of 15 flows created May 2026 (within last week)
- Suggests active rebuild in progress
- Welcome Series Website draft is 2 months old — predates rebuild — suggests it's been left behind during rebuild

### Coverage gap
- **46,120 cart abandonments** in 90d → only **8,743 reached** by Cart flow = 19% coverage
- **16,890 checkout abandonments** → 9,792 reached = 58% coverage
- **Email capture rate at checkout** is the limiting factor — many anonymous browsers
- Recommendation: add email capture popup + improve checkout email-required setting

---

## 5. WHAT WE STILL CAN'T SEE (need user)

To complete this deep-dive I need either:
1. **Klaviyo MCP scope expansion** — add `templates:read`, `flow-messages:read`, `flow-actions:read` permissions
2. **Manual screenshots / exports** of:
   - Each flow's structure (delays, splits, filters)
   - Each email message's subject + preview + body HTML
   - Each flow's profile filter and exit criteria
   - Each email's sender address (catch the `hello@` vs `orders@` mix at flow level)

Without this, I cannot answer questions like:
- Why is Welcome Series in DRAFT (specific blocker)?
- What's in the Order Confirmation that's converting at 0%?
- Are flow templates compliant (pharmacy registration #, disclaimers, no POM mentions)?
- What's the exact incentive structure in cart/checkout flows?
- Are the Triple Pixel duplicates running on same audiences (overlap)?

---

## 6. CONFIRMED + INFERRED PRIORITY ORDER

| Priority | Action | Rationale |
|----------|--------|-----------|
| 1 | Activate Welcome Series Website (after content review) | 537 recipients/90d already hitting it; biggest leverage |
| 2 | Activate Order Confirmation with marketing element | 136 recipients, 0% conv → +2200% lift potential |
| 3 | Add Email 3 to Cart Abandonment | +50% revenue per benchmark |
| 4 | Diagnose + fix Replenishment trigger | H&B = 35–50% of flow revenue lives here |
| 5 | Sunset flow build (doesn't exist yet) | Deliverability protection |
| 6 | Decide on Triple Pixel duplicates | Stop running parallel = reduce overlap + fatigue |
| 7 | Browse Abandonment Triple Pixel — investigate over-firing | 22% open vs 42% benchmark = trigger problem |
| 8 | Compliance audit on Flu Season Winter Wellness flow content | Seasonal-medicine risk |
| 9 | Win-back trigger diagnosis | 1 recipient in 90d = misconfigured |
| 10 | Search Abandonment V4 → set live or kill | Strong sample data, just stalled |
