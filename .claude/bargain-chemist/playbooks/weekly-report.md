# Playbook: Weekly Report

**Trigger**: User says "weekly report", "how did this week go", or runs `/weekly-report` (when slash command is built).

## Inputs

- Date range: last 7 complete days (Mon–Sun in Pacific/Auckland)
- Comparison: same days, previous week
- Comparison 2: same days, 4 weeks ago (to spot trend vs. seasonality)

## Steps

### 1. Spawn 3 analysts in parallel

- `klaviyo-analyst` — campaigns sent this week, flow performance, list growth, top/bottom campaigns
- `shopify-analyst` — orders, revenue, AOV, top products, new vs. returning customers, refunds
- `ads-analyst` — Google Ads spend, ROAS, top campaigns, search term anomalies *(skip if Ads not connected)*

Each writes findings to `metrics_daily` Zapier Table (when connected) and returns a structured summary.

### 2. Read prior week's `decisions-log.md` entries

Identify any predictions that resolved this week. Mark outcomes.

### 3. Synthesizer agent produces the unified report

Required structure:

```markdown
# Weekly Report — [date range]

## Headline
One sentence: did this week beat last week? By what?

## The numbers
| Metric | This week | Last week | Δ % | 4w ago | Trend |
| Revenue | ... | ... | ... | ... | ... |
| Orders | ... | ... | ... | ... | ... |
| AOV | ... | ... | ... | ... | ... |
| New customers | ... | ... | ... | ... | ... |
| Email rev/recipient | ... | ... | ... | ... | ... |
| ROAS (paid) | ... | ... | ... | ... | ... |

## What went well
- 2-3 specific wins with data

## What underperformed
- 2-3 specific issues with data

## Anomalies worth investigating
- Anything >2 std dev from baseline
- Any segment with sudden behaviour change

## Predictions resolved
- Decision X from [date]: prediction was Y, outcome was Z. Verdict: correct/wrong/partial.

## Recommendations for next week
- 3 actions max, in priority order
- Each with a falsifiable prediction

## Confidence: [Low/Med/High]
## Logged to decisions-log.md: yes
```

### 4. Append recommendations to `decisions-log.md`

One entry per recommendation, with date + prediction + confidence.

## Quality bar

- Every number has a comparison.
- No recommendation without a prediction.
- No prediction without a confidence level.
- If a metric requires a connection that isn't live, say so explicitly — don't fabricate.

## Common pitfalls

- **Holiday weeks** — flag if NZ public holiday or school holidays distort comparison.
- **Campaign vs. flow attribution** — Klaviyo attributes to whichever touched last. Don't double-count.
- **Refunds** — Shopify revenue includes them as negatives in some views; pull `gross_sales` not `total_sales` for revenue, or be explicit.
- **Sample size** — for new segments or low-volume flows, state n and don't conclude from <100 events.
