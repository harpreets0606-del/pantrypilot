# Integrations — Connection Status

Last updated: 2026-05-06

## Connected ✅

| Source | Method | Scope | Notes |
|--------|--------|-------|-------|
| Klaviyo | MCP server | Full read + write | Account ID `XCgiqg`, public key `pk_XCgiqg_...` (rotate this — was shared in chat) |
| Shopify | MCP server | Full admin access | Verify which store is active via `get-shop-info` |

## Pending ⏳ — needed for full analytical capability

### High priority

| Source | Why we need it | Setup steps |
|--------|----------------|-------------|
| **Zapier MCP** | Persistent memory (Tables), automation, glue between apps | 1. Create Zapier account if none. 2. Install Zapier MCP from claude.ai/integrations or Claude Code MCP marketplace. 3. Authorise Zapier connection. |
| **Zapier Tables** | Holds `metrics_daily`, `customers`, `campaigns_log`, `decisions`, `experiments` | Created via Zapier UI once Zapier MCP is live. Schemas defined in `memory/table-schemas.md` (will be created on Zapier connection). |
| **GA4 Data API** | True revenue attribution, channel ROI, funnel drop-off | Either (a) OAuth via Zapier — easiest, or (b) direct Google Cloud project + service account. GA4 property ID needed. |
| **Google Ads API** | CPA, ROAS, search terms, ad performance | OAuth via Zapier. Google Ads customer ID needed. |

### Medium priority

| Source | Why | Setup |
|--------|-----|-------|
| **Shopify webhooks → Zapier** | Real-time order → `metrics_daily` | Configured in Zapier UI once Tables exist. |
| **Klaviyo webhooks → Zapier** | Auto-log campaign performance | Configured in Klaviyo flow webhook actions. |
| **BigQuery (GA4 export)** | Event-level data, cohorts, multi-touch attribution, LTV models | Enable in GA4 Admin → BigQuery Linking. Free tier covers small stores. |

### Nice to have

- Meta Ads API (if running Facebook/Instagram ads)
- Google Search Console (organic traffic context)
- Slack MCP (alerts)

## Action checklist for the user

- [ ] Rotate the Klaviyo public key that was shared in chat
- [ ] Install Zapier MCP
- [ ] Connect GA4 in Zapier (find GA4 property ID first)
- [ ] Connect Google Ads in Zapier (find customer ID first)
- [ ] Enable GA4 → BigQuery export
- [ ] Decide if Meta Ads is in scope

When each of these is done, update the table above and tell Claude — it will then create the related Zapier Tables, hooks, and playbooks.
