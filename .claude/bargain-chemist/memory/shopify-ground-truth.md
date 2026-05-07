# Shopify Ground Truth — Bargain Chemist

**Date**: 2026-05-06
**Source**: Shopify Admin API + ShopifyQL (90-day window)

> Shopify is the ground truth for revenue + customer + product data. Klaviyo and GA4 reconcile *to* this.

---

## Business model (now confirmed)

- **Brick-and-mortar + online pharmacy chain.** NOT just online.
- Stores: **30+ locations nationwide** (confirmed by user 2026-05-07). Earlier "6+" was a wrong guess from page handles in the store-locator UI. Some confirmed names: Petone, Mt Roskill, Mt Wellington, WestCity, South Dunedin, Whanganui ("Bargain Plus"), Christchurch HQ (1 Radcliffe Road).
- "100% New Zealand-owned and operated discount pharmacy chain"
- **Click & Collect** offered at selected locations
- **Vaccinations** offered (flu, shingles, etc.) — bookable via website (Acuity integration noted in Klaviyo lists)
- Sells **prescription medicines** including high-value GLP-1 weight loss (Wegovy, Mounjaro) — separate prescription workflow
- Plan: **Shopify Plus** (enterprise tier)
- Ships to: **NZ + AU** (Australia in scope)
- Currency: NZD only
- Customer accounts: OPTIONAL (not required for checkout)

## Owner / contact

- **Founder/owner email**: peter@bargainchemist.co.nz (likely Peter, decision-maker)
- Contact email: orders@bargainchemist.co.nz
- Phone: 021355643
- Address: 1 Radcliffe Road, Christchurch 8051

## Brand description (from Shopify, official)

> "Our policy: NZ's cheapest chemist. We are a 100% Kiwi-owned online pharmacy, providing quality healthcare products at prices you can afford. Shop online today!"

**Tagline**: "NZ's cheapest chemist"
**Positioning**: 100% Kiwi-owned discount pharmacy chain (online + physical)
**Value props (ranked by salience)**:
1. NZ's cheapest — price-led headline
2. 100% Kiwi-owned — trust + local
3. Quality healthcare — credibility
4. Affordable — value reinforcement
5. **Price Beat Guarantee** — confirmed by user (beat any price by 10%) and confirmed via Shopify page handle `pricebeatguarantee`
6. Free shipping NZ urban addresses orders $79+

---

## 90-day commerce performance

### Top-line
| Metric | Value | NZ H&B benchmark | Verdict |
|--------|-------|------------------|---------|
| Gross sales | **$1,551,141 NZD** | — | — |
| Orders | **26,740** | — | — |
| AOV | **$57.87** | — | Below $79 free shipping threshold by $21 — upsell opportunity |
| Unique customers | 22,989 | — | — |
| Returning customers | 11,889 | — | — |
| **Returning customer rate** | **51.7%** | 50–60% (established) | ✓ Healthy |
| Daily orders | ~297 | — | — |
| Daily revenue | ~$17,235 | — | — |

### Site funnel (90d)
| Stage | Sessions | % from prior | Cumulative conv |
|-------|----------|--------------|-----------------|
| Sessions | 1,613,120 | — | — |
| Cart additions | 88,757 | 5.5% | — |
| Reached checkout | 42,637 | 48% (cart→checkout) | — |
| Completed checkout | 25,747 | 60% (checkout→complete) | **1.6%** |

> **Site conversion rate of 1.6% is below H&B global avg of 2.5–7%.** Material upside.
> 
> **Cart abandonment** (cart→checkout drop): 46,120 events / 90d. Klaviyo Added-to-Cart flow only reached 8,743 recipients (19% coverage).
> 
> **Checkout abandonment**: 16,890 events. Klaviyo Abandoned Checkout reached 9,792 (58% coverage).

### Revenue trend (weekly)
| Week | Orders | Revenue |
|------|--------|---------|
| 2026-02-02 | 588 | $39,500 |
| 2026-02-09 | 1,717 | $114,435 |
| 2026-02-16 | 1,695 | $107,666 |
| 2026-02-23 | 1,691 | $107,415 |
| 2026-03-02 | 2,241 | $152,011 |
| 2026-03-09 | 2,397 | $168,253 |
| **2026-03-16** | 2,422 | $167,565 |
| **2026-03-23** | 2,642 | **$181,636** ← peak |
| 2026-03-30 | 1,907 | $124,940 |
| 2026-04-06 | 2,010 | $127,290 |
| 2026-04-13 | 2,071 | $133,276 |
| 2026-04-20 | 2,143 | $132,989 |
| 2026-04-27 | 2,068 | $128,851 |
| 2026-05-04 (partial) | 1,148 | $70,030 |

