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

---

## NEW templates we built ourselves (in `scripts/klaviyo_flow_manager.py`)

These 4 templates were authored from scratch in the script and pushed to Klaviyo via `--create-templates`. **All 4 are seriously off-brand and violate CLAUDE.md / ASA Code 2025 / BRAND_VOICE.md** — they need a full rewrite before being used in any flow.

| Template name | Function | Status in Klaviyo |
|---|---|---|
| `[Z] Abandoned Checkout – Email 3 (72hr Final)` | `template_abandoned_checkout_email3` (line 104) | exists (also has [COMPLIANCE] copy) |
| `[Z] Browse Abandonment – Email 2 (24hr Social Proof)` | `template_browse_abandonment_email2` (line 214) | exists |
| `[Z] Browse Abandonment – Email 3 (72hr Bestsellers)` | `template_browse_abandonment_email3` (line 303) | exists |
| `[Z] ATC Abandonment – Email 3 (72hr Final)` | `template_atc_email3` (line 390) | exists |

### Issues common to ALL 4 templates

| # | Severity | Issue | Evidence |
|---|---|---|---|
| 1 | 🚨 critical | **WRONG BRAND COLOR** — used GREEN `#00833e` everywhere; BC is RED `#CC1B2A` | `.header { background:#00833e }`, `.cta { background:#00833e }`, `color:#00833e` links |
| 2 | 🚨 critical | **Wrong free shipping threshold $50** — actual is **$79** | "Free delivery on orders over $50" appears in templates 1, 2, 4 |
| 3 | 🚨 critical | **No UEMA-compliant footer** — missing "Bargain Chemist Limited", NZ address, "Always read the label", "If symptoms persist see your healthcare professional" | Footer is just © year + "Visit our store" + unsubscribe |
| 4 | 🚨 critical | **No ASA legal disclaimer block** — missing the red `#FF0031` block with RRP/pricing/pharmacist disclaimers that every real BC template has | Compare to BRAND_VOICE.md "Compliance baseline" section |
| 5 | 🚨 critical | **Wrong header structure** — missing the shipping bar (`#7B1523`) → logo (`#CC1B2A`) → nav row pattern | Real BC has 4-col nav: Shop Products / Clearance / Find a Pharmacy / Contact Us |
| 6 | 🚨 high | **No social row** (TikTok / Facebook / Instagram / LinkedIn) | All real BC templates have it |
| 7 | high | Wrong logo URL — uses `bargainchemist.co.nz/cdn/shop/files/bc-logo-white.png` (likely 404) | Real BC: `cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218` |
| 8 | high | Uses `<div>` layout instead of nested `<table>` — breaks Outlook rendering | Real BC uses tables throughout for email-client compatibility |

### Per-template additional issues

#### `template_abandoned_checkout_email3` — "[Z] Abandoned Checkout – Email 3 (72hr Final)"

| # | Severity | Issue | Evidence |
|---|---|---|---|
| AC1 | 🚨 critical | **🚨 emoji in fear context** — violates BRAND_VOICE rule that 🚨 is Price Smash only | `🚨 Stock alert: Items in your cart are subject to availability.` |
| AC2 | 🚨 critical | **Heavy fear language** — banned by ASA Code Rule 1(b) | Subject `Last chance – your cart is expiring`, hero `⏰ Last chance`, body `we can only hold stock for so long`, `Stock alert` |
| AC3 | high | **Fake scarcity** — "stock is limited" with no factual basis | The cart system doesn't enforce stock holds; this is fabricated urgency |

#### `template_atc_email3` — "[Z] ATC Abandonment – Email 3 (72hr Final)"

| # | Severity | Issue | Evidence |
|---|---|---|---|
| AT1 | 🚨 critical | **Heavy fear language** | Title `Your cart is waiting – don't miss out`, hero `⚠️ Your cart is about to expire`, `This is your final reminder`, `We can't hold your items much longer`, `Stock is limited. We can't guarantee these items will still be available after today` |
| AT2 | 🚨 high | **⏰ + ⚠️ emojis in fear context** | `⏰ Heads up:` urgency block; `⚠️ Your cart is about to expire` hero |
| AT3 | medium | "Continue shopping" link → homepage instead of last-browsed category | `{{ organization.homepage }}` |

