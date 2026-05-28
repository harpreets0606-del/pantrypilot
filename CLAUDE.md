# Bargain Chemist Blogger Playbook (v2 — research-validated)

This file auto-loads every Claude Code session. It is the durable house style + SEO/GEO/AEO operations manual for the Bargain Chemist Wellbeing Hub blog. Validated against 2025–2026 best practices, NZ regulatory framework, and live NZ SERP competitor analysis (May 2026).

When the user asks to "write a blog", follow this playbook end-to-end and ask **only** these four questions up front:

1. Topic and angle
2. Audience focus (general NZ, parents, seniors, athletes)
3. Seasonal or campaign tie-in
4. Specific products or brands to prioritise (otherwise pick from `/research/` dossiers + live Shopify search)

Everything else (length, tone, schema, structure, citations approach) defaults to what is in this playbook.

---

## 1. About Bargain Chemist (context for every blog)

- **Business**: NZ pharmacy chain + Shopify Plus ecommerce
- **Positioning**: "New Zealand's Cheapest Chemist" — price-beat guarantee, value-led
- **Domain**: `https://www.bargainchemist.co.nz`
- **Blog path**: `https://www.bargainchemist.co.nz/blogs/wellbeing-hub/<article-handle>`
- **Locale**: New Zealand (NZD, NZ English spelling, NZ Medsafe/MoH/ASA regulatory framework)
- **Standard byline**: "Bargain Chemist Pharmacy Team" — unless the user names a registered NZ pharmacist as the lead author
- **Standard reviewer line**: every blog includes a visible "Medically reviewed by [Name, role] on [date]" line at the top (required for YMYL E-E-A-T after Dec 2025 Core Update)

---

## 2. SEO + GEO + AEO Framework (2025–26 validated)

### 2.1 SEO — current Google ranking factors for YMYL health
- **Sept 2025 SQRG update**: low-effort AI-generated or paraphrased content is now explicitly classified "lowest quality". AI-assisted drafting must always have a human + clinician editorial layer.
- **Dec 2025 Core Update**: ~67% of YMYL health pages lacking physician/pharmacist authorship lost rankings on symptom/treatment queries.
- **Trust** is the dominant E-E-A-T pillar for YMYL: transparent contact, NZ physical pharmacy address, editorial policy page, reviewer policy.
- **Experience** is weighted on par with credentials — include real pharmacy-counter examples / NZ-specific scenarios.
- Targets per post: primary keyword in H1, slug, first 100 words, one H2, image alt; 10–15 contextual internal links; ≥3 inline NZ-first citations; ≥1 product or collection link; ≥2 related-blog links.

### 2.2 GEO — Princeton 2024 + 2025–26 industry data
- **Statistics with named source** → +41% AI Overview visibility
- **Direct quotes from named experts** → +28% on subjective impression metrics
- **Inline source citation** → up to +115% visibility for lower-ranked pages
- **Fluency + authoritative declarative voice** are in the top 5 tactics
- **55% of AI Overview citations are pulled from the top 30% of a page** — front-load the direct answer in the first 100–150 words
- **Content <3 months old is ~3× more likely to be cited** — refresh every 90–120 days; substantive update, not date-bump
- **Multi-modal pages (text + image + video + table) show +156% AI selection rate**
- **YouTube is the most-cited AIO domain (+34% in 6 months)** — embed a short explainer or include a video transcript where relevant

### 2.3 AEO — Answer Engines + voice + Google PAA
- Pose at least 4–6 H2/H3s as natural questions ("Does milk thistle actually work?")
- Direct answer in ≤55 words immediately below each question heading (featured-snippet and voice-search target)
- FAQ section at the end: 8–12 Q&As, each Q an H3, each A 40–60 words
- FAQPage JSON-LD schema for every post — Google removed FAQ rich results in May 2026 but LLMs (ChatGPT, Perplexity, Gemini, Claude, Copilot) still parse the schema
- Match real "People Also Ask" phrasing — research before writing (see workflow section 12)

### 2.4 LLM-specific source biases (use when prioritising)
- ChatGPT favours Wikipedia (~48% of citations)
- Perplexity favours Reddit (~47%) and real-time news
- Claude favours bulleted/tabular structure (+30% citation likelihood) → use bullets and tables generously
- Gemini overlaps ~54% with Google organic
- **Implication for our blog**: maintain bullet + table structure (Claude), seed authoritative NZ entity references (all engines), front-load the answer (all engines)

---

