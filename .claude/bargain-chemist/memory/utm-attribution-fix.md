# UTM Attribution Fix — Klaviyo + Shopify

**Date**: 2026-05-06
**Status**: VERIFIED — issue confirmed but root cause refined
**Priority**: 🔴 Critical — must fix before any campaign optimisation is measurable

---

## Verification (added 2026-05-06)

User pushed back on whether I'd actually checked. Re-verified:

### What IS configured
- Every campaign has `trackingOptions.addTrackingParams: true` ✓
- `isTrackingClicks: true`, `isTrackingOpens: true` ✓
- → Klaviyo's link tracking IS enabled

### What is NOT configured
- `trackingOptions.customTrackingParams: []` is **empty** on every campaign
- This means Klaviyo is using its internal `_kx` / `_ke` parameters for tracking, NOT standard UTMs that Shopify reports on
- Shopify's `order_referrer_source` and `order_referrer_name` over last 30 days show **NO** "klaviyo", **NO** "email", **NO** Klaviyo-flagged orders. Top sources: google search, direct, self-referral.
- Shopify ShopifyQL does NOT expose `utm_source` as a queryable dimension — so we can only see what Shopify maps to its referrer source.

### Conclusion
Klaviyo is technically tagging links, but with parameters Shopify doesn't recognise as "email" or any specific source. The fix is to **populate `customTrackingParams` with standard UTM values** that Shopify and GA4 recognise.

---

## The problem in one sentence

Shopify's "email" referrer source attributes only **2 orders / $70.95** in the last 90 days, but Klaviyo's own reporting attributes ~$48,000 to email flows alone in the same period. **UTM tagging is missing on Klaviyo links**, so every email click is being attributed to "search" or "direct" in Shopify analytics.

## Why it matters

1. **Cannot measure the impact of email changes** — improve the welcome flow, fix the cart flow, rewrite a campaign — Shopify will show no change because attribution is broken.
2. **Cannot make budget cases** — "email drives 3% of revenue" looks bad; "email drives 8% of revenue" justifies investment. Both might be true, only one is visible.
3. **Misleads Google Ads optimisation** — if email-driven traffic is mis-attributed to "search", Google Ads will look more profitable than it is, leading to over-spend.
4. **Confuses cohort + LTV analysis** — customer source data is wrong.

## What "fixed" looks like

Every link sent from Klaviyo (campaigns + flows + SMS) automatically appends:
```
?utm_source=klaviyo&utm_medium=email&utm_campaign={{campaign_or_flow_name|slug}}
```

Then Shopify's order_referrer_source = "email" (or `klaviyo`) and it shows the real revenue.

---

## The fix (Klaviyo settings)

### Klaviyo → Account → Settings → UTM Tracking

Klaviyo has a built-in setting that auto-appends UTM parameters to every link in every email/SMS sent. **It is enabled but the parameters need to be configured properly.**

1. Go to **Klaviyo → Account → Settings → UTM Tracking** (sometimes under **Settings → Other → UTM Tracking** in older UI)
2. Confirm **"Add UTM parameters to all links"** is ON (it appears to be from API check)
3. Set the standard UTM **values** (this is the missing piece):
   - **utm_source** = `klaviyo` (so Shopify reports show "klaviyo" as a source)
   - **utm_medium** = `email` for email campaigns, `sms` for SMS — Klaviyo allows different values per channel via tags
   - **utm_campaign** = `{{ campaign.name|default:flow.name }}` (templated)
   - **utm_content** (optional, for flows) = `{{ flow_message.name|default:'' }}`
4. **Importantly**: select "Apply to ALL email + SMS sends" — flows AND campaigns
5. Save.
6. Verify: send a preview to yourself, click a link, observe URL — should now have `utm_source=klaviyo&utm_medium=email&utm_campaign=...`
7. Verify in Shopify: 24h after first send, run `FROM sales SHOW orders, total_sales GROUP BY order_referrer_source, order_referrer_name SINCE -1d` — expect "klaviyo" to appear as referrer name.

### Alternative: UTMs at the campaign / flow level

If you want different `utm_source` for campaigns vs flows (e.g. `klaviyo-campaign` vs `klaviyo-flow`), set them per send rather than globally.

### What to check on Shopify

After the change is live:
- Wait 24–48 hours for new orders.
- Run: `FROM sales SHOW orders, total_sales GROUP BY order_referrer_source SINCE -7d UNTIL today`
- "email" or "klaviyo" should now be a real number.

---

## Risks of this change

- **Existing email links cached** in subscriber inboxes won't have UTM until they click again. Old emails attribute as before for next 30–60 days.
- **GA4 attribution** will also improve — will show email as a higher contributor (good thing, but stakeholders should know).
- **Google Ads "auto-tagging" interaction** — if Google Ads has GCLID + Klaviyo also tags, no conflict (different parameters).
- **Shopify's order_referrer_source uses landing-page UTM params**, so attribution will reflect the LAST click in the journey. For multi-touch attribution, use GA4.

## Risks of NOT fixing this

- Every email optimisation we do for the next quarter will be invisible in Shopify analytics.
- Cannot prove ROI of email work to Peter or anyone else.
- Decisions get made on the wrong data.

---

## Recommendation

**Make this change now**, before any flow activation or campaign rewrite. Ideally before the next campaign send (so the next send is the first to track properly).

This is a **low-risk, high-leverage settings change**. Cost: 5 minutes. Impact: every email metric becomes measurable from this point forward.

---

## Once UTMs are live, additional setup recommended

### 1. Custom Reporting in Klaviyo
Create a "Email-Attributable Revenue" custom metric using the Reporting API → group by utm_campaign → reconcile with Shopify "email" referrer over time.

### 2. Shopify analytics segment
Set up a saved Shopify Analytics report: revenue by `order_referrer_source` weekly, with email as the focus.

### 3. Track Klaviyo flow IDs in utm_campaign
Use `{{ flow.name|slugify }}_step_{{ flow_message.name|slugify }}` so we can see in Shopify which specific email in which flow drove the revenue.

### 4. Backwards reconciliation note
Klaviyo's last-90-days "$48k flow revenue" came from emails sent before UTM is added. Shopify's "$70.95 email revenue" for the same period is the under-attribution baseline. After the fix, both numbers should converge: Klaviyo attribution should be slightly higher than Shopify "email" referrer (Klaviyo uses 5d attribution window; Shopify uses last-click on landing page), but the gap should be narrow (maybe 10–30%), not 99%.

---

## Status

- [ ] User approves the change
- [ ] Settings change made in Klaviyo
- [ ] Test send + verify UTM in link
- [ ] Wait 1 week
- [ ] Pull `FROM sales SHOW orders, total_sales GROUP BY order_referrer_source SINCE -7d` and confirm email > 2 orders
- [ ] Log outcome in `decisions-log.md`

**Estimated revenue visibility recovered**: ~$48k/90d → annualised view of ~$200k+/year of email-attributable revenue that Shopify currently shows as zero.
