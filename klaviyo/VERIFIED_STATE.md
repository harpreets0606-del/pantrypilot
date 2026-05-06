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

## Per-action message config — verified across all 14 non-archived flows

**Status:** VERIFIED
**Source:** `--inspect-flow-config all` (raw REST API via script) on 2026-05-06
**Fact:** Klaviyo API revision 2025-10-15 **rejects** `send_options`, `send_strategy`, `tracking_options`, `conversion_metric_id`, `trigger_filters` as `fields[flow]` values (HTTP 400). At flow level, only `name, status, archived, created, updated, trigger_type` are exposed via API. Default GET also doesn't return those config fields. **They're set/visible only in the Klaviyo UI.**

However, **per-action `definition.data.message` IS exposed** and gives us the per-email config:

### Smart Sending (`smart_sending_enabled`) per email-send action

**ON (Y) — most flows:**
- All Post-Purchase actions ✅
- Added to Cart Abandonment E1 (98627502, LIVE) ✅
- Added to Cart Abandonment E2 (98628345, draft) ✅
- All Browse Abandonment + ATC Triple Pixel ✅
- Win-back E1 (105721759, LIVE) ✅, E2 (105721762, draft) ✅
- Welcome Series - No Coupon all 3 ✅
- All 13 Replenishment retail-first slots ✅ (good — our V1 deploy preserved Smart Sending)
- Back in Stock E1 (105627854, LIVE) ✅, E2 (draft) ✅
- Search Abandonment V4 (draft) ✅
- Abandoned Checkout - Triple Pixel (all draft) ✅

**🚨 OFF (N) — critical:**
- **Abandoned Checkout E2/E3/E4** (98627487, 98627489, 98627490, all draft) — ALL THREE follow-up emails after E1. The "$5 off coupon" CLAUDE.md violation email is one of these. If any get activated, customers who recently received any other BC email will be hit again with no suppression.
- **Welcome Series - Website**: 4 of 7 send-email actions Smart Sending OFF (100893583, 101094506, 101094786, 101094883). Inconsistent setup — if ever activated as-is, half the welcome emails would ignore Smart Sending.

### Transactional flag (`transactional`)

**🚨 ALL emails = `false` (N) across every flow.** No email is flagged transactional anywhere — including Order Confirmation (VJui9n, draft). If/when Order Confirmation activates without `transactional=true`, it'll be subject to marketing-unsubscribe suppression — which is wrong for an order confirmation (customers expect it regardless of marketing opt-out).

### Tracking params (`add_tracking_params`)

**ALL emails = `true` (Y) across every flow.** UTM tracking is enabled universally. Good.

### Custom UTM templates (`custom_tracking_params`)

Set on **only one flow**: Welcome Series - Website (4 of 7 send-email actions):
```
utm_campaign = {message_name} ({message_id})
utm_medium   = email
utm_source   = {flow_name}
```

All other flows use Klaviyo's default UTM template (which Klaviyo hard-codes as: `utm_source=email`, `utm_medium=email`, `utm_campaign={Campaign Name}` — pretty generic and not flow-aware). For attribution analytics, the Welcome Series - Website pattern is better — should be applied to other flows.

### Flow-level config visibility — not via API

API revision 2025-10-15 doesn't expose flow-level `send_options`, `send_strategy`, `tracking_options`, `conversion_metric_id` regardless of include params. To verify these you'd need:
1. Klaviyo UI manual inspection (Flow → Settings → Tracking + Conversion Metric)
2. Or upgrade revision (newer revisions may expose them)
3. Or use the Klaviyo Web app's internal API (unsupported)

## Critical configuration findings (verified, action items)

| # | Finding | Severity | Action |
|---|---|---|---|
| C1 | **Order Confirmation (VJui9n) is `draft` AND not transactional-flagged.** | 🚨 production-protective | Before activation: set `transactional=true` on its email action. Otherwise unsub'd customers won't receive their order confirmation. |
| C2 | **Abandoned Checkout E2/E3/E4 have Smart Sending OFF.** | 🚨 deliverability risk | Enable Smart Sending on actions 98627487, 98627489, 98627490 before any are activated (especially given E2 has the $5 coupon — needs both Smart Sending fix + coupon-removal copy fix). |
| C3 | **Welcome Series - Website has Smart Sending OFF on 4 of 7 emails.** | high if activated | Either consolidate (some emails are duplicates per audit) or enable Smart Sending uniformly. Since flow is `draft`, fix before activating. |
| C4 | **Custom UTM templates only on Welcome Series - Website (and only 4 of 7 actions there).** | medium attribution gap | Apply same pattern (`utm_campaign={message_name} ({message_id})`, `utm_source={flow_name}`) to all email-send actions for proper flow-level attribution in GA/analytics. |
| C5 | **Flow-level send_options / send_strategy / tracking_options / conversion_metric_id are not API-exposed.** | medium | Document via UI screenshot or direct inspection of one LIVE flow. |

---

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

## Browse + Search Abandonment — flow STRUCTURE (verified via inspect-flow-trigger 2026-05-06)