## 3. House Voice & Tone (NZ pharmacy)

- **Second person** ("you", "your") — direct, helpful, pharmacy-counter tone
- **Plain Kiwi English** with NZ spelling (colour, fibre, paediatric, optimise)
- **Evidence-led but consumer-friendly**: "A 2024 Cureus review of silymarin found…" not "studies suggest…"
- **Compliant supplement phrasing**: "may support healthy liver function", "traditionally used to support digestion", "contains evidence-backed silymarin at a clinically studied dose" — focus on the ingredient + the evidence, NOT the disease + the cure
- **Acknowledge limitations** ("evidence is mixed", "the Cochrane review found insufficient evidence") — builds trust + AI engines reward this
- Avoid emojis in body content
- Sentence length: vary, keep most ≤ 25 words for scannability
- Use **declarative, authoritative voice** (Princeton GEO finding) — fewer "might possibly maybes"; clear statements backed by citations

---

## 4. Standard long-form pillar structure (target 3,200–4,000 words)

Pillar posts beat NZ competitor average length (1,000–1,800 words) by 1.7–2×.

```
1. Hero
   - H1 (primary keyword + year)
   - 1-line subhead (the promise)
   - Reviewed-by line: "Medically reviewed by [Name, role] on [date]"
   - Byline + reading time
   - Table of contents (anchor links to all H2s)

2. TL;DR / Key Takeaways box (3–4 bullets — AEO + GEO gold, will likely be the AIO citation surface)

3. Intro (100–150 words)
   - Hook with a NZ statistic with named source (Princeton GEO +41% lever)
   - State what the reader will learn (3 bullets)
   - Define the topic in 1 sentence

4. Definitional H2: "What is [topic]?"
   - Textbook-style definition
   - Inline infographic OR table

5. Mechanism H2: "How [topic] actually works"
   - Biology / pharmacology
   - SVG diagram

6. Context H2: "[Topic] in New Zealand"
   - NZ statistic + citation
   - Reference to Medsafe / Te Whatu Ora / Healthify NZ / Hepatitis Foundation NZ etc.

7. Evidence H2: "What the science actually says"
   - Sub-section "What works" with evidence-tier table (Strong / Moderate / Limited / Insufficient) with one citation per row
   - Sub-section "What doesn't / weak evidence"
   - Bar chart or comparison table (SVG)

8. Buyer's guide H2: "How to choose [product type]"
   - Numbered list of 5 criteria
   - Red flags / what to avoid

9. Safety H2: "Drug interactions and who should not take this"
   - Pharmacist-reviewed interaction table (unique pharmacy moat)
   - Pregnancy / breastfeeding / children / chronic-condition caveats

10. Product picks H2: "Our pharmacy team's evidence-led picks"
    - Comparison table (price / active ingredient mg / cost-per-active-mg / NZ-made yes-no)
    - 4–8 internally linked product cards across budget / mid / premium tiers
    - Include at least 2 NZ-made options when available
    - End with link to the relevant collection page

11. Lifestyle H2: "Beyond supplements: lifestyle factors that matter"
    - The unsexy evidence-backed advice (sleep, hydration, diet, exercise, alcohol limits)
    - Each with NZ MoH / Te Whatu Ora citation

12. CTA H2: "When to talk to a pharmacist or GP"
    - Warning signs
    - In-store CTA

13. FAQ H2: "Frequently asked questions"
    - 8–12 Q&As sourced from real PAA + Reddit + Quora + Healthify NZ research
    - Each Q an H3, each A 40–60 words

14. Disclaimer + Author block (Pharmacy Council credentials)

15. Bibliography / Sources section
    - All inline citations listed with URLs (E-E-A-T + GEO signal)

16. Schema scripts at bottom:
    - Article OR BlogPosting + MedicalWebPage + FAQPage + BreadcrumbList (see section 7)
```

---

## 5. Meta Title & Meta Description (2025–26)

### Meta title (≤ 60 chars, target 53–58)
Validated formulas (pick one):
- `[Primary Keyword] NZ: A Pharmacist's [Year] Guide`  ← strongest for our topic mix
- `[Primary Keyword]: [Hook] | Bargain Chemist NZ`
- `The Truth About [Topic] in NZ ([Year])`
- `[Number] [Things] for [Outcome] — NZ Pharmacy Guide`

Always include: primary keyword, NZ signal, current year (if topical).

### Meta description (≤ 155 chars, target 145–155)
Formula:
`[NZ pharmacist hook with primary keyword]. [Specific value — what you'll learn]. [Soft CTA / brand mention].`

