# Bargain Chemist — Brand Voice & Design Template (v1.0 LOCKED)

**Date**: 2026-05-07
**Status**: v1.0 LOCKED — based on actual flow templates pulled via API. Visual + voice now confirmed from real artefacts, not inference.

---

## CANONICAL BRAND VOICE (gold standard)

The strongest brand voice example in the account is **Welcome No Coupon Email 1** (UC2XAR). Treat it as the template every other email should aspire to:

> "Welcome to Bargain Chemist, {{ first_name|default:'there' }}!"
> 
> "You've just joined NZ's most trusted pharmacy family."
> 
> "Hi {{ first_name|default:'there' }}, Thanks for signing up to Bargain Chemist. Whether you're after vitamins, skincare, haircare, baby products, or everyday essentials — we've got you covered with NZ's lowest prices."
> 
> "And our promise is simple: we'll beat any pharmacy price in New Zealand by 10%. So you always get the best deal, every time."
> 
> "🏆 Price Beat Guarantee · Beat any NZ pharmacy price by 10%
> 🚚 Free Shipping · On all orders over $79
> 💊 Expert..."

### Why this works
- Personalised greeting (uses Liquid)
- "NZ's most trusted pharmacy family" — community-led, not transactional
- Plain-spoken value props (vitamins, skincare, haircare — not "wellness solutions")
- Promise format: "And our promise is simple..."
- Three icons: Price Beat / Free Ship / Expert. Consistent triad.
- Tone: confident, friendly, NZ-pride, no corporate fluff

### Voice attributes (locked)

| Attribute | Description | Don't |
|-----------|-------------|-------|
| **Tone** | Friendly, plain-spoken NZ pharmacy. Confident not boastful. | Corporate, clinical, salesy |
| **Pace** | Short sentences. Active verbs. | Long compound sentences |
| **POV** | "We" + "you". Personalised first names. | Third-person ("the company"), "customers should" |
| **Vocabulary** | Kiwi vernacular (Kiwis, locals, family, pharmacy). Plain English. | Medical jargon, internal acronyms (EDLP) |
| **Numbers** | Specific ($79, 10%). | Vague ("great savings") |
| **Humour** | Light, occasional. | Forced cleverness |
| **Authority** | "Pharmacy team is friendly, knowledgeable" | Doctor-claim, prescription-comparison |

### Required value props (use one + per email)
1. **NZ's cheapest chemist** OR **NZ's most trusted pharmacy family**
2. **100% Kiwi-owned**
3. **Price Beat Guarantee — Beat any NZ pharmacy price by 10%**
4. **Free Shipping on orders $79+** (NZ urban)
5. **Click & Collect** at Bargain Chemist locations NZ-wide
6. **Expert advice** from in-store pharmacists

### Subject line patterns that work (from actual flow data)

| Pattern | Example (real, from Bargain Chemist) |
|---------|---------------------------------------|
| Personalised welcome | "Welcome to Bargain Chemist, {{ first_name\|default:'there' }}!" |
| Personalised confirmation | "{{ person.first_name\|default:'friend' }}, order confirmed!" |
| Curiosity hook | "This one's popular for a reason" |
| Direct + helpful | "Your cart's still saved" |
| Social proof | "See What Others Are Raving About 👇" |
| Local-leaning | "Your Local Bargain Chemist is Ready to Help 👋" |

> **Use Klaviyo Liquid for personalisation in subject lines**: `{{ first_name|default:'there' }}` (default fallback when name unknown).

### Subject line patterns to fix

| Pattern | Real example | Why it's weak | Replace with |
|---------|--------------|----------------|--------------|
| Generic "thanks for signing up" | "Thanks for signing up to Bargain Chemist!" | Doesn't lead with positioning | "Welcome to Bargain Chemist, {{ first_name\|default:'there' }}!" |
| Internal jargon | "...up to 30% Off EDLP!" | EDLP = Everyday Low Price (internal) | "...up to 30% Off everyday prices!" |
| Empty preview | (Nicorette Solus had empty preview) | Wasted real estate | Always fill — extend the subject |

---

## VISUAL DESIGN — LOCKED FROM TEMPLATES

### Brand colours (from actual flow templates)

