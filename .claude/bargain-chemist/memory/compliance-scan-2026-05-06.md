# Compliance Scan — Klaviyo Campaigns + Flows (NZ Pharmacy)

**Date**: 2026-05-06
**Scope**: 92 campaigns sent in last 90 days + 15 flows (subject lines + flow names)
**Limitation**: Body copy + flow message HTML inaccessible — this scan is subject-line + name only

---

## RULES BEING APPLIED (from Medsafe + Pharmacy Council NZ)

1. **Prescription-Only Medicines (POM)**: NEVER promote. Marketing emails cannot reference these by brand or active ingredient. Only transactional ("your prescription is ready").
2. **Pharmacy-Only Medicines**: only promote with disclaimer + pharmacy registration number + no therapeutic claims + no comparisons to prescription.
3. **General sales medicines**: standard advertising rules apply.
4. **Dietary supplements**: structure-function claims only. Never "cures", "treats", "prevents".
5. **No therapeutic claims** in subject lines for restricted medicines.
6. **No comparisons to prescription medicines.**
7. **No fake doctor/authority endorsements.**

---

## CAMPAIGNS FLAGGED (subject lines containing pharmacy-only / restricted medicine names)

| Campaign | Subject | Risk level | Issue |
|----------|---------|------------|-------|
| **Codral Solus - August 2025** | "Kiwis have an ally in fighting cold & flu symptoms with Codral & Sudafed" | 🔴 **HIGH** | Names BOTH Codral + Sudafed (pseudoephedrine versions = pharmacy-only); makes therapeutic claim ("ally in fighting cold & flu symptoms"); "Buy it in-store now!" preview suggests counter purchase |
| **Dulcolax + Buscopan Solus - March 2026** | (subject not in sample) | 🟡 MEDIUM | Buscopan (hyoscine butylbromide) is pharmacy-only in NZ; if subject names it, same risk as Codral |
| **Telfast Solus - February 2026** | (subject not in sample) | 🟡 MEDIUM | Higher-dose Telfast is pharmacy-only; lower doses general sales — depends on which formulation |
| **Nicorette Solus - January 2026** | "Get ready to quit smoking with Nicorette" | 🟢 LOW | Nicotine NRT is general sales since 2022 NZ. Subject is benefit-led not therapeutic claim. Probably OK. |
| **Claratyne Solus - January 2026** | (subject not in sample) | 🟢 LOW | Loratadine is general sales in NZ |
| **Levrix Solus - December 2025** | (subject not in sample) | 🟢 LOW | Levocetirizine is general sales in NZ |
| **Zaditen Solus - September 2025** | (subject not in sample) | 🟡 MEDIUM | Ketotifen eye drops can be pharmacy-only depending on strength |

### Summary
- **42 of 92 (45.6%) campaigns are "Solus" supplier-sponsored emails**
- **7 campaigns** name medicines that *could* be pharmacy-only depending on formulation
- **1 confirmed high-risk subject line** (Codral) which I have visibility on

---

## CAMPAIGNS FLAGGED (other compliance concerns)

### Therapeutic claims in subject lines
- **Codral**: "fighting cold & flu symptoms with Codral & Sudafed" — therapeutic claim
- **Performance fuel with up to 30% Off EDLP!** (Price Smash Sports & Nutrition) — borderline; "performance fuel" is structure-function, OK for supplements

### Internal jargon leaking to customers
- **EDLP** appears in 2+ subject lines / preview texts ("Save up to 35% off EDLP!", "30% Off EDLP!") — this is "everyday low price", supplier/internal terminology customers don't recognise

### Preview text issues
- **Nicorette Solus**: empty preview text — wasted real estate

---

## FLOWS FLAGGED

| Flow | Status | Concern |
|------|--------|---------|
| [Z] Flu Season - Winter Wellness | LIVE | Winter wellness category includes Codral + Sudafed (pharmacy-only). If flow content names these = same compliance issue as Codral campaign |
| [Z] Post-Purchase Series | MANUAL (paused) | User confirmed some flows paused for compliance — this fits the pattern |
| [Z] Welcome Series - Website | DRAFT | Could be paused due to incentive being a coupon for restricted product? Investigate |
| [Z] Order Confirmation | DRAFT | Confirms an order — could include POM in confirmation. If so, that's transactional and OK; if it cross-sells POM = problem |

---

## RECOMMENDED COMPLIANCE GATE PLAYBOOK

### Pre-send checklist (every campaign + flow message)

```
☐ Product classification verified (POM / Pharmacy-only / General / Supplement)
☐ Subject line names no POM (Wegovy, Mounjaro, Ozempic, etc.)
☐ Subject line names no Pharmacy-only medicine (or includes registration + disclaimer if it does)
☐ No therapeutic claims for medicines in subject ("treats", "cures", "fights symptoms")
☐ Body copy follows NZ supplement claim rules ("supports", "may help", not "treats")
☐ Pharmacy registration number visible in footer
☐ Pharmacist name disclosed if medicine promoted
☐ Required disclaimer present: "Always read the label and follow directions for use. If symptoms persist, consult your pharmacist or doctor."
☐ No comparison to prescription medicines
☐ No fake doctor/authority endorsements
☐ Testimonials free of disease claims
☐ Pharmacy manager / compliance officer signed off
```

### Hardcoded "do not send" word list (for AI copy review)

When reviewing email content, FLAG any of these for human review before sending:
- **POM brand names**: Wegovy, Mounjaro, Ozempic, Saxenda, Rybelsus, Trulicity, Ventolin, Seretide, Symbicort, Atrovent, Pulmicort, Champix
- **POM active ingredients**: semaglutide, tirzepatide, liraglutide, salbutamol, fluticasone, salmeterol, budesonide, varenicline
- **Pharmacy-only brand names that need checking**: Codral (pseudoephedrine variant), Sudafed, Buscopan, Telfast 180mg+, Voltaren rapid 25, Nurofen rapid, Panadeine
- **Therapeutic-claim words for medicines**: cures, treats, prevents, eliminates, eradicates, defeats
- **Comparative words against prescription**: "better than prescription", "alternative to prescription", "without a script"

### Recommended workflow

1. **Solus campaigns get a compliance pre-check** by pharmacy lead before send (or AI scan against above list, then human approval if any flag)
2. **Supplier marketing copy** must be reviewed and rewritten if needed — don't accept supplier copy verbatim
3. **Major campaigns** (>50k recipients) get **ANZA TAPS pre-vetting** (~$150–300, 5–10 days) for legal cover
4. **Flow templates audited quarterly** for compliance drift

---

## QUESTIONS TO RESOLVE

1. **Has Bargain Chemist been formally warned by Medsafe / Pharmacy Council** in the past? (e.g. Codral Solus from Aug 2025 — did this trigger anything?)
2. **Who is the lead compliance pharmacist** at Bargain Chemist?
3. **What's the pharmacy registration number** that should appear in email footers?
4. **Have any campaigns ever been pulled / had to be re-sent due to compliance**?
5. **Does Bargain Chemist use ANZA TAPS pre-vetting** for major campaigns?

---

## CONFIDENCE

- 🟢 **High** on the compliance rules themselves (sourced from Medsafe Marketing Guidelines + research)
- 🟢 **High** on which campaigns named which medicines (jq grep on names)
- 🟡 **Medium** on actual risk level — depends on body copy I can't see; subject line + preview alone may not constitute the offence; full email body might mitigate or worsen
- 🔴 **Low** on whether existing campaigns *currently* include the required disclaimers + registration # — I cannot read template HTML