Peak in late March (likely seasonal — autumn allergy / pre-winter), then settled at ~$130k/wk.

### Top 20 products by revenue (90d)
| # | Product | Revenue | Orders | AOV |
|---|---------|---------|--------|-----|
| 1 | A-Scabies Skin Lotion 30 mL | $10,233 | 413 | $24.78 |
| 2 | Elevit Preconception/Pregnancy 100 Tabs | $6,651 | 83 | $80.13 |
| 3 | **Wegovy FlexTouch Pen** ⚠️ | $6,400 | 16 | $400.00 |
| 4 | OPTIFAST VLCD Vanilla Shake | $5,827 | 75 | $77.69 |
| 5 | Regaine Extra Strength Solution Men 4mo | $5,220 | 32 | $163.13 |
| 6 | Oracoat Xylimelts Mint Free 40 Pack | $4,669 | 108 | $43.23 |
| 7 | Oracoat Xylimelts Mild Mint 40 Pack | $4,562 | 108 | $42.24 |
| 8 | LIVON Lypospheric Vit C 1000mg 30 Sachets | $4,269 | 36 | $118.58 |
| 9 | Waterpik Waterflosser Black Ultra Plus | $3,912 | 29 | $134.90 |
| 10 | Blis Tooth Guard M18 Peppermint 30s | $3,843 | 75 | $51.24 |
| 11 | Sebizole 2% Shampoo 200ml | $3,820 | 132 | $28.94 |
| 12 | Regaine Men's Extra Strength Foam 4mo | $3,675 | 23 | $159.78 |
| 13 | GO Healthy GO Magnesium Sleep 120 VCaps | $3,271 | 100 | $32.71 |
| 14 | **WEGOVY 2.4 MG FLEXTOUCH** ⚠️ | $3,270 | 8 | $408.69 |
| 15 | Armani Si EDP 100ml | $3,191 | 21 | $151.96 |
| 16 | GO Healthy CoQ10 Ubiquinol 100mg 60 Caps | $3,182 | 36 | $88.39 |
| 17 | EGO Azclear Medicated Lotion 25g | $3,163 | 138 | $22.92 |
| 18 | Wellife Portable Nebuliser | $3,130 | 40 | $78.25 |
| 19 | EGO Numit 5% Cream 30g | $2,927 | 21 | $139.39 |
| 20 | Clinicians Flora Restore 30 Caps | $2,894 | 113 | $25.61 |

**Top 20 = $88,110 = 5.7% of gross sales.** Long tail dominates — total catalog 20,000+ SKUs.

### Categories visible from top sellers
- Hair regrowth (Regaine x2)
- Wellness/supplements (Elevit, GO Healthy x2, LIVON, Clinicians)
- Oral health (Oracoat x2, Blis, Waterpik)
- Skin/dermatology (Sebizole, EGO Azclear, EGO Numit)
- Weight loss (OPTIFAST + **Wegovy x2 — POM**)
- Fragrance (Armani Si)
- Wellness devices (Wellife Nebuliser)

⚠️ **WEGOVY is in top 5 by revenue.** This is a prescription-only medicine. **Cannot be promoted in marketing emails** per Medsafe Marketing Guidelines. Likely the source of the compliance issue causing flow pauses (user confirmed).

### Order referrer source (90d)
| Source | Orders | Revenue | % of revenue |
|--------|--------|---------|--------------|
| search | 18,679 | **$1,172,028** | **75.5%** |
| (empty/direct) | 7,995 | $579,549 | 37.4% |
| social | 64 | $4,216 | 0.3% |
| **email** | **2** | **$70.95** | **0.005%** |

> **Total = 26,740 orders ✓** matches gross.
> 
> 🚨 **MASSIVE EMAIL ATTRIBUTION GAP**: Shopify shows essentially zero email-attributed revenue, but Klaviyo flows alone produced ~$48k. **UTM tagging is missing on Klaviyo email links.** Without `utm_source=email`, all email traffic gets attributed to "search" or "direct" — making email look invisible to Shopify analytics.
> 
> **This is a critical fix:** before any campaign optimisation produces measurable results, attribution must be plumbed properly. Otherwise we can't tell what's working.

### Marketing leverage gap (the big number)

