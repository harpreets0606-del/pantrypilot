# Bargain Chemist Blogger Playbook (v3 — evidence-validated)

This file auto-loads every Claude Code session. It is the durable house style + SEO/GEO/AEO operations manual for the Bargain Chemist Wellbeing Hub blog.

Validated against 2025–2026 SEO/GEO/AEO research, NZ statutory plain-language standards (Plain Language Act 2022), NZ health-literacy data (Kōrero Mārama, PIAAC 2023), NZ regulatory framework (Medsafe, Medicines Act 1981 s.58, ASA new code effective 1 April 2026), peer-reviewed AI Overview citation studies (Princeton GEO, Ahrefs AIO-cited-page analyses), measured competitor reading levels, and editorial standards from Healthify NZ, Healthline, Cleveland Clinic, Mayo Clinic, NHS UK and Harvard Health.

When the user asks to "write a blog", follow this playbook end-to-end and ask **only** these four questions up front:
1. Topic and angle
2. Audience focus (general NZ, parents, seniors, athletes)
3. Seasonal or campaign tie-in
4. Specific products or brands to prioritise (otherwise pick from `/research/` dossiers + live Shopify search)

Everything else defaults to what's in this playbook.

---

## 1. About Bargain Chemist (context for every blog)

- **Business**: NZ pharmacy chain + Shopify Plus ecommerce
- **Positioning**: "New Zealand's Cheapest Chemist" — price-beat guarantee, value-led
- **Domain**: `https://www.bargainchemist.co.nz`
- **Blog path**: `https://www.bargainchemist.co.nz/blogs/wellbeing-hub/<article-handle>`
- **Locale**: New Zealand (NZD, NZ English spelling, NZ Medsafe/MoH/ASA regulatory framework)
- **Standard byline**: "Bargain Chemist Pharmacy Team"
- **Reviewer line**: every blog includes a visible "Reviewed by [Pharmacist Name, NZ-Registered Pharmacist, APC #XXXXX] on [date]" line at the top. This is the Healthline + Healthify NZ E-E-A-T pattern (Dec 2025 Core Update). Use placeholders `[REVIEWING_PHARMACIST_NAME]` and `[APC_NUMBER]` for the user to fill before publish.

---

## 2. Evidence-based content targets

### 2.1 Reading level (NZ statutory + AMA/NIH ceiling)
| Metric | Target | Source |
|---|---|---|
| Flesch Reading Ease | **60–70** | digital.govt.nz / Plain Language Act 2022 |
| Flesch-Kincaid grade | **7–8** | AMA/NIH/AHRQ patient-info ceiling |
| SMOG | **≤ 9** | Rauemi Atawhai (MoH 2012) |
| Avg sentence length | **15–18 words** | NHS digital service manual |
| Hard sentence cap | **25 words** | NHS rule |
| Avg paragraph | **≤ 3 sentences** | NHS rule |
| Jargon density | **≤ 15 terms / 1,000 words** | Synthesised from NZ plain-language standard |

**Rationale**: NZ Plain Language Act 2022 legally requires public-sector agencies to write at reading age 12 / FRE ≥ 60. 56.2% of NZ adults have inadequate health literacy (Kōrero Mārama). Writing above grade 8 excludes the majority of the audience this playbook targets. A 2024 RCT (J Gen Intern Med) found that **structure (sentence length, one idea per sentence) matters more than the FK number itself** — lowering grade level alone does not measurably help low-literacy readers.

Validate every draft with `textstat` (Python). The CI check is: FRE ≥ 60 AND FK ≤ 8.5 AND no sentence > 25 words.

### 2.2 Word count
| Format | Target | Source |
|---|---|---|
| Pillar post | **2,500–3,200 words** | Ahrefs AIO study (mean cited 1,282 w; r=0.04 for length); engagement plateaus at 2,000 |
| Spoke post | **1,000–1,500 words** | Hub-and-spoke topical authority pattern |

