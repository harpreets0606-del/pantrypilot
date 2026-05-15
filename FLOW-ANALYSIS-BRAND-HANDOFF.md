# Bargain Chemist — Flow Analysis & Brand Team Handoff Playbook

> Generated 2026-05-15 from live Klaviyo API analysis of all 10 manual flows + 22 email templates.

## Verified verdicts

| Flow | ID | Verdict | Emails | Notes |
|---|---|---|:-:|---|
| Welcome Series 2026 - No Coupon | `YdejKf` | MIXED | 3 | first_name only |
| [Z] Flu Season - Winter Wellness | `V9XmEm` | MIXED | 2 | first_name / person.* |
| [Z] Post-Purchase Series | `RDJQYM` | MIXED | 2 | organization.* only (no first_name) |
| [Z] Win-back - Lapsed Customers | `T7pmf6` | MIXED | 2 | first_name only |
| [Z] Added to Cart Abandonment | `RPQXaa` | MIXED | 2 | **No cart items shown — missed opportunity** |
| [Z] Replenishment - Category Based | `Ua5LdS` | MIXED | 6 | One static template per category |
| [Z] Browse Abandonment | `RtiVC5` | **COMPLEX** | 1 | event.* — viewed product |
| [Z] Abandoned Checkout v3 | `Sr3hxz` | **COMPLEX** | 2 | event.* + checkout_url |
| [B] Search Abandonment V4 | `XbQiKg` | **COMPLEX** | 2 | event.* — search context |
| [Z] Back in Stock | `Ysj7sg` | **COMPLEX** | 2 | event.* — specific product |

**Split: 6 MIXED (17 emails) / 4 COMPLEX (7 emails) / 0 SIMPLE / 0 with universal content.**

## Critical finding: zero universal content blocks in use

Scanned 22 templates for `data-klaviyo-universal-block` attributes — **none found**. This means:
- Brand updates currently require manual edits to every affected template
- The "update once, propagate everywhere" workflow does NOT exist yet
- Setting up universal blocks is the **highest-leverage first move** before any brand handoff

## Email template IDs (for Claude Code referencing)

### MIXED flows
- **Post-Purchase**: `Vc5vyk`, `U8ub97`
- **Added to Cart Aban**: `USNhYE`, `UCUwWu`
- **Win-back**: `XRDX9U`, `YwvJmD`
- **Replenishment** (6 categories): `Wg5TLb` (Vitamins), `UdLfdw` (Skincare), `YbKhNV` (Hair Care), `RixM24` (Oral Care), `UbKf4Z` (Baby & Family), `XBkvpb` (Fallback)
- **Flu Season**: `SNtytG`, `XmsJkZ`
- **Welcome**: `VZASFD`, `WtmqBu`, `UvF2qd`

### COMPLEX flows (dynamic blocks must be preserved)
- **Browse Aban**: `WR3mRF`
- **Abandoned Checkout v3**: `Vtggdk` (1h), `Yr6YBF` (24h last touch)
- **Search Aban V4**: `S3jZGb`, `RWGKkM`
- **Back in Stock**: `XccdEd`, `RijuTw`

## Brand team handoff — required merge tags by flow tier

### For ALL MIXED flows — keep these placeholders in the design
```html
<!-- In greeting -->
{{ first_name|default:'there' }}

<!-- In signature/footer -->
{{ organization.organization_name }}

<!-- In footer (legal requirement) -->
{% unsubscribe %}
```

### For COMPLEX flows — preserve the dynamic block

The brand team designs the **wrapper** (header, hero, copy ABOVE the dynamic block; secondary copy, footer BELOW). The engineer (you, via Claude Code) preserves the existing dynamic block markup unchanged.

**Existing dynamic patterns observed:**
- Browse Aban (`WR3mRF`): renders single viewed product from `{{ event.extra }}`
- Checkout v3 (`Vtggdk`, `Yr6YBF`): renders cart items + `{{ event.checkout_url }}`
- Search V4 (`S3jZGb`, `RWGKkM`): renders search context from event
- Back in Stock (`XccdEd`, `RijuTw`): renders the specific product from event

## Recommended phasing

### Phase 1 — Universal content setup (one-time, ~2 hours)
Create 3 universal blocks in Klaviyo UI:
1. Master header (logo + nav)
2. Master footer (NZ-required physical address + social + unsubscribe wrapper)
3. Pharmacy compliance footer (if Rx-related sends need it)

Then convert all 22 existing templates to reference these blocks. Once done, every header/footer update propagates automatically.

### Phase 2 — MIXED handoff (17 emails, ~85 min)
Brand team designs each template with creative freedom; includes the 3 required merge tags in standard positions. Claude Code uploads + assigns. ~5 min each.

### Phase 3 — COMPLEX handoff (7 emails, ~140 min)
Brand team designs wrapper HTML (header + brand creative + secondary). Claude Code splices the preserved dynamic block markup in. Test send with real event data. ~20 min each.

### Phase 4 — Ongoing
- Brand updates header/footer → UI edit of universal block → instant propagation across 22 emails
- Brand creative refresh → new wrapper HTML → Claude Code swaps, dynamic blocks untouched
- New flow setup → engineering decides dynamic block needs, brand designs around

## Risk register

| Risk | Mitigation |
|---|---|
| Brand team strips required merge tags | Provide a non-editable "compliance block" template with merge tags pre-placed |
| Brand team modifies dynamic block in COMPLEX flow | Provide HTML with clear `<!-- DO NOT EDIT BELOW --> ... <!-- END DO NOT EDIT -->` markers |
| Universal block ID gets changed (delete/recreate) | Train: always edit in place, never delete |
| Brand creative breaks email client compatibility | Run Litmus/Email on Acid preview before going live |
| Added to Cart flow stays generic (current state) | Decide: do we add cart items to it? Currently a missed conversion opportunity |

## Open question (separate decision)

The **Added to Cart Abandonment flow currently does NOT show cart items**. The templates `USNhYE` and `UCUwWu` are pure brand creative with only first_name personalization. Industry best practice would include the cart contents (raise conversion 15-30%). If you want to upgrade this flow to actually show cart contents:
- Would convert it from MIXED to COMPLEX
- Requires engineering to add `{% for item in event.extra %}` style block
- Brand team designs the wrapper around it

**Recommendation: track as a separate "upgrade Added to Cart flow" project. Current MIXED templates work for handoff today; the upgrade is a future optimization.**
