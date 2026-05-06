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

---

## Flow 12: [Z] Replenishment - Reorder Reminders (V4cZMd, LIVE) 🚨

**Trigger:** Placed Order metric. **Status:** LIVE. **Volume:** unknown (throttled).
**Intent:** Reorder reminders, product/category-specific.

**Surprise finding:** **16 email messages**, not 13 (verify-flows undercounted). 50 actions total — likely uses a **conditional split per product category** so customer gets the email matching what they bought.

### Account-wide observations from this flow

- ✅ Variable syntax CORRECT here: `{{ person.first_name|default:'friend' }}` — confirms the broken `{ first_name }` bug is **isolated to Post-Purchase Series**, not universal
- ✅ All 16 use shared 600px responsive CSS — built from a single base template
- 🚨 All 16 messages have **EMPTY preview text** — major deliverability + click-rate hit
- 🚨 All 16 messages share an **IDENTICAL subject line**: `{{ person.first_name|default:'friend' }}, time to restock?` — inbox providers may flag as duplicate; users see same line repeatedly across the sequence

### Per-message inventory (subject = identical, preview = empty across all)

| # | Action ID | Msg ID | Template | Hero / category | Severity |
|---|---|---|---|---|---|
| 1 | 105717123 | WdBQF5 | RTUhv2 | "Time to Reorder Your **Regaine**" | 🚨 **CRITICAL** — Regaine = minoxidil 5%, Pharmacist-Only Medicine in NZ, ASA Therapeutic Code restricts advertising |
| 2 | 105717126 | TNaUxX | TUNbVw | "Running Low on Your Supplements?" | high (fear-adjacent, generic) |
| 3 | 105717129 | RnHYqR | Tygapr | "Running Low on Your Supplements?" | high |
| 4 | 105717132 | UXzKrP | T55Smr | "Running Low on Your Supplements?" | high |
| 5 | 105717135 | YyrwsM | SEwQEP | "Running Low on Your Supplements?" | high |
| 6 | 105717138 | XVqtQa | SfXNYd | "**Don't Get Caught Without Your Allergy Relief**" | 🚨 **HIGH** — fear language ("Don't get caught"), ASA Rule 1(b) violation |
| 7 | 105717141 | Xiprdx | RY53Mw | "Running Low on Your Supplements?" | high |
| 8 | 105717144 | YtNg7p | Xqycyc | "Running Low on Your Supplements?" | high |
| 9 | 105717147 | TCUpRb | TXxc7R | "Running Low on Your Supplements?" | high |
| 10 | 105717150 | XdLaS9 | TAZazL | "Running Low on Your Supplements?" | high |
| 11 | 105717153 | UNjeK3 | VUp6fj | "Running Low on Your Supplements?" | high |
| 12 | 105717156 | YpaZKZ | RQm3cm | "Running Low on Your Supplements?" | high |
| 13 | 105717159 | XL9X9n | QVrdp3 | "Running Low on Your Supplements?" | high |
| 14 | 105717162 | X98UwK | WYVqLk | "Running Low on Your **Oracoat**?" | 🚨 **CRITICAL** — Oracoat OraCoating gel is a therapeutic mouth-ulcer adhesive; needs ASA review for promotional advertising |
| 15 | 105717165 | SVg6Ta | XKMdXA | "Nearly Time to Restock Your Meal Plan" | low (factual, BC-tone) |
| 16 | 105717169 | Ww7RU8 | V4rwDM | "Nearly Time to Restock Your Meal Plan" | low |

### Findings