**Rationale**: Length is **not** a driver of AI Overview citation (Ahrefs Spearman 0.04 across 174,000 AIO-cited URLs). 53% of AIO-cited pages are under 1,000 words. The "beat competitors by length" logic was wrong; competitors lose on citations + structure, not length. Engagement plateaus around 2,000 and meaningfully declines past 4,000.

### 2.3 SEO basics
- Primary keyword in: H1, slug, first 100 words, at least one H2, image alt text
- Internal links: ≥ 3 collection pages and 2–4 product pages
- Outbound authority links: minimum 12 inline for pillars, with ≥ 7 of those in the **first 30% of the page** (55% of AIO citations come from there — Averi 2026 + Indig)
- Direct answer to the H1 question in first 100–150 words (≤ 55 words)

### 2.4 GEO — Princeton 2024 + 2025–26 industry data
- **Statistics with named source** → +41% AI Overview visibility
- **Direct quotes from named experts** → +28% on subjective impression metrics
- **Inline source citation** → up to +115% visibility for mid-ranked pages
- **Fluency + authoritative declarative voice** are in the top 5 tactics
- **55% of AI Overview citations** are pulled from the top 30% of a page
- **Content < 3 months old** is ~3× more likely to be cited
- **Multi-modal pages** show +156% AI selection rate

### 2.5 AEO — answer engines + voice + Google PAA
- Pose 4–6 H2/H3s as natural questions
- Direct answer in ≤ 55 words below each question heading
- FAQ section: 8–12 Q&As at the end, each Q an H3, each A 40–60 words
- FAQPage JSON-LD schema for every post

### 2.6 LLM source biases (when prioritising)
- ChatGPT favours Wikipedia (~48% of citations)
- Perplexity favours Reddit (~47%) and real-time news
- **Claude favours bulleted/tabular structure (+30% citation likelihood)** — use bullets and tables generously
- Gemini overlaps ~54% with Google organic

---

## 3. House voice & tone (NZ pharmacy)

**Voice model: Healthify NZ + Healthline structure + Cleveland Clinic named-quote pattern + NHS sentence discipline.**

- **Healthify NZ** is our regulatory + audience-fit anchor — same locale, same Medsafe regime, same audience health-literacy reality
- **Healthline structure** for AI citation share (most-cited health publisher in AIOs)
- **Cleveland Clinic** named-clinician quote pattern (Princeton GEO +28% lever) — quote our pharmacy team directly
- **NHS** sentence-length and plain-English discipline

Rules:
- **Second person** ("you", "your") — direct, helpful, pharmacy-counter tone
- **Plain Kiwi English** with NZ spelling (colour, fibre, paediatric, optimise, programmes)
- **One idea per sentence.** Short sentences. Vary length but keep most ≤ 18 words.
- **Avoid Latinate verbs.** Use → use, demonstrate → show, facilitate → help, approximately → about, additionally → also, however → but, utilise → use.
- **Compliant supplement phrasing**: "may support healthy liver function", "traditionally used to support digestion", "contains evidence-backed [ingredient] at a clinically studied dose". Focus on the ingredient + the evidence, not the disease + the cure.
- **Acknowledge limitations** ("evidence is mixed", "the Cochrane review found insufficient evidence")
- Avoid emojis in body content
- Use **declarative, authoritative voice** (Princeton GEO finding)

### 3.1 Jargon handling rule
Use the **NHS pattern**: plain word first, technical term in parentheses on first use, then alternate (e.g. "fatty liver disease (MASLD)"). For ingredient names where the term IS the topic (silymarin), use **Healthline's inverse pattern**: name the compound then define it in the same sentence ("silymarin, the active compound in milk thistle").

**The top jargon glosses for liver/detox content** (apply on first use):
- silymarin → "the active compound in milk thistle"
- NAC → "a compound your body uses to make glutathione"
- glutathione → "your liver's main antioxidant"
- Phase 1 / 2 / 3 → "your liver's three cleanup stages"
- bile → "a digestive fluid your liver makes"
- conjugation → "packaging waste for removal"
- CYP2C9 → "a liver enzyme that processes some medicines" (then just say "blood thinners and statins")
- hepatic / hepatocyte → "liver" / "liver cell"
- ALT / AST → "liver blood markers"