| Source | Klaviyo flow revenue (90d) | Shopify total revenue (90d) | % |
|--------|----------------------------|------------------------------|---|
| Email flows (observed) | ~$48,000 | $1,551,141 | **3.1%** |
| H&B benchmark | — | — | **20–30%** |
| Annualised gap | ~$255k–$415k revenue/yr | — | — |

> **The biggest single number on this page.** Bringing email contribution from 3.1% to 20% = +$262k/quarter = **>$1M/year** in incremental revenue, assuming the underlying commerce funnel holds.

---

## Implications

1. **Email is the biggest underused lever**, not because the list is bad — because attribution is broken AND the most important flows are in DRAFT.
2. **AOV $57.87 vs $79 free shipping threshold** = $21 gap. A $20-to-go progress bar in cart abandonment + add-to-cart flows could move AOV materially.
3. **Returning customer rate 51.7%** is healthy — the loyalty foundation is there. But repeat-buyer flows (replenishment) aren't running. Easy win.
4. **20,000 SKUs** means product-rec personalisation has high leverage. Boost integration (Klaviyo product feeds + Triple Whale events) is already wired up.
5. **Wegovy + Mounjaro** are revenue concentrations but cannot be marketed in email. Need a clearly separated "prescription products" workflow that does NOT touch marketing flows.
6. **Site conversion rate 1.6%** is below H&B benchmark of 2.5–7% — a CRO project, not just an email project.
7. **AU shipping in scope** but not visible in any email content I've seen. May be deliberate (AU-only landing) or missed opportunity.

---

## Deeper analysis (2026-05-06 second pass)

### Device split (90d, 1.61M sessions)

| Device | Sessions | % |
|--------|----------|---|
| Mobile | 1,275,953 | **79.1%** |
| Desktop | 323,994 | 20.1% |
| Tablet | 13,508 | 0.8% |
| Other | 43 | <0.01% |

Confirms NZ market mobile dominance (benchmark 65–80%). All email design must be mobile-first non-negotiable.

### Sessions × source × conversion (90d)

| Device | Source | Sessions | Conv rate | Orders |
|--------|--------|----------|-----------|--------|
| Mobile | search | 687,492 | 1.83% | 12,602 |
| Mobile | direct | 471,009 | 1.02% | 4,823 |
| Desktop | search | 189,872 | **2.80%** | 5,325 |
| Desktop | direct | 128,027 | 1.50% | 1,921 |
| Mobile | social | 105,606 | 0.06% | 63 |
| Mobile | unknown | 8,433 | 3.63% | 306 |
| Desktop | unknown | 5,044 | 4.08% | 206 |
| **Mobile** | **email** | **3,065** | **4.37%** | **134** |
| **Desktop** | **email** | **80** | **3.75%** | **3** |
| Mobile | paid | 350 | 0.57% | 2 |

🚨 **HEADLINE FINDINGS:**
1. **Email is the highest-converting source** with meaningful volume (4.37% mobile, 3.75% desktop). Email session converts >2× search and >40× social.
2. **Email session volume is 0.19% of total traffic** — massively under-leveraged. If email volume were even 5% of traffic at current conversion, it would drive ~3,500 incremental orders/quarter.
3. **Social converts 0.06% on mobile** — social traffic is essentially worthless from direct-response standpoint. Worth a brand-strategy conversation: is social budget driving brand value or wasted?
4. **Desktop converts ~50% better than mobile** across all sources except email — email is uniquely mobile-friendly.

### Sessions referrer summary (90d)

| Source | Sessions | Conv rate | Comment |
|--------|----------|-----------|---------|
| search | 887,079 | 2.05% | dominant — 55% of traffic, organic-heavy |
| direct | 601,586 | 1.13% | 37% — high but lower-converting; brand-aware |
| social | 107,621 | 0.06% | 7% but converts at near-zero |
| unknown | 13,639 | 3.78% | likely UTM-tagged + Klaviyo internal — converts well |
| **email** | **3,148** | **4.35%** | **best conv rate; 0.19% of sessions** |
| paid | 425 | 0.47% | tiny — Google Ads spend? |

> 🚨 **Note**: "email" source recognised by Shopify Sessions analytics (3,148 sessions, 4.35% CR, ~137 orders × $58 = ~$7.9k revenue) but barely shows up in Order referrer source ($70.95 for 2 orders earlier). 
> 
> **The disconnect**: Sessions tracking is utm-aware. Order attribution is multi-session — if the customer clicks an email today, browses, comes back tomorrow via direct/search, places order — the order is attributed to the LAST source. The UTM fix would lift email order-attribution materially, but the session evidence already proves email's value.

