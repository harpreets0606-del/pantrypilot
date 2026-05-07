# Playbook: Churn Investigation

**Trigger**: Churn risk distribution shifts (more profiles moving to High), repeat purchase rate drops, or user asks "are we losing customers?".

## Inputs

- Compare current churn-risk distribution (Klaviyo predictive) to 30 days ago
- Repeat purchase rate (Shopify) — current vs. trailing 90d

## Steps

### 1. Quantify the shift

- Pull profiles by `churn_risk_level` (Low / Medium / High) — current
- Compare to 30d-prior snapshot in Zapier Tables `metrics_daily` (when available; if not, note baseline-missing)
- Pull Shopify repeat purchase rate (90d cohort)

### 2. Identify *which* customers moved

Using Klaviyo `predicted_clv` × `churn_risk_level`:

- **High CLV + now High churn** → retention priority. List these profiles. Spot patterns: same product category? same acquisition channel? same time-since-last-order bucket?
- **Medium CLV + now High churn** → cluster into segment, evaluate winback economics.
- **Low CLV + High churn** → usually fine to let go; don't waste budget.

### 3. Look for a cause

Check what changed in the lookback window:

- **Marketing changes**: Did flow X get paused? Did campaign cadence drop? Did a key promotion end?
- **Product changes**: Did a popular product go out of stock? Did pricing change? New competitor?
- **Operational changes**: Shipping delays? Customer service complaints?
- **External**: Seasonal (NZ winter starting? Hayfever season ending?), economic, competitor activity

### 4. Recommendations

Tiered response:

**Immediate (this week)**:
- Activate winback flow for High-CLV-High-Churn profiles if not already running
- Review and unpause any paused flows that target lapsed customers

**Short term (next 4 weeks)**:
- Test winback levers (NO COUPONS — see `memory/no-coupon-strategy.md`): free-shipping threshold drop ($79 → $49), early access to new arrivals, pharmacist concierge consultation, or "what would bring you back?" survey on the High-CLV-High-Churn segment
- Review acquisition source quality — are we acquiring customers who churn fast? Update CAC payback assumptions in `kpi-baselines.md`

**Strategic**:
- If churn is acquisition-channel-correlated, recommend reweighting paid budget
- If churn is product-correlated, flag for merchandising review

### 5. Output

```markdown
# Churn Investigation — [date]

## Headline
[Net churn risk increased/decreased by X% over Y days. Driven by Z.]

## Who moved
- High-CLV-High-Churn count: X (was Y, +Z)
- Common attributes: [data-backed]

## Likely causes (ranked by evidence)
1. ... (evidence: ...)
2. ...

## Recommendations
- Immediate: ...
- Short term: ...

## Predictions
- If we run winback on High-CLV-High-Churn: expect X% reactivation within 30 days at $Y revenue.

## Confidence: [Low/Med/High]
## Logged: yes
```

## Pitfalls

- Churn risk is a model output — it can swing from data freshness (e.g., a slow week of orders shifts predictions). Always check whether the shift is real customer behaviour or a model artefact by cross-referencing actual order data.
- Don't conflate "high churn risk" with "definitely lost." It's a probability.
- NZ pharmacy customers may have legitimate gaps between purchases (seasonal medications). Adjust expected-days-between-orders by category.
