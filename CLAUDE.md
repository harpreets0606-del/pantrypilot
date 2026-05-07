# Working Principles for This Project

## Always Triple-Check Conclusions and Assumptions With Actual Data

**Never state a number, threshold, status, or fact without verifying it against a primary data source.**

When making any claim, recommendation, or assumption:

1. **Pull the actual data** from the relevant source (Shopify API, Klaviyo API, the live website, the actual file, the actual flow, etc.) before stating it.
2. **Cross-reference at least one second source** when possible (e.g. existing email templates + live site + Shopify store config).
3. **Explicitly call out** when something cannot be verified from available data, and what would be needed to verify it. Never silently assume.
4. **Default to verifying via tool call**, not from chat history or earlier-session memory — values may have changed.

### Examples of things to always verify (not assume):
- Free shipping thresholds (check Shopify shipping zones AND existing email templates AND the live site)
- Cart split thresholds (check actual AOV and cart distribution data)
- Domain authentication status (SPF/DKIM/DMARC)
- Active/paused status of flows or campaigns (verify via API after any change)
- Product/SKU tags and collections (query the actual Shopify catalogue)
- Klaviyo segment definitions and member counts
- Brand voice / tone (analyse actual sent campaigns, not assume)
- API capabilities and endpoint payloads (verify against current API docs)
- Customer behaviour patterns (query, don't estimate)

### Anti-patterns (do not do this):
- Quoting a value from earlier in chat without re-verifying it has not changed
- Assuming a "best practice" applies without checking the brand's actual data
- Using sample/template values from documentation without confirming they match the user's setup
- Stating a status update worked because the API returned 200 — verify the new state via a follow-up GET
- Carrying forward an assumption from a previous response into a new recommendation

### When the user provides a value
- Trust the user's input as the source of truth
- BUT also check it against any data we already have, and surface any discrepancy (e.g. "you said $79; the existing email template says $49 — should we update the template?")

## Project Context

This repository works with the **Bargain Chemist** Shopify store and Klaviyo account.

- Klaviyo company ID: `XCgiqg`
- Shopify store: `bargain-chemist.myshopify.com`
- Brand domain: `bargainchemist.co.nz`
- Currency: NZD
- Timezone: Pacific/Auckland
- Industry: Ecommerce, Health & Beauty (NZ pharmacy)
- All marketing flows / templates / campaigns must comply with NZ ASA Therapeutic & Health Advertising Code 2025 and the Unsolicited Electronic Messages Act 2007.

## Key Constraints (Bargain Chemist)

- **No coupon codes** can be applied in flows — incentives must be free shipping reminders, social proof, value messaging, or factual scarcity only.
- **Free shipping threshold: $79 NZD** (set via Zyber Shipping Rate Provider app, not Shopify-native — so not queryable directly).
- **Restricted products** (`_pharmacy-only`, `_pharmacist-only`, prescription) must be excluded or routed to info-only branches in promotional flows — never price-promoted.
- **No fear-based language** in subject lines or copy (e.g. "expires today", "stock alert", "running out") — banned by ASA Code Rule 1(b).
- **Mandatory email footer** must include: business name, NZ physical address, "Always read the label and use as directed", "If symptoms persist see your healthcare professional", functional unsubscribe.
- **Brand voice**: warm, descriptive, wellness-coded ("Discover", "Support", "Meet", "Feel good"). Avg subject length ~43 chars. Emoji use ~47% of campaigns. 🚨 reserved for Price Smash sale events only.

## Klaviyo API Capabilities (verified)

- ✅ Create complete flow with full definition (delays, splits, messages, template assignments) via `POST /api/flows` (revision 2025-01-15+, scope: flows:write).
- ✅ Update flow status via `PATCH /api/flows/{id}` — accepts `live`, `draft`, `manual` (NOT `paused` — that maps to `manual` internally).
- ✅ Create email templates via `POST /api/templates`.
- ✅ Update flow action settings via `PATCH /api/flow-actions/{id}` (status, tracking, sending options only — not structure).
- ❌ Cannot add/remove actions to an existing flow after creation.
- ❌ Cannot rejoin split branches (each branch terminates independently).
- ❌ Cannot create/update flow messages independently.