#### `template_browse_abandonment_email2` — "[Z] Browse Abandonment – Email 2 (24hr Social Proof)"

| # | Severity | Issue | Evidence |
|---|---|---|---|
| BR1 | medium | Subject `Still thinking it over?` is generic, doesn't match BC patterns | Should follow `Discover the…` / `Meet…` pattern or product-specific |
| BR2 | medium | "Pharmacist approved" badge unverified — may be a therapeutic claim | ASA Code 2025: only verified pharmacist endorsements |
| BR3 | low | "100,000 New Zealanders trust" — claim needs source | Numerical claims need substantiation |

#### `template_browse_abandonment_email3` — "[Z] Browse Abandonment – Email 3 (72hr Bestsellers)"

| # | Severity | Issue | Evidence |
|---|---|---|---|
| BB1 | 🚨 high | **Hardcoded product data** — will go stale (prices, availability, names drift) | FLASH Eyelash Serum $69.99 (was $89.99), Sanderson $34.99, GO Healthy Magnesium $24.99 |
| BB2 | high | **Therapeutic claims without disclaimer** — "9,500+ orders", "4.8★ from 2,000+ reviews", "#1 magnesium in NZ", "Sleep better, recover faster" | Each claim needs ASA-compliant substantiation; performance claims for supplements need "Vitamins and minerals are supplementary…" disclaimer |
| BB3 | medium | "Shop Our Best Sellers →" CTA goes to homepage, not a real "best sellers" collection | `{{ organization.homepage }}` — no `/collections/best-sellers` |

### Common subject lines that need rewriting

| Current | Issue | Suggested (BC voice) |
|---|---|---|
| `Last chance – your cart is expiring` | Fear language, ASA violation | `Your Bargain Chemist cart is waiting` |
| `Still thinking it over?` | Generic | `Take another look — your wellness picks are still here` |
| `Our customers love these too` | OK but generic | `Our top picks for {{ first_name|default:'you' }}, from $24.99` |
| `Your cart is waiting – don't miss out` | Fear ("don't miss out") | `Ready to complete your order, {{ first_name|default:'there' }}?` |

## Recommended action

**Do NOT use these 4 templates as-is.** They were drafted before BRAND_VOICE.md existed, in a generic ecommerce-panic style that contradicts:
- BC's actual brand voice (warm, descriptive, wellness-coded)
- ASA Code 2025 (no fear language, no fake urgency, no unsubstantiated claims)
- CLAUDE.md (🚨 Price Smash only, $79 threshold not $50, no fear-based subjects, mandatory UEMA footer)

**Two options:**

**A. Full rewrite** of all 4 template Python functions — restructure to match real BC template anatomy (shipping bar → logo → nav → hero in red `#CC1B2A` → body → social row → legal red block → unsubscribe red block), strip fear language, fix threshold, fix colors, add proper UEMA/ASA footer. Then re-`--create-templates`. Then assign to flows.

**B. Don't ship them at all.** The associated flows ([Z] Abandoned Checkout, [Z] Added to Cart Abandonment, [Z] Browse Abandonment) currently use other templates — verify whether these 4 are actually attached to anything live, and if not, just delete them from Klaviyo.

Recommended: **option B first** — verify whether they're in any flow message currently. If they aren't bound to live actions, deleting is safer than rewriting + potentially shipping bad copy.

## Flow audit log

- 2026-05-06 — Established BRAND_VOICE.md from 40 sent campaigns
- 2026-05-06 — Audited Flow 11 (Post-Purchase Series): 13 findings across 2 emails, 4 critical
- 2026-05-06 — Audited 4 NEW templates we created (template_abandoned_checkout_email3, template_browse_abandonment_email2, template_browse_abandonment_email3, template_atc_email3): 8 critical issues common to all + 11 per-template issues. **Recommend NOT using them; verify if in-flow first, otherwise delete.**
