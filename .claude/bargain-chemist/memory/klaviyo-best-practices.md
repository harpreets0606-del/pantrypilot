# Klaviyo Best Practices — Source of Truth

> Distilled from research of Klaviyo's official documentation, agency guides (Flowium, Titan, Omnisend, BS&Co), and 2025/2026 industry data. Cross-reference with `klaviyo-benchmarks.md` for the numeric yardsticks.

---

## PART 1 — FLOW PRIORITY (Health & Beauty / Pharmacy)

### Tier 1 — Must-have, highest ROI
1. **Abandoned Cart** — recovers 10–15% of lost revenue
2. **Abandoned Checkout** — recovers 15–20% of lost revenue (3.5× higher conversion than cart)
3. **Welcome Series (new customer, post-first-purchase)** — drives 10–25% of new-customer revenue
4. **Replenishment / Reorder** — for H&B, 35–50% of total flow revenue lives here

### Tier 2 — Strong ROI
5. **Post-Purchase nurture** — +15–25% repeat purchase rate
6. **Winback** — recovers 20–40% of lapsed customers; automated beats manual by 2,361% conversion
7. **Welcome Series (new subscriber, no purchase)** — list quality + first-purchase
8. **Back-in-Stock** — exceptional 6–24% conversion (highest-intent audience)

### Tier 3 — Moderate ROI
9. Browse Abandonment — high volume, lower conversion (0.59% avg)
10. Cross-sell / Upsell — AOV lift
11. Price Drop alert — model-dependent
12. VIP Recognition — retention, LTV +15–25%

### Tier 4 — Engagement / hygiene
13. Birthday / Anniversary
14. Review request (post-delivery)
15. Sunset (mandatory for deliverability)
16. Subscription welcome (if subscription model)

---

## PART 2 — FLOW STRUCTURE STANDARDS

### Welcome Series (new subscriber, no purchase)
- **Trigger**: Added to "Newsletter Subscriber" list (single source of truth)
- **Filter**: Hasn't purchased in last 90 days
- **Exit**: Placed Order
- **Length**: 3–4 emails over ~7 days
- **Cadence**: Email 1 immediate, Email 2 +24h, Email 3 +3d, Email 4 +6d
- **Content** (NO COUPONS — see `no-coupon-strategy.md`):
  - Email 1: Welcome + brand story + Price Beat Guarantee + free shipping over $79
  - Email 2: Best-sellers (product feed) + category education
  - Email 3: Social proof + reviews + find-a-store
  - Email 4: Soft reminder + seasonal/category hook (never expiring code)
- **A/B test priority**: Subject line on Email 1 (curiosity vs price-beat callout)

### Welcome Series (new customer, post-first-purchase)
- **Trigger**: Placed Order × first time
- **Length**: 3 emails over ~14 days
- **Content**:
  - Email 1 (immediate): Order confirmation + onboarding ("how to get the most out of your purchase")
  - Email 2 (+5d): Cross-sell complementary products
  - Email 3 (+10d): Reorder reminder / replenishment setup

### Abandoned Cart vs Abandoned Checkout
> Run both — they catch different stages.
- **Abandoned Cart**: triggered by Added to Cart (fires more often, lower intent)
- **Abandoned Checkout**: triggered by Checkout Started (fewer fires, higher intent — 3.5× conversion)
- **Length**: 3 emails (single email captures only ~15% of 3-email revenue per Klaviyo)
- **Cadence** (NO COUPONS — see `no-coupon-strategy.md`):
  - Email 1: 1–2h after trigger — reminder of cart contents + Price Beat
  - Email 2: 24h after — social proof + free shipping threshold nudge ("$X away from free shipping")
  - Email 3: 72h after — last-chance scarcity + free shipping nudge (no escalating code)
- **Filter**: hasn't placed order in last 30d to avoid double-touch
- **Exit**: Placed Order
- **A/B test priority**: Subject angle (urgency vs reassurance), free-ship progress bar vs static threshold

