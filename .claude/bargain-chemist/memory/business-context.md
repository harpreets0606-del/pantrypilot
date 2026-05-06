# Business Context — Bargain Chemist

> This file is the source of truth for "what is Bargain Chemist." Update only when the business itself changes.

## Identity

- **Legal/trading name**: Bargain Chemist
- **Website**: https://www.bargainchemist.co.nz
- **Email**: hello@bargainchemist.co.nz
- **Address**: 1 Radcliffe Road, Belfast, Christchurch 8051, Canterbury, New Zealand
- **Industry**: Ecommerce, Health & Beauty (online pharmacy)
- **Market**: New Zealand
- **Currency**: NZD
- **Timezone**: Pacific/Auckland

## Regulatory & operational context

- New Zealand pharmacy — subject to Medsafe, Pharmacy Council of NZ, and Therapeutic Products Act regulations.
- **Pharmacy-only medicines (POM)**: cannot be advertised with price as a primary message; restricted in marketing.
- **Restricted medicines**: certain claims about efficacy are prohibited.
- **Prescription medicines**: separate workflow, different fulfilment rules.
- This affects what Klaviyo campaigns can say, what segments can target, and what GA4 events represent.

## Customer base — to be filled in

- [ ] Top 5 customer personas (run analysis once data is connected)
- [ ] Geographic distribution of customers (NZ regional split)
- [ ] Repeat purchase rate (Shopify)
- [ ] Avg order value (Shopify)
- [ ] Subscription/auto-replenish flows in use (Y/N — confirm in Shopify)

## Product catalogue — to be filled in

- [ ] Number of SKUs
- [ ] Top categories by revenue
- [ ] High-margin vs. high-volume product mix
- [ ] Seasonal products (hayfever, winter cold/flu, summer skincare)
- [ ] Subscription-eligible products

## Brand voice — to be filled in

- [ ] Tone: friendly / clinical / promotional?
- [ ] Common phrases used in successful campaigns
- [ ] Phrases/topics to avoid (legal + brand reasons)
- [ ] Visual identity notes for image-heavy campaigns

## Marketing channels in use

| Channel | Confirmed? | Klaviyo metric name | Notes |
|---------|------------|---------------------|-------|
| Email (Klaviyo) | ✅ | `Received Email` etc. | Default sender: hello@bargainchemist.co.nz |
| SMS (Klaviyo) | ❓ | `Received SMS` | Confirm if active in NZ |
| Google Ads (Search) | ❓ | — | Connect Ads API to confirm |
| Google Shopping / PMax | ❓ | — | Confirm via Google Ads |
| Meta Ads (FB/IG) | ❓ | — | Confirm if in scope |
| Organic search | ❓ | — | GSC needed |
| Direct | — | — | Tracked in GA4 |

## Open questions to resolve with user

1. What are the top 3 business goals for the next 90 days? (revenue, new-customer acquisition, repeat rate, AOV?)
2. Are there products or categories with margin pressure or strategic priority?
3. Any campaigns or flows the user is *especially* proud of or worried about?
4. Compliance constraints I should hardcode into recommendations? (e.g. "never recommend campaigns to POM-buyers without pharmacist review")
