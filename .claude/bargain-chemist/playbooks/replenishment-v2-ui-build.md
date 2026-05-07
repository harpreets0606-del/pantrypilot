# Replenishment V2 — Klaviyo UI Build Guide

Reference for building the new flow structure in the Klaviyo UI after
running `klaviyo-deploy-replenishment-templates.ps1`. Why hybrid: the
`POST /api/flows` endpoint is beta with unverified conditional-split
schema. UI build is faster and 100% reliable.

## Prerequisites

1. ✅ `klaviyo-pause-replenishment-v1.ps1` has been run (V4cZMd is now
   `manual`, no new entries triggered)
2. ✅ `klaviyo-deploy-replenishment-templates.ps1` has been run
3. ✅ The 6 template IDs are saved in
   `.claude/bargain-chemist/snapshots/<date>/replenishment-template-ids.json`

Open that JSON file. You'll see something like:

```json
[
  {"Key":"vitamins","TemplateId":"AbCdEf",...},
  {"Key":"skincare","TemplateId":"GhIjKl",...},
  {"Key":"haircare","TemplateId":"MnOpQr",...},
  {"Key":"oralcare","TemplateId":"StUvWx",...},
  {"Key":"babycare","TemplateId":"YzAbCd",...},
  {"Key":"fallback","TemplateId":"EfGhIj",...}
]
```

Keep this open in another tab — you'll paste the IDs in.

## Step 1 — Create the new flow

1. In Klaviyo: Flows → **Create Flow** → **Create from scratch**
2. Name: `[Z] Replenishment - Category Based`
3. Tags: `replenishment`, `v2`
4. Click **Create Flow**

## Step 2 — Configure trigger

1. Click the trigger box at the top
2. Trigger type: **Metric**
3. Metric: `Ordered Product`
4. Click **Add a filter** under the trigger:
   - Property: `Categories` → Operator: `does not contain` → Value:
     `_pharmacy-only`
5. Click **Add a filter** again:
   - `Categories` → `does not contain` → `_pharmacist-only`
6. Click **Add a filter** again:
   - `Categories` → `does not contain` → `_prescription`
7. Save trigger

## Step 3 — Configure flow filter (re-entry guard)

1. Click **Flow filter** below the trigger
2. Click **Add a filter**:
   - `Has been in this flow` → `zero times` → `since` → `45 days ago`
3. Add another filter:
   - `Profile property` → `email_marketing_consent` → `is` → `subscribed`
4. Save

## Step 4 — Build the 5 category branches

For each category in this order: **Vitamins → Skincare → Hair Care → Oral
Care → Baby & Family**, repeat the pattern below. Order matters: first
match wins.

### 4a. Vitamins branch (first split)

1. Drag a **Conditional Split** from the sidebar onto the canvas, right
   below the trigger
2. Click the split → Edit conditions
3. Add condition:
   - `Properties about someone` → no, click **What someone has done →**
   - **Ordered Product** → `at least once` → in the timeframe `since
     starting this flow`
   - Then **Add a filter** within the condition:
     - Property: `Categories` → `contains` → `CAT=Vitamins`
4. Save the split. The split now has TRUE (yes) and FALSE (no) branches.
5. **YES branch:**
   - Drag **Time Delay** below the YES branch → set to **60 days** →
     timezone "Profile timezone"
   - Drag **Email** below the delay
   - Click the email → **Use existing template** → pick the **Vitamins**
     template ID from the snapshot JSON
   - Edit message:
     - Subject: `Time to top up your vitamins, {{ first_name|default:'there' }}`
     - Preview: `Daily wellness works best when you don't run out. Free shipping over $79.`
     - From: `hello@bargainchemist.co.nz`, Label: `Bargain Chemist`
     - Reply-to: `orders@bargainchemist.co.nz`
     - **Smart Sending**: ON
     - **Add tracking parameters**: ON
       - Custom: `utm_source=klaviyo`, `utm_medium=email`,
         `utm_campaign=replenishment-v2`, `utm_content=e1-vitamins`
   - Save → DRAFT for now (will activate after smoke test)
6. **NO branch:** leave empty for now — next split goes here

### 4b. Skincare branch (under Vitamins NO)

1. Drag another **Conditional Split** under the Vitamins NO branch
2. Same pattern: `Ordered Product at least once since starting this flow`
   filter `Categories contains "CAT=Skin Care"`
3. **YES branch:**
   - Time Delay: **45 days**
   - Email: pick **Skincare** template ID
     - Subject: `Your skincare routine misses you, {{ first_name|default:'you' }}`
     - Preview: `Consistency is what skin loves most - top up before you run dry.`
     - Smart Sending ON, UTM `utm_content=e2-skincare`
