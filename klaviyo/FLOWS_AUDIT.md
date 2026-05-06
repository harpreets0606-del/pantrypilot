# Bargain Chemist Klaviyo Flows — Audit Matrix

Cross-references `BRAND_VOICE.md` (campaign-derived patterns). Built progressively; one flow at a time, fully read before audit.

## Flow inventory (15 total, 8 LIVE / 7 DRAFT, from --verify-flows)

| # | ID | Status | Trigger | Name | Audit status |
|---|---|---|---|---|---|
| 1 | XbQiKg | draft | Metric | [B] Search Abandonment V4 - Clicked Search Result | ⏳ pending |
| 2 | Y84ruV | **live** | Metric | [Z] Abandoned Checkout | ⏳ pending |
| 3 | VMKAyS | draft | Metric | [Z] Abandoned Checkout - Triple Pixel | ⏳ pending (low priority — paused) |
| 4 | RPQXaa | **live** | Metric | [Z] Added to Cart Abandonment | ⏳ pending |
| 5 | SnakeG | draft | Metric | [Z] Added to Cart Abandonment - Triple Pixel | ⏳ pending (low priority — paused) |
| 6 | Ysj7sg | **live** | Metric | [Z] Back in Stock | ⏳ pending |
| 7 | RtiVC5 | draft | Metric | [Z] Browse Abandonment | ⏳ pending |
| 8 | RSnNak | draft | Metric | [Z] Browse Abandonment - Triple Pixel | ⏳ pending (low priority — paused) |
| 9 | V9XmEm | **live** | Added to List | [Z] Flu Season - Winter Wellness | ⏳ pending |
| 10 | VJui9n | draft | Metric | [Z] Order Confirmation | ⏳ pending (transactional) |
| 11 | RDJQYM | **live** | Metric | [Z] Post-Purchase Series | ✅ AUDITED below |
| 12 | V4cZMd | **live** | Metric | [Z] Replenishment - Reorder Reminders | ⏳ pending (LARGEST — 13 emails, never touched) |
| 13 | TsC8GZ | **live** | Added to List | [Z] Welcome Series - No Coupon | ⏳ pending |
| 14 | SehWRt | draft | Added to List | [Z] Welcome Series - Website | ⏳ pending |
| 15 | T7pmf6 | **live** | Metric | [Z] Win-back - Lapsed Customers | ⏳ pending |

---

## Flow 11: [Z] Post-Purchase Series (RDJQYM, LIVE)

**Trigger:** Placed Order metric. **Volume:** 0 recipients last 30d (per --verify-flows; either zero orders qualifying OR throttled).
**Intent:** Drive product reviews + repeat orders after purchase.

### Email 1 — msg_SP9FSD (template currently bound: original | [COMPLIANCE] candidate: TniTse)

**Currently shipping:**
- Subject: `How are you finding it?` (24 chars — too short, no signal of intent)
- Pre-header: `One week on` (cryptic, not BC pattern)
- Hero: "How are you finding it, { first_name|default:'there' }?" + "A quick moment to share your thoughts would mean the world to us"
- Body opener: "Hi { first_name|default:'there' }," + "You've had your order for about a week now — we hope you're loving it. If you have a moment, we'd really appreciate a quick review. It helps other Kiwis make confident choices."
- CTA box: 5 decorative stars + "How would you rate your experience?" + button "Write a Review" → **links to homepage `bargainchemist.co.nz`** (no review page)
- Fallback: "Not happy with something? Please reply to this email — we'd love the chance to make it right." ✅ good
- Categories: 3-up Supplements / Skin Care / Clearance ❌ dilutes the review ask
- Footer: standard BC red `#FF0031` legal block + unsubscribe ✅ already UEMA/ASA compliant

**Findings:**
| # | Severity | Issue | Cause |
|---|---|---|---|
| 1 | 🚨 critical | Variables `{ first_name }` will ship as literal text — single-brace Django syntax | template was authored wrong |
| 2 | 🚨 critical | "Write a Review" CTA → homepage; no review system wired | no Yotpo/Reviews.io/Stamped integration |
| 3 | 🚨 high | Doubled footer (my injection on top of the existing red footer) | --fix-footers didn't check for existing UEMA block |
| 4 | medium | Subject doesn't match BC voice patterns | generic question vs "Tell us how you're going" / "How are you finding your [product]?" |
| 5 | medium | No personalisation by purchased product | no `{{ event.extra.line_items }}` reference |
| 6 | medium | 3 generic category buttons dilute the single CTA | the email's job is one ask: leave a review |
| 7 | low | ASA Code 2025: pharmacy-only / restricted products **cannot solicit testimonials** | needs branching by product category |

