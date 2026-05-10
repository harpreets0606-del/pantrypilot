# Browse + Search Abandonment — UI Build Guide

Step-by-step Klaviyo UI instructions to rebuild both flows for maximum sales recovery, using verified BC data + best practice from `BRAND_VOICE.md` and `VERIFIED_STATE.md`.

**Prereqs:**
- All 4 abandonment templates POSTed to Klaviyo (run `--deploy-abandonment-templates` once that script step is added — for now, you can manually create them in the Klaviyo Templates UI by copy-pasting the HTML output of `python scripts/abandonment_templates.py --all`)
- Klaviyo account access (Flows + Templates permissions)
- 30 minutes per flow

## Decision: rebuild vs edit existing

**Recommendation: archive the existing draft flows and build fresh** because:
1. Existing flows have my injected duplicate UEMA footer in the bound templates
2. Existing flows are single-email; we need to add a second email + splits
3. Klaviyo's API doesn't accept structural additions to existing flows; UI rebuild is cleaner

**Existing flows to archive after build:**
- `RtiVC5` — [Z] Browse Abandonment (draft, will be replaced)
- `XbQiKg` — [B] Search Abandonment V4 (draft, will be replaced)

Don't delete — archive. That keeps the historical events tied to the old flow IDs.

---

## Flow 1: Browse Abandonment

### 1.1 Trigger setup

In Klaviyo → Flows → Create Flow → "Build your own"

**Trigger:** Metric → "Viewed Product"
- Use Klaviyo's native `Viewed Product` (Shopify integration), NOT the `[Boost] Viewed Product` — Klaviyo's native is more reliable and used by other Klaviyo customers' Browse Abandonment templates
- Verified firing volume: see `VERIFIED_STATE.md` → ~1,400 unique profiles/week