| Role | Hex | Used in |
|------|-----|---------|
| **Primary CTA / hero** | `#FF0031` | Almost every template — vivid red |
| **Deep brand accent** | `#7B1523` | Order Confirmation header bar |
| **Brand red mid** | `#CC1B2A` | Order Confirmation buttons |
| **Older brand burgundy** | `#861628` | Older Welcome + Cart templates (legacy) |
| **Body text dark** | `#222222` | Every template |
| **Body text mid** | `#333333` | Newer templates |
| **Body text muted** | `#666666` | Newer templates |
| **Border / divider** | `#eeeeee` | Newer templates |
| **Page background** | `#f7f7f7` / `#f9f9f9` | Most templates |
| **Promo accent (light)** | `#FDDDD9` (older), `#fef6f7` (newer) | Welcome 1, Order Confirmation |

> **Recommendation**: lock primary brand red to **`#FF0031`** (vivid) for CTAs and **`#7B1523`** (deep) for header bars. Phase out `#861628` from older templates as part of the rebuild.

### Fonts

- Older templates: heavy mix — `'Arial Black'`, `'Arial Bold'`, `Helvetica`, `Ubuntu`, multiple variants
- **Newer templates** (Welcome No Coupon, Order Confirmation): consolidated to `Helvetica, Arial, sans-serif` — cleaner

> **Recommendation**: standardise all flows + campaigns on `Helvetica, Arial, sans-serif` (already in newer templates).

### Logo

- Older templates: cloudfront-hosted Klaviyo image — generic
- Newer Order Confirmation: `https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218` — branded "logo-2025"

> **Recommendation**: use the Shopify-hosted `logo-2025.png` everywhere. Update older templates.

### Header navigation (consistent in every template)

```
Free Shipping on Orders over $79*
Shop Products | Clearance | Find a Pharmacy | Contact Us
```

### Social links (consistent — confirmed)

- Instagram: `https://instagram.com/bargainchemistnz`
- LinkedIn: `https://nz.linkedin.com/company/bargain-chemist`
- Facebook: `https://www.facebook.com/BargainChemist/`
- TikTok: `https://tiktok.com/@bargainchemistnz` *(only in newer templates)*

### Common collection links used in flows

```
/collections/clearance-deals      ← clearance
/collections/best-selling-collection ← best sellers
/collections/cold-flu             ← seasonal (winter)
/collections/allergies-hay-fever-sinus ← seasonal (spring)
/collections/fragrances           ← gift / beauty
/collections/home-household       ← household
/collections/all                  ← shop all
/pages/best-price-guarantee-our-policy-new-zealands-cheapest-chemist  ← price beat page
/pages/find-a-store               ← store locator
```

---

## TWO TEMPLATE FAMILIES — IMPORTANT

The pulled flow messages reveal **two distinct template generations**:

### Family A — "Older" (legacy, 2026-03 era)
- Files: Welcome Email 1 (87KB), Welcome Email 2 (93KB), Welcome Email 6 (52KB), Cart Email 1 (66KB), Cart Email 2 (67KB)
- Heavy HTML (50-100KB each)
- Mixed fonts (`Arial Black`, `Arial Bold`, `Ubuntu`, etc.)
- Dual-red palette: `#FF0031` + `#861628` (legacy burgundy)
- Cloudfront-hosted images
- Created early-mid 2026

### Family B — "Newer" (rebuild, 2026-05 era)
- Files: Welcome No Coupon Email 1 (9KB), Order Confirmation Email 1 (12KB)
- Lean HTML (~10KB each — **5–10× smaller**)
- Single font stack (`Helvetica, Arial, sans-serif`)
- Cleaner red palette: `#FF0031` + `#7B1523`/`#CC1B2A`
- Shopify-hosted `logo-2025.png`
- Created 2026-05-05

### Implication

The newer templates are objectively better:
- Lean HTML = faster loading on mobile
- Single font stack = consistent rendering across email clients
- Updated logo + cleaner palette = on-brand for 2026
- **Welcome Series Website is in DRAFT because it still uses Family A** while the team has been migrating to Family B (Welcome No Coupon + Order Confirmation are Family B)

