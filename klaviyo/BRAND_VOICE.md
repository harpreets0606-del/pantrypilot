# Bargain Chemist Brand Voice Reference

Source of truth: pattern analysis of **40 sent email campaigns Dec 2025 – May 2026** (live, in-market). Use this as the baseline for all flow audits and template edits. Update when campaign patterns change.

## Sender identity

- `from_label`: **Bargain Chemist**
- `from_email`: **hello@bargainchemist.co.nz**

## Subject line patterns

### Length
- Range observed: 12–80 chars
- Sweet spot: **30–55 chars** (matches CLAUDE.md ~43 avg)
- Sub-30 char subjects are rare and feel under-developed (e.g. "Running low?" — 12 chars)

### Recurring openers (pick one and stay in family)
| Opener | Example |
|---|---|
| `Discover the [brand/range]` | "Discover the Sukin Signature skincare range" |
| `Meet [product/range]` | "Meet the viral Hello Disc" / "Meet the new Trilogy Booster Serums" |
| `[Verb] [benefit], with [brand]` | "Stay sharp through hay fever season, with Telfast" / "Support for women's wellbeing, from Clinicians" / "Burn care made simple, with Burnex" |
| `Your [moment/goal]` | "Your feel-good moment for the weekend" / "Your summer, well prepared" |
| `Introducing [thing]` | "Introducing Me Today CPLX Powder Range" |
| `Get [outcome] with [brand]` | "Get your glow on with the Natio Glow skincare range ✨" |
| `[Outcome statement]` | "Skin that looks like summer, with Le Tan" / "Cheers to your good health (and good prices)!" |

### Emoji rules (verified from sent campaigns)
| Emoji | Use case | Allowed in flows? |
|---|---|---|
| 🚨 | **EXCLUSIVELY Price Smash sale events** | NO — never use in flows |
| ✨ | Skincare / glow / beauty | Yes, sparingly |
| 🎁 | Gifts / Christmas | Seasonal flows only |
| ☀️ / 😎 | Summer / sun-care | Seasonal flows only |
| 🤧 | Allergy / hayfever | Flu/winter wellness flows |
| 🛒 | Shopping / sale | Sales flows |
| 📣 | Announcement | Major launches only |
| 💘 / 💝 | Valentine's | Seasonal only |
| 🎯 / 🔄 | Functional/utility | Avoid — feels promotional, not BC tone |

Frequency: ~30–40% of subjects use emoji. Always purposeful, never decorative.

## Preview text patterns

- **Short**: typically 4–10 words
- **Common moves**:
  - Pricing tease: `[Product], from $X.XX` / `now $X.XX`
  - Pithy benefit: `Smelling good > flowers` / `Your glow, your way` / `Period care, rethought`
  - Stack value: `Stock up, spend less` / `Big brands, big range, big savings`
  - Practical: `February catalogue out now` / `Selected stores open Good Friday`

Avoid: long sentences, repetition of subject, fear hooks ("Last chance!"), exclamation pile-ons.

## Body copy voice

### Tone DNA
- **Warm + descriptive + wellness-coded**: "feel good", "support", "discover", "meet", "your glow", "your routine"
- **Conversational, not corporate**: "in case you're thinking about hitting the shops today", "Thanks, it's Skin Republic ✨"
- **NZ-specific**: "Kiwi", "Auckland", "Aotearoa" cues — never generic global English
- **Brand-led**: features supplier brand prominently; positions BC as the curator/retailer
- **Action verbs for CTAs**: Discover / Shop / Find out more / Meet / Get / Support — **not** "Buy now", "Click here"

### NEVER use
- Fear / anxiety hooks: "Don't miss out", "Last chance", "Running out", "Stock alert", "Expires today"
- Fake urgency: countdown timers, "Only X left!" unless factually backed
- Coupon codes (per CLAUDE.md — banned for Bargain Chemist)
- High-pressure sales language
- Therapeutic claims for restricted products (ASA Code 2025)
- "Click here" CTAs

## Compliance baseline (from in-production templates)

