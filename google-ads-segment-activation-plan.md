# Bargain Chemist — Google Ads × Klaviyo Segment Activation Plan

**Created:** 2026-05-14
**Status:** Plan ready — pending user approval to execute
**Next chat reference:** Read `/home/user/pantrypilot/bargain-chemist-analysis.md` first for context

---

## 1. Verified Mechanism — Customer Match is reachable

Confirmed via `mcp__c4786f6a-...__list_enabled_zapier_actions` for "Google Ads":
- ✅ `create_customer_list` (write action)
- ✅ `add_email_to_customer_list_v3` (write action)
- ✅ `add_to_customer_list_v3` (write action)
- ✅ `find_customer_list` (read)
- ✅ `remove_from_customer_list_v2` (write)
- ✅ `_zap_raw_request` (raw Google Ads API)

**Path forward**: Klaviyo segment members → Zapier Customer Match endpoints → Google Ads audience.

**Account:** OMD-managed MCC `5653976978` — should accept Customer Match (account age + spend > threshold).
**Risk flagged earlier:** account may be flagged for healthcare/pharmacy policy. Still NOT verified via actual CM list creation. **First action when CM is activated**: create one test list to confirm acceptance.

---

## 2. 14 BC Klaviyo Segments — Final Verified Counts

| Klaviyo ID | Segment | Count | Customer Match ready (≥1k matched)? |
|---|---|---|---|
| `RizxBG` | BC — Retail Purchasers L90D | **9,441** | ✅ |
| `VrP6TT` | BC — Retail Cart Abandoners 30d | **620** | ❌ below floor |
| `Ti4FKX` | BC — Retail Cart Abandoners 60d | **1,230** | ✅ just above |
| `RLk5xx` | BC — Retail VIPs (3+ retail orders 365d) | **2,868** | ✅ |
| `RTzA5N` | BC — Browse Abandoners 30d (all products) | **1,236** | ✅ just above |
| `VQ8Sz4` | BC — New Retail Customers L30D (first-time) | **1,538** | ✅ |
| `UvtwYq` | BC — Recent Retail Purchasers L7D | **~850** (estimated) | ❌ exclusion-only use |
| `RnnhTh` | BC — Lapsed Retail Customers 90-180D | **7,333** | ✅ |
| `XFc26k` | BC — Lapsed Retail 180-365D (win-back) | **13,563** | ✅ huge |
| `VvBRbu` | BC — All Retail Customers (last 1095d) | **59,314** | ✅ |
| `YgrizT` | BC — Pharmacy-Only Buyers (no retail) | **4,177** | ✅ exclusion-only |
| `X2pdkD` | BC — GLP-1 Customers (Wegovy + Mounjaro) | **24** | ❌ Klaviyo-only (prescription) |
| `YdzNmz` | BC — Unengaged Subscribed 180D (sunset) | **34,249** | ✅ but use for sunset not CM |
| `WkwEvG` | BC — High AOV Retail ($100+ order) | **0** ⚠️ | needs rebuild w/ $50+ threshold |

---

## 3. Current Google Ads Campaign Performance (May 1–12, 2026)

| Campaign | Sessions | Tx | Revenue (NZD) | CR | AOV | Health |
|---|---|---|---|---|---|---|
| Performance Max ($3+ ROAS) | 44,046 | 898 | $51,103 | 2.04% | $56.91 | 🟢 Workhorse, stable |
| Performance Max — tROAS | 14,866 | 346 | $24,564 | 2.33% | $71.00 | 🔴 Scaled 5× but efficiency dropped 40% |
| NZ — SE — Brand | 10,369 | 346 | $25,978 | 3.34% | $75.08 | 🟡 Healthy but had blackout Apr 28-30 |
| Performance Max — tCPA | 4,700 | 57 | $2,687 | 1.21% | $47.14 | 🔴 Weakest CR + lowest AOV |
| ~17 supplier Shopping campaigns | ~50-300 each | mostly 0 | small | 🔴 Most should be consolidated |

---

## 4. Campaign × Segment Mapping (the answer to "how to use these")