**Status:** VERIFIED
**Source:** `--inspect-flow-trigger RtiVC5` + `--inspect-flow-trigger XbQiKg`

### Browse Abandonment (RtiVC5) structure

```
Trigger:  Metric (specific metric ID not exposed by Klaviyo API revision 2025-10-15)
Actions:  2 total
  - 98627562  time-delay  (duration not exposed via API; visible only in UI)
  - 98627563  send-email  template=Tutaam, draft, Smart Sending ON
              subject="Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?"
```

**Missing vs best practice:**
- ❌ No `trigger-split` action (no event-time filtering)
- ❌ No `conditional-split` action (no exit if customer converts)
- ❌ No E2 follow-up
- ⚠️ Single delay duration unknown (UI inspection needed)

### Search Abandonment V4 (XbQiKg) structure

```
Trigger:  Metric (specific metric ID not exposed)
Actions:  2 total
  - 105487705  time-delay  (duration not exposed)
  - 105487706  send-email  template=RPZh8V, draft, Smart Sending ON
               subject="{% if event.productName %}Still looking for {{ event.productName }}?{% else %}Fo[und...]"
```

**🚨 New discovery — subject uses `event.productName` not `event.searchQuery`:**
- The body of template `RPZh8V` references `{{ event.searchQuery }}` (we verified earlier)
- The subject uses `{{ event.productName }}`
- These are different fields — meaning either:
  1. The trigger event provides BOTH (e.g. a custom Boost event "Search Result Clicked" with both productName and searchQuery)
  2. The subject and body were authored against different events and one is stale
  3. The flow is misconfigured

**Action:** confirm the actual trigger metric in Klaviyo UI under Flow → Trigger. If trigger is Viewed Product, body's `event.searchQuery` references are stale and won't render. If trigger is Submitted Search, subject's `event.productName` won't render.

**Missing vs best practice (same as Browse):**
- ❌ No trigger-split / conditional-split
- ❌ No E2 follow-up
- ⚠️ Trigger event mismatch between subject and body

## Browse Abandonment + Search Abandonment V4 — content audit

**Status:** VERIFIED
**Source:** `klaviyo_get_email_template Tutaam` + `klaviyo_get_email_template RPZh8V` on 2026-05-06
**Fact:**

### Browse Abandonment (RtiVC5, draft) — template `Tutaam`

Single email (action 98627563), Smart Sending ON, fires after 1 time-delay.

Content state:
- Subject: `Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?` ✅
- Hero subtitle: *"You were this close. The item you checked out is still in stock — but popular products don't always stay that way."* ⚠️ mild scarcity ("don't always stay that way") — borderline ASA Code 1(b)
- Personalisation: uses `{{ event.URL }}`, `{{ event.ProductName }}`, `{{ event.ImageURL }}`, `{{ event.Price }}` — proper Browse-event vars
- CTA: "Get It Now" → `{{ event.URL }}` (direct product link)
- Has price-beat guarantee block (substantiated)
- Has my injected duplicate UEMA footer (192 Moorhouse — address mismatch with Klaviyo registered Belfast)
- No custom UTM params (uses Klaviyo defaults; less attribution-friendly)

**Reason it's not performing:** flow is `draft`, hasn't been activated. Content ~85% there. Need: soften scarcity line, then activate.

### Search Abandonment V4 (XbQiKg, draft) — template `RPZh8V`

Single email (action 105487706), Smart Sending ON, fires after 1 time-delay.

Content state:
- Subject: uses `{{ event.searchQuery }}` and `{{ event.productName }}` (truncated in earlier output)
- Hero: *"You recently searched for "{{ event.searchQuery|default:'' }}". Pick up your search where you left off or browse our popular categories below."* ✅ factual, no fear
- CTA: "RETURN TO SEARCH" → `bargainchemist.co.nz/search?q={{ event.searchQuery|default:'' }}`
- Category fallbacks (verified URLs): `/collections/vitamins-supplements`, `/collections/home-household`, `/collections/cold-flu`, `/collections/weight-management`, `/collections/allergies-hay-fever-sinus`, `/collections/fragrances`
- Trigger requires Klevu/Boost `Submitted Search` event (confirmed metric exists)

**Reason it's not performing:** flow is `draft`, hasn't been activated. Content is solid. Likely waiting on confidence in Klevu/Boost search-event reliability before turning on.

### Boost signal volume (5 weeks ending 6 May 2026)

**Status:** VERIFIED
**Source:** `klaviyo_query_metric_aggregates` for R2KxMT, XQ2zfW, Y2qHKK, UfaNeY on 2026-05-06
**Fact:**

| Metric | Wk1 (5 Apr) | Wk2 (12 Apr) | Wk3 (19 Apr) | Wk4 (26 Apr) | Wk5 (3 May) |
|---|---|---|---|---|---|
| [Boost] Submitted Search | 4,769 / 1,280 | 2,238 / 648 | **375 / 88** | 2,040 / 515 | 2,103 / 662 |
| Viewed Product (Boost) | 11,417 / 2,602 | 5,253 / 1,266 | **1,089 / 211** | 5,213 / 1,053 | 5,599 / 1,439 |
| [Boost] Clicked Search Result | 4,722 / 1,352 | 2,104 / 647 | **388 / 87** | 1,899 / 515 | 1,892 / 640 |
| Active on Site (Boost) | 4,580 / 3,045 | 1,977 / 1,354 | **577 / 241** | 2,181 / 1,214 | 2,657 / 2,048 |

