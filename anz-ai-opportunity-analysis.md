# ANZ AI Opportunity Analysis — Which April–May 2026 Launches Are Worth Investigating for Australia & New Zealand

Compiled: 2026-05-20
Companion to `ai-businesses-april-may-2026.md`

---

## Methodology

For every notable launch in the April–May 2026 list, I scored:

1. **NZ competitor density** — how many local players are already shipping a comparable product (HIGH / MEDIUM / LOW / NONE).
2. **AU competitor density** — same, for Australia (matters because AU players often expand into NZ as the home market is too small alone).
3. **NZ-specific viability** — can this be started from NZ at all? (Capital intensity, talent depth, market size, time-zone advantage, regulatory tailwind.)
4. **Strategic moat for an ANZ founder** — what could a local founder offer that an offshore incumbent can't (data sovereignty, local integrations, language/culture, regulatory fit, Māori data sovereignty, AUKUS, IRD/ATO compliance, local channel)?

This is not a recommendation to start any specific company — it's a triage to tell you where to spend the next 4–8 weeks of investigation.

---

## The ANZ market reality you're operating in (must read before the ideas)

These facts shape what works and what doesn't, and explain the recommendations below:

- **NZ population: ~5.3M. AU population: ~27M.** Combined ANZ is smaller than Tokyo. Pure consumer plays are usually too small to fund without an export plan from day one. B2B vertical SaaS into specific regulated industries scales better.
- **NZ SME AI adoption gap:** 68% of NZ SMEs have no plans to even evaluate AI vs. 38% in Australia. 43% of non-adopters cite *lack of expertise* as the barrier — not cost, not tech. That's a *service/agent-led* gap, not a *product* gap.
- **No dedicated NZ AI regulator yet.** The country runs on the Privacy Act 2020 + Algorithm Charter for Aotearoa. Multiple legal commentators flagged this as a sovereignty risk when EU AI rules took effect in March 2026.
- **Māori data sovereignty** (WAI 2252, Te Tiriti, He Whakaputanga, UNDRIP) is a real, legally-grounded constraint. Sovereign AI infrastructure that *demonstrably* respects mātauranga Māori is a defensible local moat that offshore players cannot replicate.
- **Anthropic opened its 4th APAC office in Sydney** (announced this year). AU + NZ rank 4th and 8th globally in Claude.ai usage per capita. The model layer is here — the opportunity is the application layer.
- **Government has already endorsed ambient-AI scribes (Heidi, Lyrebird, iMedX, T-Pro, IntelliTek)** for public health. This category is *closed* — don't enter it.
- **The Series B → C gap is the biggest funding hole in Australia** (per Tech Council of Australia, AIIA, and Treasury commentary). Plan to either stay capital-efficient through B, or have a US/Asia growth round lined up.
- **Halter is NZ's first agritech unicorn** ($2B post-money) — agritech is funded and credible; *but* dairy/cattle is taken. Horticulture, viticulture, aquaculture, forestry remain underbuilt.
- **Lorikeet ($35M raised in <1 year) and Relevance AI dominate ANZ enterprise agent tooling.** Don't compete head-on; compete on vertical depth.
- **NZ flagships: Soul Machines (digital humans), Halter (dairy AI).** Both are export-led. That's the template.

---

## Competition heat map for every April–May 2026 launch in the prior file

Symbols: 🔴 too crowded in ANZ (avoid) · 🟡 moderate competition (vertical wedge only) · 🟢 white space (worth investigating) · ⚫ not viable from ANZ.

### Frontier labs & foundation models
| Company | ANZ competition | Verdict |
|---|---|---|
| Ineffable Intelligence, Recursive Superintelligence, Nof1, ModelBest, Project Prometheus | ⚫ | Capital intensity ($500M–$1B+ seed), researcher density and GPU access — impossible to fund or staff from NZ; difficult even from AU. Skip. |
| Anthropic / OpenAI JVs | ⚫ | Not replicable. |

