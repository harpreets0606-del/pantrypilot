# Playbook: Campaign Postmortem

**Trigger**: User asks for a deep dive on a specific campaign, or after any campaign that performed >2x or <0.5x median.

## Inputs

- Campaign ID (Klaviyo)
- (Optional) comparison campaign IDs

## Steps

### 1. Pull campaign metadata
- `klaviyo_get_campaign` — name, send time, audiences, channel
- `klaviyo_get_campaign_report` — all performance metrics
- If A/B test: pull each variation separately

### 2. Pull segment context
- For each included list/segment: size at send time (estimate from `metrics_daily` if available)
- Engagement profile of segment: Klaviyo predictive scores distribution if available

### 3. Pull attributed orders from Shopify
- Cross-reference order timestamps with campaign send time
- Identify orders within 5-day attribution window
- Check for products purchased — does it match the campaign's promoted products?

### 4. Compare to baseline
- vs. campaign baseline in `kpi-baselines.md`
- vs. last 5 campaigns to same segment
- vs. same campaign type sent at same day-of-week

### 5. Diagnose

Use this diagnostic tree:

```
Open rate low?
├── Subject line problem → A/B test next time
├── Sender name / preview text issue
├── Deliverability — check spam rate, bounce rate, inbox provider split
└── Wrong segment — engagement profile mismatch

Open rate fine, click rate low?
├── Content not matching subject line promise
├── Too many CTAs / unclear primary action
├── Mobile rendering issue
└── Offer not compelling

Click rate fine, conversion low?
├── Landing page mismatch
├── Price / offer not landing
├── Stock issues — products clicked through were OOS
└── Checkout friction

Everything fine, revenue low?
├── Low AOV per attributed order — was offer the issue?
├── Cannibalisation from concurrent flow / campaign
└── Attribution window too short — revenue is delayed
```

### 6. Output

```markdown
# Campaign Postmortem: [name]
**Sent**: [date/time]  **Segment**: [name, n=]  **Channel**: email/SMS

## Performance
| Metric | This campaign | Segment baseline | Last 5 to segment |
| ... | ... | ... | ... |

## Verdict
[Outperformed / Met / Underperformed expectations]

## Root cause
The biggest driver of the result, with evidence.

## What to repeat
- ...

## What to change
- ...

## Test ideas added to hypotheses.md
- ...
```

### 7. Update memory
- If this campaign type is now a baseline, update `kpi-baselines.md`
- If a new test idea emerged, append to `hypotheses.md` backlog
- If a recommendation came out of it, append to `decisions-log.md`
