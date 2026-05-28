# Bargain Chemist Blogger Playbook

This file is auto-loaded by Claude Code on every session. It is the reusable house style + SEO/GEO/AEO playbook for the Bargain Chemist Wellbeing Hub blog. When the user asks to "write a blog" or "draft a blog post", follow this playbook end-to-end without re-asking the standard questions.

The only questions to ask up front each time are:
1. Blog topic / angle
2. Audience focus (general NZ, parents, seniors, athletes, etc.)
3. Any seasonal or campaign tie-in (e.g. winter immunity, hay fever season)
4. Any specific products or brands to prioritise (otherwise pick from the product map)

Everything else (length, format, tone, schema, structure) defaults to what's in this playbook.

---

## 1. About Bargain Chemist (use for context and E-E-A-T blocks)

- **Business**: New Zealand pharmacy chain + ecommerce on Shopify Plus
- **Positioning**: "New Zealand's Cheapest Chemist" — value, price-beat guarantee
- **Domain**: `https://www.bargainchemist.co.nz`
- **Blog path**: `https://www.bargainchemist.co.nz/blogs/wellbeing-hub/<article-handle>`
- **Country / locale**: New Zealand (NZD, NZ English spelling, NZ Medsafe regulatory context)
- **Author byline for every blog**: "Bargain Chemist Pharmacy Team" (unless user specifies a named pharmacist)

---

## 2. SEO + GEO + AEO Framework

Every blog must be optimised for three layers simultaneously:

### SEO (traditional Google ranking)
- 1 primary keyword + 3–5 secondary keywords identified before writing
- Primary keyword in: H1, first 100 words, meta title, slug, at least one H2, image alt text
- Internal links to at least 3 Bargain Chemist collection pages and 2–4 product pages
- 1–2 outbound authority links to non-competing sources (Ministry of Health NZ, Medsafe, NIH ODS, Cochrane, WHO)
- Image alt text on every visual (descriptive, keyword-aware, never stuffed)
- URL slug: lowercase, hyphenated, max 5 words, primary keyword included

### GEO (Generative Engine Optimisation — for AI Overviews, ChatGPT, Perplexity, Gemini)
- Open with a clear, citation-ready **definition** in section 1 — AI engines love definitional answers
- Use **structured "What / Why / How" patterns** in H2s
- Include at least one **data table or comparison chart** — AI engines extract these into answers
- Cite **named sources inline** (e.g. "According to the NZ Ministry of Health…") — AI engines need named entities, not vague "studies show"
- Use **clear factual statements** in the first sentence of each section (the "topic sentence" pattern)
- Reference **New Zealand specifically** in headings and body (e.g. "in New Zealand", "for Kiwi consumers", "NZ Medsafe") — strengthens geographic relevance for AI engines
- Include a **TL;DR / Key Takeaways** box near the top — directly answers the query in 2–4 sentences

### AEO (Answer Engine Optimisation — Google PAA, voice search, featured snippets)
- Every blog ends with a **FAQ section of 8–12 Q&As** targeting "People Also Ask"
- Every FAQ has **FAQPage JSON-LD schema** embedded at the bottom of the blog body
- Each FAQ answer: 40–60 words, full-sentence, self-contained (no "see above")
- Include 1–2 **how-to lists** (numbered) inside the body — featured-snippet friendly
- Use **question-style H2s** where natural (e.g. "Do detox supplements actually work?")

---

## 3. House Voice & Tone

- **Second person** ("you", "your") — direct, helpful
- **Plain Kiwi English**: NZ spelling (colour, fibre, paediatric, optimise), no Americanisms
- **Pharmacy team voice**: knowledgeable but warm, never preachy
- **Evidence-led but consumer-friendly**: cite studies in plain language ("a 2021 Cochrane review found…" not "the literature suggests…")
- **No hype, no fear-mongering**: balanced, fair, honest about what's proven vs marketed
- **Use "may support" / "may help"** for supplement benefits (NZ regulatory safe)
- **Never claim cure / treat / prevent disease** for supplements (Medsafe / Therapeutic Products compliance)
- **Acknowledge limitations** ("evidence is mixed", "more research needed") — builds trust and AI engines reward this
- Avoid emojis in body content
- Sentence length: vary, but keep most sentences ≤ 25 words for scannability

