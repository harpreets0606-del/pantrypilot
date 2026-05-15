# Continuation Prompt — Drop into Next Chat Session

Copy everything between the `---` markers below into a new Claude session.

---

I'm continuing the Bargain Chemist Klaviyo × Google Ads segment activation work. Read these two files in full first — they contain everything you need to know:

1. `/home/user/pantrypilot/bargain-chemist-analysis.md` — verified account context, all 14 segment IDs + counts, capability proofs
2. `/home/user/pantrypilot/google-ads-segment-activation-plan.md` — the activation plan, campaign mappings, phases, risks

Branch: `claude/klaviyo-google-ads-research-PdMUG`. Klaviyo + Zapier (Google Ads) MCPs are already wired up against the Bargain Chemist account.

**Where we are:** Phase 0 (verify) — about to run the 5-email Customer Match acceptance test.

**What I need you to do — in order:**

1. **Re-confirm account binding.** Call `klaviyo_get_account_details` and check the org name still says "Bargain Chemist" (account `XCgiqg`).
2. **Pull the live campaign list.** Call Zapier `find_campaign_by_name` (Google Ads) — confirm whether these names exist exactly: `PMax ($3+ ROAS)`, `PMax tROAS`, `PMax tCPA`, `NZ – SE – Brand`. If not, list what IS in the account and propose the renaming map. (Bonus: try GAQL via `_zap_raw_request` — `SELECT campaign.id, campaign.name, campaign.status FROM campaign WHERE campaign.status = 'ENABLED'`.)
3. **Phase-0 CM acceptance test.** Create one Customer Match list `BC_test_5email` via `create_customer_list`, add 5 throwaway @bargainchemist.co.nz test emails via `add_email_to_customer_list_v3`. If it succeeds → Customer Match works for this MCC. If Google rejects with a healthcare-flag error → flag it and stop.
4. **Diagnose `WkwEvG` zero-count.** Pull one Placed Order event for a known retail customer via `klaviyo_query_metric_aggregates` on metric `Sxnb5T` and inspect property names. Rebuild the High AOV segment with the right field name (or with $50 threshold as fallback if $100 has no matches).
5. **Lock metric IDs.** Quick `klaviyo_get_metric` calls on `Sxnb5T`, `VvcTue`, `XQ2zfW`, `SZ8GZJ`, `W3AFKt`, `UfaNeY` to confirm the names against the analysis doc.

Then **stop and ask me** before doing Phase 1 (sync exclusion segments). I want to approve each phase boundary.

**Things you must NOT do without asking me:**
- Don't sync the GLP-1 segment (`X2pdkD`) to Google Ads — ever. Prescription-medication audiences violate Google policy.
- Don't use Pharmacy-Only (`YgrizT`) as a positive target — exclusion only.
- Don't pause/enable any campaign via `set_campaign_status`.
- Don't push commits without showing me the diff first.

---

## What you'll need before pasting that

- New Klaviyo private API key (rotate the previous one at https://www.klaviyo.com/account#api-keys-tab — the old one was visible in the prior session transcript)
- Confirm Zapier MCP is still connected to the same Google Ads account (OMD-managed MCC `5653976978` per pasted prior context — re-verify)
- Decide whether you want to run Phase 0 yourself in the Google Ads UI or have Claude do it via Zapier — the test is 60 seconds either way
