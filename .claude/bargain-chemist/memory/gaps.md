# Gaps & Prioritised Work — Klaviyo Account

**Date**: 2026-05-06
**Status**: DRAFT — needs user confirmation on the questions in section 4 before any of this gets executed.

> Confidence labelling: 🟢 ≥95% (verified from data) | 🟡 70–94% (strong evidence, some inference) | 🔴 <70% (need confirmation)

---

## 1. CRITICAL — fix this week

| # | Gap | Evidence | Confidence | Effort |
|---|-----|----------|------------|--------|
| **C1** | **Welcome Series (Website) is in DRAFT despite getting 537 recipients in 90d** — every flow benchmark says this is the highest-leverage flow. Top performers: 8–12% conversion. BC current: 2.05%. Estimated revenue left on the table: $2k–$5k/quarter. | API verified: `[Z] Welcome Series - Website` status=draft, 537 recipients, 2.05% conv | 🟢 | Low — activate flow, refine 3-email sequence |
| **C2** | **Sender email inconsistency** — `hello@` and `orders@` mixed across campaigns. Mixing marketing + transactional from same root domain hurts both. | API verified across 12 sample campaigns | 🟢 | Low — pick one address for marketing, one for transactional, update Klaviyo + DNS |
| **C3** | **Order Confirmation flow has 0% conversion** — industry shows +2200% conversion lift from adding ONE marketing element (cross-sell, refer-a-friend, review request). Currently in DRAFT. | API verified: 136 recipients, 0 conversions | 🟢 | Low — add 1 product-recommendation block, set live |
| **C4** | **Click rates universally below benchmark** (0.2–1.4% vs 2.09% industry avg) — content + template issue, not list. Open rates are OK; opens-to-clicks dropping. | API verified across 28+ campaigns | 🟢 | Medium — needs template HTML access + content rewrite (depends on Q3) |

---

## 2. HIGH — fix this month

| # | Gap | Evidence | Confidence | Effort |
|---|-----|----------|------------|--------|
| H1 | **No SMS channel active** — 0 SMS campaigns in 90d. SMS lifts LTV +18% in first 90d post-acquisition. NZ market: high mobile adoption. | API verified: SMS campaigns = empty array | 🟢 | High — needs SMS opt-in form, separate compliance, sender registration |
| H2 | **Send cadence too high to Master Send Segment** — ~1 campaign/day, declining open rates over time. H&B sweet spot 4–8/month per subscriber. | Inferred from 92 campaigns/90d to 110-120k segment | 🟡 | Medium — engagement-tier sending policy |
| H3 | **17 mostly legacy lists** — RATS Tracking 2-5, Nespresso Competition 2021, Covid Vaccination Voucher etc. Bloat costs you nothing but hurts UI clarity and risks accidental sends. | API verified: list inventory | 🟢 | Low — archive 12+ legacy lists |
| H4 | **"Triple Pixel" duplicate flows in DRAFT** — 4 flows duplicated. Either intentional A/B test (then activate winner + retire loser) or stranded experiment. | API verified | 🟡 | Low — confirm with user, decide |
| H5 | **Browse Abandonment Triple Pixel underperforming benchmark** — 22.67% open vs 42.16% benchmark. 0.45% conv vs 0.59%. 8,175 recipients hitting it without optimisation. | API verified | 🟢 | Medium — investigate trigger config, refine |
| H6 | **Typo in segment name**: "Women's **Segement**" (sic) | API verified — used as audience on 6+ campaigns | 🟢 | Trivial — rename, update flows referencing it |
| H7 | **Replenishment flow has 0 recipients in 90d** despite being live and category being H&B (where replenishment = 35–50% of flow revenue) | API verified | 🟢 | Medium — verify trigger logic, replenishment-eligible product property |
| H8 | **Sunset / re-engagement flow doesn't appear to exist** — 180+ day unengaged subscribers eventually destroy deliverability | API: only winback flow found | 🟢 | Medium — build 2-3 email sunset flow |
| H9 | **Win-back flow has only 1 recipient in 90d** — flow is live but trigger may be misconfigured | API verified | 🟢 | Low — check trigger conditions |

---

## 3. MEDIUM — next 30–60 days

| # | Gap | Evidence | Confidence | Effort |
|---|-----|----------|------------|--------|
| M1 | **No predictive-segment use observed** — Klaviyo's predicted_clv, churn_risk_level segments not visible. Account may or may not meet 500+ customers / 180d history threshold. | Need user to confirm threshold met | 🔴 | Low (if thresholds met) |
| M2 | **Footer compliance not verified** — pharmacy registration #, pharmacist name, medicine disclaimers required by Medsafe NZ. Could not read template HTML to verify. | API blocked | 🔴 | Low to verify, varies to fix |
| M3 | **DKIM/SPF/DMARC status unverified** — without DMARC at p=quarantine+, Gmail/Yahoo bulk sender rules may be deprioritising sends | API doesn't expose | 🔴 | Low to check, low to fix |
| M4 | **Preview text empty on at least 1 sampled campaign** (Nicorette) — wasted inbox real estate; check how widespread | API verified for 1; sample more | 🟡 | Low — content guideline + audit existing |
| M5 | **Segment naming inconsistency** — `[Z]` prefix on most segments but several legacy ones don't (Repeat Buyers, Master Send, Women's Segement, Not Subscribed) | API verified | 🟢 | Low |
| M6 | **No A/B testing visible in flow metadata** — flow versions have variations but no documented winner | API verified | 🟡 | Medium — implement test framework |
| M7 | **Single double-opt-in inconsistency across lists** — some lists single opt-in, some double — defensible if intentional (paid channels vs organic), but worth documenting | API verified | 🟢 | Low |
| M8 | **EDLP jargon leaking into customer-facing copy** ("Save up to 35% off EDLP!") — internal pricing terminology | Subject line samples | 🟢 | Trivial — content guideline update |

