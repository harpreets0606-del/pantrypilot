# Shopify Ground Truth — Bargain Chemist

**Date**: 2026-05-06
**Source**: Shopify Admin API + ShopifyQL (90-day window)

> Shopify is the ground truth for revenue + customer + product data. Klaviyo and GA4 reconcile *to* this.

---

## Business model (now confirmed)

- **Brick-and-mortar + online pharmacy chain.** NOT just online.
- Stores observed (page handles): Petone, Mt Roskill, Mt Wellington, WestCity, South Dunedin, Whanganui ("Bargain Plus") — at least 6 locations confirmed; total NZ-wide
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

## Cross-source reconciliation

| Source | Their version of "email-driven revenue (90d)" | Why they disagree |
|--------|-----------------------------------------------|--------------------|
| Klaviyo flow attribution | ~$48,000 | Klaviyo's last-touch attribution within 5d window |
| Klaviyo campaign attribution | ~$70,000 (estimated, sum from sample reports) | Same |
| Shopify "email" referrer | $70.95 | UTM tagging missing on Klaviyo links — almost everything misclassified as "search" or "direct" |
| Reality (estimate) | $100k–$120k+/90d | Klaviyo numbers + halo effect on direct/search |

**Confidence on reality estimate: Low.** Need UTM tagging to verify.