---

## 4. Standard long-form pillar structure (target 2,500–3,200 words)

```
1. Hero
   - H1 (primary keyword + year)
   - 1-line subhead (the promise)
   - Reviewed-by line: "Reviewed by [Name, NZ-Registered Pharmacist, APC #XXXXX] on [date]"
   - Byline + reading time
   - AI-generated hero image (see Section 7)

2. TL;DR / Key Takeaways box (3–4 bullets — AEO + GEO gold)

3. Table of contents (anchor links to all H2s)

4. Intro (100–150 words)
   - Hook with a NZ statistic with named source (Princeton GEO +41% lever)
   - State what the reader will learn (3 bullets)
   - Define the topic in 1 sentence

5. Definitional H2: "What is [topic]?"
   - Plain-English definition
   - Inline infographic OR styled HTML grid

6. Mechanism H2: "How [topic] actually works"
   - Plain-English explanation
   - SVG diagram or styled HTML cards
   - Glossed jargon (per Section 3.1)

7. Context H2: "[Topic] in New Zealand"
   - NZ statistic + citation
   - Reference to Te Whatu Ora / Healthify NZ / Hepatitis Foundation NZ etc.
   - End with explicit "supplements are not a treatment for [condition]" separator + Alcohol Drug Helpline (0800 787 797) or other relevant NZ helpline if topic warrants
   - Optional: AI-generated image of NZ context

8. Evidence H2: "What the science actually says"
   - **Evidence-tier table** (Mayo/Harvard scorecard pattern) with verdict per ingredient: Strong / Moderate / Limited / Insufficient + one citation per row
   - **SVG bar chart** of evidence strength
   - Sub-section "What doesn't / weak evidence"

9. Buyer's guide H2: "How to choose [product type]"
   - Numbered list of 5 criteria
   - Red flags / what to avoid

10. Safety H2: "Drug interactions and who should not take this"
    - Pharmacist-reviewed interaction table (unique pharmacy moat)
    - Preamble: "general information only, not medical advice"
    - Pregnancy / breastfeeding / children / chronic-condition caveats

11. Product picks H2: "Liver-support supplements stocked at Bargain Chemist" (or topic equivalent — NEVER "Our pharmacy team's evidence-led picks")
    - **Comparison table with an "Evidence verdict (per active)" column** mapped to the evidence-tier table
    - This frames the table as factual stock/price reference, not editorial endorsement (Mayo/Harvard scorecard pattern)
    - 4–8 internally linked products across budget / mid / premium tiers
    - Include at least 2 NZ-made options when available
    - Explicit "not a clinical recommendation" disclaimer
    - End with link to the relevant collection page

12. Lifestyle H2: "Beyond supplements: lifestyle factors that matter"
    - The unsexy evidence-backed advice
    - Each with NZ MoH / Te Whatu Ora citation

13. CTA H2: "When to talk to a pharmacist or GP"
    - Warning signs
    - In-store CTA + helpline

14. FAQ H2: "Frequently asked questions"
    - 8–12 Q&As sourced from real PAA + Reddit + Quora + Healthify NZ research
    - Each Q an H3, each A 40–60 words
    - **Strip disease-specific Q&As from the FAQPage JSON-LD** (keep in visible body) to avoid amplifying disease keywords in AI extraction for a commercial page

15. Disclaimer + Author block (Pharmacy Council credentials)

16. Bibliography / Sources section (E-E-A-T + GEO signal)

17. Schema scripts at bottom: Article + MedicalWebPage + FAQPage + BreadcrumbList
```

---

## 5. Meta title & meta description (2025–26)

### Meta title (≤ 60 chars, target 53–58)
Validated formulas (pick one):
- `[Primary Keyword] NZ: A Pharmacist's [Year] Guide`  ← strongest for our topic mix
- `[Primary Keyword]: [Hook] | Bargain Chemist NZ`
- `The Truth About [Topic] in NZ ([Year])`
- `[Number] [Things] for [Outcome] — NZ Pharmacy Guide`