### AI agents & autonomous workflow
| Company | ANZ competition | Verdict |
|---|---|---|
| **Sierra (enterprise agent)** | 🔴 AU: Lorikeet, Relevance AI. NZ: very thin. | Possible as a wedge into NZ-only regulated enterprise (banks, ACC, IRD, Health NZ). |
| **Skygen.AI (Computer-Use over legacy ERP/CRM/banking apps)** | 🟢 No direct ANZ player | **STRONG.** See deep-dive below. |
| **NeoCognition (self-learning enterprise agents)** | 🟢 Too early for ANZ | Watch, but US-led category. |
| **CopilotKit (app-native AI agents SDK)** | 🟢 None in ANZ | Niche dev-tools play; small ANZ buyer base. |
| **Pit (AI product team as a service for SMB ops)** | 🟢 No direct ANZ player | **STRONG.** See deep-dive. |
| **Era (software platform for AI gadgets)** | 🟢 | Hardware ecosystem too thin in NZ. |
| **Familiar Machines & Magic (consumer robot)** | ⚫ | Capex. |
| **Light Anchor / Elyra / ReasonBlocks (YC P26)** | 🟢 | Each is a US-led concept; localised ANZ takes are conceivable but require strong US-style execution. |
| **Sycamore (OS for autonomous enterprise AI)** | 🟢 No ANZ analog | Worth investigating for ANZ mid-market with NZ data residency moat. |
| **Edgerunner AI / WarClaw (military)** | 🟡 AU has AUKUS Pillar 2 demand | **Strong AU-only.** See deep-dive. |

### Coding & dev tools
| Company | ANZ competition | Verdict |
|---|---|---|
| **Factory (enterprise AI coding)** | 🔴 | Cursor / Devin / Anthropic / Copilot occupy this; no local moat. |
| **Gitar (agentic code review)** | 🟡 | Small ANZ developer base; tough TAM. |
| **Osaurus (Mac LLM server)** | 🟢 | Hobbyist category, not a fundable ANZ business. |
| **Cognition / Devin** | 🔴 | Closed. |

