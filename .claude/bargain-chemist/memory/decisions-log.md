# Decisions Log — Append-Only

> Every recommendation Claude makes goes here, with a falsifiable prediction. Future sessions read this to (a) know what's been tried and (b) check whether predictions came true.

## Format

```
## YYYY-MM-DD — <short title>
- **Context**: what was being analysed, what data
- **Recommendation**: what was proposed
- **Action taken**: <yes/no/partial — fill in next session>
- **Prediction**: if we do X, metric Y will move by Z within N days
- **Confidence**: Low / Medium / High
- **Outcome** (filled in later): what actually happened
- **Learning**: what this teaches us about Bargain Chemist
```

## Open predictions (awaiting outcome)

_None yet._

## Closed entries

_None yet — log starts when Phase 1 is complete._

---

## 2026-05-06 — Memory architecture initialised

- **Context**: User asked Claude to design persistent memory + integrations for Bargain Chemist analytics
- **Recommendation**: 3-layer architecture — repo files, Zapier Tables, hooks. Specialist subagents for parallel work. Phased rollout starting with file-based memory.
- **Action taken**: Created `.claude/bargain-chemist/` structure with CLAUDE.md, memory/, playbooks/, agents/. Awaiting Zapier + GA4 + Ads connection for Phase 2.
- **Prediction**: With this structure in place + Phase 2 integrations connected, weekly analysis time drops from "re-pull everything every session" to "diff against last week's snapshot." Untested.
- **Confidence**: Medium — structure is sound but value depends on user actually feeding the system.
- **Outcome**: TBD
- **Learning**: TBD

## 2026-05-06 — Klaviyo audit completed; user confirmed key facts

- **Context**: Full audit pulled from Klaviyo MCP. 3 research agents synthesised best practices + benchmarks + brand voice corpus. Memory written: klaviyo-benchmarks.md, klaviyo-best-practices.md, brand-voice-design-template.md (DRAFT), account-audit-2026-05-06.md, gaps.md.
- **User confirmed (logged as facts)**:
  - Top 90-day priority: total revenue growth
  - SMS not in scope this round
  - `[Z]` is internal naming, not external agency — can use freely
  - Welcome Series Website draft status: investigate + activate
- **Top 4 critical gaps identified** (high confidence): C1 Welcome Series in draft, C2 Sender address mixed, C3 Order Confirmation 0% conversion (no marketing element), C4 Click rates universally below benchmark
- **Outstanding unknowns blocking 95% confidence**: template HTML inaccessible (MCP 401), DKIM/SPF/DMARC unverified, list/segment counts not pulled, Reputation Repair Audience origin
- **Action taken**: None yet — holding until further user answers on questions 5–20 in `gaps.md`
- **Prediction (untested)**: activating Welcome Series + fixing C2-C3 alone will lift email-attributed revenue ~10-20% within 60 days. Falsifiable: compare Welcome Series 60-day revenue post-activation vs the 537-recipient × $1.68 RPR = $902 baseline over 90 days.
- **Confidence**: Medium-High on findings, Low on prediction (no comparable baseline yet).
- **Outcome**: TBD
- **Learning**: TBD
