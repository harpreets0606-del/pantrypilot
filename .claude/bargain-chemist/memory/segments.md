# Segments — Inventory & Rationale

> Every segment that exists (or should exist) for Bargain Chemist. Each entry must answer: **why does this segment exist, and what action does it enable?**

## How to add a segment

```
### [Segment name]
- **Klaviyo ID**: <id once created>
- **Definition**: <plain-English rules>
- **Why it exists**: <action this segment enables>
- **Created**: <date>
- **Last reviewed**: <date>
- **Member count**: <number>
- **Health check**: <growth/decay/stable>
- **Decision rule**: <when to retire this segment>
```

## Active segments

_To be populated by running `klaviyo_get_segments` once Phase 1 is complete._

## Recommended segments to build (Health & Beauty / NZ Pharmacy)

These are common high-leverage segments. Recommend and validate against actual customer data before creating.

### Engagement-based
- **Highly engaged 30d** — opened or clicked email in last 30 days. Used as "deliverability-safe" send list.
- **Engaged 90d** — opened in last 90 days. Default broad campaign list.
- **Cold subscribers (90d+)** — for sunset/winback flows.
- **Never-engaged** — joined >30d ago, zero opens. Suppress from broadcasts.

### Purchase-based
- **First-time buyers (last 30d)** — welcome series + first-repeat nudge.
- **Repeat buyers (2+ orders)** — loyalty messaging.
- **VIP (top 10% predicted CLV)** — exclusive offers, early access.
- **Lapsed customers (no order in 120d, prior buyer)** — winback flow eligible.
- **Avg-order high vs low** — used to tailor offer thresholds.

### Predictive (Klaviyo native — requires data threshold met)
- **High churn risk + high CLV** — retention priority. *Highest-leverage segment.*
- **Expected next order in next 14 days** — pre-emptive trigger.
- **Low churn risk + low CLV** — neutral, don't over-message.

### Behavioural
- **Browsed but didn't purchase (last 7d)** — viewed product event, no order.
- **Abandoned cart, not yet recovered** — ensure flow is firing.
- **Subscription-product buyers** — segmented by category for replenishment timing.

### Compliance-aware (NZ pharmacy specific)
- **Pharmacy-medicine buyers** — handled separately; broad promotional sends restricted.
- **Prescription customers** — different messaging rules; confirm with user.

## Segments to avoid

- "All subscribers" sends — almost always destroys deliverability.
- Geo-based segments without business reason — adds complexity, rarely improves results.
- Demographic segments without data backing — predicted_gender alone is insufficient.