**Trigger filters** (add via "Add a filter" on the trigger):
- `Has placed order at least 0 times in the last 1 days` → set to `equals 0` (don't email customers who just bought)
- `What someone has done (or not done): Has not been in this flow in the last 7 days` (frequency cap; prevents same product spam)
- (Optional but recommended) `Item: Categories does not contain "_pharmacy-only"` AND `does not contain "_pharmacist-only"` (exclude restricted SKUs from Browse Abandonment)
- `Has consented to receive email marketing equals true`

### 1.2 Profile filter (audience-level, applies to whole flow)

- `Email is not suppressed`
- `Email subscriptions: receives marketing email`
- (Optional) `Has placed at least 1 order ever` — i.e. only retarget previous buyers, not first-time browsers, OR remove this if you want to retarget first-time visitors too. **Industry standard is no filter here** — give first-time visitors the chance.

### 1.3 Flow structure

```
[Trigger: Viewed Product]
       ↓
   [Smart Sending: ON globally for the flow]
       ↓
   ⏱ Time delay: 4 hours
       ↓
   🚪 Conditional split:
       Has Started Checkout in last 4 hours? → END
       Has Placed Order in last 4 hours? → END
       Otherwise ↓
       ↓
   📧 Email 1: "[BC-Abandonment] Browse E1"
       Smart Sending: ON
       Transactional: OFF
       Add tracking params: ON
       Custom UTM: utm_campaign={message_name} ({message_id}),
                   utm_medium=email,
                   utm_source=browse-abandonment-e1
       ↓
   ⏱ Time delay: 24 hours
       ↓
   🚪 Conditional split:
       Has Started Checkout in last 28 hours? → END
       Has Placed Order in last 28 hours? → END
       Has Viewed Product in last 24 hours? → END (they came back)
       Otherwise ↓
       ↓
   📧 Email 2: "[BC-Abandonment] Browse E2"
       Smart Sending: ON
       Transactional: OFF
       Add tracking params: ON
       Custom UTM: ...source=browse-abandonment-e2
       ↓
   END
```

### 1.4 Email 1 settings

- Subject: `Still thinking it over, {{ first_name|default:'there' }}?`
- Preview text: `Pick up where you left off — your wellness pick is still here.`
- From: `Bargain Chemist <hello@bargainchemist.co.nz>`
- Template: `[BC-Abandonment] Browse E1`
- Smart Sending: ON
- Send-time: any time (Klaviyo will respect quiet hours per profile)
- Click tracking: ON
- UTM tracking: ON with custom params above

### 1.5 Email 2 settings

- Subject: `Take another look, {{ first_name|default:'there' }}`
- Preview text: `Saved for you, plus a few related picks.`
- Template: `[BC-Abandonment] Browse E2`
- **Important:** in the Klaviyo template editor, replace the placeholder text in the "Kiwis also love" section with a **Product Block** (Klaviyo's dynamic content):
  - Source: Recommended products
  - Filter by: Categories contains `{{ event.Categories }}` (Klaviyo will fall back to top sellers if no match)
  - Show: 3 products
  - Sort by: best sellers
- Same Smart Sending / tracking settings as E1

### 1.6 Smart Sending + send window

- Flow-level: Smart Sending ON
- Quiet hours: 8pm–8am local (NZ) — apply if BC has this configured account-wide

### 1.7 Conversion metric

- Set flow's conversion metric to `Placed Order` (`Sxnb5T`)
- Window: 5 days from email send (industry standard for abandonment)

---

## Flow 2: Search Abandonment

### 2.1 Trigger setup

**Trigger:** Metric → choose ONE based on which fires more reliably:
- `Submitted Search` (Shopify native, ID `XX5ssW`)
- `[Boost] Submitted Search` (Boost integration, ID `R2KxMT`) — verified higher volume per `VERIFIED_STATE.md`

Recommend: `[Boost] Submitted Search` for higher fuel.

**Trigger filters:**
- `Has not Clicked Search Result in last 1 hour` (didn't find what they wanted)
- `Has not Placed Order in last 1 day`
- `Has not been in this flow in last 14 days`
- `Has consented to receive email marketing`
- `Event property: searchQuery is not blank`

### 2.2 Profile filter

Same as Browse Abandonment.

### 2.3 Flow structure

```
[Trigger: [Boost] Submitted Search]
       ↓
   ⏱ Time delay: 2 hours (search is high-intent — react fast)
       ↓
   🚪 Conditional split:
       Has Clicked Search Result in last 2 hours? → END
       Has Placed Order in last 2 hours? → END
       Otherwise ↓
       ↓
   📧 Email 1: "[BC-Abandonment] Search E1"
       UTM: source=search-abandonment-e1
       ↓
   ⏱ Time delay: 48 hours
       ↓
   🚪 Conditional split:
       Has Placed Order in last 50 hours? → END
       Has Viewed Product in last 48 hours? → END (they came back)
       Otherwise ↓
       ↓
   📧 Email 2: "[BC-Abandonment] Search E2"
       UTM: source=search-abandonment-e2
       ↓
   END
```

### 2.4 Email 1 settings

- Subject: `Still looking for {{ event.searchQuery|default:'something' }}?`
- Preview text: `Pick up where you left off.`
- Template: `[BC-Abandonment] Search E1`
- Same tracking settings as Browse E1

### 2.5 Email 2 settings

- Subject: `More like '{{ event.searchQuery|default:'that' }}'`
- Preview text: `Top picks across our range.`
- Template: `[BC-Abandonment] Search E2`
- In Klaviyo template editor, replace placeholder with Product Block — top sellers fallback (since searchQuery may be too narrow for a useful filter)

### 2.6 Conversion metric

Same as Browse — `Placed Order`, 5-day window.

---

## Activation checklist

For each flow, before flipping to live:

- [ ] All trigger filters added
- [ ] All exit conditions (conditional splits) added
- [ ] Both templates created in Klaviyo Templates library
- [ ] Both emails bound to correct templates
- [ ] Smart Sending ON for both emails
- [ ] Transactional OFF for both
- [ ] UTM tracking ON with custom params
- [ ] Conversion metric set to `Placed Order` with 5-day window
- [ ] Run a test send to a personal email (Klaviyo's "Preview & Send Test")
- [ ] Profile filter set (suppress unsubscribes + bouncers)
- [ ] Set flow status to `Live` once tested

After activation, monitor in Klaviyo's Flow Performance dashboard:
- Open rate target: >40% (industry standard for Browse/Search Abandonment)
- Click rate target: >15%
- Conversion rate target: >2%

If any of those underperform after 2 weeks of data, revisit subject lines and timing.

---

## Pause-then-archive of existing draft flows

Once new flows are LIVE and confirmed firing, in Klaviyo UI:
1. Go to RtiVC5 ([Z] Browse Abandonment)
2. Confirm status is draft (it is per `VERIFIED_STATE.md`)
3. Archive (Flow Settings → Archive)
4. Repeat for XbQiKg ([B] Search Abandonment V4)

This keeps historical events but cleans up the flow list.
