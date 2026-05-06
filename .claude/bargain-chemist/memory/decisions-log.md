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
- **Confidence**: Medium — structure is sound but value depends on user actually feeding the system (logging decisions, refreshing baselines).
- **Outcome**: TBD
- **Learning**: TBD
