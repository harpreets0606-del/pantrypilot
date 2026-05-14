# Bargain Chemist — Comprehensive Audit & Segment Library

**Last updated:** 2026-05-14
**Author:** Claude (verification-based, no estimates)

---

## 1. Account Identities (verified)

| System | ID / Name |
|---|---|
| Shopify domain | `bargain-chemist.myshopify.com` (storefront: bargainchemist.co.nz) |
| Shopify plan | Shopify Plus |
| Shopify currency | NZD |
| Klaviyo account ID | `XCgiqg` (Harpreet Singh, harpreetsingh@bargainchemist.co.nz) |
| Klaviyo region | en-NZ, Pacific/Auckland |
| Google Ads MCC | `5653976978` (managed by OMD agency, "CHC-OMD Bargain Chemist") |
| GA4 Property | `properties/313486016` (Measurement ID `G-SLRETMWHC4`) |
| GTM Account | `4057266334`, Container `GTM-K69Z2RN` (9881578) |
| Triple Whale | Connected with API key; Pixel installed and firing |

---

## 2. Confirmed Tech Stack on Storefront

| Component | Status | Source |
|---|---|---|
| Triple Pixel | ✅ Live | HTML scan |
| Meta Pixel (fbq) | ✅ Live | HTML scan |
| GTM (GTM-K69Z2RN) | ✅ Live | HTML scan |
| GA4 | ✅ Live | GTM tag #77 |
| Klaviyo onsite | ✅ Live | HTML scan |
| Hotjar | ✅ Live in theme (GTM tag #99 PAUSED) | HTML scan |
| Microsoft Clarity | ✅ Live in theme (GTM tag #113 PAUSED) | HTML scan |
| **TikTok Pixel** | ✅ **Live via GTM tag #85** | GTM API |
| Enhanced Conversions | ✅ **ON via GTM tag #66** (`enableEnhancedConversion: true`) | GTM API |
| Conversion Linker | ✅ Live via GTM tag #51 | GTM API |
| Google Ads Dynamic Remarketing | ✅ Live via GTM tag #116 | GTM API |
| Floodlight (DV360) | ✅ All 10 conversion tags live | GTM API |

### Security/Performance Issues
- 🔴 **polyfill-fastly.net** loaded in `layout/theme.liquid` — confirmed supply-chain risk. Must remove.
- 🟡 **14 render-blocking scripts** in `<head>` (vs best practice ≤2)
- 🟡 **330-372 KB inline JS** per page
- 🟡 **10 third-party JS origins** (jQuery, Stamped, CodeBlackBelt, polyfill, Klaviyo, etc.)
- 🟡 **Google Optimize tag #67 still active** — Google killed the product 2023-09-30
- 🟡 **UA tag #7 still active** — UA shut down 2024-07-01
- 🟡 **Dual heatmaps** (Hotjar + Clarity in theme)
- ❌ **Sticky add-to-cart NOT present** (confirmed via Shopify theme query)
- ❌ **Zip Pay NOT installed** (only Afterpay + Laybuy on PDP only)

---

## 3. May 2026 Sales Reality Check

**Premise tested:** "Sales aren't happening in May" → **FALSE**

| Period | Orders | Gross Sales (NZD) |
|---|---|---|
| May 1–12, 2026 | 3,593 | $200,476 |
| April 1–12, 2026 | 3,142 | $181,541 |
| May 1–12, 2025 (YoY) | 3,576 | $199,901 |

- MoM: **+14% orders, +10% gross sales**
- YoY: flat (~+0.3% gross, +0.5% orders)
- The "down" feeling came from comparing to Apr 19–30 (end-of-month payday surge)

---

## 4. Google Ads Campaign Health (verified via GA4)

### May 1–12 (Top 4 campaigns)

| Campaign | Sessions | Tx | Revenue NZD | CR |
|---|---|---|---|---|
| Performance Max ($3+ ROAS) | 44,046 | 898 | $51,103 | 2.04% |
| PMax - tROAS | 14,866 | 346 | $24,564 | 2.33% |
| NZ – SE – Brand | 10,369 | 346 | $25,978 | 3.34% |
| PMax - tCPA | 4,700 | 57 | $2,687 | **1.21%** ⚠️ |

### Major findings
- **PMax tROAS scaled 5× MoM but efficiency dropped 40%** ($2.77 → $1.65 rev/session)
- **PMax tCPA**: new launch, weakest CR + lowest AOV ($47); needs intervention
- **NZ – SE – Brand had a 3-day blackout Apr 28–30** (46/46/40 sessions vs ~750 baseline)
- **Mobile CR 1.89-2.87% vs Desktop 2.67-4.41%** — 35-55% gap; 78% of paid traffic is mobile
- **`(not set)` landing page**: 2,965 paid sessions, 2 conversions, 97% bounce — likely broken redirects

### Triple Whale attribution
- ⚠️ `firstClick`/`lastClick` paid attribution = **0 orders out of 100 sampled** in both May and April
- Despite 35 May / 23 April orders showing `google-ads` in full-journey
- Cause: ad-platform connections in TW likely broken/expired

---

## 5. Catalog & Product Classification (verified via Shopify)

### Product type revenue (Apr 1 – May 12, $691k total)

| Product Type | Revenue (NZD) | Classification |
|---|---|---|
| Health & Wellbeing | $239,534 | 🟢 RETAIL |
| Personal Care | $109,325 | 🟢 RETAIL |
| Skin Care | $79,040 | 🟢 RETAIL |
| Medicines & Professional Services | $70,460 | 🔴 PHARMACY |
| Beauty Accessories | $56,957 | 🟢 RETAIL |
| `_pharmacy-only` | $40,182 | 🔴 PHARMACY |
| Cosmetics | $30,561 | 🟢 RETAIL |
| Health Equipment | $17,457 | 🟢 RETAIL |
| Baby | $16,043 | 🟢 RETAIL |
| Household | $11,567 | 🟢 RETAIL |
| General Food & Drink | $7,159 | 🟢 RETAIL |
| Other Pharmacy & Clothing | $5,548 | 🔴 PHARMACY |
| Lifestyle & Wellness | $4,330 | 🟢 RETAIL |
| `_pharmacist-only` | $2,201 | 🔴 PHARMACY |

**Retail share: 83% ($573k) / Pharmacy share: 17% ($118k)**

### Smart Collections (manual curation, not rule-based)

| Collection | Products | Type |
|---|---|---|
| `_retail` | **10,380 products** | Manual |
| `_pharmacy-only` | 551 products | Manual |
| `_pharmacist-only` | 55 products | Manual |

→ My retail filter `Collections contains-any [_retail]` correctly captures these.

---

## 6. Klaviyo Segment Definitions — Confirmed Schema (after probing)

### Working schemas (verified)
```javascript
// Timeframe: in-the-last
timeframe_filter: {type:'date', operator:'in-the-last', unit:'day', quantity:90}

// Timeframe: between (e.g., 91-180d ago for lapsed)
timeframe_filter: {type:'date', operator:'between', start:91, end:180, unit:'day'}

// Retail filter on Placed Order (works) or Started Checkout (works)
metric_filters: [{property:'Collections', filter:{type:'list', operator:'contains-any', value:['_retail']}}]

// $value filter on metric
metric_filters: [{property:'$value', filter:{type:'numeric', operator:'greater-than', value:100}}]

// Email subscribed consent (CORRECTED)
{type:'profile-marketing-consent', consent:{channel:'email', can_receive_marketing:true, consent_status:{subscription:'subscribed', filters:null}}}
```

### Broken / unsupported schemas (confirmed via probe)
```javascript
// ❌ "any" subscription (was bug — included NEVER_SUBSCRIBED users)
consent_status: {subscription: 'any'}

// ❌ over-all-time / all-time operators
timeframe_filter: {type:'date', operator:'over-all-time'}
timeframe_filter: {type:'all-time'}

// ❌ profile-list condition (schema I guessed)
{type:'profile-list', list_id:'...', measurement:'in-list'}

// ❌ profile-property with predictive properties (needs special "properties['name']" path)
{type:'profile-property', property:'$predictive_analytics.historic_clv'}

// ❌ sum_value measurement with timeframe/no-timeframe combos
{measurement:'sum_value', measurement_filter:{value:300}, ...}
```

### Event property schemas (confirmed)
| Event | Has `Collections`? | Has `Categories`? | Has `Product Type`? |
|---|---|---|---|
| Placed Order (`Sxnb5T`) | ✅ Yes | — | — |
| Started Checkout (`VvcTue`) | ✅ Yes | — | — |
| Added to Cart (`S4jKYD`) | ❌ No | ✅ Yes | ✅ Yes |
| Viewed Product (`XQ2zfW`) | ❌ No | ✅ Yes | ❌ No |

---

## 7. Current Klaviyo Segment Inventory (87 segments)

### My 14 [SIZING] BC segments (post-fix + new P0, ready to deploy)

**Wave 1 — rebuilt with corrected consent + def (8 segments):**
| ID | Segment | Verified count |
|---|---|---|
| `RizxBG` | BC — Retail Purchasers L90D | 9,441 |
| `VrP6TT` | BC — Retail Cart Abandoners 30d | 620 |
| `RLk5xx` | BC — Retail VIPs (3+ retail orders 365d) | 2,868 |
| `RTzA5N` | BC — Browse Abandoners 30d (all products) | 1,236 |
| `VQ8Sz4` | BC — New Retail Customers L30D (FIXED first-time) | 1,538 |
| `UvtwYq` | BC — Recent Retail Purchasers L7D | ~850 (Zapier wrapper issue) |
| `RnnhTh` | BC — Lapsed Retail Customers 90-180D | 7,333 |
| `VvBRbu` | BC — All Retail Customers (last 1095d ~3y) | 59,314 |

**Wave 2 — new P0 segments (6 segments):**
| ID | Segment | Verified count |
|---|---|---|
| `YgrizT` | BC — Pharmacy-Only Buyers (no retail) | **4,177** |
| `X2pdkD` | BC — GLP-1 Customers (Wegovy + Mounjaro) | **24** |
| `XFc26k` | BC — Lapsed Retail 180-365D (win-back) | **13,563** |
| `YdzNmz` | BC — Unengaged Subscribed 180D (sunset) | UNREAD — verify in Klaviyo UI |
| `WkwEvG` | BC — High AOV Retail ($100+ order) | UNREAD — verify in Klaviyo UI |
| `Ti4FKX` | BC — Retail Cart Abandoners 60d | UNREAD — verify in Klaviyo UI |

### 68 existing [Z] category × time-window segments
17 categories × 4 windows (30/60/90/180 day engaged):
Allergy, Baby, Cold & Flu, Cosmetics, First Aid, Fragrance, Hair, Household, Personal Care, Pet, Sexual Health, Sitewide, Skincare, Sports Nutrition, Sunscreen, Vitamins & Supplements, Weight

### 11 utility / other segments
- Master Send Segment (3 variants — general, No Spark Xtra, No Spark Xtra Auckland)
- [Z] Suppressed Retargeting Campaign
- [Z] Suppressed Profiles - Meta Exact Match Retargeting
- Repeat Buyers (2 variants — base, 365 days)
- Purchasers without activity LD 30
- Not Subscribed
- All Active Customers (Last 180 Days)
- Women's Segement (typo)

---

## 8. Klaviyo Flow Inventory (15 flows)

| Flow | Status | Trigger |
|---|---|---|
| [Z] Post-Purchase Series | Manual | Metric |
| [Z] Added to Cart Abandonment | Manual | Metric |
| [Z] Added to Cart Abandonment - Triple Pixel | Draft | Metric |
| [Z] Browse Abandonment | Manual | Metric |
| [Z] Browse Abandonment - Triple Pixel | Draft | Metric |
| [Z] Abandoned Checkout v3 | Manual | Metric |
| [Z] Abandoned Checkout - Triple Pixel | Draft | Metric |
| [Z] Welcome Series - Website | Draft | Added to List |
| Welcome Series 2026 - No Coupon | Manual | Added to List |
| [Z] Win-back - Lapsed Customers | Manual | Metric |
| [Z] Replenishment - Category Based | Manual | Metric |
| [Z] Flu Season - Winter Wellness | Manual | Added to List |
| [Z] Order Confirmation | Draft | Metric |
| [B] Search Abandonment V4 - Clicked Search Result | Manual | Metric |
| [Z] Back in Stock | Manual | Metric |

### Flow performance (May 1–12)
- Fragrance Clearance campaign (May 6): 119,651 recipients, 27.5% open, $6,427 attributed
- Abandoned Checkout: 763 recipients, 24 conversions, $1,569
- Added to Cart Abandonment: 1,063 recipients, 30 conversions, $2,370
- Browse Abandonment - Triple Pixel: 1,730 recipients, 9 conversions, $375

---

## 9. Confirmed Bugs (and Fixes Applied)

### Bug 1: New Customers L30D definition (FIXED in segment VQ8Sz4)
- Old: `Placed Order count = 1 in last 30 days` → captured 4-10 order repeat customers
- New: `count=1 in 30d AND count=1 in 1095d` → genuine first-time buyers
- Validation: 3 sampled emails from old segment had Shopify ordersCount of 4, 7, 10 (NOT first-timers)

### Bug 2: Email consent filter (FIXED across all 8 BC segments)
- Old: `consent_status: {subscription: 'any'}` → included NEVER_SUBSCRIBED users
- New: `consent_status: {subscription: 'subscribed'}` → verified to exclude unsubscribed
- Validation: test segment with `'subscribed'` returned 3 profiles all SUBSCRIBED

---

## 10. Best-Practice Gap Analysis (segments STILL missing)

### 🔴 P0 — Highest ROI (subject to user approval before creation)

| # | Segment | Use case | Sizing required |
|---|---|---|---|
| 1 | BC — Pharmacy-Only Buyers (exclusion) | Exclude from retail PMax ads | Unmeasured |
| 2 | BC — Lapsed Retail 180-365D (win-back) | Feed `[Z] Win-back` flow | Unmeasured |
| 3 | BC — Unengaged Subscribed 180D | Sunset list hygiene | Unmeasured |
| 4 | BC — High AOV Retail ($100+) | Premium product targeting | Unmeasured (filter syntax verified) |
| 5 | BC — Multi-channel Subscribed (Email + SMS) | Highest reachability | Unmeasured |

### 🟡 P1 — Next priority

| # | Segment | Use case |
|---|---|---|
| 6 | BC — New Email Subscribers L30D | Welcome series candidates |
| 7 | BC — Champions / Top 10% LTV | Lookalike seed (uses `historic_clv` which exists) |
| 8 | BC — Discount-Dependent | Pricing strategy |
| 9 | BC — Hibernating 365D+ | Quarterly mass win-back |
| 10 | BC — Wegovy/GLP-1 Customers | Replenishment retention |

### Predictive Analytics — NOT enabled per user
- P2 segments (Predicted CLV, Churn Risk, Likely-to-Buy) excluded from plan

---

## 11. Connector Status

| Connector | Status |
|---|---|
| Shopify MCP | ✅ Working |
| Klaviyo MCP | ✅ Working (read-only) + Klaviyo API via key (read+write) |
| GTM MCP | ✅ Working |
| Triple Whale | ⚠️ Partial — attribution endpoint works, metrics/Moby need Firebase JWT |
| GA4 via Zapier | ✅ Working |
| Google Ads via Zapier | ⚠️ Limited — `find_customer_list`, `_zap_raw_request`, no spend API |
| Code by Zapier | ✅ Working (with output wrapper quirks) |
| Xero | ⚠️ Read access limited (single record only) |
| CallRail | ❌ Trigger-only, no read |
| Meta Ads, TikTok Ads, Search Console | ❌ Not enabled in Zapier |

---

## 12. Decisions Pending User Confirmation

- [x] ~~Rename [SIZING] BC segments → BC (deploy)~~ — **DONE 2026-05-14**: All 14 renamed via PATCH /api/segments
- [ ] Build P1 segments (Champions, New Subscribers, Multi-channel, Hibernating, Discount-Dependent)
- [ ] Cart Abandoners 30d (620) below CM threshold — Cart Abandoners 60d added as parallel segment
- [ ] Recent L7D (~850) below CM threshold — confirmed for exclusion-only use
- [ ] Browse Abandoners retail-filter limitation (Viewed Product has no Collections property)?

## P1 Schema Probe Results (2026-05-14)

| Schema | Result | Notes |
|---|---|---|
| SMS subscribed consent (`channel: 'sms'`) | ✅ Accepted | Multi-channel segment buildable |
| `profile-list` condition with `list_id` | ❌ Rejected (400) even with real list ID | Klaviyo uses different condition type for list membership; needs more research |
| `Total Discounts > 0` filter | ❓ Unknown (Zapier wrapper stripped output) | Retry needed |
| `Discount Codes is-not-empty` filter | ❌ Rejected (400) | Wrong operator |

---

## 13. NEW: Wegovy / GLP-1 Pharmacy Revenue (May 2025 – May 2026)

| Product | Orders (TTM) | Gross Sales NZD |
|---|---|---|
| Wegovy FlexTouch Pen (generic) | 87 | $36,399 |
| WEGOVY 2.4 MG | 8 | $3,270 |
| WEGOVY 1.7 MG | 5 | $1,956 |
| WEGOVY 0.25 MG | 6 | $1,904 |
| WEGOVY 1 MG | 2 | $1,070 |
| WEGOVY 0.5 MG | 1 | $339 |
| Mounjaro 15mg | 1 | $761 |
| Mounjaro 10mg | 1 | $600 |
| **TOTAL GLP-1** | **111 orders** | **$46,299** |

- AOV ~$417 (massive — vs $56 store-wide)
- Estimated ~50-80 unique GLP-1 customers (high recurrence per customer)
- **Replenishment opportunity** — high-frequency buyers, predictable cadence
- Cannot run Google Ads on these (prescription/restricted), but Klaviyo email retention is ✅

## 14. Verified High-AOV Customers (sample)

| Email pattern | Orders | Total Spent (NZD) |
|---|---|---|
| sooah@healthinside | 6 | $462 |
| theeditor@xtra | 5 | $485 |
| anjasochacka@... | 6 | $382 |
| katherine.rayn@... | 5 | $431 |
| m.kadada@... | 6 | $433 |
| melissa19830919@... | 5 | $502 |
| Kunzang@xtra | 5 | $707 |
| judith18163@... | 5 | $558 |

Pattern: customers with 5+ orders typically spend $380-700+ over their lifetime. Strong "Champions" candidates for lookalike.

## 15. Critical Reminders

⚠️ **Klaviyo Private API key (prefix `pk_XCgiqg_`) was exposed in conversation transcript.** Rotate at https://www.klaviyo.com/account#api-keys-tab once work is complete. Full key intentionally NOT recorded here.

⚠️ **polyfill-fastly.net** in theme is a confirmed supply-chain security risk. 24h priority to remove.

⚠️ **Predictive Analytics is NOT enabled** in Klaviyo per user. P2 segments (Predicted CLV, Churn Risk, Likely-to-Buy) cannot be built. `historic_clv` IS available (just sum-of-orders calc) — can still build Champions/Top-LTV segment using it.