| # | Severity | Issue | Action required |
|---|---|---|---|
| R1 | 🚨 CRITICAL | **Regaine email (WdBQF5)** is shipping promotional content for a Pharmacist-Only Medicine — direct violation of ASA Therapeutic & Health Advertising Code 2025 + CLAUDE.md restricted-product rule | Pause this branch; audit product list against `_pharmacist-only` tag |
| R2 | 🚨 CRITICAL | **Oracoat email (X98UwK)** likely violates same — needs Medsafe / ASA classification check | Verify product classification; pause if restricted |
| R3 | 🚨 high | **Allergy email (XVqtQa)** subject hero "Don't Get Caught Without…" is fear language | Rewrite to BC voice: "Top up your hayfever essentials" or similar |
| R4 | 🚨 high | **All 16 emails identical subject** | Personalise per category: "Top up your daily multi", "Reorder your skincare routine", etc. |
| R5 | 🚨 high | **All 16 empty preview text** | Add per-message preview matching BC patterns (4–10 words, factual or pithy benefit) |
| R6 | medium | 12 templates use generic "Running Low on Your Supplements?" hero — fear-adjacent + repetitive | Differentiate by actual category (vitamins / probiotics / digestive / etc.) and rewrite to BC tone |
| R7 | medium | `person.first_name` used instead of `first_name` (both valid, but BC campaigns use `first_name`) | Standardise across flows |
| R8 | unknown | Footer / structure / threshold — not yet verified per template | Need full HTML read of 1–2 templates |
| R9 | unknown | Trigger timing / branching logic — how does it decide which of 16 emails fires? | Need to inspect flow structure (delays + conditional splits) |

### Compliance escalation (CORRECTED after Shopify verification)

Verified product classifications by querying Shopify catalog directly:

- **Regaine (msg WdBQF5)** — ✅ **CONFIRMED restricted**
  - Product type: `Medicines & Professional Services`
  - Tags: `Pharmacy_Only_check`, `Pharmacy`, `BRAND=Regaine`, `CONCERN=Hair Loss`
  - All 4 Regaine SKUs in BC catalog (Men's Foam 60g $71.99, Men's Solution 4-month $179.99, Men's Foam 4-month $186.99, Women's archived) carry the Pharmacy_Only_check tag
  - **A "time to restock" promotional reorder email is a CLAUDE.md restricted-product violation** (rule: "never price-promoted") and likely contravenes ASA Therapeutic & Health Advertising Code 2025
  - **Action: pause the Regaine branch of this flow today.**

- **Oracoat Xylimelts (msg X98UwK)** — ❌ **MY EARLIER FLAG WAS WRONG**
  - Product type: `Personal Care` (NOT Medicines)
  - Tags: `personal-care`, `oral-care`, `dental-care`, `dry-mouth`, `breath-freshener` — NO Pharmacy tags
  - These are over-the-counter xylitol oral-comfort lozenges, sold at general retail
  - **No restriction. Safe to keep in the flow as-is** (subject + preview still need rewrites for brand voice).

### Shopify-grounded product additions / replacements

Pulled top-selling products by orders (last 90 days, 4,325 orders total). Filtered out anything tagged `Pharmacy` / `Pharmacy_Only_check` / `Limit X per Customer` / `_pharmacist-only`.

**Safe high-volume replenishment candidates — RETAIL-FIRST ranking** (pure retail / personal care / consumer supplements before pharmacy-adjacent items):

#### Tier 1: Pure RETAIL (skincare, body care, oral care)

| Rank | Product | Vendor | 90d orders | AOV | Replenishment cycle |
|---|---|---|---|---|---|
| 1 | La Roche-Posay Anthelios UVm400 SPF 50+ | La Roche Posay | 79 | $35 | Daily sunscreen, 30–60 days |
| 2 | CeraVe Face Moisturising Lotion PM 52ml | Cerave | 79 | $27 | Daily skincare, 30–60 days |
| 3 | Palmer's Tahitian Vanilla Body Oil 192ml | Palmer's | **114** | $20 | Daily body care, 30–60 days |
| 4 | Palmer's Tahitian Vanilla Body Lotion 400ml | Palmer's | 76 | $12 | Daily body care, 30–60 days |
| 5 | Blis Tooth Guard M18 Lozenges 30s | BLIS | 75 | $51 | Daily oral care, 30 days |
| 6 | Miradent Xylitol Spearmint Gum 30s | Miradent | 93 | $13 | Daily oral care, 15–30 days |

#### Tier 2: Consumer SUPPLEMENTS (general retail, no pharmacist consultation needed)