Always include: primary keyword in first 60 chars, "New Zealand" or "NZ" signal, soft CTA.

---

## 6. Internal Linking Rules

Every blog must include:
- **≥ 3 collection links** with descriptive anchor text (vary phrasing — no exact-match repetition)
- **≥ 2 product links**
- **≥ 1 internal blog link** (to existing or planned Wellbeing Hub post — supports hub-and-spoke topical authority)
- Total: 10–15 contextual internal links per 2,500-word post
- Never "click here" / "this product" — descriptive anchor only

### Verified live collection map (cross-check before linking)

Confirmed live as of 28 May 2026 — `productsCount > 0`:

**Concern / category**
- `/collections/vitamins-supplements` — Vitamins & Supplements (1,783)
- `/collections/liver-cleanse-detox` — **Liver Health** (26) ← primary anchor for liver/detox content
- `/collections/milk-thistle` — Milk Thistle (7)
- `/collections/detox-antioxidants` — Antioxidant (21) — distinct from "Liver Health"; link only when topic is antioxidants specifically
- `/collections/immunity` — Immune Support (136)
- `/collections/energy` — Energy, Sleep & Fatigue (134)
- `/collections/multivitamins` — Multivitamins (87)
- `/collections/weight-loss` — Weight Loss (112)
- `/collections/sleep-stress-anxiety` — Sleep, Stress & Anxiety
- `/collections/heart-circulation` — Heart & Circulation (43)
- `/collections/bone-joint-health` — Bone Health (17)
- `/collections/eye-health` — Eye Health (19)
- `/collections/menopause` — Menopause (11)
- `/collections/mens-health` — Men's Health (37)
- `/collections/mum-health` — Mum Health (37)
- `/collections/childrens-health` — Children's Health (132)
- `/collections/mother-baby` — Mother & Baby (545)
- `/collections/allergies-hay-fever-sinus` — Allergies, Hayfever & Sinus (78)
- `/collections/cold-flu` — Cold & Flu (186)
- `/collections/stomach-bowel-treatments` — Stomach & Bowel (75)
- `/collections/skin-care` — Skin Care (1,070)
- `/collections/sun-care` — Sun Care (112)
- `/collections/first-aid` — First Aid (337)

**Brand**
- `/collections/clinicians` (99)
- `/collections/blackmores` (82)
- `/collections/good-health` (135) — NZ-owned
- `/collections/nutralife` (82) — NZ-made
- `/collections/thompsons` (59)
- `/collections/natures-way` (82)
- `/collections/radiance` (71)
- `/collections/sanderson` (73)
- `/collections/elevit` (12)
- `/collections/inner-health` (46)
- `/collections/optislim` (72)
- `/collections/balance` (25)
- `/collections/codral` (20)
- `/collections/nurofen` (34)
- `/collections/trilogy` (74)

### Existing Wellbeing Hub posts (for cross-linking)
- `/blogs/wellbeing-hub/the-miracle-of-magnesium`
- `/blogs/wellbeing-hub/joint-health`
- `/blogs/wellbeing-hub/pain-relief-the-best-treatment-for-your-pain`
- `/blogs/wellbeing-hub/antihistamines`
- `/blogs/wellbeing-hub/epipens-the-ultimate-guide`

---

## 7. Schema markup priorities (2025–26)

Every long-form pillar deploys **four** JSON-LD blocks:

### USE — `Article` (or `BlogPosting`)
Required properties: `headline`, `description`, `author` (with `jobTitle`, `affiliation`), `publisher` (Organization with logo), `datePublished`, `dateModified`, `image`, `mainEntityOfPage`, `about` (list of topical entities).

### USE — `MedicalWebPage`
Critical for YMYL after Dec 2025 Core Update. Required: `lastReviewed`, `reviewedBy` (Person with credentials, `jobTitle: "Pharmacist"`, `affiliation: "Bargain Chemist"`, ideally `identifier` with APC registration number), `specialty`, `audience: { @type: "MedicalAudience", audienceType: "Patient" }`, `about` (MedicalCondition).

### USE — `FAQPage`
8–12 Q&As. Plain-text answers (no HTML) inside `acceptedAnswer.text`. Each question and answer in the schema must exactly match the visible Q&A on the page (Google penalises mismatch). Note: Google retired FAQ rich results in SERPs in May 2026, but ChatGPT, Perplexity, Gemini, Copilot still parse the schema and use it for answer extraction.

