# Can you legally run a Legal AI / Immigration AI / Tenancy AI business in NZ & AU?

Compiled: 2026-05-20

> **Important caveat.** This is research, not legal advice. Before incorporating or going live, you must engage an actual NZ-admitted lawyer (for NZ) and an Australian-admitted lawyer (for each AU state you trade in). The penalties for getting this wrong in immigration are serious (up to 7 years' prison in NZ); the penalties for unauthorised legal practice are also criminal in both jurisdictions.

---

## Top-line verdict

| Category | NZ | AU | Bottom line |
|---|---|---|---|
| **Legal AI** | ✅ Legal as a B2B tool for lawyers · ⚠️ "legal information" to consumers is a grey zone · ❌ "legal advice" to consumers without a lawyer is restricted | Same | **Yes, with the right structure.** Sell to lawyers, not as a lawyer. |
| **Immigration AI** | ❌ Consumer-facing advice is a criminal offence (up to 7 yrs / $100k) · ✅ B2B for licensed advisers, or operating as a licensed adviser | ❌ Section 280 Migration Act 1958 limits this to "authorised persons" · OMARA guidance (Mar 2026) confirms AI must be used *by* a registered migration agent | **Yes, but only by partnering with / employing a licensed adviser or RMA, or building B2B-only tools.** |
| **Tenancy AI** | ✅ As SaaS — but NZ has a new "light-touch" property manager regulation regime (training, licensing, practice standards) from 2025 onward · ⚠️ direct consumer tenancy advice is risky (see 1News April 2026 story) | ✅ As SaaS — but state-by-state property manager licensing applies if you act as a property manager · ⚠️ consumer advice subject to Australian Consumer Law + Privacy Act | **Yes, the most permissive of the three.** Stay a software vendor, not a service provider. |

---

## 1. Legal AI

### What the law says (NZ)

**Lawyers and Conveyancers Act 2006:**
- Section 6 defines "lawyer" and "legal services."
- Reserved areas of work (court advocacy, conveyancing, probate, trust administration) are restricted to admitted lawyers / qualified conveyancers with current practising certificates.
- Anyone holding out as a lawyer or providing "regulated services" without authorisation commits an offence under the Act.
- New Zealand Law Society regulates standards; NZ courts published GenAI guidelines for lawyers in December 2023.

**Key distinction in NZ law:**
- **Legal information** = telling someone what the law *says* (e.g., "the Residential Tenancies Act gives you 21 days' notice"). Generally fine.
- **Legal advice** = applying law to a specific person's situation (e.g., "in your case, you should serve 21 days' notice and here's the wording"). Restricted to lawyers in many contexts; absolutely restricted in reserved areas.
- "Holding out as a lawyer" or charging fees for legal services as a non-lawyer is an offence.

### What the law says (AU)

- **Legal Profession Uniform Law** (operating in NSW, VIC, WA — others have parallel state Acts in QLD, SA, TAS, NT, ACT).
- **Australian Solicitors' Conduct Rules 2015 (ASCR)** + Barristers' Conduct Rules apply to solicitors and barristers.
- Joint statement (NSW Law Society + Victorian Legal Services Board + WA Legal Practice Board, 6 Dec 2024) on AI use in practice.
- **NSW Supreme Court Practice Note (3 Feb 2025)** specifically on generative AI in litigation — formal guidelines.
- Each state has unauthorised practice of law offences (e.g., NSW *Legal Profession Uniform Law* s.10).

### What you can legally do

✅ **B2B legal AI for law firms / corporate counsel.** This is what LawVu ($400M valuation, Tauranga), AI Legal Assistant (230+ ANZ firms), Harvey, Legora, Spellbook all do. Selling a tool *to* a lawyer is not regulated as legal practice — the lawyer remains responsible for advice given to their client. Both NZ Law Society and AU joint statement explicitly permit this with caveats around accuracy and confidentiality.

✅ **Legal information products for consumers** — for example, "explain this clause" or "summarise the Residential Tenancies Act." Phrase as information, never as advice. Add disclaimers. Watch the line carefully.

✅ **Operating as a licensed legal practice that uses AI** — incorporate as an Incorporated Law Firm (NZ) or under the Uniform Law (AU). The lawyer is on the hook; the AI is a tool.

### What you can NOT legally do

❌ Selling AI-generated "legal advice" to consumers without a lawyer in the loop.
❌ Holding out the product as "lawyer-equivalent" or letting users believe it gives binding legal advice.
❌ Providing reserved-area services (court advocacy, conveyancing, probate) in NZ without qualifications.
❌ Charging clients for legal services as an unqualified entity.

### Practical structure for a legal AI startup in ANZ

- **Option A: Pure SaaS for law firms.** Cleanest path. No regulatory licensing required for the company. (LawVu, AI Legal Assistant model.)
- **Option B: "Legal information" consumer product** — works, but high care needed on disclaimers, marketing, and not crossing into specific-fact advice. Add a "talk to a real lawyer" button. (Spellbook hybrid model.)
- **Option C: "Lawyer-on-staff" AI firm** — register as an incorporated law firm and use AI behind the scenes. Pay a salaried admitted lawyer to be the responsible practitioner. (More expensive but unlocks consumer revenue.)

### Sources
- [Lawyers and Conveyancers Act 2006 (NZ Legislation)](https://www.legislation.govt.nz/act/public/2006/0001/latest/whole.html)
- [The Lawyers and Conveyancers Act Explained (LegalPath)](https://legalpath.co.nz/the-lawyers-and-conveyancers-act-explained)
- [GenAI Guidelines for Lawyers (Courts of NZ, Dec 2023)](https://www.courtsofnz.govt.nz/assets/6-Going-to-Court/practice-directions/practice-guidelines/all-benches/20231207-GenAI-Guidelines-Lawyers.pdf)
- [AI and the Legal Profession (Law Council of Australia)](https://lawcouncil.au/policy-agenda/advancing-the-profession/artificial-intelligence-and-the-legal-profession)
- [Use of AI in Legal Practice (ACT Law Society)](https://www.actlawsociety.asn.au/article/use-of-ai-in-legal-practice)
- [LPBWA AI Joint Statement](https://www.lpbwa.org.au/artificial-intelligence-joint-statement)
- [NSW Supreme Court's new rules for AI in legal practice (Barry Nilsson)](https://bnlaw.com.au/knowledge-hub/insights/nsw-supreme-courts-new-rules-for-ai-in-legal-practice/)

---

## 2. Immigration AI

This is the most dangerous of the three. Both NZ and AU treat unlicensed immigration advice as a criminal offence — and AU's OMARA explicitly addressed AI in March 2026.

### What the law says (NZ) — strictest jurisdiction

**Immigration Advisers Licensing Act 2007:**
- Anyone giving New Zealand immigration advice must be **licensed** by the Immigration Advisers Authority (IAA) or **exempt** (lawyers, MPs, certain government officials).
- **Applies extraterritorially** — even if you provide advice from outside NZ, the Act applies.
- **Penalties:** Up to **7 years' imprisonment** and a **fine of up to NZ$100,000** for providing immigration advice without a licence.
- IAA actively investigates and prosecutes — multiple convictions every year (see IACADT decisions).

The IAA defines "immigration advice" broadly: any advice in connection with visa applications, immigration matters, or NZ immigration law applied to a specific person. Generic information is allowed; person-specific is not.

### What the law says (AU)

**Migration Act 1958 (Cth), section 280:**
- Immigration assistance can only be provided by "authorised persons":
  - Registered Migration Agents (RMAs) listed on the OMARA register, OR
  - Australian legal practitioners (admitted lawyers).
- Operating outside this is a criminal offence under the Migration Act.

**OMARA guidance on AI (March 2026):**
- **"It is not legal to use AI to write or help with a visa application unless it is done by someone who is an authorised person."** (Direct quote from OMARA guidance reporting.)
- RMAs **may** use AI tools, but remain **fully responsible** for accuracy and adequacy regardless of AI involvement.
- The Migration Agents Code of Conduct continues to apply.
- OMARA may discipline RMAs for AI misuse (e.g., hallucinated citations, undisclosed AI use).

### What you can legally do

✅ **B2B AI tools for licensed advisers / RMAs.** Workflow automation, document drafting templates, eligibility scoring, evidence checklists, application form generation that a licensed agent reviews — fine. This is the cleanest path.

✅ **Operate as / partner with a licensed adviser.** You can build an "AI-assisted immigration consultancy" where every customer is matched to a licensed adviser (NZ) or RMA (AU) who personally reviews and submits. The AI is the engine; the licensed human carries the regulatory responsibility.

✅ **Generic, non-personalised information products.** "Here's the published Skilled Migrant Category points threshold" is information. Be careful — even a chatbot that asks for the user's personal details and gives a personalised answer is providing advice, not information.

### What you can NOT legally do

❌ A consumer-facing chatbot that answers personalised visa questions for a fee — without a licensed adviser in the loop. This is a clear breach in both jurisdictions.
❌ Auto-generating visa applications and submitting them on behalf of a customer. (Section 280, plus IAA equivalent.)
❌ Marketing as an "AI immigration adviser" when no licensed adviser is involved — even if free.
❌ Providing advice from outside NZ to NZ-bound migrants without a NZ licence (extraterritorial provision).

### Practical structure for an immigration AI startup in ANZ

- **Option A: SaaS for RMAs and NZ Licensed Immigration Advisers.** Cleanest. Tool, not advice. Sell to the ~3,500 RMAs in AU and ~650 LIAs in NZ. Small market but defensible.
- **Option B: "AI-first immigration firm"** — incorporate, hire/contract licensed advisers, build AI workflow under the bonnet, sell direct to consumers. Higher revenue but the licensed adviser is your gating constraint and personally accountable.
- **Option C: Generic information + lead-gen to RMAs/LIAs.** Free content, monetise via referrals to licensed advisers. Avoids regulatory exposure but lower margin.

### Why a startup is still possible here

- Despite the regulatory minefield, there's a real workflow gap: RMAs and LIAs spend hours on document preparation, eligibility analysis, and form completion for repetitive cases. A productised AI workflow tool sold to them is a clean B2B play with no immigration regulator exposure for you (only for them, as they're already regulated).
- NZ Immigration alone processes ~2M visa applications/year. AU is bigger. RMAs/LIAs make NZ$2k–10k per case. They will pay for tools that reduce hours per case.

### Sources
- [Immigration Advisers Licensing Act 2007 (NZ Legislation)](https://www.legislation.govt.nz/act/public/2007/15/en/latest/)
- [Offences under the Immigration Advisers Licensing Act (IAA)](https://www.iaa.govt.nz/about-us/what-we-do/offences-under-the-immigration-advisers-licensing-act/)
- [Who can give immigration advice (Immigration NZ)](https://www.immigration.govt.nz/assist-migrants-and-students/advise-migrants/regulations-and-licensing/regulations)
- [Office of the Migration Agents Registration Authority (OMARA)](https://www.mara.gov.au/)
- [OMARA Guidance on AI in Migration Assistance, March 2026 (Migration Alliance)](https://migrationalliance.com.au/immigration-daily-news/entry/2026-03-omara-guidance-on-the-use-of-artificial-intelligence-in-migration-assistance.html)
- [OMARA AI guidance summary (This is Australia Lawyers)](https://tia.au/news/omara-guidance-on-ai-in-migration-assistance/)
- [Migration Act 1958 (AU Legislation)](https://www.legislation.gov.au/Details/C2018C00427) — section 280
- [Department of Home Affairs' Regulation of Migration Agents (ANAO audit)](https://www.anao.gov.au/work/performance-audit/department-home-affairs-regulation-migration-agents)

---

## 3. Tenancy AI

The most permissive of the three — but not unregulated. Both jurisdictions are moving toward stricter property manager licensing, and the consumer-side has real risk.

### What the law says (NZ)

**Residential Tenancies Act 1986** governs landlord/tenant relationships.

**Major changes in 2025:**
- 90-day no-cause terminations reinstated.
- 21-day notice from tenants.
- Pet ownership requests (1 Dec 2025).
- Stronger protections against retaliatory termination.

**Residential Property Managers regulation (new, "light-touch" regime):**
- Government introducing national standards: training, licensing, practice standards.
- Property managers will need to be licensed.
- Administered through Te Tūāpapa Kura Kāinga (Ministry of Housing and Urban Development).

**Important real example:** In April 2026, 1News reported that an AI advised a tenant to ask for a $40,000 rent reduction. The Tenancy Tribunal awarded her $80. The AI hallucinated a much stronger legal position than actually existed. This is the consumer-facing tenancy AI risk in one story.

### What the law says (AU)

- **Each state has its own Residential Tenancies Act** (NSW, VIC, QLD, WA, SA, TAS, NT, ACT).
- **Property manager licensing is state-by-state:**
  - **NSW:** Real estate licence or registration (Fair Trading NSW).
  - **VIC:** Real estate agent's licence or employment by a licensed agent (Consumer Affairs Victoria).
  - **QLD:** Real estate licence (Office of Fair Trading QLD).
  - **WA:** Registered with DMIRS, supervised by licensed real estate agent.
  - **TAS, SA, ACT, NT:** Each has its own scheme.
- **Australian Consumer Law (federal)** applies to all consumer dealings.
- **Privacy Act 1988** — OAIC has flagged that AI-generated personal information (including hallucinations) is treated as collected personal information; the agency is responsible for accuracy.

### What you can legally do

✅ **Tenancy software for landlords and property managers** — pure SaaS. Rentally, Keyhook, Re-Leased, MRI Palace, myRent operate legally in this space. You provide tools; users do their own compliance. (This is the dominant model.)

✅ **Healthy Homes / compliance checklists / receipt-scanning expense tracking** — fine as a tool.

✅ **Tenant-facing tenancy-information products** — phrase as information, link to Tenancy Services / Citizens Advice Bureau / community law centres for advice.

✅ **AI-assisted property management business** — if you operate it, you need the relevant state licence (AU) or the forthcoming NZ property manager licence.

### What you can NOT legally do (or shouldn't)

⚠️ **Consumer-facing AI that gives personalised legal advice on tenancy disputes** — the 1News April 2026 story shows this can backfire spectacularly. Not strictly illegal in the same way as immigration, but exposes you to:
- Privacy Act 2020 (NZ) / Privacy Act 1988 (AU) liability for inaccurate personal data outputs.
- Australian Consumer Law misleading-or-deceptive-conduct claims (s.18 ACL).
- Fair Trading Act 1986 (NZ) equivalent.
- Defamation risk if AI characterises landlords inaccurately.
- Reputational and Tenancy Tribunal cost orders against your users (when they relied on your wrong advice).

❌ **Operating as a property manager** in any AU state without the relevant licence.
❌ **Operating as a property manager in NZ** without meeting the new "light-touch" regulation (coming into effect through the new regime).

### Practical structure for a tenancy AI startup in ANZ

- **Option A: Pure SaaS for landlords / property managers** — Rentally / Keyhook model. No specific regulatory licensing required for the company.
- **Option B: SaaS for tenants** that organises documents and surfaces *information* (with disclaimers and "talk to community law" CTAs) — works, but flag risk explicitly.
- **Option C: AI-assisted property management business** — get the relevant state licence (AU) or new NZ regime registration; AI is your operational efficiency layer.
- **Option D: Strata / body corporate operations** — same regulatory considerations, but a much less competitive niche per the prior reality check.

### Sources
- [Residential Tenancies Act 1986 (NZ Legislation)](https://www.legislation.govt.nz/act/public/1986/0120/latest/DLM94278.html)
- [New regulations for residential property managers (Tenancy Services NZ)](https://www.tenancy.govt.nz/about-tenancy-services/news/new-regulations-for-residential-property-managers-and-organisations/)
- [Regulation of residential property managers (HUD NZ)](https://www.hud.govt.nz/our-work/regulation-of-residential-property-managers)
- [What's New in the Residential Tenancies Act 2025 (Point Property Management)](https://www.pointpropertymanagement.co.nz/articles/whats-new-in-the-residential-tenancies-act-2025-update/)
- [AI tells tenant she should ask for $40k — tribunal hands her $80 (1News, April 2026)](https://www.1news.co.nz/2026/04/21/ai-tells-tenant-she-should-ask-for-40k-tribunal-hands-her-80/)
- [Understanding Property Management Laws in Australia (Lawpath)](https://lawpath.com.au/blog/understanding-property-management-laws)
- [Property management — Consumer Affairs Victoria](https://www.consumer.vic.gov.au/licensing-and-registration/estate-agents/running-your-business/property-management)
- [Property Management Laws (LegalVision)](https://legalvision.com.au/property-management/)
- [AI Compliance Property Management (PMVA)](https://www.pmva.com.au/ai-compliance-property-management/)

---

## What I'd actually recommend

Rank-ordered by *how easy it is to launch legally*, given the verified regulatory frameworks above:

| Rank | Idea | Why |
|---|---|---|
| 🥇 | **Tenancy AI as SaaS for landlords / property managers** | Lowest regulatory friction. Clear precedent (Rentally, Keyhook). No specific licensing needed for the company. |
| 🥈 | **Legal AI as B2B for lawyers** | Clear permitted path (joint statement, NSW Practice Note). LawVu and AI Legal Assistant prove it's funded. But — see the prior reality check; you need a vertical wedge. |
| 🥉 | **Immigration AI as B2B for RMAs and LIAs** | Possible but small TAM. Avoid consumer-facing. |

The two structures that get you in prison:
- ❌ Consumer-facing immigration "AI adviser" — 7 years' prison and NZ$100k in NZ; criminal offence in AU.
- ❌ Consumer-facing legal "AI lawyer" — unauthorised legal practice offence in both jurisdictions.

The structure that gets you sued (not prosecuted):
- ⚠️ Consumer-facing tenancy "AI adviser" giving personalised advice — Privacy Act, ACL/Fair Trading, defamation, Tribunal-cost exposure. The 1News April 2026 story is the cautionary tale.

---

## Practical next steps (whichever you pick)

1. **Engage a NZ-admitted lawyer** familiar with the relevant Act (Lawyers and Conveyancers Act for legal; IAA-experienced for immigration; tenancy specialist for property). Costs ~NZ$2k–5k for a structuring memo.
2. **Engage an AU-admitted lawyer** in the state(s) you'll trade in. AU is state-by-state for legal and property; federal for immigration (Migration Act).
3. **For immigration specifically:** call IAA in NZ and OMARA in AU directly. Both have public guidance lines and have given written rulings on novel structures.
4. **Draft customer-facing T&Cs and disclaimers** that explicitly carve out the regulated-advice line. Lawyers do this for ~NZ$3k–8k.
5. **For consumer-facing products:** have a clear "this is not legal/immigration/tenancy advice — see a licensed [adviser/lawyer/property manager] for personalised advice" disclaimer surfaced *before* the user uses the product, not buried in T&Cs.

---

## Honest assessment

- **The two ideas above with the highest *startup* potential (legal and immigration) also have the highest *regulatory* friction.** That's not a bug — it's the moat. The licensing barriers that make these markets hard to enter are the same barriers that protect you once you're in.
- **The tenancy idea is the lowest friction but also the lowest moat.** Lots of existing SaaS players (per the reality check).
- **If I were ranking these for an ANZ founder with no legal background:** Tenancy AI SaaS > Legal AI B2B > Immigration AI B2B. The first is launchable in weeks; the others need 3–6 months of regulatory structuring before you can take a paid customer.

Final caveat repeated: **this is research, not legal advice.** Engage your own lawyer before building.
