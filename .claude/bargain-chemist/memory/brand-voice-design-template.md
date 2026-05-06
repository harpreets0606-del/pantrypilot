# Bargain Chemist — Brand Voice & Design Template (DRAFT)

> **Status: DRAFT — needs user confirmation.**
> Inferred from 12 campaign subject + preview samples (Aug 2025 – May 2026). Email template HTML was inaccessible via API (Klaviyo MCP returned 401 for `klaviyo_get_email_template`), so visual design language is unobserved. **Do not treat this as locked-in until user confirms.**

---

## EVIDENCE BASE

### Sample subject lines + preview text (12 campaigns)

| # | Campaign | Subject | Preview |
|---|----------|---------|---------|
| 1 | Fragrance Clearance May 2026 | Fragrance finds. Clearance prices. 🚨 | Lots online. Limited in-store. |
| 2 | Trilogy Solus April 2026 | Meet the new Trilogy Booster Serums | Targeted serums for your skin goals |
| 3 | Christmas Gifting 1 Dec 2025 | Nice gifts. Nicer prices. | Gift ideas perfect for stockings, Secret Santas, and everything in between. |
| 4 | Black Friday First Day Nov 2025 | 🚨 Huge Black Friday Sale Starts Today! 🚨 | 8 days only! Shop now! |
| 5 | Black Friday Last Day Nov 2025 | Last Chance to Shop our Black Friday Bargains! ⏳ | Don't miss out! Sale ends midnight. |
| 6 | Codral Solus Aug 2025 | Kiwis have an ally in fighting cold & flu symptoms with Codral & Sudafed | Buy it in-store now! |
| 7 | Mums & Bubs Sept 2025 | Shop our wide range of Mums & Bubs deals before they go! | Save up to 35% off EDLP! |
| 8 | New Year Deals 1 Jan 2026 | Cheers to your good health (and good prices)! | January catalogue out now |
| 9 | Father's Day EDM Sept 2025 | Haven't got a gift for Father's Day yet? 👨 | We've got you covered! |
| 10 | Bonus Box Oct 2025 | FREE Bonus Box When You Spend $99 In Store! | Limited time only don't miss out! |
| 11 | Price Smash Sports Aug 2025 | Performance fuel with up to 30% Off EDLP! | Shop your favourite fitness brands now! |
| 12 | Nicorette Solus Jan 2026 | Get ready to quit smoking with Nicorette | (empty) |

### Sender configuration observed
- **Sender label**: "Bargain Chemist" — consistent across all 12 ✓
- **Sender email**: split between `hello@bargainchemist.co.nz` AND `orders@bargainchemist.co.nz` — **inconsistent**
- **Reply-to**: never set
- **Smart Sending**: enabled on all sampled campaigns ✓

---

## INFERRED BRAND VOICE (DRAFT — confirm with user)

### Personality
- **Friendly value-led NZ pharmacy**
- Practical, accessible, anti-pretentious
- Strong on price/savings narrative
- Health-first but not clinical
- Lighthearted humour acceptable ("Cheers to your good health (and good prices)!")
- Uses NZ vernacular ("Kiwis", "in-store", "Mums & Bubs", "EDM")

