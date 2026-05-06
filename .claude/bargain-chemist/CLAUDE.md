# Bargain Chemist — Operating Instructions

You are analysing **Bargain Chemist** (https://www.bargainchemist.co.nz), a New Zealand ecommerce pharmacy. Klaviyo account ID: `XCgiqg`. Industry: Ecommerce, Health & Beauty. Currency: NZD. Timezone: Pacific/Auckland.

## How to work on this account

### Always do these things

1. **Read `memory/business-context.md`** first when starting any analytical task — it contains brand voice, regulatory context, customer personas.
2. **Check `memory/decisions-log.md`** (last 14 days) — to see what's been tried, what worked, what predictions are still open.
3. **Use the right playbook** — for repeatable tasks (`playbooks/weekly-report.md`, `playbooks/campaign-postmortem.md`, etc.), follow it step by step.
4. **At session end, append to `memory/decisions-log.md`** — date, what was recommended, what data backed it, and a falsifiable prediction.

### Data sources (check `INTEGRATIONS.md` for live status)

- **Klaviyo MCP** ✅ — full access to profiles, campaigns, flows, metrics, segments
- **Shopify MCP** ✅ — orders, products, customers, inventory, ShopifyQL analytics
- **Zapier MCP / Tables** ⏳ — pending setup (will hold persistent metric snapshots)
- **GA4 Data API** ⏳ — pending OAuth (true revenue attribution lives here)
- **Google Ads API** ⏳ — pending OAuth (CPA, ROAS, search terms)
- **BigQuery** ⏳ — pending (event-level GA4 data for cohort/LTV analysis)

### Pulling data — defaults

- **Date ranges**: prefer last 28 days for most metrics, with last 28 days of *prior* period as comparison.
- **Currency**: always NZD. Don't convert.
- **Timezone**: Pacific/Auckland for all date-bucketing.
- **Pagination**: Klaviyo and GA4 paginate via cursors — always exhaust pagination for full datasets unless analysing a sample.

### Reasoning rules

- **Significance > magnitude.** A 20% lift on n=50 is noise. State sample size and don't draw conclusions from <500 events unless you flag the limitation.
- **Always compare to baseline.** Numbers without context are useless. Pull from `kpi-baselines.md` or compute prior-period comparison.
- **Attribution is fragile.** Klaviyo's "attributed revenue" uses last-touch within an attribution window. GA4 default is data-driven. They will disagree. Reconcile, don't pick one.
- **Causation ≠ correlation.** When recommending, state confidence level and what would falsify the recommendation.

### Output format for analyses

Every analytical output must end with:

```
## TL;DR
- One sentence answer
- Top 3 actions in priority order

## Confidence: [Low / Medium / High]
## Falsifiable prediction:
If we do X, metric Y will move by Z within N days.
## Decision logged: [yes/no — append to decisions-log.md if recommending action]
```

### When to spawn subagents

Use specialists in `agents/` in parallel when the task requires data from 2+ platforms:
- `klaviyo-analyst` — email/SMS performance, flow audits, segment health
- `shopify-analyst` — orders, AOV, product velocity, inventory
- `ads-analyst` — Google Ads + GA4 performance, ROAS, attribution
- `synthesizer` — receives all three outputs, produces unified narrative

For single-platform questions, just use the relevant MCP tools directly.

### Things to never do

- Send a campaign or modify a flow without explicit user approval.
- Update a profile or add to a list in bulk without dry-run + approval.
- Recommend an action without stating the prediction and confidence.
- Treat Klaviyo's revenue numbers as ground truth — Shopify is ground truth for orders.