(format: events / unique profiles per week)

**Findings:**
1. **Boost integration is firing at meaningful volume in normal weeks.** Sufficient trigger fuel for Browse + Search abandonment flows.
2. **🚨 Week of 19 April 2026 had an 80–95% dip across ALL Boost metrics.** Simultaneous collapse — indicates an integration outage (Boost service, BC site, or pixel installation). Recovered fully in subsequent weeks. **Worth investigating before activating dependent flows** to avoid future silent outages.

### Both flows — common gaps

- ⚠️ Single email only (no E2 follow-up, no escalation logic)
- ⚠️ My injected duplicate footer with Moorhouse address (matches the address-mismatch issue noted earlier)
- ⚠️ No `custom_tracking_params` set — Klaviyo defaults applied. For attribution consistency they'd benefit from the same template Welcome Series - Website uses (`utm_campaign={message_name} ({message_id})`, `utm_source={flow_name}`)

---

## CONSOLIDATED FLOW INVENTORY (15 flows total)

**Status:** VERIFIED
**Source:** `--audit-action-statuses` + `--inspect-flow-config all` on 2026-05-06

### LIVE flows (7) — actively sending or eligible

| Flow ID | Name | LIVE actions | Issues (verified) |
|---|---|---|---|
| RPQXaa | [Z] Added to Cart Abandonment | E1 (98627502) | ✅ Clean — A-grade voice, Smart Sending ON |
| TsC8GZ | [Z] Welcome Series - No Coupon | E1 + E2 (105721561, 105721565) | Empty preview text on all 3 emails |
| T7pmf6 | [Z] Win-back - Lapsed Customers | E1 (105721759) | Empty preview text on both emails |
| Y84ruV | [Z] Abandoned Checkout | E1 (98627483) | E1 fine. **E2-E4 draft + Smart Sending OFF**. E2 has $5 coupon (CLAUDE.md violation) |
| Ysj7sg | [Z] Back in Stock | E1 (105627854) | Fear language in both: "selling fast", "limited stock", "don't miss your chance" |
| V9XmEm | [Z] Flu Season - Winter Wellness | E1 (105627866) | Missing UEMA footer (no "Bargain Chemist Limited" + NZ address) |
| V4cZMd | [Z] Replenishment - Reorder Reminders | **0 actions live** | Flow status=live but every action draft/manual. New retail-first V1 templates deployed today, awaiting activation |

### DRAFT/MANUAL flows (8)

| Flow ID | Name | Status | Recommended action |
|---|---|---|---|
| VJui9n | [Z] Order Confirmation | draft | 🚨 **Should be LIVE** (transactional). Set `transactional=true` flag before activation. |
| RDJQYM | [Z] Post-Purchase Series | manual | Paused today (E1 had wrong content + broken `{ first_name }`). Needs rewrite + rebind to review-request template before re-activating |
| RtiVC5 | [Z] Browse Abandonment | draft | Audit + activate. Largest unutilised retention flow. |
| XbQiKg | [B] Search Abandonment V4 | draft | Audit + decide. Has good UTM template pattern (`utm_campaign={message_name} ({message_id})`). |
| SehWRt | [Z] Welcome Series - Website | draft | 4 of 7 emails have Smart Sending OFF. Either fix + activate (replacing TsC8GZ?) or archive. |
| RSnNak | [Z] Browse Abandonment - Triple Pixel | draft | Triple Pixel deprecated — archive |
| VMKAyS | [Z] Abandoned Checkout - Triple Pixel | draft | Same — archive |
| SnakeG | [Z] Added to Cart Abandonment - Triple Pixel | draft | Same — archive |

### Genuinely missing flows (not in inventory)

Verified by absence in flow list + segment audit:

1. **Birthday flow** — no Date-Based-trigger flow exists
2. **VIP / High-LTV recognition** — no value-based segment, no flow targeting top-spend customers
3. **Mum & Bubs welcome series** — `[Z] Baby (30 day engaged)` segment exists but not wired as a flow trigger
4. **Cross-sell by category** — Replenishment is reorder-only; no flow suggests related categories after first purchase
5. **Anniversary / Customer-for-N-years** — no Date-Based flow

### What's correctly NOT a missing flow (assumptions corrected)

- ❌ "No SMS channel" — WRONG; SMS infrastructure exists (Sent SMS, Subscribed to SMS Marketing metrics)
- ❌ "No category segmentation" — WRONG; 10+ category-engagement segments exist
- ❌ "No Triple Whale tracking" — WRONG; active integration with 5 metrics
- ❌ "Mum & Bubs / Baby segment doesn't exist" — WRONG; segment exists, just not wired into a flow

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