Always include: primary keyword, NZ signal, current year (if topical).

### Meta description (≤ 155 chars, target 145–155)
Formula: `[NZ pharmacist hook with primary keyword]. [Specific value]. [Soft CTA / brand mention].`

Always include: primary keyword in first 60 chars, "New Zealand" or "NZ" signal, soft CTA.

---

## 6. Internal linking rules

Every blog must include:
- **≥ 3 collection links** with descriptive anchor text (vary phrasing)
- **≥ 2 product links**
- **≥ 1 internal blog link**
- Total: 10–15 contextual internal links per 2,500-word post
- Never "click here" / "this product" — descriptive anchor only

### Verified live collection map (confirmed 28 May 2026)

**Concern / category**
- `/collections/vitamins-supplements` — Vitamins & Supplements (1,783)
- `/collections/liver-cleanse-detox` — **Liver Health** (26) ← primary anchor for liver/detox content
- `/collections/milk-thistle` — Milk Thistle (7)
- `/collections/detox-antioxidants` — Antioxidant (21) — distinct from "Liver Health"
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
- `/collections/clinicians` (99) · `/collections/blackmores` (82) · `/collections/good-health` (135, NZ-owned) · `/collections/nutralife` (82, NZ-made) · `/collections/thompsons` (59) · `/collections/natures-way` (82) · `/collections/radiance` (71) · `/collections/sanderson` (73) · `/collections/elevit` (12) · `/collections/inner-health` (46) · `/collections/optislim` (72) · `/collections/balance` (25) · `/collections/codral` (20) · `/collections/nurofen` (34) · `/collections/trilogy` (74)

### Existing Wellbeing Hub posts (cross-link)
- `/blogs/wellbeing-hub/the-miracle-of-magnesium`
- `/blogs/wellbeing-hub/joint-health`
- `/blogs/wellbeing-hub/pain-relief-the-best-treatment-for-your-pain`
- `/blogs/wellbeing-hub/antihistamines`
- `/blogs/wellbeing-hub/epipens-the-ultimate-guide`

---

## 7. Visuals standard (multi-modal +156% AIO selection)

**Bargain Chemist visual mix** (no YouTube videos — by user direction):

Every long-form pillar must include **a mix from these three formats**, totalling at least 4 visuals:

### Format A: Tables (every pillar must have at least 2)
- One evidence-tier scorecard (per ingredient with verdict)
- One product comparison table (with verdict column mapped to scorecard)
- Optional: drug interaction table, lifestyle factors table, FAQ-equivalent table
- Tables outperform bar charts for value comparison in low-literacy populations (PLOS One)
- Claude favours tabular structure (+30% citation likelihood)

### Format B: Graphs / SVG charts (every pillar must have at least 1)
- Inline SVG so it renders as an image in Shopify with no external dependency
- Use horizontal bar chart for evidence-strength rankings (preferred)
- Use grouped tile grid for Strong/Moderate/Limited/Insufficient bands
- Use simple flow diagram for mechanism (e.g. Phase 1/2/3)
- Brand palette: deep blue `#0d3b66`, accent orange `#ee964b`, neutral background `#f6f7fb`, success green `#06a77d`, alert red `#d62828`, text `#1f2937`
- Every SVG includes `<title>` and `<desc>` tags inside for accessibility / SEO
- Every figure has a `<figcaption>` with a 1-line takeaway

### Format C: AI-generated images (every pillar must have at least 1)
**For each AI image needed, the blog HTML includes**:
1. A `<figure class="bc-ai-image">` placeholder block with `<img>` tag and descriptive alt text
2. An HTML comment containing the AI image brief (subject, style, dimensions, alt text)
3. The detailed AI prompt to paste into Midjourney / DALL-E / Imagen / Adobe Firefly

**The user generates the image, uploads to Shopify CDN, replaces the placeholder `src`.**

