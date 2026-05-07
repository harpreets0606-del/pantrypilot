# Klaviyo Account Audit — Bargain Chemist

**Date**: 2026-05-06
**Account ID**: XCgiqg
**Audit window**: last 90 days (where API allowed)
**Audit completeness**: ~85% — limited by Klaviyo MCP scope (template HTML, list member counts, profile-level predictive data not accessible)

---

## 1. INVENTORY (verified from API)

### Flows — 15 total
| Status | Count | Names |
|--------|-------|-------|
| **Live** | 7 | Added to Cart Abandonment, Abandoned Checkout, Win-back Lapsed, Welcome Series No Coupon, Replenishment, Flu Season Winter Wellness, Back in Stock |
| **Draft** | 7 | Welcome Series Website, Browse Abandonment, Browse Abandonment Triple Pixel, Added to Cart Abandonment Triple Pixel, Order Confirmation, Abandoned Checkout Triple Pixel, Search Abandonment V4 |
| **Manual** | 1 | Post-Purchase Series |

**Naming pattern**: `[Z]` prefix on most flows, `[B]` on a couple (Search Abandonment). Likely agency code (Z = Zyber? — needs confirmation).

**Triple Pixel duplicates**: 4 flows duplicated as "Triple Pixel" versions in DRAFT — appears to be alternative tracking via Triple Whale integration. Status unclear.

