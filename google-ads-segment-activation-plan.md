# Google Ads × Klaviyo Segment Activation Plan — Bargain Chemist

> Companion to `bargain-chemist-analysis.md`. Branch: `claude/klaviyo-google-ads-research-PdMUG`.
> Strategic framework reflects standard Customer Match best-practice playbook for ecommerce; numeric inputs are verified from live Klaviyo (2026-05-15). Campaign-side claims marked **(unverified)** must be confirmed in Phase 0 before launch.

---

## 0. Why this matters (the "why" answer in one paragraph)

Google's Smart Bidding (used by Performance Max, tROAS, tCPA) optimises against your conversion data — but it only sees *anonymous click → purchase* signal. Feeding it Customer Match audiences does three distinct things, each with different leverage:

1. **Exclusions remove waste.** People who bought in the last 7 days don't need an acquisition ad shown to them tomorrow. Pharmacy-only customers shouldn't see retail product ads. Excluding 573 + 4,177 = ~4,750 wasted impressions per cycle.
2. **Audience signals teach Smart Bidding.** Telling PMax "find more people like our 2,871 retail VIPs" gives the bidder a high-LTV anchor it cannot infer from a single click. This is the highest-leverage use for any PMax campaign with poor or shallow conversion history.
3. **Win-back/lapsed campaigns become tractable.** 13,563 retail customers haven't bought in 6-12 months. They already know the brand — paid reach to them at NZ$5-8 CPM is dramatically cheaper than acquiring an equivalent net-new customer.

The combined effect on existing campaigns: cleaner targeting (exclusions), smarter bidding (signals), and at least one new high-yield campaign type (win-back) that can't exist without these audiences.

---

## 1. Segment → Customer Match Eligibility

| # | Segment | Profiles | CM-eligible? | Reason |
|---|---|---:|:---:|---|
| 1 | Retail Purchasers L90D `RizxBG` | 9,444 | ✅ | Above 1k floor, marketing-consented |
| 2 | Cart Abandoners 30d `VrP6TT` | 620 | ❌ | Below 1k CM minimum — keep as Klaviyo flow scope only |
| 3 | Cart Abandoners 60d `Ti4FKX` | 1,230 | ✅ | Just above floor — display retargeting candidate |
| 4 | Retail VIPs `RLk5xx` | 2,871 | ✅ | **Best LTV signal** for Smart Bidding |
| 5 | Browse Abandoners 30d `RTzA5N` | 1,237 | ✅ | Display only |
| 6 | New Retail L30D `VQ8Sz4` | 1,539 | ✅ | Cross-sell + acquisition exclusion |
| 7 | Recent Retail L7D `UvtwYq` | 573 | ⚠️ | Below 1k floor BUT acceptable as **exclusion** (CM exclusion has no minimum) |
| 8 | Lapsed 90-180D `RnnhTh` | 7,333 | ✅ | Win-back lower urgency tier |
| 9 | Lapsed 180-365D `XFc26k` | 13,563 | ✅ | **Highest single win-back opportunity** |
| 10 | All Retail (1095d) `VvBRbu` | 59,315 | ✅ | Master observation / bid-modifier audience |
| 11 | Pharmacy-Only `YgrizT` | 4,177 | ✅ | **Exclusion only** — never positive target |
| 12 | GLP-1 Customers `X2pdkD` | 24 | ❌ | Both: prescription medication (Google policy block) AND below floor. Klaviyo-only. |
| 13 | Unengaged Subscribed 180D `YdzNmz` | 34,248 | ✅ | Sunset via paid reach — cheaper than email re-perm |
| 14 | High AOV ($100+) `WkwEvG` | 0 | ⛔ | Filter bug — fix first (see analysis §3) |

**Eligible for activation today: 11 segments.**

---

## 2. Campaign × Segment Mapping

> Campaign names below come from the pasted prior-session context and must be confirmed against live Google Ads in Phase 0. The segment recommendations are correct *given those campaign types* (PMax, Search Brand, etc.) — if names differ, the assignment logic still applies based on campaign type.

### A. Existing campaigns — attach audiences (no new campaigns needed)

#### **PMax (3+ ROAS workhorse)** — *(unverified name)*
- ➕ **Audience Signal:** `RLk5xx` Retail VIPs (2,871) + `RizxBG` Retail Purchasers L90D (9,444)
- ➖ **Exclude:** `UvtwYq` Recent L7D + `YgrizT` Pharmacy-Only
- **Why:** It's already winning — protect it. Signal sharpens lookalike modelling without overriding the bidder's freedom. Exclusions stop wasted impressions on customers who just bought or who don't buy retail products.

#### **PMax tROAS** — *(unverified name; pasted v1 noted "40% efficiency drop")*
- ➕ **Audience Signal:** `RLk5xx` VIPs + `RizxBG` L90D + `VQ8Sz4` New Customers
- ➖ **Exclude:** `UvtwYq` + `YgrizT`
- **Why:** This campaign benefits *most* from audience signals. tROAS bidding is starved when conversion volume drops — VIP + recent-purchaser signal gives it a high-confidence anchor to extrapolate from.

#### **PMax tCPA** — *(unverified name; pasted v1 noted "weakest CR 1.21%")*
- ➕ **Audience Signal:** `VQ8Sz4` New Retail Customers L30D (1,539) — *only*, deliberately
- ➖ **Exclude:** `RizxBG` Retail Purchasers L90D (purges existing customers — this campaign is acquisition-only)
- **Why:** A tCPA target is best paired with first-time-buyer pattern matching. Excluding existing customers stops the campaign mis-attributing organic-repeat purchases to paid acquisition.