Rules for AI images on health/pharmacy content:
- ✅ Use AI images for **atmosphere and lifestyle context** (hero shots, healthy food, Kiwi pharmacy counter, exercise, nature)
- ❌ NEVER use AI images depicting **clinical scenarios, fake patients, fake healthcare professionals, fake medical equipment, fake test results**. Google's YMYL E-E-A-T penalises fabricated medical imagery.
- ❌ Do not depict specific medical conditions
- ✅ Always disclose AI generation in the `<figcaption>` or alt text if material to the meaning
- Alt text 80–125 chars: factual description + topical context (no keyword stuffing)
- WebP/AVIF; hero image NEVER lazy-loaded (kills LCP); below-the-fold lazy-loaded
- Descriptive file names (`liver-health-kiwi-lifestyle-hero.webp`, not `IMG_123.webp`)

### Recommended visual mix for a 2,500–3,200 word pillar
- 1 hero AI-generated image (top, above fold) — lifestyle/atmosphere
- 1 mechanism infographic (SVG or styled HTML cards) — e.g. Phase 1/2/3
- 1 evidence-strength SVG bar chart
- 2–3 tables (evidence scorecard + product comparison + optional interactions)
- 1 mid-article AI-generated image (lifestyle context, breaks up wall of text)
- Optional: 1 callout/quote card with a named pharmacy-team quote (Cleveland Clinic pattern — Princeton GEO +28%)

---

## 8. Citation standard (Princeton GEO — +115% for low-ranked content)

Every long-form pillar requires **≥ 12 inline citations** (was ≥ 8 in v2) with hyperlinks. **Front-load ≥ 7 citations in the first 30% of the page** (55% of AIO citations come from there).

### Priority order (cite first available)
1. **NZ official**: Medsafe, Health NZ / Te Whatu Ora, Ministry of Health, Stats NZ, Pharmac (Rx only)
2. **NZ authoritative consumer / clinical**: Healthify NZ, Hepatitis Foundation NZ, NZ Science Media Centre, ASA NZ, NZ Pharmacy Council, University of Otago / Auckland
3. **NZ commercial / industry data**: Consumer NZ, NutraIngredients NZ coverage, NZIER reports
4. **International authoritative**: NCCIH / NIH ODS, Cochrane Library, WHO, Mayo Clinic, Johns Hopkins, Cleveland Clinic, BDA (UK)
5. **Peer-reviewed journals**: PubMed / PMC, BMJ, JAMA, NEJM, Lancet, Cureus, J Hum Nutr Diet, Clin Nutr, Frontiers

### Avoid
Wikipedia, brand sites (use their fact-sheets only for product specs), uncited "studies show", year-undated claims.

### Inline citation format
`Hyperlinked source name [(Year)]` — e.g. "[NCCIH](https://www.nccih.nih.gov/health/milk-thistle) (2024)"

### Bibliography
Always include a "Sources" section at the bottom listing every inline-cited URL with title + year.

---

## 9. NZ regulatory compliance — red lines

| ❌ Never do this | Why |
|---|---|
| Claim a supplement "prevents", "cures", "treats", "alleviates" or "manages" a named disease | Medsafe Dietary Supplements Regulations 1985 ; Medicines Act 1981 s.58 |
| Pair a named product with a named disease state ("for fatty liver") | Medsafe |
| Name specific symptoms a supplement relieves | Medsafe |
| Use HCP endorsements implying therapeutic benefit ("Pharmacist X recommends this for liver disease") | Medicines Act s.58(1)(c)(ii) |
| Publish consumer testimonials implying therapeutic improvement | Medicines Act s.58(1)(c)(iii) ; ASA Code |
| Apply off-label clinical evidence to justify a claim | ASA Therapeutic & Health Advertising Code |
| Portray unrealistic outcomes / exploit emotional vulnerability / target low-health-literacy | Updated ASA Code (effective 1 Apr 2026) |
| Make therapeutic claims on supplemented food | MPI / Food Standards Code 1.2.7 |
| Promote a supplement without an evidence basis | Pharmacy Council Code of Ethics 2018 |