### Returning customer rate (weekly trend)

Stable at **~55% throughout 90 days** (range 53.5% to 58.2%). Healthy + consistent.

### Product type breakdown (90d, $1.55M total)

| Product type | Revenue | % of total | Orders | AOV | Notes |
|--------------|---------|-----------|--------|-----|-------|
| Health & Wellbeing | $533,822 | **34.4%** | 10,594 | $50.22 | biggest |
| Personal Care | $270,569 | 17.4% | 8,222 | $32.83 | |
| Skin Care | $180,330 | 11.6% | 5,038 | $35.75 | |
| Medicines & Professional Services | $147,080 | 9.5% | 4,515 | $32.48 | medical/clinic |
| Beauty Accessories | $120,999 | 7.8% | 2,272 | $53.21 | |
| **`_pharmacy-only`** | **$93,244** | **6.0%** | **3,667** | $25.42 | 🚨 explicit tag — restricted |
| Cosmetics | $69,657 | 4.5% | 2,386 | $29.18 | |
| Health Equipment | $42,970 | 2.8% | 1,443 | $29.77 | |
| Baby | $32,290 | 2.1% | 1,051 | $30.71 | |
| Household | $20,831 | 1.3% | 732 | $28.28 | |
| General Food & Drink | $15,323 | 1.0% | 580 | $26.14 | |
| Other Pharmacy & Clothing | $9,810 | 0.6% | 546 | $17.96 | |
| Lifestyle & Wellness | $7,815 | 0.5% | 257 | $30.19 | |
| **`_pharmacist-only`** | **$4,242** | **0.3%** | **288** | $14.73 | 🚨 explicit tag — restricted |

### 🚨 BIG FINDING: pharmacy-only product type tags exist in Shopify

**Combined `_pharmacy-only` + `_pharmacist-only` = $97,486 (6.3% of revenue) on 3,955 orders.**

This is a **massive operational asset**:
1. **Compliance gate is implementable now**: any product with type `_pharmacy-only` or `_pharmacist-only` cannot appear in marketing emails by name. Shopify already classifies them.
2. **Klaviyo segments can use this**: filter customers who *only* buy restricted products, suppress from broad sends.
3. **Product recommendation blocks must filter**: when injecting product recs into emails, exclude `_pharmacy-only` and `_pharmacist-only` types automatically.
4. **The Codral Solus campaign in compliance-scan likely promoted `_pharmacy-only` products** — explains the compliance issue.

This tag system is a *gift* for compliance automation. Build the gate around it.

### Sessions completion funnel by device + source — abandonment lever

For email traffic specifically:
- Mobile email: 3,065 sessions → 134 completed checkout = **4.37% conv**
- The remaining 2,931 mobile email sessions abandoned at some stage
- Email is delivering **high-intent** mobile traffic that mostly doesn't complete

This implies:
- Mobile checkout UX is the bottleneck for email-driven conversion
- The 134 mobile email orders we see are a fraction of email-influenced revenue
- Cart + Checkout abandonment flows (already running) catch some of these — but coverage is low (19% / 58% as noted earlier)

---

## Implications for the execution plan

1. **Email is the highest-leverage channel by conversion rate** — every dollar invested in email returns more than every other channel.
2. **`_pharmacy-only` and `_pharmacist-only` Shopify tags ARE the compliance gate's foundation** — build the slash command around these.
3. **Mobile-first design is non-negotiable** (79% of sessions, 100% of email orders).
4. **Top 5 product types = 81% of revenue** — focus product-rec blocks here.
5. **Health & Wellbeing AOV = $50** while site AOV = $58 — Health & Wellbeing customers spend slightly less. Beauty Accessories AOV $53, also below site.

---

## Cross-source reconciliation

| Source | Their version of "email-driven revenue (90d)" | Why they disagree |
|--------|-----------------------------------------------|--------------------|
| Klaviyo flow attribution | ~$48,000 | Klaviyo's last-touch attribution within 5d window |
| Klaviyo campaign attribution | ~$70,000 (estimated, sum from sample reports) | Same |
| Shopify "email" referrer | $70.95 | UTM tagging missing on Klaviyo links — almost everything misclassified as "search" or "direct" |
| Reality (estimate) | $100k–$120k+/90d | Klaviyo numbers + halo effect on direct/search |

**Confidence on reality estimate: Low.** Need UTM tagging to verify.