| Rank | Product | Vendor | 90d orders | AOV | Replenishment cycle |
|---|---|---|---|---|---|
| 7 | **Elevit Preconception & Pregnancy Multi 100 Tablets** | Elevit | 84 | **$80** | Daily, 100-day cycle; highest AOV |
| 8 | Sanderson Omega 3 Fish Oil 3000 150 Caps | Sanderson | 84 | $33 | Daily, 75–150 days |
| 9 | GO Healthy Magnesium Sleep 120 VCaps | Go Healthy | 101 | $33 | Daily, 60–120 days |
| 10 | Nutra-life Magnesium Glycinate 60s | Nutra-Life | 80 | $22 | Daily, 60 days |
| 11 | Clinicians Flora Restore 30 Capsules (probiotic) | Clinicians | 114 | $25 | Daily, 30 days |
| 12 | Clinicians Sunshine Vitamin D3 60 Tablets | Clinicians | 70 | $17 | Daily, 60 days |
| 13 | Musashi Creatine 350g (sports nutrition) | Musashi | 75 | $33 | Daily, 70 days |

#### Tier 3: Skip (pharmacy-adjacent, may need exclusion check)

- **OPTIFAST VLCD Shake** — clinical meal replacement programme, may need pharmacy/clinical context
- **Iron Melts Chewable Iron** — supplement but iron supplementation has clinical context; verify tags before including
- (Anything else with `Pharmacy` or `Pharmacy_Only_check` tags — auto-exclude)

### Recommended Replenishment flow restructure

**Replace 1 branch:**
- ❌ Remove Regaine branch (msg WdBQF5) — pause, then either delete or convert to a generic "personal care reorder" branch that excludes restricted SKUs

**Keep:**
- ✅ Oracoat Xylimelts (msg X98UwK) — was incorrectly flagged; rewrite subject only
- ✅ Meal Plan branches (msg SVg6Ta, Ww7RU8) — likely OPTIFAST related, factual tone
- ✅ Allergy Relief (msg XVqtQa) — keep but rewrite hero from "Don't Get Caught Without…" to BC tone

**Add new branches for missing top sellers — RETAIL-WEIGHTED priority:**

Tier 1 (retail-first, ship these new branches first):
1. **Daily skincare** branch — La Roche-Posay SPF + CeraVe PM (combined 158 orders / 90d) — split or combined depending on flow capacity
2. **Body care** branch — Palmer's Body Oil + Body Lotion (190 orders combined)
3. **Daily oral care** branch — Blis Tooth Guard + Miradent Xylitol Gum (168 orders combined)

Tier 2 (consumer supplements, ship after retail tier):
4. **Elevit (preconception/pregnancy)** — high AOV ($80), 84 orders/90d, 100-day cycle
5. **Magnesium** branch — GO Healthy Sleep + Nutra-life Glycinate (181 orders combined)
6. **Probiotic** branch — Clinicians Flora Restore (114 orders, 30-day exact cycle)
7. **Omega 3** branch — Sanderson Fish Oil
8. **Vitamin D3** branch — Clinicians Sunshine
9. **Sports nutrition** branch — Musashi Creatine

The current flow is **overweighted on pharmacy/medicine SKUs**. After this rebalance, the flow should target retail/personal-care/consumer-supplement repeat purchases — which is also where Bargain Chemist's strongest brand voice already lives (per BRAND_VOICE.md analysis of 40 sent campaigns: "feel good", "discover", "your routine", "your glow").

**Rewrite all 14 remaining branches** to:
- Per-category subject (e.g. "Top up your Vitamin D, {{ first_name|default:'there' }}?" / "Time to reorder your Elevit?")
- Add preview text (4–10 words, factual)
- Replace generic "Running Low on Your Supplements?" hero with category-specific BC-tone copy
- Use `first_name` not `person.first_name` to standardise with rest of account
- Verify `{{ }}` variable syntax (likely fine here, but check)

### Audience filter — this is the real fix

The Replenishment flow currently triggers on `Placed Order` metric for any order. To be ASA-safe and prevent accidental restricted-product targeting:

```
Add filter on "Was in product variant" condition:
  EXCLUDE customers whose last order included any product tagged:
    - Pharmacy_Only_check
    - Pharmacy
    - product_type == "Medicines & Professional Services"
    - any "Limit X per Customer" SKU
```

This makes the entire flow ASA-safe by default — Regaine and any future restricted products are automatically excluded regardless of which branch fires.

---

---

## Flow 2: [Z] Abandoned Checkout (Y84ruV, LIVE) 🚨

**Trigger:** Started Checkout metric. **Status:** LIVE. **Volume:** 1,714 recipients last 30d (high — biggest active flow we have data on).
**Intent:** Recover abandoned checkouts.

**Structure:** 8 actions, 4 emails. Likely structure: trigger → wait → E1 → wait → E2 → conditional split → E3 (branch A) / E4 (branch B). E3 and E4 have identical subject/preview, suggesting a value-based split where both branches end with the same nudge.

**Templates appear to be MJML-built** (Klaviyo drag-and-drop editor) — different template family from the bespoke BC red `#CC1B2A` templates we saw earlier. Need to verify they share BC's footer/header anatomy.

### Per-message audit

| # | Action | Msg | Subject (chars) | Preview | Template | Voice / issues |
|---|---|---|---|---|---|---|
| 1 | 98627483 | S7KJkR | "One step away from everyday savings" (37) | "Your items are waiting — no rush." | TUbBRk | ✅ "no rush" is anti-fear — **exemplary BC tone** |
| 2 | 98627487 | SE9wC6 | "$5 off to complete your checkout" (32) | "Because you were so close." | TjFTnU | 🚨 **CRITICAL — incentive/coupon offer violates CLAUDE.md "no coupon codes" rule** |
| 3 | 98627489 | VBYf2r | "Ready when you are" (18) | "Finish checkout in just a few clicks." | TFpqRc | ✅ helpful, BC-tone |
| 4 | 98627490 | TcxiTj | "Ready when you are" (18) | "Finish checkout in just a few clicks." | TuHa4f | ⚠️ **identical subject + preview to E3** |

### Findings

| # | Severity | Issue | Action |
|---|---|---|---|
| AC1 | 🚨 CRITICAL | **E2 offers "$5 off" — direct violation of CLAUDE.md** ("No coupon codes can be applied in flows — incentives must be free shipping reminders, social proof, value messaging, or factual scarcity only") | Pause E2 today. Rewrite without the discount offer; lean on free-shipping-over-$79 instead |
| AC2 | high | **E3 + E4 share identical subject + preview** | Either differentiate per branch (e.g. E4 = "still here for you, {{ first_name }}?") OR consolidate into one email if the conditional split adds no value |
| AC3 | unknown | Need to verify E3 vs E4 template bodies actually differ (might just be a duplicated branch) | Read both templates' HTML |
| AC4 | unknown | Footer — these are MJML/Klaviyo-editor templates, not the bespoke BC anatomy. Need to confirm UEMA footer + brand colors present | Inspect full HTML |
| AC5 | medium | E1 subject "everyday savings" — **value-led, not coupon-led, so OK if body delivers value (not a discount)** | Verify body doesn't actually contain a discount code |
| AC6 | low | E2 subject only 32 chars — fine; E4 subject 18 chars — short but works | None |

**Voice strengths to keep:**
- "no rush" preview text on E1 is **the best anti-fear copy I've seen across this audit** — opposite of "Last chance!" panic
- "Ready when you are" / "in just a few clicks" — calm, helpful, on-brand
- "Because you were so close" preview text on E2 — empathetic, BC-tone (just remove the $5 incentive from the subject)

**Voice issues:**
- "$5 off" subject is a coupon-style incentive, banned by CLAUDE.md. The rest of the email's voice is fine; just the offer needs replacing.

### Suggested rewrites (pre-approval, do NOT execute yet)

**E2 — replace the discount with a free-shipping nudge or social proof:**
| Current | Suggested |
|---|---|
| Subject: `$5 off to complete your checkout` | `Free delivery over $79 — your cart's already there?` (~50 chars) OR `Your wellness picks are still waiting` |
| Preview: `Because you were so close.` | `No code needed — just complete your order` (free-shipping nudge) |