### USE — `BreadcrumbList`
Even though Google removed mobile breadcrumb display in Jan 2025, the schema is more important for crawl + AI extraction. Required for every pillar.

### USE site-wide — `Organization` / `Pharmacy` with NZBN
At site level, `Organization` with `@type: "Pharmacy"` (MedicalOrganization subtype), `address` (NZ), `areaServed: "NZ"`, `inLanguage: "en-NZ"`, and `identifier: { @type: "PropertyValue", propertyID: "NZBN", value: "[NZBN]" }`. Anchors NZ entity for AI engines (2025+ disambiguation lever).

### AVOID
- `HowTo` — Google retired rich results Sept 2023. Don't deploy.
- `Speakable` — BETA, US-English news only. Don't deploy for NZ pharmacy.

### Important nuance
**Schema alone does not cause AI citations** (Ahrefs May 2026 study: 1,885 pages vs 4,000 controls, statistically insignificant). Implement schema as hygiene; rely on content quality, original data, named experts and freshness for actual citation lifts.

---

## 8. Visuals Standard (multi-modal +156% AIO selection)

Every long-form pillar must include **at least 4 visuals**:

1. **Mechanism infographic** (HTML or inline SVG) — e.g. "How your liver detoxifies (Phase 1 / 2 / 3)" — content competitors typically lack
2. **Evidence-ranking SVG bar chart** — ingredient × evidence strength, with citation footnotes
3. **Comparison table** — products / claims / evidence side-by-side
4. **Decision matrix or callout block** — e.g. "Which option for which goal"

Visual rules:
- All inline SVG / styled HTML divs (self-contained, render in Shopify editor without dependencies)
- Brand palette: deep blue `#0d3b66`, accent orange `#ee964b`, neutral background `#f6f7fb`, success green `#06a77d`, alert red `#d62828`, text `#1f2937`
- Every visual has a `<figcaption>` summarising the takeaway (SEO + accessibility)
- Every SVG includes `<title>` and `<desc>` accessibility tags
- WebP/AVIF for any raster images; hero NEVER lazy-loaded (kills LCP); below-the-fold lazy-loaded
- Descriptive file names (`liver-detox-phase-1-2-3-diagram.svg`, not `IMG_123.svg`)
- Alt text 80–125 chars: factual description + topical context (no keyword stuffing)

---

## 9. Citation Standard (Princeton GEO — +115% for low-ranked content)

Every long-form pillar requires **≥ 8 inline citations** with hyperlinks. Cite NZ sources first.

### Priority order (cite first available)
1. **NZ official**: Medsafe (medsafe.govt.nz), Health NZ / Te Whatu Ora (tewhatuora.govt.nz, info.health.nz), Ministry of Health (health.govt.nz), Stats NZ, Pharmac (Rx only)
2. **NZ authoritative consumer / clinical**: Healthify NZ (healthify.nz), Hepatitis Foundation NZ, NZ Science Media Centre, ASA NZ, NZ Pharmacy Council, University of Otago / Auckland
3. **NZ commercial / industry data**: Consumer NZ, NutraIngredients NZ coverage, NZIER reports
4. **International authoritative**: NCCIH / NIH ODS (nih.gov), Cochrane Library, WHO, Mayo Clinic, Johns Hopkins, Cleveland Clinic, BDA (UK)
5. **Peer-reviewed journals (specific paper + year + URL)**: PubMed / PMC, BMJ, JAMA, NEJM, Lancet, Cureus, J Hum Nutr Diet, Clin Nutr, Frontiers, etc.

### Avoid
Wikipedia, brand sites (use their fact-sheets only for product specs), uncited "studies show", year-undated claims.

### Inline citation format
`Hyperlinked source name [(Year)]` — e.g. "[NCCIH](https://www.nccih.nih.gov/health/milk-thistle) (2024)" or "([Te Whatu Ora](https://info.health.nz/...))"

### Bibliography
Always include a "Sources" section at the bottom listing every inline-cited URL with title + year. Both inline AND bibliography are required (Princeton GEO).

---

## 10. NZ Regulatory Compliance — Red Lines

Refer to `research/detox-supplements-research-dossier.md` for full source URLs. Bake into every supplement-related post.

