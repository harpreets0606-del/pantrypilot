# Bargain Chemist — Verified Context

> Generated 2026-05-15 from live Klaviyo + Zapier MCP queries. Branch: `claude/klaviyo-google-ads-research-PdMUG`.
> Every number below was independently retrieved this session — see "Source" column.

## 1. Account Identity (verified — Klaviyo `get_account_details`)

| Field | Value |
|---|---|
| Klaviyo account ID | `XCgiqg` |
| Organisation | Bargain Chemist |
| Industry | Ecommerce, Health & Beauty |
| Sender | hello@bargainchemist.co.nz |
| Site | https://www.bargainchemist.co.nz |
| Address | 1 Radcliffe Road, Belfast, Christchurch, Canterbury 8051, NZ |
| Currency | NZD |
| Timezone | Pacific/Auckland |

## 2. Klaviyo Segments — All 14 BC Segments (verified 2026-05-15)

Profile counts pulled live with `includeProfileCount=true`. Source column = direct API response from `klaviyo_get_segment`.

| # | Name | ID | Profiles | Notes |
|---|---|---|---:|---|
| 1 | BC — Retail Purchasers L90D | `RizxBG` | **9,444** | Recent buyers — best lookalike seed |
| 2 | BC — Retail Cart Abandoners 30d | `VrP6TT` | **620** | Klaviyo flow scope (too small for CM minimum) |
| 3 | BC — Retail Cart Abandoners 60d | `Ti4FKX` | **1,230** | Just above CM 1,000 floor |
| 4 | BC — Retail VIPs (3+ retail orders 365d) | `RLk5xx` | **2,871** | Highest-LTV signal for Smart Bidding |
| 5 | BC — Browse Abandoners 30d (all products) | `RTzA5N` | **1,237** | Display retargeting candidate |
| 6 | BC — New Retail Customers L30D (first-time) | `VQ8Sz4` | **1,539** | First-time = exclude from acquisition; cross-sell candidate |
| 7 | BC — Recent Retail Purchasers L7D | `UvtwYq` | **573** | Exclusion-only (was estimated ~850 in pasted v1; actual 573) |
| 8 | BC — Lapsed Retail Customers 90-180D | `RnnhTh` | **7,333** | Mid-window win-back |
| 9 | BC — Lapsed Retail 180-365D (win-back) | `XFc26k` | **13,563** | **Highest single win-back opportunity** |
| 10 | BC — All Retail Customers (last 1095d) | `VvBRbu` | **59,315** | Master observation audience |
| 11 | BC — Pharmacy-Only Buyers (no retail) | `YgrizT` | **4,177** | **Exclusion-only** for retail campaigns |
| 12 | BC — GLP-1 Customers (Wegovy + Mounjaro) | `X2pdkD` | **24** | Klaviyo-only; Rx items, NOT eligible for Google Ads |
| 13 | BC — Unengaged Subscribed 180D (sunset) | `YdzNmz` | **34,248** | Sunset/win-back via paid media (cheaper than email re-perm) |
| 14 | BC — High AOV Retail ($100+ order) | `WkwEvG` | **0 ⚠️** | **Filter bug — see §3** |

Pre-existing legacy segments (verified, untouched):
- `UFV7eu` Master Send Segment - No Spark (Xtra) - Auckland Subscribers
- `S6sijb` `[Z]` Sitewide (30d engaged), `VmBy2n` 60d, `Wby7tp` 90d, `RKdgTM` 180d
- `QYmdK4` `[Z]` Vitamins & Supplements (180d engaged)

## 3. The High AOV ($100+) Zero-Count Issue

`WkwEvG` definition (verified):
```
Placed Order (count > 0) WHERE
  $value > 100  AND  Collections contains_any [_retail]
  in last 1095 days
AND profile is subscribed (email)
```

Returns **0 profiles** despite store-wide AOV ~$56 (so $100+ orders certainly exist). Likely root causes, in order of likelihood:

1. **Property name mismatch** — Klaviyo's Shopify integration may emit order value as `Total Price`, `value`, or `Order Value` rather than `$value`. Two filters within the same condition are ANDed *on the same event*, so a missing/mis-cased property silently zeroes the result.
2. **AND-on-same-event interaction** — combined `$value > 100` AND `Collections contains_any _retail` requires both on the *same* order event. If product collection metadata isn't on the order event itself (only on line items), the join fails.
3. Threshold genuinely too high (less likely given store volume).

**Phase-1 fix path:** open one Placed Order event for a known $100+ retail customer in Klaviyo UI (`/metric/Sxnb5T`), inspect actual property names, rebuild filter against the right field. Try $50 threshold as fallback.

## 4. Google Ads Customer Match Capability (verified — Zapier `list_enabled_zapier_actions`)

All required Customer Match endpoints are enabled and OAuth-authenticated via Zapier:

| Action | Key | Use |
|---|---|---|
| Create Customer List | `create_customer_list` | Create the audience shell in Google Ads |
| Add Contact w/ Email | `add_email_to_customer_list_v3` | Sync emails (1k+ minimum) |
| Add Contact (full) | `add_to_customer_list_v3` | Sync emails + phones + names (better match rate) |
| Remove Contact | `remove_from_customer_list_v2` | Keep audience fresh |
| Find Customer List | `find_customer_list` | Lookup existing list IDs |
| Find Campaign by Name | `find_campaign_by_name` | Locate campaign for audience attach |
| Find Campaign by Id | `find_campaign_by_id` | Same, by ID |
| Set Campaign Status | `set_campaign_status` | Enable/pause campaigns |
| Send Offline Conversion | `send_offline_conversion_v2` | Server-side conversion uploads |
| Make API GET / Mutating Request | `_zap_raw_request` | Raw GAQL fallback for anything not covered above |

**What this proves:** the *mechanism* exists. What it does NOT prove (still a Phase-1 verification task):
- Whether Bargain Chemist's specific MCC accepts Customer Match given the Health & Beauty industry classification (Google restricts CM for "Personal hardships"/medical categories — pharmacy borderline).
- Whether OMD agency (per pasted context) has audience-attach permissions on the live campaigns.

## 5. Klaviyo Metrics Used by Segments (referenced metric IDs)

From segment definitions verified above:

| Metric ID | Inferred meaning (from usage) |
|---|---|
| `Sxnb5T` | Placed Order |
| `VvcTue` | Started Checkout / Cart |
| `XQ2zfW` | Viewed Product |
| `SZ8GZJ` | Opened Email |
| `W3AFKt` | Clicked Email |
| `UfaNeY` | One of: Active on Site / Received Email / SMS metric |

Phase-1 confirmation: call `klaviyo_get_metric` on each ID to lock the names — the segment logic is correct regardless, this is just for documentation hygiene.

## 6. What This Session Did NOT Verify

Honest list of unknowns the next session must resolve before promising results:

1. **Campaign names + IDs** — pasted plan referenced "PMax ($3+ ROAS)", "PMax tROAS", "PMax tCPA", "NZ – SE – Brand". Not verified in this session because Zapier `find_campaign_by_name` requires interactive OAuth account selection. Phase 1: confirm via raw GAQL or in Google Ads UI.
2. **Per-campaign performance** (ROAS / CPA / CR claims in pasted v1) — no Google Ads read access in this session.
3. **Customer Match acceptance** for this specific MCC (healthcare flag).
4. **OMD agency change-management** workflow.
5. **Klaviyo Audience Sync UI** (the native CM connector) status — pasted v1 said it failed; not re-tested here. If the native sync works, prefer it over Zapier (real-time + automatic refresh).