4. **NO branch:** continue to next split

### 4c. Hair Care branch

- Filter: `Categories contains "CAT=Hair Care"`
- YES → Delay **60 days** → Email (Hair Care template)
  - Subject: `{{ first_name|default:'Hey' }}, ready for a hair care top-up?`
  - Preview: `Shampoo, conditioner, styling - everything you need from NZ's best prices.`
  - UTM `utm_content=e3-haircare`

### 4d. Oral Care branch

- Filter: `Categories contains "CAT=Oral Hygiene & Care"`
- YES → Delay **30 days** → Email (Oral Care template)
  - Subject: `Your oral care kit needs a refresh, {{ first_name|default:'there' }}`
  - Preview: `Toothpaste, mouthwash, floss - the daily basics, ready when you are.`
  - UTM `utm_content=e4-oralcare`

### 4e. Baby & Family branch

- Filter: `Categories contains "CAT=Baby Care"`
- YES → Delay **30 days** → Email (Baby template)
  - Subject: `Time to restock the baby essentials, {{ first_name|default:'there' }}`
  - Preview: `Nappy creams, wipes and the everyday basics - all at NZ's lowest prices.`
  - UTM `utm_content=e5-babycare`

## Step 5 — Universal fallback

After the 5th split's NO branch:

1. Drag **Time Delay**: **45 days**
2. Drag **Email**: pick **Fallback** template ID
   - Subject: `{{ first_name|default:'There' }}, time to restock your favourites?`
   - Preview: `Whatever you ordered last time - restock it at the same great Bargain Chemist price.`
   - Smart Sending ON, UTM `utm_content=e6-fallback`

## Step 6 — Final structure check

Your flow should look like:

```
Trigger (Ordered Product, filtered)
   |
Flow filter (45-day re-entry, consented)
   |
Split 1: bought Vitamins?
   YES -> Delay 60d -> E1 Vitamins (DRAFT)
   NO  -> Split 2: bought Skincare?
            YES -> Delay 45d -> E2 Skincare (DRAFT)
            NO  -> Split 3: bought Hair Care?
                     YES -> Delay 60d -> E3 Hair Care (DRAFT)
                     NO  -> Split 4: bought Oral Care?
                              YES -> Delay 30d -> E4 Oral Care (DRAFT)
                              NO  -> Split 5: bought Baby Care?
                                       YES -> Delay 30d -> E5 Baby & Family (DRAFT)
                                       NO  -> Delay 45d -> E6 Fallback (DRAFT)
```

## Step 7 — Smoke test

1. Make sure flow status overall is `manual` (top-right toggle)
2. For each email, click **Preview** → **Send a preview** → enter your
   own email address → check rendering on:
   - Gmail (web + iOS)
   - Apple Mail (iOS)
   - Outlook (desktop)
3. Click each CTA, verify it goes to the right `/collections/<handle>`
4. Verify UTM params arrive in browser URL
5. Check mobile rendering: hero is centred, value-prop strip stacks
   1-col below 480px

## Step 8 — Activate

1. Once smoke test passes, set each email status to `live` (not draft)
2. Toggle the flow status: `manual` → `live`
3. Verify in flow list that status now shows `live`

## Step 9 — Snapshot for the record

Run the dump script to capture the new flow's full definition:

```powershell
.\.claude\bargain-chemist\scripts\klaviyo-dump-flow-definition.ps1 -FlowId <new_flow_id>
```

Commit the snapshot to git. This is our source-of-truth for what got
built.

## Step 10 — 14-day review and archival

After the new flow has been live for 14 days:

1. Pull V2 metrics: entry rate, send rate per branch, open/click/CVR
2. Compare to V4cZMd's prior 14 days (approximately zero — most emails
   were draft)
3. If V2 is performing (any non-zero engagement on at least 3 of 6
   emails), proceed:
   - Archive old V4cZMd via UI: open V4cZMd → Settings → **Archive**
   - Or via API: `PATCH /api/flows/V4cZMd/` with `attributes.archived = true`
4. If V2 is underperforming, root-cause first before archiving the old
   one (kept paused for fallback rollback)

## Notes

- **Re-entry**: 45-day flow filter prevents spam from frequent buyers.
  A customer ordering monthly enters the flow at most every 45 days.
- **Smart sending**: ON for all 6 emails. Suppresses if customer got any
  other Klaviyo email in the last 16 hours.
- **No coupons** anywhere. Everything points to free shipping over $79
  and Price Beat 10% Guarantee.
- **No fear language**. Subjects all front-loaded, factual.
- **Pharmacy-only / pharmacist-only / prescription** are excluded at the
  trigger filter level. A customer with a mixed cart still enters for
  the OTC line items.