### Tone (varies by context)
| Context | Tone |
|---------|------|
| Promotional / sale | Urgent, punchy, exclamation-led |
| Brand product launch (Solus) | Informative + benefit-led |
| Seasonal (Christmas, Father's Day) | Warm, conversational |
| Health / cold + flu | Reassuring, kiwi-vernacular |

### Recurring rhetorical devices
1. **Parallel structure** — short paired clauses
   - "Nice gifts. Nicer prices."
   - "Fragrance finds. Clearance prices."
   - "Lots online. Limited in-store."
   - → **This is the strongest brand pattern.** Use it more.
2. **Question hooks** — "Haven't got a gift for Father's Day yet?"
3. **Urgency phrases** — "Last Chance", "before they go", "Limited time", "Today only", "8 days only"
4. **Value anchors** — "Bargain", "deals", "Save up to X%", "FREE", "Off"
5. **NZ vernacular** — "Kiwis", "EDM" (electronic direct mail), "Mums & Bubs"

### Words to use
- Bargain, deal, save, prices, finds, picks
- Shop, grab, snag, score
- Kiwi, NZ, in-store, online
- Welcome, cheers, fancy

### Words to avoid (inferred + compliance)
- Clinical: "diagnose", "cure", "treat", "proven to..."
- Boastful: "best in NZ", "guaranteed", "world-class"
- Spam triggers: ALL CAPS subject lines, multiple !!!, "100% free"
- Pharmacy-jargon leaks: **"EDLP"** (everyday low price — internal jargon, customers don't know this)

---

## DESIGN TEMPLATE (TO BUILD — visual unverified)

> **API didn't allow template HTML read.** This template structure is recommended best practice for Bargain Chemist's positioning, NOT observed from existing templates. User to confirm whether existing templates already follow this structure.

### Universal email blocks Bargain Chemist should standardise

```
┌─────────────────────────────────────┐
│ HEADER                              │
│ - Logo (left, 120-180px wide)      │
│ - Nav: Shop / Vitamins / Skincare / │
│   Account (max 4 links)            │
│ - "Find a store" link               │
└─────────────────────────────────────┘
│ HERO BLOCK                          │
│ - 1 image (600×400px max)          │
│ - 1 headline (parallel structure)  │
│ - 1 sub-headline                    │
│ - 1 primary CTA button              │
└─────────────────────────────────────┘
│ BODY                                │
│ - Up to 3 product blocks OR        │
│   1 content section                │
└─────────────────────────────────────┘
│ SOCIAL PROOF                        │
│ - Review snippet OR                │
│ - "Trusted by NZ since [year]"     │
└─────────────────────────────────────┘
│ SECONDARY CTA                       │
│ - "Find your local store" OR       │
│ - "Shop by category"                │
└─────────────────────────────────────┘
│ FOOTER (compliance — mandatory)    │
│ - Bargain Chemist                  │
│ - 1 Radcliffe Road, Belfast,       │
│   Christchurch 8051                │
│ - Pharmacy registration number     │
│ - Pharmacist name (medicine emails)│
│ - Unsubscribe (one-click)          │
│ - Manage preferences               │
│ - Privacy policy                   │
│ - Social links                     │
└─────────────────────────────────────┘
```

### Design specs (recommended)

| Element | Spec |
|---------|------|
| Email width | 600px desktop / responsive ≤480px mobile |
| Body font | 14–16px, line height 1.4–1.6 |
| Headline font | 22–28px |
| Button | 44×44px tap target min, ≥12px padding, brand colour |
| Image-to-text ratio | 60% text / 40% image (avoid all-image emails) |
| Alt text | every image, descriptive |
| Dark mode | logos + transparent PNGs tested |

### Colour palette (TO BE CONFIRMED)
- Primary brand colour: ?
- Accent colour: ?
- Sale / urgency colour: ?
- Body text: dark grey (#222) — never pure black (jarring on dark mode)

> **Action**: pull current website CSS / brand guide to lock these.

---

## SUBJECT LINE & PREVIEW TEXT TEMPLATE

### Subject line formulas to use

1. **Parallel two-clause** (Bargain Chemist's strongest pattern):
   - "[Noun phrase]. [Noun phrase]."
   - e.g. "Skin saviours. Sale prices." / "Winter must-haves. Mid-season prices."
2. **Question hook** (use sparingly, only when warm/seasonal):
   - "Need [X] for [occasion]?"
3. **Urgency + value**:
   - "[Last Chance / Today only]: [Value statement]"
4. **NZ-led brand-product reveal** (Solus campaigns):
   - "Meet the new [brand] [product]"
   - "Kiwis love [product] — here's why"

### Subject line rules
- 30–50 chars target (current range 17–72 — too variable)
- 1 emoji max if used; place at start OR end consistently (don't bracket)
- Never ALL CAPS in subject (one-time emphasis word OK: "FREE")
- No more than 1 exclamation mark

### Preview text rules
- ALWAYS fill it (Nicorette had empty — wasted real estate)
- 40–130 chars
- **Don't repeat the subject** — extend or reinforce
- Include CTA-relevant detail: timeframe, value, exclusivity
- Bad: "Buy it in-store now!" (Codral) — generic
- Good: "Free NZ-wide shipping over $50 ends midnight Sunday."

### Sender address policy
- **All marketing emails**: from `hello@bargainchemist.co.nz` (or a new `marketing@`)
- **All transactional emails (order confirmations, shipping)**: from `orders@bargainchemist.co.nz`
- **Never mix** — currently mixed in marketing campaigns. Fix this.

---

## CONTENT FRAMEWORKS (for body copy)

### When to use which framework
| Scenario | Framework | Example |
|----------|-----------|---------|
| Promo / sale | **PAS** (Problem-Agitate-Solution) | "Cold + flu hitting your house? It only gets worse if untreated. Codral + Sudafed deliver fast relief — at bargain prices." |
| Education / info | **AIDA** (Attention-Interest-Desire-Action) | New product launches |
| Repeat / value reinforcement | **Before-After-Bridge** | Replenishment flows |
| Lifestyle / brand-led | **Story-led** | Welcome series Email 2 |

### Always-include checklist for body copy
- [ ] One primary message (not 3)
- [ ] One primary CTA
- [ ] Mobile-readable (no walls of text)
- [ ] Brand voice (parallel structure where possible)
- [ ] Compliance disclaimer (if medicine promo)
- [ ] Pharmacist name + registration in footer
- [ ] Social proof somewhere

---

## OUTSTANDING UNKNOWNS (need user confirmation)

I cannot finalise this template without:

1. **Visual design language** — colours, typography, logo treatment, image style. (API blocked from reading template HTML.)
2. **Existing templates** — are they already using a consistent block structure?
3. **Brand voice intent** — is the casual + value-led tone deliberate, or accidental drift across writers?
4. **Sender domain decision** — `hello@` vs `marketing@` vs `mail.bargainchemist.co.nz`?
5. **Compliance baseline** — do current emails include pharmacy registration + pharmacist name + medicine disclaimers? (Couldn't verify — need template HTML.)
6. **NZ market positioning** — "bargain" pharmacy implies budget-conscious. Is this the brand strategy or just a name? Affects whether we lean further into value or rebalance toward quality/care.

---

**Until those are answered, treat this file as Draft v0.1.** Once confirmed I'll log the decision in `decisions-log.md`.
