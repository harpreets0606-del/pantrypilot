# Business Context — Bargain Chemist

> This file is the source of truth for "what is Bargain Chemist." Update only when the business itself changes.

## Identity

- **Legal/trading name**: Bargain Chemist
- **Website**: https://www.bargainchemist.co.nz (Shopify Plus)
- **Founder/owner email**: peter@bargainchemist.co.nz (decision-maker)
- **Marketing email**: hello@bargainchemist.co.nz
- **Transactional email**: orders@bargainchemist.co.nz
- **Phone**: 021 355 643
- **Address**: 1 Radcliffe Road, Belfast, Christchurch 8051, Canterbury, New Zealand (HQ)
- **Industry**: Ecommerce, Health & Beauty (online pharmacy + retail chain)
- **Markets**: New Zealand (primary) + Australia (ships)
- **Currency**: NZD
- **Timezone**: Pacific/Auckland
- **Tagline (official, from Shopify)**: "NZ's cheapest chemist"
- **Brand description (official)**: "Our policy: NZ's cheapest chemist. We are a 100% Kiwi-owned online pharmacy, providing quality healthcare products at prices you can afford."
- **Business model**: 100% NZ-owned discount pharmacy chain — physical stores + online + Click & Collect + vaccinations + prescriptions
- **Locations confirmed**: Petone, Mt Roskill, Mt Wellington, WestCity, South Dunedin, Whanganui (Bargain Plus brand). NZ-wide chain.
- **Catalog size**: 20,000+ SKUs

## Confirmed value propositions (use in marketing)

1. **NZ's cheapest chemist** — bold value-led tagline
2. **100% Kiwi-owned** — local trust
3. **Price Beat Guarantee** — beat any competitor's price by 10% (page: `/pages/pricebeatguarantee`)
4. **Free shipping on orders $79+** to NZ urban (FAQs confirmed)
5. **Click & Collect free** in-store pickup at selected locations
6. **Vaccinations** bookable in-store (flu, shingles)
7. **Prescriptions filled** including specialised programs (Wegovy / Mounjaro for weight loss)

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

## Confirmed by user (2026-05-06)
- **Top priority next 90d**: Total revenue growth
- **SMS**: NOT in scope this round — email only
- **`[Z]` prefix**: internal naming convention (NOT an agency); use it freely
- **Welcome Series Website status**: user doesn't know why it's draft — cleared to investigate + activate

## Still open (to resolve with user)

1. Are there products or categories with margin pressure or strategic priority?
2. Any campaigns or flows the user is *especially* proud of or worried about?
3. Compliance constraints I should hardcode into recommendations? (e.g. "never recommend campaigns to POM-buyers without pharmacist review")
4. Pharmacy registration number for footer
5. Lead pharmacist name for medicine-promotion emails
6. DKIM / SPF / DMARC current status