> **Recommendation**: complete the rebuild — port all flow templates to Family B style. The current draft state of Welcome Series Website is actually a transition-in-progress.

---

## COMPLIANCE — WHAT'S IN, WHAT'S MISSING

### Currently in EVERY flow template ✓
- Medicine disclaimer language ("always read the label / symptoms persist / consult your pharmacist or doctor")
- Free shipping $79+ messaging
- Price Beat Guarantee mention
- Klaviyo `{% unsubscribe %}` link

### Missing from EVERY flow template 🚨
- **Pharmacy registration number** — Medsafe requirement for medicine-promoting emails
- **Pharmacist name** disclosed — required when promoting medicines

### Inconsistent across templates ⚠️
- "100% Kiwi-owned" mention — only 1 of 7 templates says it explicitly (Welcome Email 1)
- Footer full address ("1 Radcliffe Road, Christchurch") — only 3 of 7 templates display it (relying on Klaviyo's `{{ organization.full_address }}` macro which may not render in all contexts)

### Confirmed clean ✓
- No POM brand names (Wegovy, Mounjaro, Ozempic, etc.) anywhere in flow body content
- No pharmacy-only brand names (Codral, Sudafed) in flow content
- No therapeutic claims (treats/cures/prevents)

> **Action**: build a "compliance footer block" with pharmacy registration # + pharmacist name + full address + medicine disclaimer. Insert as Klaviyo Universal Content block in every template.

---

## TEMPLATE STRUCTURE (recommended, derived from newer templates)

Match the Family B structure:

```
┌─────────────────────────────────────┐
│ TOP STRIP                           │
│ "Free Shipping on Orders over $79*"│
└─────────────────────────────────────┘
│ HEADER                              │
│ Logo (Shopify logo-2025.png)        │
│ Nav: Shop / Clearance / Find a      │
│      Pharmacy / Contact Us          │
└─────────────────────────────────────┘
│ HERO                                │
│ One image OR coloured panel         │
│ Headline (24-28px, brand red)       │
│ Sub-headline (16-18px, dark grey)   │
│ Primary CTA button (#FF0031, white) │
└─────────────────────────────────────┘
│ BODY                                │
│ Greeting with {{ first_name }}     │
│ Short personal copy                 │
│ Optional: 3 product blocks OR      │
│           1 content section         │
│ Single secondary CTA                │
└─────────────────────────────────────┘
│ VALUE PROPS STRIP (3 icons)        │
│ 🏆 Price Beat 10% │ 🚚 Free $79+ │ │
│ 💊 Expert Advice                    │
└─────────────────────────────────────┘
│ FOOTER (compliance + social)       │
│ - Bargain Chemist                  │
│ - 1 Radcliffe Road, Christchurch   │
│ - Pharmacy Registration #: <TBD>   │
│ - Lead Pharmacist: <Name TBD>      │
│ - Always read the label disclaimer │
│ - Unsubscribe (one-click)          │
│ - Manage preferences               │
│ - Social: IG / FB / LinkedIn / TikTok │
└─────────────────────────────────────┘
```

### Specs

| Element | Spec |
|---------|------|
| Email width | 600px desktop / responsive ≤480px mobile |
| Body font | 14-16px Helvetica/Arial/sans-serif, line height 1.5 |
| Headline | 22-28px, `#FF0031` or `#7B1523` |
| Body text | `#222222` heading, `#333333` body, `#666666` muted |
| CTA button | Background `#FF0031`, text `#FFFFFF`, padding ≥12px, min 44×44px tap target, border-radius 4-6px |
| Image:text ratio | 60% text / 40% image (avoid all-image emails) |
| Alt text | every image, descriptive |
| Logo | `https://cdn.shopify.com/s/files/1/0317/1926/0297/files/logo-2025.png?v=1747706218` (Shopify-hosted) |

---

## STILL UNKNOWN (need user)

- **Pharmacy registration number** (for footer compliance)
- **Lead pharmacist name** (for medicine email footer)
- Exact form-factor of value-props icon strip (text icons 🏆🚚💊 vs custom images)
- Whether Family B template structure was AI-generated or designer-created (parallel agent's work?)

> Update those above as known and this v1.0 graduates to v1.1 with full compliance baseline.