### Campaigns — 92 sent in last 90 days (≈1/day)
- **Channel**: 100% email. **0 SMS** sent in 90 days.
- **Status**: 91 Sent, 1 Draft (Revlon Solus Feb 2026 — never sent, likely abandoned)
- **Naming pattern**: most are "[Brand] Solus - [Month YYYY]" supplier-sponsored sends. Plus seasonal (Christmas Gifting, Black Friday, New Year Deals, Father's Day, Mums & Bubs, Valentines), category-bundled (Price Smash Vitamins/Beauty/Sports), and "Supplier 1/2/3" templated batches.

### Lists — 17+ (paginated subset shown)
**Active**: Website Form Subscribe (created Mar 2026), Klaviyo Forms Master List, Back In Stock Send Update, Shopify Accepts Marketing
**Legacy / dormant**: 13+ — RATS Tracking 2/3/4/5, RATS Email Follow Up, Legacy ActiveCampaign upload, Nespresso Competition (2021), Facebook Leads, Covid Vaccination Voucher (2021), AA Membership, Flu Vaccine, Preview List
**Opt-in process**: mix of single + double opt-in
**Note**: list member counts not available via current MCP scope.

### Segments — 50+ (across pagination, mostly category × engagement window)
| Pattern | Examples |
|---------|----------|
| Category × engagement window (most common) | `[Z] Vitamins & Supplements (30/60/90/180 day engaged)`, `[Z] Skincare (30/60/90/180)`, `[Z] Allergy (30/60/90/180)`, `[Z] Hair (30/60/90)`, `[Z] Sports Nutrition (30/60/90/180)`, `[Z] Baby (30/60/180)`, `[Z] First Aid (30/60/90/180)`, `[Z] Sitewide (30/60/90/180)`, `[Z] Sunscreen (30/60/90)`, `[Z] Fragrance (30/60/90/180)`, `[Z] Personal Care (30/60/90/180)`, `[Z] Pet (30/60/90/180)`, `[Z] Weight (30/60/90/180)`, `[Z] Household (60/90/180)`, `[Z] Cold & Flu (30/90/180)`, `[Z] Sexual Health (30/90/180)`, `[Z] Cosmetics (30/60/90)` |
| Send segments | `Master Send Segment`, `Master Send Segment - No Spark (Xtra)`, `Master Send Segment - No Spark (Xtra) - Auckland Subscribers`, `Women's Segement` (sic — typo) |
| Customer-state | `Repeat Buyers`, `Repeat Buyers (365 days)`, `All Active Customers (Last 180 Days)`, `Purchasers without activity LD 30`, `Not Subscribed` |
| Other | `[Z] Suppressed - Retargeting Campaign`, `[Z] Suppressed Profiles - Meta Exact Match Retargeting` |

**Recency pattern**: most `[Z]` segments created 29–31 March 2026 — recent rebuild or agency takeover.

### Metrics — 80+ recognised
- **Klaviyo native**: opens, clicks, bounces, spam, sub/unsub, etc. ✓
- **Shopify integrated**: Placed Order (`Sxnb5T`), Viewed Collection, Added to Cart, Checkout Started, Refunded Order, Cancelled Order, Fulfilled Order, etc. ✓
- **Triple Whale Triple Pixel**: Active on Site, Checkout Started, Added to Cart, Viewed Product, Survey Answer
- **"Boost" prefix metrics**: Submitted Search, Clicked Filter, Clicked Product, Viewed Collection, Pre-Order Added to cart, Clicked Recommendation, Clicked Search Result — likely a personalisation/recommendation engine
- **Klevu Search** integration
- **Typeform** (Filled Out Form)
- **Meta Ads** (Filled Out Lead Ad)
- **Custom**: Interstore Order, Interstore Notification, Coupon Used, Coupon Assigned, Multiplied Personalised Media

---

## 2. PERFORMANCE (last 90 days)

### Flow performance — top performers
| Flow | Status | Recipients | Open | Click | Conv | RPR | Revenue |
|------|--------|-----------|------|-------|------|-----|---------|
| **Added to Cart Abandonment** ⭐ | Live | 8,743 | 41.18% | 6.10% | 2.48% | $2.31 | **$20,144** |
| **Abandoned Checkout** | Live | 9,792 | 44.86% | 6.20% | 2.44% | $1.81 | $17,614 |
| **Browse Abandonment - Triple Pixel** | Draft | 8,175 | 22.67% | 1.48% | 0.45% | $0.36 | $2,938 |
| **Welcome Series - Website** | Draft | 537 | 48.13% | 10.45% | 2.05% | $1.68 | $902 |
| **Browse Abandonment** | Draft | 1,376 | 44.89% | 4.89% | 0.73% | $0.49 | $676 |
| Added to Cart Abandonment - Triple Pixel | Draft | 1,888 | 28.25% | 4.01% | 1.82% | $1.81 | $3,388 |
| Abandoned Checkout - Triple Pixel | Draft | 845 | 31.64% | 5.21% | 1.33% | $1.48 | $1,220 |
| Search Abandonment V3 (Zyber) | (legacy?) | 294 | 44.86% | 7.19% | 0% | $0 | $0 |
| Search Abandonment - Zyber Boost Test | (legacy?) | 131 | 56.49% | 9.16% | 4.58% | $3.54 | $463 |
| Order Confirmation | (custom) | 136 | 57.35% | 0.74% | 0% | $0 | $0 |
| Win-back Lapsed | Live | 1 | — | — | — | — | $0 |
| Welcome Series No Coupon | Live | 8 | 50% | 12.5% | 0% | $0 | $0 |
| Flu Season Winter Wellness | Live | 22 | 36.36% | 0% | 0% | $0 | $0 |

**Total flow revenue (90d, observed)**: ~$48,000 NZD

### Campaign performance — sample of 28 large sends
| Pattern | Open rate | Click rate | Conv rate | RPR |
|---------|-----------|-----------|-----------|-----|
| Large sends to Master Send (110-120k) | 22-37% | 0.2-1.4% | 0.02-0.08% | $0.018-$0.06 |
| Mid sends to Women's Segement (46-50k) | 34-48% | 0.2-0.8% | 0.06-0.12% | $0.04-$0.11 |
| Small targeted sends (5-22k) | 40-55% | 0.4-1.4% | 0.1-0.25% | $0.07-$0.17 |

**Key observations**:
- **Click rates universally below benchmark.** Industry avg is 2.09%; BC range 0.2–1.4%. **None hit benchmark.**
- **Open rates decent on smaller sends**, poor on Master Send (suggests over-mailing fatigue at the top of the list).
- **One concerning bounce**: Clinicians Solus Feb 2026 — 7.37% bounce rate (one campaign anomaly, list quality at the time).
- **Highest performing single campaign**: Trilogy Solus April 2026 — 54% open, $0.17 RPR. Targeted to Women's Segment.
- **Lowest performing**: Fragrance Clearance May 2026 — 22% open, $0.018 RPR (most recent, signalling decline).

### Comparison to benchmarks (90d)
| Metric | BC observed | H&B benchmark | Verdict |
|--------|-------------|---------------|---------|
| Campaign open rate | 22-55% | 30.5% avg / 45-50% top quartile | Mixed — small sends OK, large fatigued |
| Campaign click rate | 0.2-1.4% | 2.09% avg | **Below benchmark across the board** |
| Campaign conversion | 0.02-0.25% | 0.10% avg | At/below avg |
| Campaign RPR | $0.018-$0.17 | $0.11 USD avg | At/below avg |
| Welcome flow open | 48% | 45-50% avg | At benchmark |
| Welcome flow conversion | 2.05% | 8-12% avg | **Way below benchmark** |
| Cart flow open | 41-45% | 50.5% avg | Below benchmark |
| Cart flow conversion | 2.4-2.5% | 3.33% avg | Below benchmark |
| Cart flow RPR | $1.81-$2.31 | $3.65 avg / $2.65 H&B | Approaching H&B benchmark |
| Browse abandonment conversion | 0.45-0.73% | 0.59% avg | Mixed — Triple Pixel below |

---

## 3. CONFIGURATION OBSERVATIONS

### Sender configuration
- **Sender label**: "Bargain Chemist" — consistent ✓
- **Sender email**: split between `hello@bargainchemist.co.nz` AND `orders@bargainchemist.co.nz`
  - `hello@` used on more recent campaigns
  - `orders@` used on most legacy campaigns + Black Friday 2025
  - **Mixing marketing and transactional senders is a deliverability red flag**
- **Reply-to**: never set
- **Smart Sending**: enabled on all sampled campaigns ✓
- **Tracking**: opens + clicks tracked, UTM params added ✓

### Authentication / deliverability — UNVERIFIED
- DKIM, SPF, DMARC status: cannot verify via Klaviyo MCP. Need user to check Klaviyo Settings → Domains and Senders.
- One-click unsubscribe (RFC 8058): can't verify but Klaviyo enables by default — confirm.
- BIMI: unknown.

### Audience patterns
- Most campaigns sent to **Master Send Segment** (110-120k recipients) — unsegmented broadcast
- Some campaigns target **Women's Segement** (typo!) — 46-50k
- Recent campaigns (April+) excluded **Reputation Repair Audience** — suggests past deliverability incident; flag for clarification
- One Auckland-only campaign (AFC Social Ticket) — geo-segmentation works ✓

### Volume / cadence
- **92 campaigns in 90 days = ~1 send/day to large list**
- Combined with ~16,000 flow recipients/90d, average BC subscriber receives ~7-10 emails/month
- Above the H&B sweet spot (4–8/month)
- Fatigue signs: declining open rates on Master Send sends over time

---

## 4. THINGS I COULDN'T VERIFY (audit gaps)

| Item | Why blocked | How to unblock |
|------|-------------|----------------|
| Email template HTML | API returned 401 on `klaviyo_get_email_template` | Klaviyo MCP scope expansion OR user provides template screenshots |
| List member counts | Pagination didn't include profile_count by default | Re-run with `additional-fields[list]=profile_count` |
| Segment member counts | Same — not pulled | Re-run with `additional-fields[segment]=profile_count` |
| Predictive analytics availability | Need profile sample with predictive_analytics field | User confirms 500+ customers / 180d history threshold met |
| DKIM/SPF/DMARC records | Not exposed via API | User checks Klaviyo Settings → Domains |
| Form HTML / signup UX | Form metadata not pulled | Add `klaviyo_get_forms` to follow-up audit |
| Flow message content (subject/body/conditions) | Sub-resource not loaded in this round | Pull `klaviyo_get_flow_messages` per flow |
| Profile-level data hygiene | Need profile sample with custom property usage | Sample 100 random profiles |
| Triple Pixel vs standard flow split logic | Not visible from flow metadata | User explains testing strategy |
| Brand voice intent (deliberate vs drift) | Inferred only from 12 subject lines | User confirmation |

---

## 5. POSITIVE FINDINGS (things working well)

1. ✓ **Recent segmentation rebuild** — 50+ category × engagement segments created late March 2026 — solid foundation
2. ✓ **Cart + Checkout flows live and converting** — primary revenue flows are running, RPR approaching H&B benchmark
3. ✓ **Smart Sending enabled** on all campaigns
4. ✓ **Excluded Reputation Repair audience** on recent campaigns — sign of deliverability awareness
5. ✓ **Geo-targeting works** — Auckland-only campaign for AFC tickets
6. ✓ **Multiple integrations active** — Shopify, Triple Whale, Klevu, Boost (recommendations), Typeform, Meta
7. ✓ **Customer browse + product viewed events tracked** via Triple Pixel — unusually rich event data
8. ✓ **Strong brand voice pattern detectable** — parallel-structure subject lines are distinctive
9. ✓ **Sender label consistent** ("Bargain Chemist")

---

## 6. AUDIT SUMMARY (high-level, no recommendations yet)

The account is **structurally sound but operationally underperforming**:

- **Foundations are in place** — flows exist, segments exist, integrations are active.
- **Three core flows are running** (Cart, Checkout, Browse Abandonment-Triple Pixel) and producing measurable revenue (~$48k in 90d).
- **The Welcome Series — the highest-leverage flow — is in DRAFT** despite receiving 537 recipients. **This is the single biggest miss.**
- **Click rates are universally below benchmark** across all campaigns — signals content / template issue, not list issue (open rates are decent on smaller sends).
- **Send volume is ~1 campaign/day** which is at the upper edge of safe; declining engagement on Master Send confirms fatigue.
- **Sender address is inconsistent** (`hello@` vs `orders@`) — fixable in 5 minutes, deliverability impact.
- **17 lists, mostly legacy** — list hygiene work needed.
- **Recent segmentation rebuild (March 2026)** suggests the account is in transition — likely agency handover or strategy reset (the `[Z]` prefix suggests agency Zyber).

Recommendations are deferred to `gaps.md` once user confirms baseline assumptions.