**What it should say (proposed):**
- Subject: `How's the {{ event.extra.first_item_name|default:"order" }} going, {{ first_name|default:"there" }}?` (~50 chars)
- Pre-header: `Quick review = real impact for other Kiwis` (~45 chars)
- Hero: BC red, headline "Tell us how it's going, {{ first_name|default:'there' }}"
- Body: reference their actual order if data available; one CTA only
- CTA: clickable star rating 1–5 → deep-link to review system (Yotpo/Reviews.io); rating prefilled
- Fallback: keep "Not happy? Reply directly"
- Drop the categories block
- Branch: if `customer.last_order` contains restricted SKUs (pharmacy-only / prescription) → skip review ask, send "thanks for your order" instead

### Email 2 — msg_Ycrkq6 (currently bound: [COMPLIANCE] template YdbfXy)

**Currently shipping:**
- Subject: `Running low?` (12 chars, fear-adjacent — does NOT match BC voice)
- Pre-header: `Two-week reminder` (functional, not pithy)
- Hero (dark `#1a1a1a` bg — anomaly vs BC red): "Running low, { first_name }?" + "It's been two weeks — time to think about restocking"
- Body: "It's been about two weeks since your last order. If you're on a supplement or health routine, now's a good time to reorder before you run out — staying consistent is what makes these products work."
- CTA: "🔄 Time to Restock?" → "Reorder Now" → `/collections/all` ❌ entire shop, not their product
- 4-column category grid
- Inline disclaimer: "Always read the label and use as directed. If symptoms persist, consult your healthcare professional." ✅
- Footer: standard BC red `#FF0031` legal block ✅ + my injected duplicate ❌

**Findings:**
| # | Severity | Issue | Cause |
|---|---|---|---|
| 1 | 🚨 critical | Variables `{ first_name }` broken (same bug as E1) | template authored wrong |
| 2 | 🚨 critical | 2-week trigger is wrong for supplements (typically 30+ day cycle) — creates spam-feel | timing logic |
| 3 | 🚨 high | "Running low?" + "before you run out" is fear-adjacent; off-brand | copy |
| 4 | 🚨 high | Reorder CTA → `/collections/all` (whole shop) instead of their actual products | no event-data deep-link |
| 5 | 🚨 high | Doubled footer | same as E1 |
| 6 | medium | Dark hero `#1a1a1a` is inconsistent with BC red `#CC1B2A` brand standard | template-level |
| 7 | medium | 🔄 emoji not part of BC palette (per BRAND_VOICE.md emoji rules) | copy |

**What it should say (proposed):**
- Subject: `Time to top up your routine, {{ first_name|default:'there' }}?` (~50 chars) — proactive, BC voice
- Pre-header: `Reorder in seconds — same products, same prices` (matches existing BC preview style)
- Hero: BC red `#CC1B2A`, headline "Stay consistent, {{ first_name|default:'there' }}"
- Body: "It's been [N] days since your order — if you're on a routine, now's a good time to top up. Reorder in seconds and stay consistent." (no fear, factual)
- CTA: deep-link to their actual product(s) or pre-populated cart
- Drop the 4-up category grid (or move below the CTA, smaller)
- Free shipping nudge: "Add anything else and qualify for free delivery over $79"
- **Re-time trigger:** 25–28 days post-purchase (one week before typical 30-day supply runs out)

### Trigger logic critique
- Filter: only customers whose order included supplement/repeat-purchase SKUs (don't send replenishment for one-off cosmetic purchases)
- Skip: customers who've already placed a follow-up order in the window
- Skip: customers with active subscriptions (if BC offers any)

---

## Flow audit log

- 2026-05-06 — Established BRAND_VOICE.md from 40 sent campaigns
- 2026-05-06 — Audited Flow 11 (Post-Purchase Series): 13 findings across 2 emails, 4 critical