**Compliant alternatives**: "may support healthy liver function", "traditionally used to support digestion", "contains evidence-backed silymarin at a clinically studied dose".

**Compliance-safe pattern for named pharmacist reviewer + product table** (the v3 resolution): keep the named pharmacist + APC reviewer line (Healthline/Healthify pattern, Dec 2025 Core Update E-E-A-T requirement), AND frame the product table as a **Mayo/Harvard-style scorecard with per-ingredient evidence verdicts** rather than as the pharmacist's therapeutic recommendations. The product table is information ("these are stocked here at these prices, here's the per-ingredient evidence verdict"), not editorial endorsement of therapeutic benefit.

Standard disclaimer (paste at bottom of every blog):

> **Disclaimer**: This article is general information only and is not medical advice. It does not replace advice from a registered pharmacist, GP or other healthcare professional. Always read the label, use only as directed, and consult your healthcare provider before starting any new supplement — especially if you are pregnant, breastfeeding, on prescription medication, or managing a health condition. If symptoms persist, see your healthcare professional.

---

## 10. Schema markup priorities (2025–26)

Every long-form pillar deploys **four** JSON-LD blocks: `Article` + `MedicalWebPage` + `FAQPage` + `BreadcrumbList`.

### Critical 2025–26 changes
- **HowTo schema is dead** (retired Sept 2023). Do not deploy.
- **FAQ rich results in SERPs retired May 2026** but FAQPage schema still parsed by ChatGPT, Perplexity, Gemini, Copilot. Keep it.
- **Schema alone does not cause AI citations** (Ahrefs May 2026 study). Implement as hygiene.
- **Speakable schema is BETA, US-English news only**. Do not deploy.
- **NZBN** as `identifier.value` in Organization schema = NZ-specific AI disambiguation lever.

### MedicalWebPage required fields
`lastReviewed`, `reviewedBy` (Person with credentials, jobTitle "Pharmacist", affiliation "Bargain Chemist", identifier with APC registration number), `specialty`, `audience.@type "MedicalAudience"`, `audience.geographicArea` (Country "New Zealand"), `about` (MedicalCondition).

### FAQPage hygiene
- 8–12 Q&As, each `acceptedAnswer.text` plain text (no HTML)
- Visible Q&A on page must exactly match schema Q&A
- **Strip disease-specific Q&As from the schema** (e.g. "Can a supplement reverse fatty liver disease?") to avoid amplifying disease keywords in AI extraction. Keep them as visible body content.

---

## 11. Author E-E-A-T block (paste at bottom of every blog)

```html
<div class="bc-author-block">
  <strong>About the Bargain Chemist Pharmacy Team</strong>
  This article was written and reviewed by Bargain Chemist's New Zealand-registered pharmacy team in line with the <a href="https://pharmacycouncil.org.nz/wp-content/uploads/2021/03/Code-of-Ethics-2018-FINAL.pdf">Pharmacy Council of New Zealand Code of Ethics</a> and our editorial commitment to evidence-based, unbiased information about supplement quality, safety and effectiveness. We combine peer-reviewed research, Medsafe and Te Whatu Ora guidance, and everyday experience helping Kiwi families. Visit any Bargain Chemist store or contact our team at <a href="https://www.bargainchemist.co.nz/pages/contact">bargainchemist.co.nz/pages/contact</a>.
</div>
```

---

## 12. Workflow when the user asks for a new blog

1. **Ask 4 questions** (topic, audience, season, products to prioritise)
2. **Research-first** — run these in parallel for any new topic without a `research/<topic>-research-dossier.md`:
   - WebSearch / WebFetch for top 5 NZ ranking pages (competitor structure)
   - Google PAA + Reddit + Quora + Healthify NZ sweep for real user questions
   - Citation verification — every claim needs a real URL
   - NZ regulatory check
   - Shopify search via `mcp__shopify__graphql_query` for live products + collections (filter `status:active`)