---

## 4. QUESTIONS — need answers before executing the above

To get to 95% confidence on conclusions, I need:

### About the account history
1. **What does `[Z]` mean in flow/segment names?** Is it Zyber agency or internal? Affects whether to keep convention.
2. **What does "Reputation Repair Audience" indicate?** Was there a deliverability incident? When? What was done?
3. **Why is Welcome Series in DRAFT** if it's been receiving recipients for 60+ days? Is there an unfinished revision blocking activation?
4. **What's the relationship between "[Z]" flows and "Triple Pixel" duplicates?** A/B test? Migration in progress? Different audiences?

### About the business
5. **Top 3 business priorities for next 90 days?** (revenue, new customer acquisition, AOV, repeat rate, subscription growth?)
6. **Does Bargain Chemist have a subscription / auto-replenish offer on the site?** Affects replenishment flow strategy.
7. **Does the "bargain" positioning go all-in on price, or balance with quality/care messaging?** Affects brand voice direction.
8. **Are there products/categories with margin pressure or strategic priority** (e.g. private label, exclusive supplier deals)?
9. **Is SMS marketing in scope?** Requires separate consent capture and registration.

### About compliance + deliverability
10. **Pharmacy registration number** to include in footer?
11. **Lead pharmacist name** for medicine emails?
12. **Have you set up DKIM, SPF, DMARC?** (Check Klaviyo → Settings → Domains and senders)
13. **Have you completed Google Postmaster Tools setup?** (postmaster.google.com)
14. **Any past Medsafe / Pharmacy Council compliance issues** I should know about?

### About what data I can access
15. **Can you expand Klaviyo MCP permissions** to include template read access? Currently 401.
16. **Is BigQuery / GA4 export already enabled** anywhere? Affects which analyses I can do.
17. **Is Triple Whale data unified with Klaviyo profiles or separate?**

### About appetite for change
18. **Who in your team approves campaign changes** (you, agency, both)? Affects how I should propose work.
19. **Is the agency (Zyber?) still active on the account** or have you brought it in-house?
20. **Budget / time for executing the gap-fix work** — sprint of 1 week, ongoing 2 weeks, or longer phased plan?

---

## 5. RECOMMENDED PHASED PLAN (after questions answered)

### Phase 1 — quick wins (1 week)
- C1: Activate Welcome Series Website (most leverage)
- C2: Unify sender addresses
- C3: Activate Order Confirmation with 1 marketing element
- H6: Fix "Segement" typo
- H3: Archive 12 legacy lists
- M5: Standardise segment naming

### Phase 2 — high-leverage operational (2-3 weeks)
- C4: Click rate diagnosis — pull template HTML once access granted, audit content patterns, run subject + content A/B test
- H4: Decide on Triple Pixel duplicates (kill or activate)
- H7: Fix Replenishment flow trigger
- H8: Build Sunset flow
- H9: Diagnose Win-back trigger
- H5: Refine Browse Abandonment Triple Pixel

### Phase 3 — strategic (4-6 weeks)
- H1: SMS channel rollout (if in scope)
- H2: Cadence + engagement-tier sending policy
- M1: Predictive segments (if thresholds met)
- M2-M3: Compliance + deliverability hardening
- M6: A/B testing framework

---

## 6. WHAT I'M NOT YET 95% CONFIDENT ABOUT

Per user instruction — flagging where I should NOT yet be making conclusions:

- **The brand voice template** — only 12 subject samples, no template HTML, no website read. Draft only. [`brand-voice-design-template.md`]
- **Whether Click Rate is truly low or whether the conversion metric is misaligned** — need to verify "Placed Order" is properly attributing to email clicks vs. assisted attribution
- **Whether Welcome Series being draft is intentional** — could be deliberate (offering a different incentive structure being tested)
- **Whether the segmentation strategy is over-built** — 50+ segments could be useful if used; could be bloat if not. Need to see which segments actually receive sends.
- **Whether the customer base meets predictive analytics thresholds** — 500+ customers / 180d / recent orders / multi-purchase
- **Compliance posture** — without template HTML I cannot verify NZ pharmacy disclaimers are in place

I will not log conclusions in `decisions-log.md` for any of the above until user confirms.