Every BC template observed includes:
1. **Free shipping bar** at the very top: `Free Shipping on Orders over $79*` (red `#7B1523`)
2. **Logo header** with red `#CC1B2A` background
3. **Nav row**: Shop Products / Clearance / Find a Pharmacy / Contact Us
4. **Hero block** with red `#CC1B2A` background + headline
5. **Body content** in 600px-max wrapper
6. **Social row** with TikTok / Facebook / Instagram / LinkedIn icons
7. **Legal block** (red `#FF0031`) with: pricing/RRP disclaimer, "Always read the label, use only as directed", "If symptoms persist, see your healthcare professional", pharmacist-only product disclaimer
8. **Unsubscribe block** (red `#FF0031`) with `{% unsubscribe %}` and `{{ organization.name }} {{ organization.full_address }}`

**This means: every template already has a UEMA/ASA-compliant footer.** The "[COMPLIANCE]" footer my script injected at the bottom of `</body>` is **redundant and breaks the layout** because it sits outside the 600px wrapper `<div>`.

## Brand colors

- Brand red (primary): `#CC1B2A`
- Deep red (accent / shipping bar): `#7B1523`
- Bright red (legal blocks): `#FF0031`
- Body text: `#333333` / `#1a1a1a`
- Muted: `#666666` / `#999999`
- Highlight backgrounds: `#fef6f7` (light pink/cream)

## Klaviyo template syntax

- Variables: `{{ first_name|default:'there' }}` — **double braces required**
- Single braces `{ first_name }` will render literally and ship broken
- Unsubscribe tag: `{% unsubscribe %}` (no quotes) OR `{% unsubscribe 'Unsubscribe' %}` (with link text)
- Org placeholders: `{{ organization.name }}`, `{{ organization.full_address }}`, `{{ organization.homepage }}`
- Event/order data: `{{ event.extra.line_items }}`, `{{ customer.last_order_items }}`

## Trigger timing (industry + BC observed)

| Flow type | Industry-standard delay | Notes |
|---|---|---|
| Abandoned Checkout E1 | 30 min – 1 hr | Speed matters |
| Abandoned Checkout E2 | 24 hr | |
| Abandoned Checkout E3 | 48–72 hr | |
| Added to Cart E1 | 4 hr | |
| Browse Abandonment | 12–24 hr | |
| Welcome E1 | Immediate | |
| Welcome E2 | 2–3 days | |
| Welcome E3 | 5–7 days | |
| Post-Purchase Review | 7–14 days post-delivery | Allow time to actually use |
| Replenishment | **Match product cycle** (30/60/90d) — **NOT 14 days for vitamins** |
| Win-back | 60+ days no engagement | |
| Back in Stock | Real-time on inventory event | |

## Anti-patterns I've already shipped (correct in next round)

1. **Generic `[COMPLIANCE]` footer injected at raw `</body>`** — duplicate of in-template footer + breaks 600px wrapper. Remove + add a "skip if already compliant" check.
2. **Single-brace Django variables** `{ first_name|default:'there' }` — fix to `{{ }}` across all templates that have this bug.
3. **CTAs pointing to homepage** when they should deep-link (e.g. Post-Purchase E1 "Write a Review" → bargainchemist.co.nz, useless).
4. **Replenishment timing of 14 days** — wrong for vitamins (30+ day cycle) and supplements.
5. **Generic "Running low?" subject** — fear-adjacent, doesn't match BC voice.

## How to apply this document

Before editing any template, run through this checklist:

- [ ] Subject 30–55 chars, follows a recurring opener pattern
- [ ] Preview text 4–10 words, pithy or factual
- [ ] No 🚨 unless Price Smash
- [ ] No fear / urgency language
- [ ] No coupon codes
- [ ] All variables `{{ }}` not `{ }`
- [ ] CTA destinations actually work (not homepage)
- [ ] Existing in-template footer present? Don't double-footer
- [ ] Pharmacy-only / restricted SKUs not price-promoted
- [ ] NZ tone (Kiwi-friendly), `$79` free-shipping threshold, NZD currency
- [ ] Trigger timing matches industry standard for the flow type
