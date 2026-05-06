# Bargain Chemist Analytics Memory

Persistent memory and playbooks for analysing Bargain Chemist (bargainchemist.co.nz) across Klaviyo, Shopify, GA4, and Google Ads.

## Layout

```
.claude/bargain-chemist/
├── CLAUDE.md              # Loaded at session start — how to work on this account
├── INTEGRATIONS.md        # Connection status for every data source
├── memory/                # Source of truth Claude reads + appends to
│   ├── business-context.md    # Brand, products, voice, market — rarely changes
│   ├── kpi-baselines.md       # Current performance benchmarks — refreshed monthly
│   ├── segments.md            # Audience segments + the reason each exists
│   ├── decisions-log.md       # Append-only: every recommendation + outcome
│   └── hypotheses.md          # Active experiments — hypothesis, test, result
├── playbooks/             # Standard recipes Claude follows
│   ├── weekly-report.md
│   ├── campaign-postmortem.md
│   └── churn-investigation.md
└── agents/                # Specialist subagent definitions
    ├── klaviyo-analyst.md
    ├── shopify-analyst.md
    ├── ads-analyst.md
    └── synthesizer.md
```

## How it works

1. **Session start** → `CLAUDE.md` is read. It points Claude at relevant memory files for the task at hand.
2. **During work** → Claude reads playbooks and follows them. Specialist subagents are spawned for parallel data pulls.
3. **Session end** → Claude appends key findings, decisions, and predictions to `decisions-log.md`.
4. **Next session** → Claude reads recent decisions log entries and checks if predictions came true.

## What's missing

Anything not listed in `INTEGRATIONS.md` as ✅ connected requires user action. See that file for the current setup checklist.