### A. Performance Max ($3+ ROAS) — the workhorse
**Goal:** maintain & grow at current efficiency
- **Audience Signals (positive)**: `RLk5xx` Retail VIPs, `RizxBG` Retail Purchasers L90D
- **Exclusions (negative)**: `UvtwYq` Recent L7D (don't re-acquire), `YgrizT` Pharmacy-Only (irrelevant retail audience)
- **Why**: tells Smart Bidding to find more people like your best buyers, stops wasting impressions on recent purchasers and pharmacy-only customers

### B. Performance Max — tROAS — the recovery campaign
**Goal:** recover the 40% efficiency drop from over-scaling
- **Audience Signals**: `RLk5xx` Retail VIPs, `RizxBG` Retail Purchasers L90D, `VQ8Sz4` New Retail Customers
- **Exclusions**: `UvtwYq` Recent L7D, `YgrizT` Pharmacy-Only
- **Why**: this campaign currently buys low-quality inventory; audience signals = first-party data telling Google "these are the good customers"

### C. Performance Max — tCPA — needs structural fix
**Goal:** improve CR from 1.21% and AOV from $47
- **Audience Signals**: `VQ8Sz4` New Customers L30D (find similar first-timers)
- **Exclusions**: `RizxBG` Retail Purchasers L90D (focus on acquisition only), `YgrizT` Pharmacy-Only
- **Why**: tCPA is going after cheap conversions; the new-customer signal teaches it to find higher-quality first-time buyers

### D. NZ — SE — Brand — already healthy
**Goal:** maintain brand search efficiency
- **Audience Signal**: `VvBRbu` All Retail Customers (observation/bid+)
- **Exclusions**: `UvtwYq` Recent L7D (already-bought brand searchers)
- **Why**: brand search converts well; minimal optimisation needed

---

## 5. NEW campaigns to launch using these segments

### 5.1 🟢 PRIORITY: Win-Back Search/Display Campaign
- **Target audience**: `XFc26k` Lapsed Retail 180-365D (**13,563 customers**)
- **Campaign type**: Standard Search with audience targeting, OR Display Retargeting
- **Creative angle**: "We miss you" + 15-20% off welcome-back code
- **Budget**: $50-100/day to test
- **Why huge**: 13,563 customers worth ~$56 AOV. At a conservative 2% reactivation rate × $56 = **$15,176 incremental revenue**
- **Customer Match required**: Yes (Klaviyo Sync OR CSV upload)

### 5.2 🟢 Display Retargeting — Cart Abandoners
- **Target**: `Ti4FKX` Cart Abandoners 60d (1,230)
- **Campaign type**: Display + Discovery
- **Creative**: dynamic product remarketing — show the product they abandoned
- **Budget**: $30-50/day
- **Why**: 1,230 high-intent customers right now. Industry standard 5-10% recovery rate

### 5.3 🟢 Display Retargeting — Browse Abandoners
- **Target**: `RTzA5N` Browse Abandoners 30d (1,236)
- **Campaign type**: Display + Discovery (lower intent than cart)
- **Creative**: category-level reminder, no specific product
- **Budget**: $20-40/day
- **Why**: viewed PDPs but didn't add to cart — needs different message than cart abandoners

### 5.4 🟡 New Customer Cross-sell — Search
- **Target**: `VQ8Sz4` New Customers L30D (1,538)
- **Campaign type**: Search with bid modifier +50% for this audience
- **Goal**: drive 2nd purchase within first 60 days
- **Why**: first-purchase-to-second-purchase conversion is critical for LTV

### 5.5 🟢 Pharmacy-Only Buyer Exclusion (cross-campaign)
- **Action**: Add `YgrizT` Pharmacy-Only Buyers as exclusion to ALL retail PMax campaigns
- **Why**: 4,177 customers who've only bought pharmacy items. Showing them retail ads = wasted impressions. Free efficiency lift.

---

## 6. Klaviyo Email/Flow Activation (parallel to Google Ads)

| Segment | Email/Flow Use |
|---|---|
| `XFc26k` Lapsed 180-365D Win-back | Connect to existing `[Z] Win-back - Lapsed Customers` flow (currently no proper segment feeding it) |
| `X2pdkD` GLP-1 Customers | Connect to `[Z] Replenishment - Category Based` flow OR build dedicated GLP-1 refill reminder flow |
| `YdzNmz` Unengaged 180D Sunset | Sunset email series → final attempt before suppression |
| `VQ8Sz4` New Customers L30D | Welcome series 2.0 — post-purchase cross-sell |
| `VrP6TT` Cart Abandoners 30d | Verify existing `[Z] Abandoned Checkout v3` flow uses this segment (or its event trigger covers it) |

---

## 7. Expected Impact Summary (conservative, data-grounded)

| Initiative | Expected impact | Confidence |
|---|---|---|
| Exclude Recent L7D from acquisition | 5-10% acquisition spend savings | Medium — industry standard |
| Audience signals on PMax tROAS | 10-15% efficiency recovery (currently -40%) | Medium — Klaviyo data → PMax is well-documented |
| Win-back campaign on 13,563 lapsed | ~$15k incremental at 2% reactivation × $56 AOV | Medium — depends on offer strength |
| Cart Abandoners 60d Display retargeting | ~$3-5k/month at 5% recovery × $56 AOV × 1,230 audience | Medium |
| Pharmacy-Only exclusion | Stops impression waste on irrelevant audience | High — direct waste removal |
| GLP-1 Klaviyo replenishment flow | Retain $46k+ annual GLP-1 revenue | High — clear product cadence |
| Unengaged 180D sunset | Protect sender reputation, improve deliverability | High — best practice |

---

## 8. Execution Order (4 phases)

### Phase 1 — Verify Customer Match works (24h, BLOCKING)
1. Create test CM list via Zapier `create_customer_list` with a tiny seed (5 emails)
2. If accepted → proceed with full CM strategy
3. If rejected (healthcare flag) → pivot to CSV upload via Google Ads UI OR pause CM-dependent initiatives

### Phase 2 — Add exclusions to existing campaigns (24-48h)
1. Sync `UvtwYq` Recent L7D as CM list → add as exclusion to all PMax campaigns
2. Sync `YgrizT` Pharmacy-Only Buyers as CM list → add as exclusion to retail PMax
3. **Zero downside**: removing waste, no new spend

### Phase 3 — Add audience signals to existing PMax (1 week)
1. Sync `RLk5xx` Retail VIPs, `RizxBG` Purchasers L90D, `VQ8Sz4` New Customers as CM lists
2. Attach as audience signals to PMax campaigns per Section 4 mapping
3. Wait 2 weeks for Smart Bidding to learn

### Phase 4 — Launch new campaigns (2-4 weeks)
1. Win-back Search/Display campaign (highest ROI)
2. Cart Abandoners 60d Display
3. Browse Abandoners 30d Display
4. New Customer Cross-sell Search

---

## 9. KNOWN RISKS / OPEN ITEMS

| Item | Risk | Mitigation |
|---|---|---|
| Customer Match account-level eligibility | Pharmacy/healthcare flag could block CM | Phase 1 test confirms or denies |
| Klaviyo Audience Sync UI failure (user reported) | May not be a viable mechanism | Use Zapier CM endpoints as fallback |
| `WkwEvG` High AOV segment = 0 | Filter may be broken OR $100 too high | Rebuild with $50 threshold or test filter |
| GLP-1 segment 24 customers | Below CM minimum (irrelevant for ads anyway) | Use Klaviyo flows only |
| `VrP6TT` Cart Aban 30d (620) below CM floor | Can't standalone-target in Search | Use 60d version (`Ti4FKX`) for ads; 30d for Klaviyo flow |
| OMD agency manages account | Need their approval/coordination to attach audiences | Coordinate via shared Slack/email |
| No ad spend data verified | All ROI estimates are conservative ranges, not precise | Get Google Ads spend data via Google Ads API |

---

## 10. Continuation Plan — How to Resume in Next Chat

**At start of next session, the AI should:**

1. **Read context first**:
   - `/home/user/pantrypilot/bargain-chemist-analysis.md` — full account/tech/segment context
   - `/home/user/pantrypilot/google-ads-segment-activation-plan.md` — THIS FILE

2. **Required from user at start of new chat:**
   - Re-shared Klaviyo Private API key (the old one in transcript should have been rotated)
   - Confirmation of which phase to start with (typically Phase 1: test CM list creation)
   - Decision on rebuild of `WkwEvG` High AOV segment ($50 threshold? $75?)

3. **Tools the next chat needs:**
   - Klaviyo MCP (already configured via Zapier or direct)
   - Shopify MCP (for cross-reference)
   - Google Ads via Zapier (`create_customer_list`, `add_email_to_customer_list_v3`)
   - Code by Zapier (for HTTP calls when MCPs lack a feature)

4. **First action in next chat (suggested):**
   ```
   Phase 1: Verify Customer Match by creating a test list with 5 emails from BC — Retail VIPs.
   If 201 OK → proceed to Phase 2 (sync exclusion lists).
   If policy-blocked → pivot to manual CSV upload via Google Ads UI.
   ```

5. **Reminder**: The Zapier output wrapper aggressively corrupts numeric output. Use word-encoded numbers (`['zero','one','two',...].split('').map(...).join('-')`) when reading counts. Or read directly via the Klaviyo MCP.

6. **Memory file conventions:**
   - Update `bargain-chemist-analysis.md` whenever a segment is created/deleted/renamed
   - Update THIS FILE whenever a phase advances
   - Commit + push to `claude/analyze-shopify-sales-may-BuKXp` branch after each meaningful change

---

## 11. Quick-Reference Decision Matrix (for fast resume)

**Q: Which segment should I use as Audience Signal for [campaign]?**
- Acquisition PMax → `RLk5xx` VIPs + `RizxBG` Purchasers L90D
- PMax tCPA → `VQ8Sz4` New Customers
- Win-back → `XFc26k` Lapsed 180-365D
- Brand search → `VvBRbu` All Retail (observation only)

**Q: Which segment should I EXCLUDE from [campaign]?**
- All acquisition → `UvtwYq` Recent L7D + `YgrizT` Pharmacy-Only
- Win-back → `RizxBG` Purchasers L90D (don't target recent buyers in win-back)

**Q: Which campaigns to NEW build?**
1. Lapsed Retail Win-back Search ($50-100/day) — highest ROI
2. Cart Abandoners 60d Display ($30-50/day)
3. Browse Abandoners 30d Display ($20-40/day)
4. New Customer Cross-sell Search (bid modifier on existing)

---

⚠️ **API KEY EXPOSED IN TRANSCRIPT** — Rotate `pk_XCgiqg_867245db8f4a9648d27f71a29c2e78f6f8` before next chat.

⚠️ **OMD agency coordination** — they own the Google Ads account; changes need their approval/access.

⚠️ **Polyfill.io still in theme** — separate but critical 24h security action.