### Enterprise & B2B
| Company | ANZ competition | Verdict |
|---|---|---|
| **Whirl AI (enterprise system metadata + IT agents)** | 🟢 No ANZ analog | **STRONG.** See deep-dive — NZ govt + bank legacy estates are perfect ICP. |
| **Agaton (call-conversation analysis)** | 🟡 Lorikeet adjacent | Possible only if you go vertical (e.g., NZ healthcare contact centres, Māori-language compliance). |
| **Vast Data** | ⚫ | Infra capex. |
| **Upscale AI** | ⚫ | Infra capex. |
| **Synthetic (AI bookkeeping)** | 🟡 Nymbo (AU); Xero/MYOB AI integrations | NZ-only wedge possible if you go deep on IRD payday filing + GST. |
| **DesignVerse (enterprise software from a company's own docs)** | 🟢 None in ANZ | **STRONG.** See deep-dive — perfect for NZ SME "we have no IT" gap. |
| **Fresh People (AI talent management)** | 🟡 | Sapia.ai (AU) overlaps. |
| **Certifyde** | 🟢 | Watch. |

### Robotics & physical AI
| Company | ANZ competition | Verdict |
|---|---|---|
| **Genesis AI, Physical Intelligence, Sudu, humanoid unicorns** | ⚫ | Capex + supply chain. |
| **Automated Tire / SmartBay** | 🟡 | Niche. AU is plausible (large auto-service market); NZ too small. |

### Voice AI
| Company | ANZ competition | Verdict |
|---|---|---|
| **Vapi (voice agent platform)** | 🔴 | Already used by ANZ system integrators. |
| **Newo.ai (missed-call AI for SMB)** | 🔴 NZ already saturated: Talkify, AIVOLVE, SystemPros, HighPeak Digital, Trade AI Tools, Pulsebay, Voice-AI.co.nz, D3V; AU: Sophiie.ai, LocaliQ ANZ launched April 2026. | **Avoid.** This is the most crowded ANZ category. |
| **PollyReach** | 🔴 | Same. |

### Video & creative
| Company | ANZ competition | Verdict |
|---|---|---|
| **Innovative Dreams (AWS-backed Hollywood AI)** | 🟡 NZ has Wētā FX / Wētā Workshop / Park Road | **Interesting.** Wētā ecosystem + NZ film rebate is a defensible base. |
| **Novi AI (long-form video)** | 🟡 | Global category, no ANZ moat. |
| **Runway / OpenCV-founders video startup** | 🔴 | Closed at the top. |

### Legal AI
| Company | ANZ competition | Verdict |
|---|---|---|
| **Legora ($5.6B), Harvey ($11B), Anthropic Claude for Legal** | 🟢 in ANZ specifically — none are localised to NZ/AU statutes, NZLS rules, ASIC/FMA, or the Legal Services Act 2011 (NZ). | **STRONGEST single opportunity for NZ.** See deep-dive. |
| **Thirdfort** | 🟡 | KYC/AML for law firms — useful niche. |

### Healthcare AI
| Company | ANZ competition | Verdict |
|---|---|---|
| **AI medical scribes (Commure-style ambient dictation)** | 🔴 NZ govt has formally endorsed Heidi, Lyrebird, iMedX, T-Pro, IntelliTek across Te Whatu Ora. 1,250+ ED clinicians, expanding to mental-health crisis teams; 1,000 more licenses being procured. | **Closed category. Do not enter.** |
| **Commure-style RCM / clinical workflow ops (not scribing)** | 🟢 | **STRONG.** See deep-dive. |
| **Abridge** | 🔴 | Same as scribes. |

### Fintech AI
| Company | ANZ competition | Verdict |
|---|---|---|
| **Hiro (AI personal finance)** | 🟡 AU/NZ has Frollo, WeMoney, Sharesight | Possible only with Open Banking moat (CDR in AU; NZ Consumer Data Right coming). |
| **Decart.AI** | ⚫ | Generic. |
| **Nof1 (AI for markets)** | ⚫ | Researcher density needed. |

### Defense / security infrastructure
| Company | ANZ competition | Verdict |
|---|---|---|
| **Edgerunner AI / WarClaw** | 🟢 in AU (AUKUS, ASCA) | **STRONG for AU.** See deep-dive. |
| **Trent AI (agent security)** | 🟢 | Growing category, low ANZ competition. |
| **UK Sovereign-AI batch (Callosum, Prima Mente, Cosine, Cursive, Doubleword, Twig Bio, Odyssey)** | 🟢 | NZ has a structural sovereign-AI policy gap. **STRONG.** See deep-dive. |

### Consumer & social
| Company | ANZ competition | Verdict |
|---|---|---|
| **Series (iMessage social AI)** | ⚫ | US/iMessage cultural product. |
| **Hint (Martha Stewart AI home management)** | 🟢 **Total white space in ANZ.** | **STRONG.** See deep-dive. |
| **Ask Product Hunt AI, Claude Design** | ⚫ | Big-platform features. |

### Sales/marketing/GTM
| Company | ANZ competition | Verdict |
|---|---|---|
| **Trade Desk Koa Agents, Hightouch, Netomi, Actively** | 🔴 | Lorikeet + Relevance + global incumbents. |
| **Voker, Pipali, ShioriCode, Stitch 2.0, Wonder** | 🔴 | Global product-led category. |

---

## The 7 ideas worth investigating in depth for ANZ

Below: what they are, current ANZ market state, *why a local entrant still wins*, what to validate in weeks 1–8, and the realistic risks.

---

### 1. Legal AI built for ANZ statutes and law-firm workflows (Legora/Harvey-style, ANZ-native)

**The parent:** Legora hit $5.55B valuation on April 30, 2026, with Nvidia backing; Harvey hit $11B in March; Anthropic launched Claude for Legal (TechCrunch, May 12).

**ANZ market state:**
- Legora and Harvey are *not* localised to NZ statute law, ANZSCO, NZLS practice rules, Australian state Bars, ASIC/FMA, or AU's Privacy Act 1988 / NZ's Privacy Act 2020. They train on US/UK corpora.
- NZ legal hiring is recovering selectively; lawyers who can combine legal + AI are now differentiators (LawFuel).
- LexisNexis NZ is moving in but is a publisher, not a workflow agent.

**Why a local wins:**
- A model+RAG stack indexed on PCO statutes, NZ case law, NZLS guidance, Inland Revenue rulings, FMA notices, ASIC RGs, and the Federal Court Rules has a hard data moat.
- Trust + procurement: NZ/AU firms care about data residency (Privacy Act 2020) and Māori data sovereignty for tikanga-related matters. Offshore SaaS struggles to clear that bar at large firms (MinterEllison, Russell McVeagh, Bell Gully, Chapman Tripp).
- AU has 15K+ law firms; NZ has ~2K. Combined TAM is enough for a $50–100M ARR business at full penetration.

**Validate in weeks 1–8:**
- 20 founder-led customer interviews across NZLS top-30 firms and AU AmLaw/large-firm equivalents. Test willingness to pay $200–500/lawyer/month for a Harvey-equivalent that's NZ/AU-statute-native.
- Probe whether they'd switch from existing tools (LexisNexis, Thomson Reuters Practical Law, Harvey trials) for a local product.
- Pilot a single workflow: M&A due-diligence checklist + reg-change monitoring under FMA / ASIC.

**Risks:**
- Harvey/Legora may localise. *But* — they've shown no urgency in two-language markets; AU/NZ is English so they may treat it as solved.
- Big-4 (PwC, Deloitte) and Allens already deploying their own. You need to be 10× better on workflow.

**Why investigate:** Strongest single opportunity. Defensible, large, fundable, and the parents are unlocking the market.

---

### 2. AI home/property management (Hint-style) — built for the ANZ rental & owner-occupier market

**The parent:** Hint (Martha Stewart + Yih-Han Ma) raised $10M seed from Slow Ventures on May 13, 2026. Manages a home before things break — desktop + iOS this summer.

**ANZ market state:**
- ListAssist sold to a US firm and serves North America. NZ AI Homes is a property-management agency, not a SaaS.
- AU property managers use AI for *commercial* maintenance prediction. No consumer/owner product.
- 35% of NZ commercial real estate firms have begun AI implementation, but the consumer/homeowner side is empty.

**Why a local wins:**
- AU rental laws differ state-by-state (NSW/VIC/QLD). NZ has the Residential Tenancies Act 1986 + Healthy Homes Standards. A local product can natively handle Healthy Homes compliance, BWoF, ground-rent reviews, body corporates — none of which Hint touches.
- Distribution: partner with Trade Me Property, OneRoof, Domain, REA Group.
- The Healthy Homes deadline drove huge compliance spend in NZ in 2024–25; landlords are primed buyers.

**Validate:**
- Interview 30 NZ landlords (small-portfolio 1–10 properties — the majority) and 30 AU strata managers.
- Build a Healthy Homes compliance + predictive maintenance MVP for $0–$5k. Test as a Trade Me Property add-on.

**Risks:**
- Long sales cycle to landlords; consumer LTV unclear.
- Hint or EliseAI may expand to ANZ. Move fast.

**Why investigate:** True white space. Regulatory tailwinds (Healthy Homes, Tenancy Tribunal compliance). Cheap to validate.

---

### 3. AI-driven enterprise modernisation for legacy government & bank systems (Skygen/Whirl AI-style)

**The parents:**
- Skygen.AI (May 2026, $7M) — Computer-Use mode visually drives legacy CRM/ERP/banking apps.
- Whirl AI (April 1, $8.9M, ICONIQ) — ingests metadata across enterprise systems for IT change-management agents.

**ANZ market state:**
- NZ government runs on decades-old systems (Te Whatu Ora's IDF, IRD's START — a NZ$1.5B+ multi-year build, MSD's SWIFTT, ACC's Juno). The Auditor-General has repeatedly flagged digital-modernisation risk.
- Big-4 (ANZ Bank, Westpac, ASB, BNZ) and major super funds are still in COBOL/Java legacy migrations.
- No local AI agentic-modernisation player — local consultancies (Datacom, Theta, Catalyst IT, Advancer) do bespoke work, not productised AI.

**Why a local wins:**
- Data sovereignty is mandatory for govt contracts (DIA, GCDO, NZ Government All-of-Government cloud framework). Offshore-only SaaS is procurement-blocked.
- AOG cloud panels (Spark, Datacom, Catalyst Cloud) are local; native NZ-AU hosting via these is a moat.
- Procurement experience is a moat — incumbents like Skygen need 18+ months to learn how to sell to the NZ govt.

**Validate:**
- Conversations with GCDIO, DIA, MoH, IRD, Te Whatu Ora digital teams. Sprout Agritech and Callaghan Innovation can warm-intro.
- Whether a productised Computer-Use agent for a specific legacy workflow (e.g., MSD case-worker triage) can be sold standalone.

**Risks:**
- Long sales cycles (12–24 months for govt).
- Big-4 consultancies (Accenture, Deloitte, KPMG) will resist or rebadge.

**Why investigate:** TAM in just NZ govt + ANZ banks is >$500M. Skygen and Whirl have proved venture appetite. Sovereignty gates the offshore players out.

---

### 4. Pit-style "AI product team as a service" for ANZ SME operations

**The parent:** Pit (Stockholm, Voi/Klarna founders) raised €13.6M from a16z on May 7, 2026. Pit Studio + Pit Cloud — replaces spreadsheets/SaaS in enterprise ops, live with Voi, Tre, Stena, Kry.

**ANZ market state:**
- The NZ SME AI adoption gap (68% no plans, 43% cite lack of expertise) is a *service-led* gap, not a product gap.
- Lorikeet and Relevance AI build agents *for* large enterprises but don't replace SaaS sprawl for SMEs.
- Pit itself isn't in ANZ.

**Why a local wins:**
- ANZ SMEs run on Xero + MYOB + Shopify + Vend + Lightspeed — a tighter stack than Europe. A Pit-equivalent that ships *Xero-native* AI replacements (e.g., AP/AR ops, inventory, payroll) has unique distribution.
- Xero App Store partnership channel is real and underused.
- Cultural fit: NZ SMEs trust local providers more (per MBIE AI uptake research). Local CX is a moat.

**Validate:**
- 50 SME founder interviews across hospitality, trades, and retail. Are they willing to pay $300–$1,500/month for an AI-built ops layer?
- One paid pilot built on Xero + Shopify in 2–4 weeks.

**Risks:**
- Pit itself could expand to ANZ via a16z portfolio channels.
- "AI-built bespoke software" has high churn risk if you can't scale ops.

**Why investigate:** Validated globally, gap locally, easy to test cheaply.

---

### 5. Healthcare AI for ops/RCM/admin (Commure-style, not scribing)

**The parent:** Commure raised $70M at $7B post-money on May 19, 2026. RCM + clinical workflow tools, 500+ orgs, 3,000+ sites. Launched ambient dictation in any text field.

**ANZ market state:**
- **Avoid scribing.** Te Whatu Ora has endorsed Heidi + Lyrebird + iMedX + T-Pro + IntelliTek. Closed.
- **But:** RCM/admin/prior-auth/ACC claims/PHO ops are *not* covered. Te Whatu Ora's $14B annual budget includes huge admin overhead. AU's Medicare + private health funds (Bupa, Medibank, nib, HCF) have manual claims pipelines.
- ACC (NZ) processes 2M+ claims/year mostly via legacy workflows.

**Why a local wins:**
- ACC, Medicare and AU PHI claims are jurisdiction-specific data and rules. Commure can't ship a localised product without 18–24 months of compliance work.
- HISO (Health Information Standards Organisation NZ) data residency requirements gate offshore vendors.
- Health NZ procurement loves "approved-by-the-advisory-group" wins (like Heidi/Lyrebird) — credible local players win panel access.

**Validate:**
- Pilot one workflow: ACC claim triage or PHO funding-claim automation. Talk to 5 GP networks and 2 PHOs (ProCare, Tāmaki Health, Pegasus Health).
- Talk to Bupa/nib AU on prior-auth automation.

**Risks:**
- Health sales cycles 18 months+.
- Te Whatu Ora budgetary constraints in 2026.

**Why investigate:** Adjacent to a category that's already paid (scribes), but not yet covered. Capital-efficient if you start with a single payer/provider pilot.

---

### 6. AU defense AI for AUKUS Pillar 2 (Edgerunner / WarClaw-style)

**The parent:** Edgerunner AI launched WarClaw in April 2026 — agentic AI assistant for military, integrates Microsoft 365.

**ANZ market state:**
- Anduril Australia is hiring fast; Helsing has not entered AU.
- ASCA (Advanced Strategic Capabilities Accelerator) and Defence Innovation Hub are actively funding AI agents for AUKUS Pillar 2 (AI, quantum, hypersonics, undersea, EW).
- No local ANZ player at WarClaw's level for defense-tuned agentic AI.

**Why a local wins:**
- AUKUS clearance and FVEY data handling are *the* moat. US Edgerunner/Helsing need years of ITAR equivalents.
- AU defense procurement (~A$50B/year capability investment plan) is real and growing.
- DSTG and CSIRO Data61 partnerships available.

**Validate:**
- Conversations with ASCA, DSTG and Defence Innovation Hub.
- AUKUS Pillar 2 RFI/RFT calendar — pick a workflow (e.g., intel report fusion or sustainment AI).

**Risks:**
- Long procurement; security clearance friction; reputation risk if mis-handled.
- Capital-heavy and requires veteran/ex-defense founding team.

**Why investigate:** Defense is the one ANZ category where AU has a *better* set-up than NZ (Five Eyes, AUKUS, ASCA). High barrier = high moat.

---

### 7. Sovereign AI infrastructure for NZ regulated industries & Māori data

**The parents:** Callosum, Prima Mente, Cosine, Cursive, Doubleword, Twig Bio, Odyssey — UK's first Sovereign AI Unit cohort (Apr 16). Each is solving a sovereignty layer.

**ANZ market state:**
- NZ has *no* equivalent to the UK's £500M Sovereign AI Unit, despite the EU AI Act extraterritoriality risk (March 2026 commentary).
- Māori Data Sovereignty (Te Mana Raraunga) is a *legal* framework that demands local guardianship — no US-led product can satisfy WAI 2252.
- NZ AI Forum awarded NZIAT research grants but no productisation.

**Why a local wins:**
- Iwi-partnered sovereign cloud + AI gateway (à la Doubleword's "sovereign inference infrastructure") is a defensible local platform play. Iwi data-centre investment is already underway (Taiuru & Associates analysis).
- Health NZ, ACC, IRD, MoJ, Stats NZ, MoE — every Crown entity needs a sovereign inference path.
- The Privacy Act 2020 + Algorithm Charter + HISO + Te Tiriti obligations together form a regulatory wedge no offshore vendor can match.

**Validate:**
- Conversations with Te Mana Raraunga, DIA, GCDO, and 2–3 iwi data-trust executives.
- Confirm budget reality: GCDO 2026–27 budget line for sovereign AI.

**Risks:**
- Capital-intensive (data centres, dedicated inference hardware).
- Politically sensitive — partnership credibility with iwi is everything.

**Why investigate:** Highest "local-only" moat of any idea on this list. The product can't be cloned from Delaware.

---

## Honourable mentions — worth a short investigation but lower priority

| Idea | Why it's interesting | Why it's #8+ not top 7 |
|---|---|---|
| Vertical agritech AI beyond dairy (viticulture, aquaculture, horticulture) | Halter proves the funding path | Long iteration cycles; capex on hardware; Halter's wake covers the press |
| Local Trent-AI equivalent (agent runtime security) for ANZ banks under APRA CPS 234 / RBNZ BS11 | Real reg tailwind | Small TAM; better as a feature than a company |
| Wētā-ecosystem AI video tools (Innovative Dreams equivalent) | Park Road + Wētā FX is real industry depth | Hollywood pipeline integration is hard; Runway/Sora pace |
| NZ-specific Synthetic-style AI bookkeeping with IRD payday-filing depth | IRD APIs are accessible | Nymbo (AU) is already there; Xero is the gravity well |
| Tradies/SMB voice AI | Huge demand | **The most crowded ANZ category** — 8+ NZ players already shipping. AVOID. |
| Ambient-AI medical scribes | Funding flowing | Te Whatu Ora already endorsed 4 players. CLOSED. |

---

## What to do this week

If I were investigating these for real, I would, in this order:

1. **Pick 2 of the top 7 above** — one capital-light (Hint-style home management, or Pit-style ops), one capital-defensible (Legal AI ANZ-native, or Sovereign AI infra).
2. **Run 20 customer interviews in 14 days.** No code. Just calls. Bias-test the demand.
3. **Build one paid pilot in 2–4 weeks.** Charge for it, even $500. Paying customers de-risk the whole thesis.
4. **Look at funding alignment** — Icehouse Ventures, GD1, Movac, Blackbird (AU/NZ), Square Peg, AirTree, King River Capital, Folklore for AU. Callaghan Innovation R&D Tax Credit (NZ) and ARC/CRC (AU) for non-dilutive runway.
5. **Plan for export from day one.** ANZ alone won't fund a Series B unless you're targeting NZ govt or AU defense. Otherwise pick a category that exports to UK or SE Asia by Series A.

---

## Sources

- [Top 10 AI Companies Leading New Zealand's Tech Boom 2026 (IBTimes AU)](https://www.ibtimes.com.au/top-10-ai-companies-leading-new-zealands-tech-boom-2026-1867637)
- [Top 38 NZ Startups to Watch 2026 (Failory)](https://www.failory.com/startups/new-zealand)
- [NZ Tech Trends 2026 (Ecosystm)](https://ecosystm.io/insights/new-zealand-tech-trends-2026/)
- [AI Blueprint for Aotearoa to 2030 (Tech New Zealand)](https://technewzealand.org.nz/2026/05/06/ai-blueprint-for-aotearoa-a-refreshed-vision-to-2030/)
- [Addressing barriers to AI uptake in NZ (MBIE)](https://www.mbie.govt.nz/business-and-employment/economic-growth/digital-policy/new-zealands-ai-strategy-investing-with-confidence/addressing-barriers-to-ai-uptake-in-new-zealand)
- [Sovereign AI patterns for NZ regulated industries (ASI Solutions)](https://asi.co.nz/sovereign-ai-infrastructure-patterns-for-regulated-industries/)
- [Sovereign AI in NZ — Global innovation with local control (Ecosystm)](https://ecosystm.io/insights/sovereign-ai-new-zealand/)
- [Māori AI Sovereign Principles (Taiuru & Associates)](https://www.taiuru.co.nz/maori-ai-sovereignty-principles/)
- [NZ Faces Legal & Sovereignty Risks as EU AI Rules Take Effect (Business Scoop)](https://business.scoop.co.nz/2026/03/17/nz-faces-legal-and-sovereignty-risks-as-eu-ai-rules-take-effect-experts/)
- [Australian Tech Funding Landscape May 2026 (FBI)](https://fbi.org.au/blog/2026-05-11-australian-tech-ecosystem-funding-may-2026/)
- [Australian Startup Funding Q1 2026 $1.8B Report (Wholesale Investor)](https://www.wholesaleinvestor.com/australian-startup-funding-q1-2026/)
- [Tech Council of Australia — AI as 'real and immediate' opportunity](https://techcouncil.com.au/newsroom/media-release-tech-leaders-see-real-and-immediate-opportunity-in-ai-as-australias-tech-ecosystem-matures/)
- [Australia's AI Ecosystem (National AI Centre)](https://www.ai.gov.au/news-and-insights/reports/australias-artificial-intelligence-ecosystem-growth-and-opportunities)
- [10 Rising Australian Startups to Watch 2026 (IBTimes AU)](https://www.ibtimes.com.au/10-rising-australian-startups-watch-2026-ai-agents-space-tech-robotics-1862055)
- [Halter raises $220M Series E at $2B (SmartCompany)](https://www.smartcompany.com.au/startupsmart/australian-new-zealand-startup-funding-february-2026-193-million/)
- [Anthropic opens Sydney office](https://www.anthropic.com/news/sydney-fourth-office-asia-pacific)
- [Two AI medical scribes endorsed by Health NZ (HiNZ)](https://www.hinz.org.nz/news/706270/Two-AI-medical-scribes-endorsed-by-Health-NZ.htm)
- [NZ expanding national AI scribe rollout to emergency mental health (HealthcareITNews)](https://www.healthcareitnews.com/news/anz/new-zealand-expanding-national-ai-scribe-rollout-emergency-mental-health)
- [AI scribe wars heating up (Medical Republic)](https://www.medicalrepublic.com.au/ai-scribe-wars-heating-up/19900)
- [Best AI Scribe Software Australia 2026 (Grounded Scribe)](https://www.groundedscribe.com/compare/best-ai-scribe-australia)
- [AI Voice Agents in New Zealand (VoiceInfra)](https://voiceinfra.ai/countries/new-zealand)
- [LocaliQ ANZ launches AI Voice Agent (BusinessWire)](https://www.businesswire.com/news/home/20260414980136/en/LocaliQ-ANZ-Launches-AI-Voice-Agent-to-Help-Businesses-Capture-and-Convert-Every-Call)
- [Talkify NZ — AI phone agent for NZ trades](https://talkify.nz/)
- [SystemPros NZ AI voice agents](https://systempros.ai/locations/new-zealand/)
- [AIVOLVE — 24/7 AI Receptionist for NZ Trades](https://www.aivolve.co.nz/)
- [Sophiie.ai for AU trades](https://www.sophiie.ai/industries/trades)
- [Lorikeet $35M / Australia conversational AI (Callbox)](https://www.callboxinc.com.au/company-rankings/best-ai-companies-australia/)
- [Lorikeet beats Canva + Perplexity on a16z spend report (SmartCompany)](https://www.smartcompany.com.au/artificial-intelligence/a16z-ai-application-startup-spending-report-lorikeet-beats-canva-perplexity/)
- [Relevance AI competitor analysis](https://www.g2.com/products/lorikeet/competitors/alternatives)
- [Nymbo — AU Xero AI alternative](https://nymbo.com.au/)
- [Accounting software faces AI rivals in bookkeeping shift (ITBrief NZ)](https://itbrief.co.nz/story/accounting-software-faces-ai-rivals-in-bookkeeping-shift)
- [ListAssist NZ acquired by Inside Real Estate (NZ Herald)](https://www.nzherald.co.nz/business/auckland-ai-start-up-listassist-sells-to-us-firm-inside-real-estate/GMGMPJAIANA47ASN3LLC6CQZAY/)
- [The AI-Only Real Estate Agency: How a Fully Automated Brand Could Disrupt NZ & Australia (PropertyNoise)](https://www.propertynoise.co.nz/ai-only-real-estate-agency-nz-australia/)
- [NZ Legal Market Recovery (LawFuel)](https://www.lawfuel.com/nzs-legal-market-recovery-has-started-but-dont-expect-champagne-in-the-boardroom-yet/)
- [Anthropic gets in on legal AI (TechCrunch)](https://techcrunch.com/2026/05/12/the-ai-legal-services-industry-is-heating-up-anthropic-is-getting-in-on-the-action/)
- [LexisNexis NZ Legal AI](https://www.lexisnexis.com/en-nz/legal-artificial-intelligence)
- [UK Agritech Innovators heading to NZ via Sprout Agritech (Scoop)](https://www.scoop.co.nz/stories/BU2605/S00255/uk-agritech-innovators-heading-to-new-zealand-to-road-test-the-future-of-farming.htm)
- [Implementing AI in property NZ (WT Partnership)](https://wtpartnership.co.nz/insights/implementing-ai-in-property-from-buzzword-to-practical-tools/)
- [Te Whatu Ora — Generative AI guidance](https://www.tewhatuora.govt.nz/health-services-and-programmes/digital-health/generative-ai-and-large-language-points)