**E4 (if branch logic warrants keeping it separate from E3):**
| Current | Suggested |
|---|---|
| Subject: `Ready when you are` (duplicate) | `Still here for you, {{ first_name|default:'there' }}` (~38 chars) |
| Preview: `Finish checkout in just a few clicks.` (duplicate) | `Same products, same prices — pick up where you left off` |

---

---

## Flow 4: [Z] Added to Cart Abandonment (RPQXaa, LIVE) ⭐ GOLD STANDARD

**Trigger:** Added to Cart metric. **Status:** LIVE. **Volume:** 1,408 recipients last 30d.
**Intent:** Recover ATC abandons.
**Structure:** 5 actions, 2 emails. Likely: trigger → wait → E1 → wait → E2.

### Per-message audit

| # | Action | Msg | Subject (chars) | Preview | Template | Voice |
|---|---|---|---|---|---|---|
| 1 | 98627502 | TCgQED | "This one's popular for a reason" (32) | "Just popping in - your item's still waiting." | VqGJb8 | ✅ Social-proof angle + casual "popping in" |
| 2 | 98628345 | TpkzDd | "Your cart's still saved" (23) | "No pressure — just a quick reminder." | RWKxKR | ✅ **"No pressure" — exemplary anti-fear** |

### Findings

| # | Severity | Issue | Action |
|---|---|---|---|
| ATC1 | ✅ none | **Cleanest BC voice in the audit so far.** Both emails actively counter fear language ("Just popping in", "No pressure"). Inverse of typical e-commerce panic copy. | Use as the **template/voice exemplar** for rewriting other flows |
| ATC2 | low | E2 subject 23 chars — on the lower end of BC sweet spot (30–55) but acceptable | Optional: extend to ~35 chars (e.g. `Your cart's still saved, {{ first_name|default:'there' }}`) |
| ATC3 | medium | E1 social-proof angle ("popular for a reason") — body must actually deliver social proof (review counts, reorder rate) | Verify body content has substance — read template HTML |
| ATC4 | unknown | Templates are MJML-generated (Klaviyo drag-drop) — need to verify UEMA footer + brand colors | Same as Abandoned Checkout — read full HTML |
| ATC5 | unknown | No `first_name` personalisation visible in subjects/previews | Worth A/B testing personalised subjects |

**This is the flow whose voice we should clone everywhere else.** Specifically these moves:
- "No pressure" / "no rush" / "Just popping in" / "Ready when you are" — **anti-fear BC vocabulary**
- Subject + preview that pair: factual statement + warm reassurance
- Calm, helpful, Kiwi-casual

If Replenishment / Post-Purchase / Welcome had this voice, the audit would be far cleaner. Keep this as the reference.

---

## Flow audit log

- 2026-05-06 — Established BRAND_VOICE.md from 40 sent campaigns
- 2026-05-06 — Audited Flow 11 (Post-Purchase Series): 13 findings across 2 emails, 4 critical
- 2026-05-06 — Audited 4 NEW templates we created: 8 critical issues common to all. **Confirmed not in Klaviyo library — Python source deleted from script.**
- 2026-05-06 — Audited Flow 12 (Replenishment): 16 emails. CORRECTED: only Regaine (msg WdBQF5) is restricted (Pharmacy_Only_check tag); Oracoat Xylimelts is Personal Care, not restricted. Plus retail-first additions plan from Shopify top-sellers.
- 2026-05-06 — Audited Flow 2 (Abandoned Checkout): 4 emails, 1,714 recipients/30d. **CRITICAL: E2 offers "$5 off" — direct CLAUDE.md "no coupon" violation.** E3+E4 share identical subject + preview. E1 voice exemplary.
- 2026-05-06 — Audited Flow 4 (Added to Cart Abandonment): 2 emails, 1,408 recipients/30d. **GOLD STANDARD — cleanest BC voice in the audit.** "No pressure" / "Just popping in" — anti-fear copy across both emails. Templates MJML, need HTML verification of footer/colors.