3. **Save the dossier** to `/research/<topic>-research-dossier.md`
4. **Verify collection URL handles are live** before writing
5. **Draft `<slug>.html`** in `/blogs/` following the 17-section structure (Section 4)
6. **Draft `<slug>.meta.md`** in `/blogs/` with SEO brief including **AI image prompts** (Section 13)
7. **Validate**: textstat run (FRE ≥ 60, FK ≤ 8.5), Top-25 checklist, both audits if heavy revisions
8. **Commit** on the branch specified in the session header and push
9. **Report**: file paths, FRE / FK / word count, internal link count, schema blocks deployed, AI image briefs included

---

## 13. SEO brief deliverable (every blog gets one `.meta.md`)

`blogs/<slug>.meta.md` includes:
- Shopify field values (title, slug, tags, author)
- Meta title + character count
- Meta description + character count
- Primary keyword + secondary + long-tail + FAQ-targeted keywords
- Keywords to AVOID (compliance + intent-mismatch)
- **Reading-level results** (FRE, FK grade, SMOG, sentence stats from textstat run)
- Featured image brief (subject, style, file name, alt text, dimensions)
- **AI image briefs with full prompts** for each AI-generated image used in the body (Midjourney/DALL-E/Imagen/Firefly prompts, alt text, dimensions, where to insert)
- Internal link map (every collection + product + blog link used)
- Outbound citation list with verified URLs
- Suggested social copy (FB, IG, LinkedIn — 1 line each)
- Post-publish QA checklist (test schemas, verify rendering, schedule first refresh +90 days)

---

## 14. TOP 25 MUST-DO CHECKLIST (v3 — evidence-validated)

Verify YES/NO before publishing.

1. Primary keyword in H1 (exact or near-exact match)
2. Primary keyword in URL slug (kebab-case, no stop words)
3. Primary keyword + variant in first 100 words
4. Direct answer to the headline question in the first 150 words (≤ 55 words)
5. Meta title ≤ 60 chars, includes primary keyword + "NZ" or brand
6. Meta description ≤ 155 chars, includes CTA + benefit
7. **Flesch Reading Ease ≥ 60** (`textstat` measured)
8. **Flesch-Kincaid grade ≤ 8.5** (`textstat` measured)
9. **No sentence > 25 words** (`textstat` measured)
10. ≥ 1 statistic with named NZ source in first 300 words (Princeton GEO +41%)
11. ≥ 1 direct quote from a named, credentialled clinician or NZ authority (Princeton GEO +28%)
12. **≥ 12 inline citations to authoritative sources**, NZ-first, with **≥ 7 in the first 30% of the page** (Princeton GEO +115%; AIO top-30% pattern)
13. Byline links to an author page; credentials visible
14. "Reviewed by [Name, role, APC #] on [date]" line visible at top
15. `datePublished` AND `dateModified` shown to users AND in schema
16. `Article` + `MedicalWebPage` + `BreadcrumbList` + `FAQPage` schema deployed
17. FAQPage schema block with 8–12 Q&As; disease-specific Q&As stripped from schema (kept in visible body)
18. Each FAQ question is an H3 with a 40–60 word direct answer below
19. ≥ 2 tables (evidence scorecard + product comparison) — Claude favours tables (+30%)
20. ≥ 1 SVG chart with `<title>` and `<desc>` accessibility tags
21. ≥ 1 AI-generated image with prompt documented in `.meta.md` (no clinical scenes)
22. 10–15 contextual internal links: ≥ 1 product/collection, ≥ 2 related blogs, ≥ 1 pillar
23. NZ entity signals: NZD pricing, "in New Zealand", NZ phone format where relevant; helpline number (e.g. 0800 787 797) if topic warrants
24. NZ Medicines Act compliance check: no unapproved therapeutic claims; no HCP endorsement implying therapeutic benefit; no consumer testimonials implying therapeutic improvement; product table uses Mayo/Harvard scorecard framing not "team's picks"
25. Refresh scheduled at +90 days with owner + substantive update brief (not date-bump) — content < 3 months old is 3× more likely to be AI-cited