#### Cart-value tier playbook — DATA-DRIVEN, verified 2026-05-08

Single binary `<$79` / `≥$79` split is wrong for Bargain Chemist. Real cart-value distribution from 200-event live sample:
- 64.5% under $79 (median $49.62, mean $65.17)
- 35.5% at/above $79
- **77% of under-$79 carts are MORE than $30 below threshold** — saying "add $X for free shipping" lands wrong (gap too big to feel actionable).

**Three tiers, verified Klaviyo Django syntax (see `klaviyo-template-syntax-verified.md`):**

| Tier | Cart `$value` | Share | Right copy angle | Reason |
|---|---|---|---|---|
| **A** | < $30 | 29% | Trust + price ("Your cart is saved at NZ's lowest pharmacy prices") | Free-ship gap too large to feel actionable; small-impulse psychology |
| **B** | $30–$78 | 35.5% | Free-ship gap nudge ("Free shipping kicks in at $79 — add a few more items") | Gap is bridgeable in 1-2 items; highest-leverage segment |
| **C** | ≥ $79 | 35.5% | Honest reassurance ("Your cart was at our free-shipping tier ($79+) — finish checkout when you're ready") | Already qualified at submission; no logistics ask. Use past-tense to avoid ASA misleading-promise risk (cart can change between submission and click). |

Tier C MUST NOT use "free shipping is yours" or any future-tense promise — user could remove items between submission and click, no longer qualify. Use past-tense "was at" or "qualifies at submission".

**Implementation pattern in template body:**
```django
{% if event|lookup:'$value' < 30 %}
  [ Tier A copy ]
{% elif event|lookup:'$value' < 79 %}
  [ Tier B copy ]
{% else %}
  [ Tier C copy ]
{% endif %}
```

**Subject + preview**: keep universal (single line for all tiers). Tier-based subject lines are technically possible but add maintenance burden and complicate A/B testing.

**Verified deploy workflow:** `scripts/klaviyo_rebuild_email1_branded.py` — surgical edit of source brand template + render-test all tier paths + auto-rollback if any tier fails.