---

## 4. Standard Blog Structure (long-form pillar, 2,000–3,000 words)

Every blog follows this skeleton:

```
1. Hero
   - H1 (includes primary keyword + year if topical)
   - 1-line subhead (the "promise")
   - TL;DR / Key Takeaways box (3-4 bullets — AEO + GEO gold)
   - Reading time
   - "By Bargain Chemist Pharmacy Team · Reviewed: <month year>"

2. Intro (100-150 words)
   - Hook with a NZ-relevant fact or statistic
   - State what the reader will learn (3 bullets)
   - Define the topic in 1 sentence (GEO ranking signal)

3. Definitional H2: "What is [topic]?"
   - Clear textbook-style definition
   - Inline infographic OR table

4. Context H2: "[Topic] in New Zealand"
   - NZ-specific data or framing
   - Mention Ministry of Health / Medsafe where relevant

5. Evidence H2: "What the science actually says"
   - Sub-section "What works" (with citations)
   - Sub-section "What doesn't work / weak evidence"
   - Bar chart or comparison table (SVG)

6. Buyer's guide H2: "How to choose [product type]"
   - Numbered list of 5 criteria
   - Red flags / what to avoid

7. Product picks H2: "Our pharmacy team's top picks"
   - 4-6 internally-linked product cards
   - Mix of price points (budget / mid / premium)
   - Link to relevant collection page at end of section

8. Lifestyle H2: "Beyond supplements: lifestyle factors that matter"
   - The "boring" evidence-backed advice (sleep, hydration, diet, exercise)

9. Safety H2: "When to talk to a pharmacist or GP"
   - Interactions, contraindications, pregnancy/breastfeeding, kids
   - CTA: "Pop into your local Bargain Chemist and chat to our pharmacy team"

10. FAQ H2: "Frequently asked questions"
    - 8-12 Q&As
    - Each answer 40-60 words

11. Disclaimer + Author block
    - Standard medical disclaimer
    - Bargain Chemist Pharmacy Team byline + brief credentials line

12. FAQPage JSON-LD schema (inside <script type="application/ld+json">)
```

---

## 5. Meta Title & Meta Description Formulas

### Meta title (50-60 chars, keep under 60)
Formulas (pick one):
- `[Primary Keyword]: [Benefit/Hook] | Bargain Chemist NZ`
- `The Truth About [Topic]: [Year] NZ Guide`
- `[Number] [Things] for [Outcome] | NZ Pharmacy Guide`
- `[Topic] in NZ: What Works & What Doesn't ([Year])`

Always include: primary keyword, NZ or "Kiwi" signal, current year if topical.

### Meta description (140-155 chars)
Formula:
`[Hook sentence with primary keyword]. [Value promise — what reader gets]. [Soft CTA / brand mention].`

Example:
`A NZ pharmacist's evidence-based guide to detox supplements. Discover what really works, what doesn't, and how to choose. Shop online or in-store.`

Always include: primary keyword in first 60 chars, NZ-relevant phrasing, soft CTA.

---

## 6. Internal Linking Rules

Every blog must include:
- **At least 3 collection links** (e.g. `/collections/detox-antioxidants`)
- **At least 2 product links** (e.g. `/products/go-healthy-go-liver-detox-1-a-day-60-capsules`)
- **At least 1 internal blog link** (link to another Wellbeing Hub article when relevant)
- Use descriptive anchor text, never "click here" or "this product"

### Public-facing collection map (most useful for blog linking)

Use these collection handles — they are confirmed live on the site:

**Concern / Category collections**
- `/collections/vitamins-supplements` — Vitamins & Supplements (1,783 products)
- `/collections/detox-antioxidants` — Antioxidant / Detox (21 products) ⭐ best detox/cleanse anchor
- `/collections/immunity` — Immune Support (136 products)
- `/collections/energy` — Energy, Sleep & Fatigue (134 products)
- `/collections/multivitamins` — Multivitamin Supplements (87 products)
- `/collections/weight-loss` — Weight Loss (112 products)
- `/collections/sleep-stress-anxiety` — Sleep, Stress & Anxiety
- `/collections/heart-circulation` — Heart & Circulation (43 products)
- `/collections/bone-joint-health` — Bone Health (17 products)
- `/collections/eye-health` — Eye Health Supplements (19 products)
- `/collections/menopause` — Menopause (11 products)
- `/collections/mens-health` — Men's Health (37 products)
- `/collections/mum-health` — Mum Health (37 products)
- `/collections/childrens-health` — Children's Health (132 products)
- `/collections/mother-baby` — Mother & Baby (545 products)
- `/collections/allergies-hay-fever-sinus` — Allergies, Hayfever & Sinus (78 products)
- `/collections/cold-flu` — Cold & Flu Medication (186 products)
- `/collections/stomach-bowel-treatments` — Stomach & Bowel Treatments (75 products)
- `/collections/skin-care` — Skin Care (1,070 products)
- `/collections/sun-care` — Sun Care (112 products)
- `/collections/first-aid` — First Aid (337 products)

**Brand collections (use for ingredient/brand-focused posts)**
- `/collections/clinicians` (99 products)
- `/collections/blackmores` (82 products)
- `/collections/good-health` — Good Health Supplements (135 products)
- `/collections/nutralife` — Nutra-Life Supplements (82 products)
- `/collections/thompsons` — Thompson's (59 products)
- `/collections/natures-way` — Nature's Way Supplements (82 products)
- `/collections/radiance` (71 products)
- `/collections/sanderson` (73 products)
- `/collections/elevit` (12 products)
- `/collections/inner-health` (46 products)
- `/collections/optislim` — Weight Loss (72 products)
- `/collections/balance` — Sports Nutrition (25 products)
- `/collections/codral` (20 products)
- `/collections/nurofen` (34 products)
- `/collections/trilogy` (74 products)

### Reference blog posts to link to (existing Wellbeing Hub articles)
- `/blogs/wellbeing-hub/the-miracle-of-magnesium`
- `/blogs/wellbeing-hub/joint-health`
- `/blogs/wellbeing-hub/pain-relief-the-best-treatment-for-your-pain`
- `/blogs/wellbeing-hub/antihistamines`
- `/blogs/wellbeing-hub/epipens-the-ultimate-guide`

---

## 7. Visuals Standard

Every long-form pillar blog must include **at least 3 visuals**:
1. **One hero/section infographic** — pure HTML/CSS divs, no external images needed. Used for "how it works" diagrams (e.g. "How your body detoxes").
2. **One SVG chart** — inline SVG (bar or pie), embedded directly in HTML. Renders as an image in Shopify when pasted.
3. **One comparison table or "claim vs evidence" infographic** — styled HTML divs.

Visual rules:
- All inline SVG — no external image URLs (so blog stays self-contained, no broken images)
- Brand palette: deep blue `#0d3b66`, accent orange `#ee964b`, neutral background `#f6f7fb`, success green `#06a77d`, alert red `#d62828`, text `#1f2937`
- Every visual has `<figcaption>` with a 1-line description (SEO + accessibility)
- Every SVG includes `<title>` and `<desc>` tags inside for accessibility / SEO

---

## 8. Citation Standard (for GEO — AI engines need named sources)

Acceptable inline citation sources (these carry weight with AI engines):
- **NZ Ministry of Health** (`health.govt.nz`)
- **Medsafe NZ** (`medsafe.govt.nz`)
- **Pharmac NZ**
- **NIH Office of Dietary Supplements** (`ods.od.nih.gov`)
- **Cochrane Library** (`cochranelibrary.com`)
- **World Health Organization** (`who.int`)
- **NHS UK** (`nhs.uk`)
- **Peer-reviewed journals**: BMJ, Lancet, NEJM, Cochrane Reviews, JAMA
- **Specific year + source pattern**: "A 2021 Cochrane review of 18 trials found…"

Avoid citing: Wikipedia, blogs, supplement brand sites, "studies show" without naming the study.