---

## 15. Refresh cadence + content lifecycle

- **Every blog refresh logged at +90 days**
- Refresh must include ≥ 1 substantive update: new stat, new regulatory change, new evidence, new product, new FAQ
- Update `dateModified` AND a visible "Last reviewed by [Name] on [date]" line
- Cosmetic date-bumping is detected by Google and devalued; never do it
- Pages refreshed within 2 months earn ~28% more AI Overview citations

---

## 16. Topical cluster strategy (hub-and-spoke)

Each pillar should anchor 3–5 supporting "spoke" posts (~1,200 words each) that link UP to the pillar; the pillar links DOWN to every spoke.

Example clusters to plan:
- **Liver health pillar** → milk thistle deep-dive, supplements + alcohol, MASLD/fatty liver NZ guide, liver-friendly diet NZ, gut–liver axis
- **Immunity pillar** → winter immunity NZ, kids immune support, vitamin C / zinc / elderberry comparisons, post-illness recovery
- **Sleep pillar** → magnesium for sleep (existing post), melatonin in NZ, sleep hygiene, shift-worker tips
- **Hayfever pillar** → antihistamines comparison (existing post), nasal sprays, child-friendly options, NZ pollen calendar

---

## 17. Deliverables per blog

Two files in `/blogs/`:

1. **`<slug>.html`** — single self-contained HTML file. Paste into Shopify blog editor's HTML view. Contains hero, TOC, all body, inline SVG charts, infographics, AI image placeholders with prompts in HTML comments, FAQ, disclaimer, author block, plus all four JSON-LD schema scripts.

2. **`<slug>.meta.md`** — SEO brief. Contains Shopify field values, meta title + description with character counts, keyword strategy, **textstat results**, featured image brief, **AI image prompts**, internal link map, outbound citation list, social share copy, post-publish QA checklist.

Plus one optional supporting file in `/research/`:

3. **`research/<topic>-research-dossier.md`** — for any new topic with no existing dossier. Captures verified citations, keyword research, NZ user questions, competitor gaps, regulatory context. Reused for refresh cycles + spoke posts.

---

## 18. Evidence sources for this playbook (v3)

- Ahrefs AIO citation studies — https://ahrefs.com/blog/ai-overview-citations-top-10/ and https://ahrefs.com/blog/short-vs-long-content-in-ai-overviews/
- Princeton GEO paper (Aggarwal et al. 2024, SIGKDD) — https://arxiv.org/pdf/2311.09735
- NZ Plain Language Act 2022 — https://www.legislation.govt.nz/act/public/2022/0054/latest/whole.html
- digital.govt.nz plain-language guidance — https://www.digital.govt.nz/standards-and-guidance/design-and-ux/content-design-guidance/writing-style/readability
- Kōrero Mārama (NZ health literacy) — https://www.health.govt.nz/system/files/2011-11/korero-marama.pdf
- OECD PIAAC 2023 NZ — https://www.oecd.org/en/publications/survey-of-adults-skills-2023-country-notes_ab4f6b8c-en/new-zealand_d67971ff-en.html
- AHRQ Health Literacy Universal Precautions Toolkit — https://www.ahrq.gov/sites/default/files/wysiwyg/professionals/quality-patient-safety/quality-resources/tools/literacy-toolkit/healthlittoolkit2_tool11.pdf
- NHS digital service manual "How we write" — https://service-manual.nhs.uk/content/how-we-write
- Healthify NZ "Why you can trust us" — https://healthify.nz/about-healthify/why-you-can-trust-us
- Healthline editorial process — https://www.healthline.com/about/process
- Cleveland Clinic OnBrand writing guidelines — https://my.clevelandclinic.org/onbrand/guidelines/writing
- Search Engine Land SQRG Sept 2025 — https://searchengineland.com/google-updates-search-quality-raters-guidelines-adding-ai-overview-examples-ymyl-definitions-461908
- 2024 RCT on health-content reading level — https://pmc.ncbi.nlm.nih.gov/articles/PMC12119439/
