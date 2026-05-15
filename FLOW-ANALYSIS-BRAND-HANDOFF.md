# Bargain Chemist — Flow Analysis & Brand Team Handoff Playbook (v2 — VERIFIED)

> Generated 2026-05-15 from live Klaviyo API + content inspection of all 10 manual flows + 22 email templates. 4-tier classification.

## Verified verdicts

| Flow | ID | Tier | Emails | Notes |
|---|---|---|:-:|---|
| Added to Cart Abandonment | `RPQXaa` | 🟢 CREATIVE-ONLY | 2 | Generic "you left something" — no products/categories shown |
| Replenishment - Category Based | `Ua5LdS` | 🟢 CREATIVE-ONLY | 6 | Per-category templates, each with 1 collection link |
| Post-Purchase Series | `RDJQYM` | 🟡 CATEGORY LINKS | 2 | 3-4 collection cards per email |
| Win-back - Lapsed Customers | `T7pmf6` | 🟡 CATEGORY LINKS | 2 | 6-8 category links per email |
| Flu Season - Winter Wellness | `V9XmEm` | 🟡 CATEGORY LINKS | 2 | 3-6 category cards per email |
| **Welcome Series 2026** | `YdejKf` | 🟠 **PRODUCT SHOWCASE** | 3 | **Email 2 has 4 hardcoded products + "refresh quarterly" comment** |
| Browse Abandonment | `RtiVC5` | 🔴 EVENT-DRIVEN | 1 | Renders viewed product from event payload |
| Abandoned Checkout v3 | `Sr3hxz` | 🔴 EVENT-DRIVEN | 2 | Cart items + `checkout_url` |
| Search Abandonment V4 | `XbQiKg` | 🔴 EVENT-DRIVEN | 2 | Search context from event |
| Back in Stock | `Ysj7sg` | 🔴 EVENT-DRIVEN | 2 | Specific product from event |

**Split: 8 CREATIVE-ONLY + 6 CATEGORY LINKS + 1 PRODUCT SHOWCASE + 7 EVENT-DRIVEN emails (22 total)**

## Critical finding

**Zero of 22 templates use Klaviyo's Universal Content Blocks** (`data-klaviyo-universal-block` not present in any template). Setting these up is the highest-leverage one-time task before brand handoff.

## Template-ID directory

### 🟢 CREATIVE-ONLY (8 emails)
- Added to Cart: `USNhYE`, `UCUwWu`
- Welcome 1 (Welcome to the Family): `VZASFD`
- Welcome 3 (Last Nudge): `UvF2qd`
- Replenishment Vitamins: `Wg5TLb`
- Replenishment Skincare: `UdLfdw`
- Replenishment Hair Care: `YbKhNV`
- Replenishment Oral Care: `RixM24`
- Replenishment Baby & Family: `UbKf4Z`
- Replenishment Fallback: `XBkvpb`

### 🟡 CATEGORY LINKS (6 emails)
- Post-Purchase: `Vc5vyk` (4 cats), `U8ub97` (3 cats)
- Win-back: `XRDX9U` (6 cats), `YwvJmD` (8 cats)
- Flu Season: `SNtytG` (3 cats), `XmsJkZ` (6 cats)

### 🟠 PRODUCT SHOWCASE (1 email — outlier)
- Welcome Email 2 (Best Sellers): `WtmqBu`
- **4 hardcoded `/products/` URLs, 3 unique prices, 3 CDN images, contains "hardcoded; refresh quarterly" comment**

### 🔴 EVENT-DRIVEN (7 emails)
- Browse Aban: `WR3mRF`
- Checkout v3: `Vtggdk` (1h), `Yr6YBF` (24h last touch)
- Search V4: `S3jZGb`, `RWGKkM`
- Back in Stock: `XccdEd`, `RijuTw`

## Brand team handoff by tier

### 🟢 CREATIVE-ONLY (8 emails) — fastest path

Brand team designs HTML with full creative freedom. Required merge tags in standard positions:
```
{{ first_name|default:'there' }}    — in greeting
{{ organization.name }}             — in signature
{{ organization.full_address }}     — in footer
{% unsubscribe 'Unsubscribe' %}     — in footer (legal requirement)
```

**Workflow:** brand HTML → Claude Code uploads + assigns → live. ~5 min per template.

### 🟡 CATEGORY LINKS (6 emails) — same workflow + 1 thing