### Browse Abandonment
- **Trigger**: Viewed Product (or Klaviyo's "Active on Site")
- **Filter**: hasn't added to cart in last 24h, hasn't bought product
- **Length**: 1–3 emails
- **Cadence**: Email 1 +2–4h, Email 2 +24h, Email 3 +5–7d
- **Lower expected conversion** (0.59% benchmark) — volume compensates
- **No coupons** — replace with reminder + product detail / reviews / Price Beat reassurance (see `no-coupon-strategy.md`)

### Post-Purchase / Order Confirmation
- **Trigger**: Placed Order
- **Critical**: include ONE marketing element in confirmation (cross-sell, refer-a-friend, review request, social share). +2200% conversion lift.
- **Sequence**: confirmation (immediate) → ship notification (transactional) → +5d "thanks + how to use" → +10d cross-sell → +30d review request

### Replenishment
- **Trigger**: Placed Order with replenishment-eligible products (custom property)
- **Timing**: based on product cycle (vitamins ~30d, skincare ~60d, fragrance ~90d)
- **Send 5–7 days BEFORE expected runout**
- **Content** (NO COUPONS): re-order CTA + Price Beat reassurance + auto-replenish/subscribe option (no discount code)
- **Conversion benchmark**: 8–15% (5.7–15× higher than promotional)

### Winback / Lapsed
- **Trigger**: hasn't placed order in 60–90d (custom by category cycle)
- **Length**: 3–4 emails over 14–21 days
- **Reactivation levers (NO COUPONS)**: "we've missed you" + new arrivals → Price Beat reminder → free-shipping reminder + pharmacist concierge → "what would bring you back?" survey (see `no-coupon-strategy.md`)
- **Reactivation rate**: 20–40% best-in-class

### Sunset
- **Trigger**: hasn't opened/clicked in 180d AND hasn't ordered in 365d
- **Length**: 2–3 final emails over 14d
- **Last email**: "we're saying goodbye unless you click here"
- **After flow**: suppress or move to "graveyard" segment
- **Why critical**: protects sender reputation; unengaged recipients destroy deliverability

### Back-in-Stock
- **Trigger**: profile has "Back in Stock subscription" + product becomes available
- **Length**: 1 email (+ optional reminder if not opened in 72h)
- **Conversion benchmark**: 6–24% — highest of any flow

---

## PART 3 — SUBJECT LINE & PREVIEW TEXT

- **Subject line length**: 30–50 characters (mobile previews ~30–40)
- **Preview text length**: 40–130 characters — never empty, never repeat subject
- **Personalisation**: first name in subject lifts open rate ~10–15%; in preview lifts conversion
- **Emoji use**: helps open rate when used sparingly (1, max 2). Test by audience.
- **Spam triggers to avoid**: "FREE", excessive caps, !!!, "guaranteed", "risk-free", "click here"
- **Test variables (in priority)**:
  1. Subject angle (curiosity vs benefit vs urgency)
  2. Personalisation (with/without first name)
  3. Length (short vs long)
  4. Emoji (with/without)

---

## PART 4 — TEMPLATE / DESIGN

### Mobile-first non-negotiables
- Single-column layout (60–600px width)
- Body font ≥14px, headlines ≥22px
- Buttons ≥44×44px tap target, padding ≥12px
- Image-to-text ratio: aim 60% text / 40% image (avoid all-image emails — spam risk + accessibility fail)
- Alt text on every image
- Dark-mode tested (logos, transparent PNGs)

### Structural template
1. Header: logo (left), nav links (3 max)
2. Hero block: 1 image + 1 headline + 1 sub-headline + 1 CTA
3. Body: 1–3 product blocks OR content sections
4. Social proof: review snippets, ratings, UGC
5. Secondary CTA
6. Footer: physical address, unsubscribe, preference centre, social links, pharmacy registration

### Footer requirements (NZ pharmacy + general)
- Physical NZ address (1 Radcliffe Road, Belfast, Christchurch 8051)
- Unsubscribe link (one-click compliant per RFC 8058 — required for Gmail bulk senders)
- Preference centre link
- Pharmacy registration number
- Pharmacist name (where promoting medicines)
- Privacy policy link

### Saved blocks / universal content
- Build a header block, footer block, social-proof block, CTA-button block once → reuse across all templates
- Update one place, propagates everywhere

---

## PART 5 — DELIVERABILITY (CRITICAL — affects EVERYTHING)

### Authentication (set once, monitor monthly)
- **SPF**: `v=spf1 include:_spf.klaviyo.com -all` on root domain
- **DKIM**: Klaviyo provides 2 CNAMEs — add both
- **DMARC**: start `p=none` for monitoring → move to `p=quarantine` → ultimately `p=reject`
- **One-click unsubscribe**: enabled in Klaviyo by default; verify it works
- **BIMI** (advanced): brand logo in inbox — requires DMARC at `p=quarantine`+ and a VMC

### Sender domain
- Use a **branded subdomain** for marketing: e.g. `mail.bargainchemist.co.nz`
- Keep transactional on a different subdomain: `orders@bargainchemist.co.nz`
- **Never mix marketing and transactional from the same address** — kills deliverability of both
- Sender label consistent: always "Bargain Chemist" (✓ this is already done)

### List hygiene (continuous)
- **Auto-suppress hard bounces** immediately
- **Auto-suppress soft bounces** after 3–5 attempts
- **Auto-suppress spam complaints** immediately
- **Sunset unengaged**: 180d no open/click → suppress (after sunset flow)
- **Engagement-based sending**: campaigns to 30–90d engaged ONLY (not all subscribers)

### Volume & cadence
- 4–8 sends/month/subscriber is the sweet spot for H&B
- **>10 sends/month → unsub rate balloons + complaint rate rises**
- New domain warming: ramp from 1k → 5k → 10k → 25k → full list over 4 weeks

### Critical thresholds (Gmail, Yahoo, Apple)
- Spam complaint rate: warning at **0.1%**, ISP filtering at **0.3%**, blocking at **0.5%**
- Bounce rate: keep < **2%** (target < 1%)
- Open rate trend declining → re-warm engaged segment, pause less-engaged sends

---

## PART 6 — SIGNUP FORMS & UX

- **Form types** (use 2–3 max):
  1. Exit-intent popup (highest conversion, ~5–8%)
  2. Embedded form (footer or "subscribe" page)
  3. Flyout / sliding form (less aggressive)
- **Trigger timing**:
  - Time on page ≥10–15s
  - Scroll % ≥50%
  - Exit intent (mouse leaving viewport)
- **Two-step pattern (NO COUPONS)**: value teaser ("Beat any NZ pharmacy price by 10%") → email field → optional SMS
- **Fields — minimum viable**: just email. Phone optional. Never ask for first name + last name + DOB on first form.
- **Consent**: explicit checkbox for marketing (NZ Privacy Act 2020 + Privacy Amendment Act 2025 compliance)
- **Post-submit**:
  - Show confirmation message + first-email preview ("watch for our welcome email")
  - Set expectation ("watch for 'Bargain Chemist' in your inbox in 5 min")
  - Tag profile with form source (custom property)

---

## PART 7 — SEGMENTATION

### Foundational segments every account needs
1. **Highly engaged 30d** — opened or clicked in last 30 days (campaign target)
2. **Engaged 90d** — broader campaign list
3. **Unengaged 90d+** — for sunset + suppress
4. **First-time buyers (last 30d)** — welcome flow + first-repeat nurture
5. **Repeat buyers (2+ orders)** — VIP messaging
6. **Lapsed customers (no order 120d+)** — winback eligible
7. **High CLV (top 10% predicted)** — VIP / exclusive access
8. **High churn risk + high CLV** — retention priority (highest leverage)
9. **Subscription product buyers** — replenishment
10. **Browsed but didn't purchase (7d)** — browse abandonment

### Anti-patterns
- Hundreds of micro-segments rarely sent to (wasted maintenance, signal-to-noise crushed)
- Demographic segments without behavioural data backing them
- "All subscribers" sends — almost always destroys deliverability

---

## PART 8 — A/B TESTING DISCIPLINE

- **Test ONE variable at a time** — never confound
- **Run 2–4 weeks minimum** — single-day results are noise
- **Match metric to variable**:
  - Subject line → measure open rate
  - Offer → measure conversion / RPR
  - Send time → measure conversion (not opens)
- **Sample size minimum**: ~1,000 recipients per variant for 80% power on small effects
- **Document**: date, variables, winner, lift % — log to `hypotheses.md`

### High-ROI tests to run first (NO COUPONS — see `no-coupon-strategy.md`)
1. Welcome Email 1 subject line: curiosity vs Price Beat callout (~10–15% lift)
2. Abandoned cart Email 1 timing: 1h vs 3h (~15–25% conv lift)
3. Winback levers: free-shipping threshold drop vs new-arrivals vs pharmacist concierge (~10–20% lift)
4. Cart Email 3: free-shipping progress bar vs static threshold reminder
5. Browse abandonment: single product vs multiple options (~5–15% CTR)

---

## PART 9 — MULTI-CHANNEL (Email vs SMS)

- **SMS strengths**: 90%+ open rate, read in 3 min, 3–5× email CTR
- **SMS weaknesses**: intrusive, 160 char limit, requires explicit opt-in
- **When to use SMS in flows**:
  - Abandoned checkout (high-intent, time-sensitive)
  - Back-in-stock alert
  - Flash sale / limited drop
  - Delivery / fulfilment update
- **When NOT to use SMS**:
  - Welcome nurture (too intrusive early)
  - Browse abandonment (too low intent)
  - Educational content (channel mismatch)
- **Cadence**: max 1–2 SMS per customer per day; quiet hours 8am–9pm local
- **LTV lift adding SMS**: +18% (concentrated in first 90 days)

---

## PART 10 — NZ PHARMACY COMPLIANCE (CRITICAL)

### Hard rules
- **Prescription-only medicines (POM)**: NEVER promote in marketing emails. Transactional only ("your prescription is ready").
- **Pharmacy-only medicines**: only promote with pharmacy registration visible + warning disclaimer + pharmacist name
- **Dietary supplements**: structure-function claims only ("supports", "may help", "contributes to") — NEVER therapeutic ("treats", "cures", "prevents")
- **No comparisons to prescription medicines**
- **No fake doctor / authority endorsements**
- **Pharmacy registration number visible in footer** — every email
- **TAPS pre-vetting** ($150–300, 5–10 business days) for major campaigns — strongly recommended

### Mandatory disclaimer for medicine promotions
> "Always read the label and follow directions for use. If symptoms persist, consult your pharmacist or doctor."

### Allowed claim language (supplements)
- ✅ "Supports immune health"
- ✅ "Helps maintain healthy joints"
- ✅ "Contributes to bone health"
- ❌ "Cures colds"
- ❌ "Prevents arthritis"
- ❌ "Clinically proven to treat..."

### Privacy Act 2020 + Amendment 2025
- Explicit consent for marketing (no pre-ticked boxes)
- IPP 3A from May 2026: notify individuals when personal info collected from sources other than themselves (affects Meta Lead Ads, list uploads)
- Easy unsubscribe (one-click compliant)
- Right to access, correct, erase

### Monthly compliance audit
- All promoted products correctly classified
- No therapeutic claims in subject/preview/body
- Disclaimers present
- Registration number + pharmacist name in footer
- Age-gated products (codeine etc.) only sent to verified 18+ segment
- Testimonials free of disease claims

---

## PART 11 — SMART SENDING & QUIET HOURS

- **Smart Sending default**: skip recipients who got an email in last 16 hours. **Keep enabled** for promotional. **Disable** for transactional.
- **Quiet hours**: respect local time; no marketing 9pm–8am Pacific/Auckland for NZ
- **Throttling**: ramp big sends (>50k) over 1–2 hours to avoid ISP rate-limit penalties
- **Send Time Optimisation (STO)**: enable on campaigns to engaged segments

---

## PART 12 — NAMING & ORGANISATION

### Naming conventions (recommended)
- Flows: `[Type] - [Purpose] [v#]` — e.g. `[Welcome] New Subscriber v2`
- Campaigns: `[YYYY-MM-DD] [Type] - [Audience] - [Subject Theme]` — e.g. `2026-05-06 Promo - Engaged30 - Fragrance Clearance`
- Segments: `[Type] - [Definition]` — e.g. `Engaged 30d - All channels`
- Templates: `[Use Case] - [Variant]` — e.g. `Solus Email - Standard`

### Tagging strategy
- One tag set for: channel (email/sms), purpose (promo/lifecycle/transactional), audience (engaged/lapsed/VIP)
- Use tags consistently — they enable cross-flow + cross-campaign reporting

### Archive policy
- Quarterly: archive flows not used in 6 months (reduce UI clutter)
- Templates over 12 months old without use → archive

---

## SOURCES (key)

- Klaviyo official: benchmarks, flow guides, deliverability, design, SMS compliance
- Flowium, Titan Marketing Agency, Omnisend, BS&Co (industry guides)
- Medsafe NZ, Pharmacy Council of NZ, ANZA TAPS (NZ pharmacy compliance)
- RFC 8058 (one-click unsubscribe), Google + Yahoo bulk sender requirements
- NZ Privacy Act 2020 + Privacy Amendment Act 2025

> Detailed sources are in agent transcripts. This file is the distilled action guide. For numbers see `klaviyo-benchmarks.md`. For audit findings see `account-audit-2026-05-06.md`. For prioritised work see `gaps.md`.
