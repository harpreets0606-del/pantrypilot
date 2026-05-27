# Darpan — Validation Register

> **The rule:** validate every assumption *first*, to ~95% where research can, and be
> honest about what research cannot reach. Nothing past Stage 0 gets built until the
> items below are green to the founder's satisfaction.
>
> **Two axes (don't confuse them):**
> - **Validation** = is the assumption proven with data?
> - **Build** = does code exist? (A separate question — tracked as `⚙️` so it's never
>   mistaken for validation.)
>
> **The honest ceiling:** market facts and demand *signals* can be validated to ~95% by
> research. Whether *this customer pays for this offer at this price* — **behavioral** —
> cannot. Only a live test closes it. Claiming otherwise would be false certainty.

**Status legend:** `✅` Validated (data-backed, ≳90%) · `🟡` Signal-only (directional,
~50–80%) · `🔴` Unvalidated (needs live/primary data) · `⚙️` Build task (not a validation
question).

---

## A. Market & demand
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| A1 | Large, fast-growing online-astrology market | ✅ | 95% | India app mkt $0.24B→$8.8B by 2034 (~49% CAGR); 62% of Indians consult astrologers; +48% downloads since 2020 | — |
| A2 | Kundli/marriage matching is a core use case | ✅ | 90% | Vedic = ~46% of revenue; matching central to category | — |
| A3 | Manglik/Mangal Dosha is a major matching factor | ✅ | 90% | ~42–45% have some form; ~70% believe; key matchmaking parameter | — |
| A4 | NRI diaspora is large & high-value | ✅ | 95% | 35.4M diaspora; UAE & US ~17% each; +30% willingness; $120B remittances | — |

## B. Customer & willingness-to-pay
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| B1 | Incumbents have a trust problem users resent | ✅ | 90% | Documented fear-selling, "fake astrologer," billing complaints across platforms + regulatory concern | — |
| B2 | Users *want* an honest/trustworthy alternative | 🟡 | 70% | Strong pain signal; "honest astrology" niche exists. But wanting ≠ switching | Live test / interviews |
| **B3** | **Users will PAY for our offer at target price (NRI)** | **🔴** | **—** | The core unknown. Research cannot prove purchase behavior | **Smoke test (the gate — see below)** |
| B4 | *Citations specifically* drive conversion (vs generic trust) | 🟡 | 40% | No online demand found for "cited astrology"; trust ≠ footnotes | Live A/B: trust-only vs citation messaging |
| B5 | NRIs pay a premium | ✅ | 85% | +30% per-minute; matrimony premium; reports $15–49 | Confirm exact price points in test |

## C. Competition & differentiation
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| C1 | AstroTalk dominant; per-minute ≈80% revenue → innovator's dilemma | ✅ | 90% | ₹1,210 Cr FY25; ~30M users; ~40% share; ~80% from consults | — |
| C2 | Trust/transparency is an unoccupied, hard-to-copy position | 🟡 | 65% | Logical + small honest-astrology players exist; unproven at scale | Test + watch incumbent response |
| C3 | Regulatory tailwind favors transparency | ✅ | 80% | ASCI bans "100% guarantee"; CCPA penalties ₹10–50 lakh; advocacy for verified credentials | — |

## D. Supply side
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| D1 | Abundant astrologer supply exists | ✅ | 90% | ~48k astrologers on AstroTalk alone | — |
| D2 | Astrologers dissatisfied w/ high commissions (recruiting lever) | 🟡 | 55% | AstroTalk takes 20–50%; comp rated below average. **But no direct evidence of dissatisfaction/migration found** | Interview practicing astrologers |
| **D3** | **Good astrologers will join under no-upsell/integrity rules (adverse selection)** | **🔴** | **—** | Their income partly *is* the upsell we ban | Primary research: recruit a pilot cohort |

## E. Product / technical
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| E1 | Charts computable exactly (deterministic) | ✅ | 100% | Built + tested; real Mesha Sankranti astronomy check passes | — |
| E2 | 36-point Gun Milan computable | ✅ | 95% | Built + tested; high-weight kootas exact (Yoni/Vashya simplified) | Refine Yoni/Vashya matrices |
| E3 | Manglik / Mangal Dosha detection | ⚙️ | — | **Not built** — needed for credible marriage matching (A3) | Build it |
| E4 | AI can produce *reliably cited* interpretations | 🟡 | 60% | Citations API exists, but LLMs fabricate & RAG still hallucinates | Build + eval harness on a sample |
| E5 | Knowledge-Map curation feasible at reasonable cost | 🔴 | — | The hardest, uncosted piece | Scoped spike on one vertical (Gun Milan) |

## F. Channel & distribution
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| F1 | Web PWA avoids App Store rejection + 30% cut | ✅ | 95% | Apple 4.3 rejects astrology; IAP 15–30% vs ~3% web; iOS PWA push (16.4+) | — |
| F2 | WhatsApp effective for diaspora engagement | 🟡 | 70% | Widely held; limited direct data | Measure in pilot |
| F3 | Smoke-test demand is cheaply measurable | ✅ | 90% | LP conversion median 2.35% / opt-in ~10%; CPL ~$70–166 | — |

## G. Legal / compliance / licensing
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| G1 | Swiss Ephemeris needs commercial license for proprietary SaaS | ✅ | 100% | Dual AGPL/commercial; CHF 750 + 400/ea | Buy license before public deploy |
| G2 | DPDP / GDPR / cold-email obligations known | ✅ | 90% | DPDP (deadline May 2027); CAN-SPAM/CASL/GDPR/PECR per-country | — |
| G3 | Must avoid "guaranteed" claims; disclaimers ≠ full shield | ✅ | 85% | ASCI + CCPA (₹10–50 lakh); UK/EU CPR; "entertainment only" not a complete defence | Legal review of copy |

## H. Unit economics / cost
| ID | Assumption | Status | Conf | Evidence | To close |
|---|---|---|---|---|---|
| H1 | AI inference cost negligible (cents/report) | ✅ | 90% | Opus $5/$25, caching −90%, batch −50% per M tokens | — |
| H2 | Build cost staging ($0.5–2k / $15–60k / $250k–1M+) | 🟡 | 60% | Ranges; geography- and hire-vs-founder-dependent | Firm up with a chosen team/quote |
| H3 | CAC sustainable vs LTV (NRI) | 🔴 | — | Depends on smoke-test CPL + future retention/ARPU | Smoke test CPL + cohort data |

---

## Scoreboard
- **✅ Validated (~95%): 17** · **🟡 Signal-only: 7** · **🔴 Needs live/primary data: 4** · **⚙️ Build task: 1**
- The 🔴 items: **B3 paid demand (the gate)**, D3 supply adverse-selection, E5 Knowledge-Map feasibility, H3 CAC↔LTV.

## The single gate — B3, and how the smoke test closes it
Everything else is downstream of one question: **will NRIs pay for this?** The test:

1. **Drive targeted NRI traffic** (US/UAE; Meta/Google) to the Stage-0 page.
2. **Measure three funnel steps:**
   - Visitor → completes a free match (engagement).
   - Match → submits email for the full report (soft intent).
   - **Match → clicks a *priced* "Get my sourced report — $X" / "Reserve" button (hard, willingness-to-pay intent).** ← the real signal.
3. **Go / no-go thresholds** (anchored to benchmarks; median LP conversion ~2.35%, warm opt-in ~10%, lead-magnet ~23%):
   - **GO:** ≥ ~10% of match-completers give email **and** ≥ ~3–5% click the priced CTA, at **CPL ≲ $30–50** (well under the $70–166 norm, given a warm niche).
   - **NO-GO / rethink:** strong free engagement but priced-CTA click near zero → people want it free, not paid → revisit model.
   - **PIVOT signal:** trust-messaging variant beats citation variant decisively (B4) → lead on trust, keep citations as the proof layer.

**Honest note:** even a strong result is ~the best research-plus-behavioral evidence achievable pre-launch — it validates *intent*, not booked revenue. That's the ceiling, and it's enough to justify Stage-1 spend.

## Sources
New this round:
- [Manglik prevalence & belief — sociological analysis (PDF)](https://serialsjournals.com/abstract/29102_8-abhinandan.pdf) · [AstroPuja](https://astropuja.com/blog/post/how-maanglik-dosha-affects-marriage-prospects-career)
- [Landing-page conversion benchmarks — WordStream](https://www.wordstream.com/blog/conversion-rate-benchmarks) · [CPL by industry — First Page Sage](https://firstpagesage.com/reports/average-cost-per-lead-by-industry/)
- [ASCI Code](https://www.ascionline.in/the-asci-code/) · [Astrology apps & rising regulatory concern — Storyboard18](https://www.storyboard18.com/how-it-works/biz-of-belief-how-indias-astrology-apps-are-turning-faith-into-fortune-amid-rising-regulatory-concerns-83027.htm) · [UK/EU consumer law & astrology](https://www.astrology.co.uk/news/cpr.htm)

All other rows cite sources already recorded in `ARCHITECTURE.md` §16.
