# Verified Klaviyo & Shopify Account State — Bargain Chemist

**Purpose:** Single source of ground truth. Every claim cites a specific MCP tool call or query that produced it. Treat these facts as authoritative until a fresher tool call returns different data, at which point this file is updated and the old fact marked SUPERSEDED with a date.

Each fact follows this format:

```
## [TOPIC]
**Status:** VERIFIED | UNVERIFIED | SUPERSEDED
**Source:** <tool_name> on <date>
**Fact:** <statement>
```

If something here turns out wrong, replace it (don't delete) and add a SUPERSEDED note with the date and reason. Don't make any "gap" or "recommendation" claim that isn't backed by a fact in this file.

---

## Account fundamentals

**Status:** VERIFIED
**Source:** `klaviyo_get_account_details` on 2026-05-06
**Fact:**
- Account ID: `XCgiqg`
- Public API Key: `XCgiqg`
- Test account: `false`
- Organization name: `Bargain Chemist`
- Industry: `Ecommerce, Health & Beauty`
- Default sender name: `Bargain Chemist`
- Default sender email: `hello@bargainchemist.co.nz`
- Website: `https://www.bargainchemist.co.nz`
- Currency: `NZD`
- Timezone: `Pacific/Auckland`
- Locale: `en-US` ⚠️ (should arguably be `en-NZ` for NZ-only audience)

## Registered organization address (UEMA s9 sender field)

**Status:** VERIFIED
**Source:** `klaviyo_get_account_details` on 2026-05-06
**Fact:** Klaviyo registered address is:
```
1 Radcliffe Road
Belfast
Christchurch, Canterbury 8051
New Zealand
```

**🚨 CONFLICT IDENTIFIED:** UEMA footers in existing BC templates AND in my `--fix-footers` injection use `192 Moorhouse Avenue, Christchurch 8011`. **One of these is wrong** — the customer-facing UEMA address must match the registered sender. Belfast is likely a warehouse/distribution centre; Moorhouse may be a retail-store address. Need user to confirm which address should be used in customer-facing footers (probably the registered company address per UEMA s9, which is whatever appears in the Companies Office record for "Bargain Chemist Limited").

**Implication for our V1 deploy:** the new Replenishment templates do NOT include the address (we use `{{ organization.full_address }}` which Klaviyo populates from the registered address `1 Radcliffe Road, Belfast`). So our V1 templates use the *registered* address. If retail templates should show Moorhouse instead, that needs separate handling.

## Lists (page 1 of N)

**Status:** PARTIALLY VERIFIED (only first page returned, more exist)
**Source:** `klaviyo_get_lists` on 2026-05-06
**Fact:** First 10 lists, ordered by ID:

| List ID | Name | Opt-in | Created |
|---|---|---|---|
| RhChwn | Back In Stock Send Update | double_opt_in | 2022-07-20 |
| SJgE8E | RATS Tracking 2 | double_opt_in | 2022-03-10 |
| SLvzvJ | RATS 5 Pack Follow Up | double_opt_in | 2022-03-04 |
| SbQ97n | Klaviyo Forms Master List | single_opt_in | 2020-04-28 |
| SgUdtd | Facebook Leads | double_opt_in | 2021-05-25 |
| SxBenU | **Website Form Subscribe** | single_opt_in | **2026-03-03** (recently active) |
| Sz3j75 | RATS Tracking 5 | double_opt_in | 2022-03-15 |
| TV98D7 | Legacy Upload - ActiveCampaign | double_opt_in | 2020-06-11 |
| Tjid3e | RATS Tracking 4 | double_opt_in | 2022-03-14 |
| TvtXH4 | Nespresso Competition NovDec 2021 | double_opt_in | 2021-11-18 |

Most lists are stale (RATS = COVID rapid antigen tests from 2022; legacy migration; old competitions). Only **Website Form Subscribe (SxBenU, 2026-03-03)** appears actively used.

**Need to do:** paginate through remaining lists; check member counts per list.

## Segments

**Status:** PARTIALLY VERIFIED (first page only)
**Source:** `klaviyo_get_segments` on 2026-05-06
**Fact:** 10 segments visible, all `is_active: true`, all created 2026-03-29 to 2026-03-31. **Bargain Chemist HAS sophisticated category-engagement segmentation** — earlier claim of "no segmentation" was wrong.

| Segment ID | Name | Window | Active |
|---|---|---|---|
| QYmdK4 | [Z] Vitamins & Supplements (180 day engaged) | 180d | yes |
| R4w64M | [Z] Allergy (90 day engaged) | 90d | yes |
| RKdgTM | [Z] Sitewide (180 day engaged) | 180d | yes |
| RKznVV | [Z] Hair (30 day engaged) | 30d | yes |
| RbKkDz | [Z] Sports Nutrition (90 day engaged) | 90d | yes |
| Rqi7Vc | [Z] Baby (30 day engaged) | 30d | yes |
| RxQh3S | [Z] First Aid (90 day engaged) | 90d | yes |
| S6sijb | [Z] Sitewide (30 day engaged) | 30d | yes |
| SDysAW | [Z] Sunscreen (30 day engaged) | 30d | yes |
| SVce5P | [Z] Fragrance (60 day engaged) | 60d | yes |

These align with Replenishment categories. Suggests segmentation infrastructure for category-targeted flows is built; need to verify if any flow USES these segments as triggers.

**Need to do:** paginate remaining segments; check if any flow uses these as audience filter or trigger.

## Metrics + integrations active

**Status:** VERIFIED
**Source:** `klaviyo_get_metrics` on 2026-05-06
**Fact:**

**Active integrations:**
- ✅ **Shopify** (`0eMvjm`) — eCommerce: Placed Order (`Sxnb5T`), Ordered Product (`UWP7cZ`), Added to Cart (`S4jKYD`), Checkout Started (`VvcTue`), Viewed Collection (`R8NG8X`), Refunded Order (`TGLZXK`), Cancelled Order (`W8dW6R`), Fulfilled Order (`RUm8tg`), Submitted Search (`XX5ssW`)
- ✅ **Triple Whale** (`01HR2GG8FTKG9P1RFQ0BRFCGEX`, "Triple Pixel") — Active on Site, Survey Answer, Checkout Started, Added to Cart, Viewed Product (all `*-Triple Pixel` named)
- ✅ **API integration** (`7FtS4J`) — Boost (Submitted Search, Clicked Filter, Clicked Product, Viewed Collection, Clicked Search Result, Pre-Order Added to Cart, Clicked Recommendation), Klevu Search, Active on Site, Webhook Send Successful, Multiplied Personalised Media, Form events
- ✅ **Klaviyo internal** — full email + SMS + push event tracking
- ✅ **Typeform** (`M25ZuJ`) — Filled Out Form
- ✅ **Meta Ads** (`gGC9Jb`) — Filled Out Lead Ad

**🚨 CORRECTIONS to my earlier claims:**
- "No SMS channel" — **WRONG.** SMS metrics exist: `Sent SMS` (`VWHzmM`), `Received SMS` (`UMiJtV`), `Clicked SMS` (`WzJBYq`), `Subscribed to SMS Marketing` (`UahFRi`), `Unsubscribed from SMS Marketing` (`SmRNkP`), `Failed to Deliver SMS` (`YnavuT`), `Received Automated Response SMS` (`XLk6PJ`). SMS infrastructure is set up. **Whether it's actively used is still unverified.**
- "No push notifications" — **PARTIALLY WRONG.** `Received Push` (`V2GKSW`), `Opened Push` (`WP8Dpr`), `Bounced Push` (`X6e7S5`) exist. Mobile push capability is set up.
- "No Triple Whale tracking" — **WRONG.** Triple Whale is active and tracking events; that's why we have Triple Pixel flow variants.

**🚨 OBSERVATION re: coupons:**
- `Coupon Used` (`UmMHDc`) and `Coupon Assigned` (`Yfz3Nk`) metrics exist
- CLAUDE.md says "No coupon codes can be applied in flows"
- These metrics being present doesn't violate the rule (they may track Shopify-level coupons or campaigns), but worth flagging that coupon tracking infrastructure is in place

## Currently LIVE flows (sending now)

**Status:** VERIFIED
**Source:** `--audit-action-statuses` on 2026-05-06 + flow MCP reads
**Fact:** Across 15 total flows, only 6 actions have status `live` AND are inside a `live` flow:

| Flow | Action ID | Template | Subject | Voice grade |
|---|---|---|---|---|
| [Z] Abandoned Checkout | 98627483 | TUbBRk | "One step away from everyday savings" | A (no rush, no fear) |
| [Z] Added to Cart Abandonment | 98627502 | VqGJb8 | "This one's popular for a reason" | **A (gold standard)** |
| [Z] Win-back - Lapsed | 105721759 | XRDX9U | "We've missed you" | A |
| [Z] Welcome Series - No Coupon | 105721561 | WqsR7k | "Welcome to Bargain Chemist" | A |
| [Z] Welcome Series - No Coupon | 105721565 | VMrNuH | "We'll beat any pharmacy price" | A |
| [Z] Flu Season - Winter Wellness | 105627866 | SJwrxf | "Stay well this flu season" | B (missing UEMA footer in body) |

Plus 1 currently `manual` (paused by us today): action 105717123 (Regaine, RTUhv2) and 105717138 (Hayfexo→ now bound to RwcaXp daily-multi-immune content).

## Replenishment flow (V4cZMd) — V1 retail-first deploy

**Status:** VERIFIED
**Source:** `--deploy-all-replenishment-templates --confirm` on 2026-05-06
**Fact:** All 16 actions:

| Slot | Action | Bound template | Status | Category |
|---|---|---|---|---|
| 1 | 105717123 | RTUhv2 | manual | Regaine (paused, pharmacy-only excluded) |
| 2 | 105717126 | RQWsnq | draft | Skincare daily |
| 3 | 105717129 | SDPfJb | draft | Sun protection |
| 4 | 105717132 | SzMfr9 | draft | Body care |
| 5 | 105717135 | WAnydr | draft | Hair care |
| 6 | 105717138 | RwcaXp | manual | Daily multi & immune (replaces Hayfexo) |
| 7 | 105717141 | V52VPQ | draft | Magnesium |
| 8 | 105717144 | YmXVE7 | draft | Probiotic |
| 9 | 105717147 | V6drUy | draft | Omega 3 |
| 10 | 105717150 | Tb9hUa | draft | Hydration / electrolytes |
| 11 | 105717153 | Yj8rrM | draft | Sports / protein |
| 12 | 105717156 | XJHD23 | draft | Cosmetics daily |
| 13 | 105717159 | WUr5y7 | draft | Baby & postpartum |
| 14 | 105717162 | Xi9BaU | draft | Oral care daily |
| 15 | 105717165 | Tw2jiD | draft | Meal replacement |
| 16 | 105717169 | Xjk7fC | draft | First aid |

All retail-first templates are `[BC-Replenishment] <category>` named with BC bespoke anatomy. CTAs all link to `/collections/all` (V1 limit; V2 will use per-slot collection URLs). No product images yet (V2).

## Shopify product types — order volume (180 days)

**Status:** VERIFIED
**Source:** `run-analytics-query` (FROM sales SHOW orders, gross_sales GROUP BY product_type) on 2026-05-06
**Fact:**

| Type | Orders | Revenue | Pharmacy/Retail |
|---|---|---|---|
| Health & Wellbeing | 20,828 | $1.03M | mostly retail (supplements + Optifast) |
| Personal Care | 16,949 | $554k | retail |
| Skin Care | 10,018 | $349k | retail |
| Medicines & Professional Services | 8,815 | $295k | pharmacy |
| _pharmacy-only | 7,244 | $185k | pharmacy |
| Beauty Accessories (mostly fragrance) | 5,648 | $326k | retail |
| Cosmetics | 5,035 | $152k | retail |
| Health Equipment | 2,836 | $83k | retail (mostly one-off) |
| Baby | 2,096 | $66k | retail |
| Household | 1,509 | $46k | retail |
| General Food & Drink | 1,221 | $34k | retail |

Retail total ~63k orders / $1.66M; pharmacy total ~16k / $480k. Retail is **4×** the pharmacy volume by orders.

## Pharmacy-restricted SKUs identified (do not promote in flows)

**Status:** VERIFIED
**Source:** `search_products` on 2026-05-06
**Fact:** Confirmed restricted via `Pharmacy_Only_check` tag and/or `_pharmacy-only` product_type:
- All 4 Regaine SKUs (Men's Foam 60g, Solution 4-month, Foam 4-month, Women's archived) — `Pharmacy_Only_check`, productType `Medicines & Professional Services`
- Hayfexo Hayfever Relief 180mg 70 Tablets — vendor Dr. Reddy's, productType `_pharmacy-only`
- Plus all products in product_type `_pharmacy-only` and `_pharmacist-only` (full list available via Shopify query)

## Confirmed retail-safe (no Pharmacy_Only_check tags)

**Status:** VERIFIED
**Source:** `search_products` on 2026-05-06
**Fact:** Verified non-pharmacy:
- La Roche Posay (vendor) — productType `Skin Care`
- GO Healthy supplements — productType `Health & Wellbeing`
- Oracoat Xylimelts — productType `Personal Care`

Other vendors mentioned in slot configs (Palmer's, CeraVe, Wild Ferns, Weleda, Sukin, BEING, Hask, Shea Moisture, Neutrogena, Sanderson, Nutra-Life, Clinicians, Musashi, Nothing Naughty, Optifast, FLASH, Maybelline, 1000HOUR, Sudocrem, Bepanthen, Viva la Vulva, Lansinoh, Childs Farm, Biotene, Miradent, Oral-B, Band-Aid, Savlon, USL Medical, Multisorb) — assumed retail based on category but **not individually tag-verified**. Add to "need to verify" list.

---

## Segment definitions — full structure

**Status:** VERIFIED (8 of 10 visible segments fully read)
**Source:** `klaviyo_get_segments` with `fields[segment]=name,definition,is_active` on 2026-05-06
**Fact:** Each `[Z] <Category> (<N> day engaged)` segment uses **identical sophisticated structure**:

```
conditionGroup 1 (AND):
  - profile.properties['Preferences'] CONTAINS "<Category>"        ← self-declared interest
  - [Boost] Clicked Search Result on category-tagged products      (Y2qHKK)
  - Viewed Product on category-tagged Categories list              (XQ2zfW)
  - [Boost] Added To Cart on category Collections                  (VKDiey)
  - Placed Order on category Collections                           (Sxnb5T)
  ALL within the time window (30/60/90/180 days)
conditionGroup 2 (AND with above):
  - email marketing consent = subscribed
```

**Implications:**
1. **Bargain Chemist has a Preference Center / profile property `Preferences`** — customers self-identify their category interests. Confirmed values used in segments: `Vitamins & Supplements`, `Allergy`, `Sports Nutrition`, `Baby & Children's Health`, `First Aid`, `Sunscreen`, `Fragrance`, `Hair`.
2. Segments combine self-declared preference + cross-channel engagement (search, view, ATC, order) + email consent. Best-practice setup.
3. Sitewide segments don't use Preferences — purely engagement based, plus Triple Pixel `Active on Site` (`SvTg8J`), Klaviyo `Opened Email` (`SZ8GZJ`), `Clicked Email` (`W3AFKt`).
4. Time-window strategy varies: 30 days (Hair, Baby, Sunscreen, Sitewide-30) / 60 days (Fragrance) / 90 days (Allergy, Sports Nutrition, First Aid) / 180 days (Vitamins, Sitewide-180).

**Need to do:** read the remaining 2 segments (likely 1+ pages remaining); read the actual `Preferences` profile property values in use.

## Active campaigns

**Status:** VERIFIED
**Source:** `klaviyo_get_campaigns` filtered by `status: any of [Scheduled, Sending, Adding Recipients, Preparing to send]`, `channel: email` on 2026-05-06
**Fact:** **Zero email campaigns currently scheduled or sending.** No queued blasts right now.

**Need to do:** check SMS-channel campaigns for active state; query recent past campaigns for cadence.

## Klaviyo flow attributes — MCP exposure limits

**Status:** VERIFIED (limitation, not a fact about the account)
**Source:** `klaviyo_get_flow` returns shape on 2026-05-06
**Fact:** The MCP `klaviyo_get_flow` tool returns ONLY: `name`, `status`, `archived`, `created`, `updated`, `triggerType`. It does NOT expose:
- `send_options` (Smart Sending toggle, etc.)
- `tracking_options` (UTM params, click tracking)
- `send_strategy`
- `conversion_metric_id`
- audience filter / trigger details

**Implication:** to verify those fields, must use the raw Klaviyo REST API via the script (`scripts/klaviyo_flow_manager.py` already has `safe_get` plumbing — we'd need a `--inspect-flow-config` step, or have the user paste output of a curl). Or use Klaviyo UI manually.

## What MCP cannot expose (need other tools)

**Status:** VERIFIED (tool inventory)
**Fact:** The available Klaviyo MCP tools do not expose:
- Per-flow `send_options` / `tracking_options` / `send_strategy` / `conversion_metric_id`
- Account-level frequency caps / send-rate caps
- Domain authentication (SPF / DKIM / DMARC) status
- Forms inventory (popup forms, embed forms, multi-step forms) — no `klaviyo_get_forms` tool surfaced
- Suppressed-list size / bounce stats — not exposed via current tools
- Profile property schema (only individual profile reads available)
- Webhook / private app integration details

To verify these, options are:
1. Raw REST API via `scripts/klaviyo_flow_manager.py` (works, but needs new commands)
2. Manual Klaviyo UI inspection by user
3. Klaviyo OpenAPI spec to confirm whether MCP simply doesn't surface these or they're API-not-exposed

---

## ❓ Unverified — DO NOT make claims about these until checked

The following items I've previously made claims/recommendations about WITHOUT verifying. Need MCP queries before stating any "gap" or "recommendation" involving them:

1. **Per-flow `send_options.use_smart_sending`** — is Smart Sending on by default? Need: `klaviyo_get_flow` with `fields[flow]=send_options`
2. **Account-level frequency caps** — does BC have global caps preventing over-emailing? Need: account settings query (may not be exposed via API)
3. **Domain authentication (SPF / DKIM / DMARC)** — Need: account/sending domain query
4. **SMS active usage** — metrics exist; are SMS campaigns actually sending? Need: `klaviyo_get_campaigns?channel=sms`
5. **Forms / signup methods** — what types? popup / embed / multi-step? Need: forms API query (if available via MCP)
6. **A/B test history** — any flow / campaign A/B tested? Need: campaign query with audience details
7. **Suppressed list size + bounce stats** — Need: profile query with suppressed filter
8. **Segment → flow trigger wiring** — do the [Z] category segments actually drive any flow? Need: read each flow's trigger/audience definition
9. **Conversion metric per flow** — set or unset? Need: `klaviyo_get_flow` with conversion_metric_id field
10. **`tracking_options` per flow (UTM params, click tracking)** — Need: flow query
11. **Profile properties available** — what custom properties does BC capture? Need: profile schema query
12. **List member counts** — sizes of each list? Need: list query with size include
13. **Active scheduled campaigns** — what's queued to send? Need: campaign query filtered by status=Scheduled
14. **Webhook / private app integrations** — beyond the integrations metric list, are there custom webhooks? Need: integrations query
15. **Address mismatch resolution** — Klaviyo registered = `1 Radcliffe Road Belfast` vs UEMA footer = `192 Moorhouse Avenue` — which is the correct customer-facing address per BC's Companies Office NZ registration?
16. **All 7 DRAFT flows status detail** — are they in active development, archived-but-not-archived, or stale? Need flow-by-flow read.
17. **Per-product Shopify tag verification** — Palmer's, CeraVe, etc. assumed retail but not tag-checked.

## Pattern I will follow going forward

Before making any "gap" / "recommendation" / "missing" claim:
1. Find the question in the unverified list above (or add it)
2. Run the specific MCP query that resolves it
3. Update this file with the fact + source
4. Only then make the claim

If a fact in this file is contradicted by a fresher MCP result, replace the fact and add a SUPERSEDED note with the date and reason.