#### **NZ – SE – Brand** — *(unverified name)*
- ➕ **Observation Audience (bid +5–10%):** `VvBRbu` All Retail Customers (59,315)
- ➖ **Exclude:** `UvtwYq` Recent L7D
- **Why:** Brand campaigns are already efficient. Don't restrict targeting; use observation mode to bid up known customers (higher CR), exclude very-recent buyers from re-acquisition.

### B. New campaigns to launch (each needs a new Customer Match list)

| Priority | Campaign type | Target audience | Estimated incremental revenue (assumptions in §3) |
|:-:|---|---|---|
| 🟢 P1 | Win-Back Search/Display | `XFc26k` Lapsed 180-365D (13,563) | ~NZ$15.2k (2% reactivation × NZ$56 AOV) |
| 🟢 P2 | Cart Abandoner 60d Display (DPR) | `Ti4FKX` (1,230) | Direct-response retargeting; expect 4-6% return-to-cart |
| 🟢 P3 | Browse Abandoner 30d Display | `RTzA5N` (1,237) | Category-reminder; lower CR than cart but cheaper CPMs |
| 🟡 P4 | Sunset / Re-engagement Display | `YdzNmz` (34,248) | Cheaper than re-permission email; reactivates subset before sunset suppression |
| 🟡 P5 | New Customer Cross-sell Search | bid modifier on `VQ8Sz4` (1,539) | Margin-positive cross-sell to first-timers in their 30-day repeat window |

---

## 3. Estimated Impact — Assumptions Stated

Win-back P1 calculation: 13,563 × 2% reactivation × NZ$56 AOV = NZ$15,191. Sources:
- 13,563: verified live count (`klaviyo_get_segment` `XFc26k`)
- 2% reactivation: industry baseline for paid win-back of <12-month lapsed customers; tighten after 30 days of campaign data
- NZ$56 AOV: per pasted prior-session context (**unverified** in this session — re-derive from `query_metric_aggregates` on Placed Order if precision matters)

The other estimates are deliberately not numericised — they require campaign-level cost data we don't have read access to in this session.

---

## 4. Execution Phases

### Phase 0 — Verify (next session, ~30 min)
- [ ] Confirm campaign names + IDs via Google Ads (GAQL or UI walkthrough)
- [ ] Confirm Customer Match works for this MCC: create one 5-email test list
- [ ] Decide on `WkwEvG` rebuild: inspect a real $100+ retail order to find correct property name
- [ ] Confirm whether OMD agency or owner makes the audience-attach changes

### Phase 1 — Exclusion-only sync (24-48h, lowest risk)
Sync the two exclusion segments to Google Ads CM. Attach to all existing campaigns as exclusions. Zero downside — only stops waste, can't overspend.
- `UvtwYq` Recent L7D → `BC_excl_recent_purchasers_7d`
- `YgrizT` Pharmacy-Only → `BC_excl_pharmacy_only`

### Phase 2 — Audience signals to existing PMax (week 1)
Sync the signal segments. Attach as Audience Signals to PMax campaigns per §2A mapping.
- `RLk5xx` VIPs → `BC_signal_retail_vips`
- `RizxBG` L90D Purchasers → `BC_signal_l90d_purchasers`
- `VQ8Sz4` New Customers → `BC_signal_new_customers_l30d`
- `VvBRbu` All Retail → `BC_obs_all_retail_customers`

### Phase 3 — Launch new campaigns (week 2-4)
Roll P1 → P5 in priority order. Don't launch all at once — give each 7 days of solo data before attribution gets noisy.

### Ongoing — Sync hygiene
Customer Match lists go stale. Daily Zapier flow (or daily Klaviyo Audience Sync if native UI works) to push new joiners and remove dropouts. Without this, lapsed-365D becomes lapsed-400D and stops converting.

---

## 5. Decision Matrix — When to Pick Which Sync Mechanism

| Need | Tool | Why |
|---|---|---|
| Real-time, automated, no maintenance | Klaviyo native Audience Sync | Built-in, no glue code. **Pasted v1 said this failed — re-test in Phase 0.** |
| Reliable fallback if native sync broken | Zapier `add_email_to_customer_list_v3` | Confirmed working this session; needs scheduled trigger (Zapier polling or webhook from Klaviyo) |
| One-shot bulk seed | Klaviyo CSV export → Google Ads UI upload | Fastest to get a list live for testing |
| Fully programmatic | Direct Google Ads API via service account | Future state; out of scope for first 30 days |

---

## 6. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|---|:-:|:-:|---|
| Customer Match rejected for healthcare | Med | High | Phase-0 5-email test — fail fast |
| Native sync still broken | High (per v1) | Med | Zapier path validated; uglier but works |
| GLP-1 segment used in CM by mistake | Low | **Very high** (Google policy violation → account suspension) | Hard rule: `X2pdkD` never leaves Klaviyo |
| Pharmacy-only included as positive target | Low | High (relevance + waste) | Hard rule: `YgrizT` only ever appears in EXCLUSIONS |
| Audience overlap inflates frequency | Med | Low | Exclude downstream segments from upstream campaigns (e.g. exclude L90D from win-back) |