| ❌ Never do this | Why |
|---|---|
| Claim a supplement "prevents", "cures", "treats", "alleviates" or "manages" a named disease | Medsafe Dietary Supplements Regulations 1985 ; Medicines Act 1981 s.58 |
| Name disease states a supplement helps with ("for fatty liver") | Medsafe |
| Name specific symptoms a supplement relieves | Medsafe |
| Use HCP endorsements implying therapeutic benefit ("Pharmacist X recommends this for liver disease") | Medicines Act s.58(1)(c)(ii) |
| Publish consumer testimonials implying therapeutic improvement | Medicines Act s.58(1)(c)(iii) ; ASA Code |
| Apply off-label clinical evidence to justify a claim | ASA Therapeutic & Health Advertising Code |
| Portray unrealistic outcomes / exploit emotional vulnerability / target low-health-literacy | Updated ASA Code (effective 1 Apr 2026) |
| Make therapeutic claims on supplemented food | MPI / Food Standards Code 1.2.7 |
| Promote a supplement without an evidence basis | Pharmacy Council Code of Ethics 2018 |

**Compliant alternatives**: "may support healthy liver function", "traditionally used to support digestion", "contains evidence-backed silymarin at a clinically studied dose", "an ingredient with growing clinical research"

**E-E-A-T framing for pharmacy-team byline**: write/review as an evidence-led pharmacy team. Recommend categories of *evidence-backed ingredient*, not a *therapeutic outcome for a named disease*.

**Standard disclaimer** (paste at bottom of every blog):

> **Disclaimer**: This article is general information only and is not medical advice. It does not replace advice from a registered pharmacist, GP or other healthcare professional. Always read the label, use only as directed, and consult your healthcare provider before starting any new supplement — especially if you are pregnant, breastfeeding, on prescription medication, or managing a health condition. If symptoms persist, see your healthcare professional.

---

## 11. Author E-E-A-T Block (paste at bottom of every blog)

```html
<div class="bc-author-block">
  <strong>About the Bargain Chemist Pharmacy Team</strong>
  This article was written and reviewed by Bargain Chemist's New Zealand-registered pharmacy team in line with the <a href="https://pharmacycouncil.org.nz/wp-content/uploads/2021/03/Code-of-Ethics-2018-FINAL.pdf">Pharmacy Council of New Zealand Code of Ethics</a> and our editorial commitment to evidence-based, unbiased information about supplement quality, safety and effectiveness. We combine peer-reviewed research, Medsafe and Te Whatu Ora guidance, and everyday experience helping Kiwi families. Visit any Bargain Chemist store or contact our team at <a href="https://www.bargainchemist.co.nz/pages/contact">bargainchemist.co.nz/pages/contact</a>.
</div>
```

---

## 12. Workflow — when the user asks for a new blog

1. **Ask 4 questions** (topic, audience, season, products to prioritise)
2. **Research-first** — run these in parallel for any new topic where we don't already have a `research/<topic>-research-dossier.md`:
   - WebSearch / WebFetch for top 5 NZ ranking pages (competitor structure)
   - Google PAA + Reddit + Quora + Healthify NZ sweep for real user questions
   - Citation verification — every claim needs a real URL
   - NZ regulatory check — Medsafe / Te Whatu Ora / ASA current guidance
   - Shopify search via `mcp__shopify__graphql_query` for live products + collections (filter `status:active`)
3. **Save the dossier** to `/research/<topic>-research-dossier.md`
4. **Verify the collection URL handles are live** before writing
5. **Draft `<slug>.html`** in `/blogs/` following the 16-section structure (section 4 above)
6. **Draft `<slug>.meta.md`** in `/blogs/` with SEO brief (section 13)
7. **Validate** using the Top 25 checklist (section 14 — every item must pass)
8. **Commit** on the branch specified in the session header and push
9. **Report**: file paths, meta title + description, slug, word count, internal link count, schema blocks deployed, any "could not verify" items flagged

---

## 13. SEO brief deliverable (every blog gets one `.meta.md`)

`blogs/<slug>.meta.md` includes:
- Shopify field values (title, slug, tags, author)
- Meta title + character count
- Meta description + character count
- Primary keyword + secondary + long-tail + FAQ-targeted keywords (each with intent)
- Keywords to AVOID (compliance + intent-mismatch)
- Featured image brief (subject, style, file name, alt text, dimensions)
- Internal link map (every collection + product + blog link used)
- Outbound citation list with verified URLs
- Suggested social copy (FB, IG, LinkedIn — 1 line each)
- Post-publish QA checklist (test schemas, verify rendering, schedule first refresh +90 days)

---

## 14. TOP 25 MUST-DO CHECKLIST

Verify YES/NO before publishing. Source: synthesised 2025–26 SEO/GEO/AEO research (see `research/detox-supplements-research-dossier.md` section 5).