Outbound links: open in same tab, no `rel="nofollow"` for authority sources.

---

## 9. Regulatory & Safety Compliance (NZ pharmacy)

- **Never claim** a supplement cures, treats or prevents any disease
- **Use approved phrasing**: "may support", "may help maintain", "traditionally used for"
- **Always include** a medical disclaimer footer
- **For OTC medicines**: state active ingredient, indication only as per Medsafe data sheet
- **Pregnancy/breastfeeding**: always flag a "talk to your pharmacist first" caveat
- **Children**: always flag age-appropriate dosing / consult pharmacist
- **Drug interactions**: mention category-level warnings (e.g. "if you take blood thinners…")

Standard disclaimer (paste at bottom of every blog):

> **Disclaimer**: This article is for general information only and is not intended as medical advice. The information here does not replace advice from a registered pharmacist, GP or other healthcare professional. Always read the label, use only as directed, and consult your healthcare provider before starting any new supplement — especially if you are pregnant, breastfeeding, on prescription medication, or managing a health condition. If symptoms persist, see your healthcare professional.

---

## 10. Author E-E-A-T Block (paste at bottom of every blog)

```html
<div class="bc-author-block">
  <strong>About the Bargain Chemist Pharmacy Team</strong><br>
  Our content is written and reviewed by Bargain Chemist's New Zealand-registered pharmacists and pharmacy team. We combine evidence from peer-reviewed research, NZ Ministry of Health and Medsafe guidance, and our day-to-day experience helping Kiwi families look after their health. Have a question? Visit us in-store or message our team via <a href="https://www.bargainchemist.co.nz/pages/contact">bargainchemist.co.nz/pages/contact</a>.
</div>
```

---

## 11. FAQ + Schema Standard

Every blog ends with a FAQ section (8–12 questions) AND a `<script type="application/ld+json">` block containing `FAQPage` schema with all the same Q&As. The schema must be valid JSON — Q&As inside the schema must match the visible Q&As exactly (Google penalises mismatch).

Schema template:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "QUESTION HERE",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ANSWER HERE (plain text, no HTML)"
      }
    }
  ]
}
</script>
```

Also recommended: add `Article` schema at the top of the page. Template:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "ARTICLE H1",
  "description": "META DESCRIPTION",
  "author": {
    "@type": "Organization",
    "name": "Bargain Chemist Pharmacy Team",
    "url": "https://www.bargainchemist.co.nz"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Bargain Chemist",
    "logo": {
      "@type": "ImageObject",
      "url": "https://www.bargainchemist.co.nz/cdn/shop/files/logo.png"
    }
  },
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "mainEntityOfPage": "https://www.bargainchemist.co.nz/blogs/wellbeing-hub/SLUG"
}
</script>
```

---

## 12. Deliverables per Blog

Each blog produces **two files** in `/blogs/`:

1. **`<slug>.html`** — single self-contained HTML file. User pastes the body into Shopify's blog editor (HTML view). Contains: full article body, inline SVG charts, infographic divs, FAQ section, and both JSON-LD schema blocks.

2. **`<slug>.meta.md`** — the SEO brief. Contains:
   - Meta title (with character count)
   - Meta description (with character count)
   - URL slug
   - Primary keyword + secondary keywords
   - Featured image brief (subject, alt text, suggested dimensions)
   - Internal link map (every collection + product link used)
   - Outbound citation list
   - Suggested social share copy (1 line for FB, 1 for Insta, 1 for LinkedIn)

---

## 13. Workflow When User Asks for a New Blog

1. Confirm topic, audience, season, products to feature (4 questions max)
2. Search Shopify for relevant products via `mcp__f4ea65a1-be91-4e1a-ab91-fe78027d6605__search_products` or `graphql_query` (filter by `status:active`)
3. Confirm collection handles from section 6 above
4. Draft both files (`<slug>.html` and `<slug>.meta.md`) in `/blogs/`
5. Commit on the branch specified in the session instructions and push
6. Report back: file paths, meta title, meta description, slug, and a 1-line summary of internal links used