Same as CREATIVE-ONLY plus: brand team decides which Shopify collections to feature. They use the actual collection URLs (e.g. `https://www.bargainchemist.co.nz/collections/skincare`). These URLs are durable — only need updating if you restructure your category taxonomy in Shopify (rare).

**Workflow:** same as above. ~5 min per template.

### 🟠 PRODUCT SHOWCASE (Welcome Email 2 only) — needs ongoing maintenance

This is the only template that requires quarterly product refresh. Brand team designs the template; engineering OR brand team updates the 4 product cards (image, URL, price, name) every quarter as featured products shift.

**Recommended fix:** convert this template to either:
- **Category-link version** like Flu Season Email 2 — easier to maintain, no per-product updates
- **Klaviyo Catalog feed version** — dynamic "Recommended Products" or "Best Sellers" feed from your product catalog; auto-updates as catalog changes

Either eliminates the quarterly burden. Currently the maintenance cadence is documented in the HTML by whoever built it: `<!-- TOP 3 BEST-SELLERS (hardcoded; refresh quarterly) -->`

### 🔴 EVENT-DRIVEN (7 emails) — wrapper pattern

Brand team designs the wrapper (header + creative above + creative below + footer). Engineering preserves the dynamic block in the middle:

```
┌─────────────────────────────┐
│  Brand-designed header      │ ← brand owns
│  Hero + copy                │ ← brand owns
├─────────────────────────────┤
│  ⚠ DYNAMIC ⚠                │ ← engineering owns
│  - Browse Aban: viewed product card from event
│  - Checkout: {% for item in line_items %}
│  - Search: search context block
│  - Back in Stock: specific product block
├─────────────────────────────┤
│  Brand-designed secondary   │ ← brand owns
│  Footer                     │ ← brand owns
└─────────────────────────────┘
```

**Workflow:** brand sends wrapper HTML → Claude Code splices in the preserved dynamic block markup → test send with a real event payload → live. ~20 min per template because of splice + verification.

## Recommended phasing

### Phase 1 — Universal Content setup (one-time, ~2 hours)
Create universal blocks in Klaviyo UI:
- **Master header** (logo + nav)
- **Master footer** (physical address + social + unsubscribe wrapper)
- **Pharmacist disclaimer footer** (if pharmacy-related sends need it)

Retrofit existing 22 templates to reference these blocks. Once done, every header/footer update propagates automatically.

### Phase 2 — Brand handoff for tiers 🟢🟡 (14 emails, ~70 min)
14 emails are creative-or-category. Brand designs each, you upload + assign. Easy.

### Phase 3 — Decision on Welcome Email 2 (1 email)
Either:
- Accept the quarterly refresh cadence (document it, schedule the reminder)
- Convert to category-link or Klaviyo Catalog feed (eliminates ongoing maintenance)

### Phase 4 — Wrapper handoff for tier 🔴 (7 emails, ~140 min)
Engineering provides the "frozen" dynamic block HTML; brand designs wrapper; you splice + test.

### Phase 5 — Ongoing
- Brand updates header/footer → edits universal block once → propagates everywhere
- Brand creative refresh → new wrapper HTML → swap in (dynamic blocks untouched)
- Quarterly: refresh Welcome Email 2 products IF you don't convert it

## Risk register

| Risk | Mitigation |
|---|---|
| Brand strips required merge tags | Provide template skeleton with merge tags pre-placed in standard positions |
| Brand modifies dynamic block in EVENT-DRIVEN flow | Mark blocks with `<!-- DO NOT EDIT BELOW --> ... <!-- END -->` comments |
| Universal block ID gets deleted/recreated | Train: always edit in place, never delete |
| Welcome Email 2 products go stale | Calendar reminder for quarterly refresh, OR convert to dynamic feed |
| New flow built with hardcoded products without flag | Add lint check: search for `/products/` URLs in any committed template |

## Open opportunity (separate decision)

**Added to Cart Abandonment is currently CREATIVE-ONLY** — no cart contents are rendered. Industry best practice is to show actual cart items in cart-recovery emails (typically lifts conversion 15-30%). To upgrade:
- Move from CREATIVE-ONLY → EVENT-DRIVEN tier
- Engineering adds `{% for item in event.extra.line_items %}` block
- Brand designs wrapper around it

**Recommendation: separate "upgrade Added to Cart flow" project. Current CREATIVE-ONLY templates ship today for the brand handoff; upgrade is a future revenue-lift project.**