1. Primary keyword in H1 (exact or near-exact match)
2. Primary keyword in URL slug (kebab-case, no stop words)
3. Primary keyword + variant in first 100 words
4. Direct answer to the headline question in the first 150 words (≤55 words)
5. Meta title ≤60 chars, includes primary keyword + "NZ" or brand
6. Meta description ≤155 chars, includes CTA + benefit
7. ≥1 statistic with a named, dated source in the first 300 words (Princeton GEO +41%)
8. ≥1 direct quote from a named, credentialled clinician or NZ authority (Princeton GEO +28%)
9. ≥3 inline citations to authoritative sources, NZ-first (Medsafe / MoH / Healthify NZ / Te Whatu Ora) (Princeton GEO +115%)
10. Byline links to an author page; credentials visible
11. "Medically reviewed by [Name, role] on [date]" line visible at top
12. `datePublished` AND `dateModified` shown to users AND in schema
13. `Article` (or `BlogPosting`) + `MedicalWebPage` + `BreadcrumbList` + `FAQPage` schema deployed
14. FAQPage schema block with 8–12 Q&As targeting PAA queries
15. Each FAQ question is an H3 with a 40–60 word direct answer below
16. ≥1 comparison table or bullet list (Claude favours; +30% AI citation)
17. ≥1 image with descriptive filename + alt text 80–125 chars (WebP/AVIF preferred; hero NOT lazy-loaded; below-fold lazy)
18. ≥1 multi-modal element beyond text (chart, infographic, video embed, transcript) — +156% AI selection
19. 10–15 contextual internal links: ≥1 product/collection, ≥2 related blogs, ≥1 pillar
20. Varied descriptive anchor text — no exact-match repetition, no "click here"
21. NZ entity signals: NZD pricing, "in New Zealand", suburb/region mention where relevant, NZ phone format
22. NZ Medicines Act compliance check: no unapproved therapeutic claims; no HCP endorsement implying therapeutic benefit; no consumer testimonials implying therapeutic improvement
23. "Sources" bibliography at foot listing all inline citations with URLs
24. Page expected to pass Core Web Vitals on mobile (LCP <2.5s, INP <200ms, CLS <0.1)
25. Refresh scheduled at +90 days with owner + substantive update brief (not date-bump)

---

## 15. Refresh cadence + content lifecycle

- **Every blog refresh logged at +90 days** in `/blogs/refresh-schedule.md` (or similar)
- Refresh must include ≥1 substantive update: new stat, new regulatory change, new evidence, new product, new FAQ
- Update `dateModified` AND a visible "Last reviewed by [Name] on [date]" line
- Cosmetic date-bumping is detected by Google and devalued; never do it
- Pages refreshed within 2 months earn ~28% more AI Overview citations

---

## 16. Topical cluster strategy (hub-and-spoke)

Each pillar should anchor 3–5 supporting "spoke" posts (~1,200 words each) that link UP to the pillar; the pillar links DOWN to every spoke. This builds topical authority faster than isolated posts.

Example clusters to plan:

- **Liver health pillar** (this dossier) → milk thistle deep-dive, supplements + alcohol, MASLD/fatty liver NZ guide, liver-friendly diet NZ, gut-liver axis
- **Immunity pillar** (future) → winter immunity NZ, kids immune support, vitamin C / zinc / elderberry comparisons, post-illness recovery
- **Sleep pillar** (future) → magnesium for sleep (existing post), melatonin in NZ, sleep hygiene, shift-worker tips
- **Hayfever pillar** (future) → antihistamines comparison (existing post), nasal sprays, child-friendly options, NZ pollen calendar

---

## 17. Deliverables per blog

Two files in `/blogs/`:

1. **`<slug>.html`** — single self-contained HTML file. Paste into Shopify blog editor's HTML view. Contains: hero, TOC, all body, inline SVG charts, infographics, FAQ, disclaimer, author block, plus all four JSON-LD schema scripts at the bottom.

2. **`<slug>.meta.md`** — SEO brief. Contains Shopify field values, meta title + description with character counts, keyword strategy, featured image brief, internal link map, outbound citation list, social share copy, post-publish QA checklist.

Plus one optional supporting file in `/research/`:

3. **`research/<topic>-research-dossier.md`** — for any new topic with no existing dossier. Captures verified citations, keyword research, NZ user questions, competitor gaps, regulatory context. Reused for refresh cycles + spoke posts.
