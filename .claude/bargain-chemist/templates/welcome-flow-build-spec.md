# Welcome Series 2026 — Build Spec
*New flow to build alongside the existing `SehWRt` (which stays in DRAFT, untouched)*

---

## 0. Prerequisite — deploy templates

Before building the flow, run:

```powershell
.\.claude\bargain-chemist\scripts\klaviyo-deploy-templates.ps1
```

This uploads all 4 HTML files to Klaviyo as templates. The script prints each template's ID + edit URL. You'll reference these by name in step 4 below.

---

## 1. Flow metadata

| Field | Value |
|-------|-------|
| **Flow name** | `Welcome Series 2026 - No Coupon` |
| **Tag** | `bc-welcome-2026-05` |
| **Status (initial)** | DRAFT (turn on after preview) |
| **Existing flow `SehWRt`** | Leave AS-IS in DRAFT — do not touch |

**To create:** Klaviyo → Flows → Create From Scratch → name it as above.

---

## 2. Trigger

| Field | Value |
|-------|-------|
| **Trigger type** | List trigger (or Form Submit, whichever the existing form connects to) |
| **Trigger** | "When someone is added to **Website Form** list" — match exactly what `SehWRt` uses (so this flow takes over the same audience) |
| **Trigger filter** | `Email` is set AND `Email Marketing Consent` equals `subscribed` |

**Why same trigger as SehWRt:** when you turn this new flow ON and SehWRt OFF (or leave SehWRt DRAFT), profiles flow into this one without any re-tagging.

---

## 3. Flow filters

Add these on the trigger card → "Flow filters":

| Filter | Why |
|--------|-----|
| Has not been in this flow in the last 30 days | Prevents re-entry on resubscribe |
| `Email` is set | Defensive — no email = nothing to send |

---

## 4. Flow steps (in order)

### Step 1 — Time Delay
- **Wait:** 5 minutes
- **Reason:** Lets Klaviyo finish profile sync from form submit before sending

### Step 2 — Send Email (Email 1)
- **Template:** `BC - Welcome Email 1 - Welcome to the Family`
- **Subject line:** `Welcome to Bargain Chemist, {{ first_name|default:'there' }}`
- **Preview text:** `NZ's most trusted pharmacy — and your best price starts now.`
- **From name:** `Bargain Chemist`
- **From email:** `hello@bargainchemist.co.nz`
- **Reply-to:** `hello@bargainchemist.co.nz`
- **Smart Sending:** ON (skip if any send in last 16h)
- **Add UTM tracking:** ON
  - `utm_source=klaviyo`
  - `utm_medium=email`
  - `utm_campaign=welcome_e1_2026`

### Step 3 — Time Delay
- **Wait:** 1 day

### Step 4 — Conditional Split
- **Condition:** "What someone has done (or not done)"
- **Filter:** `Placed Order` at least once **since starting this flow**
- **YES branch:** → connect to "Exit flow" (or just leave empty — flow ends)
- **NO branch:** → continue to Step 5

### Step 5 — Send Email (Email 2)
- **Template:** `BC - Welcome Email 2 - Best Sellers`
- **Subject line:** `{{ first_name|default:'There' }}, here's what's flying off our shelves`
- **Preview text:** `NZ's best-selling vitamins, skincare and pharmacy essentials — see what Kiwis love.`
- **From name:** `Bargain Chemist`
- **From email:** `hello@bargainchemist.co.nz`
- **Reply-to:** `hello@bargainchemist.co.nz`
- **Smart Sending:** ON
- **Add UTM tracking:** ON
  - `utm_source=klaviyo`
  - `utm_medium=email`
  - `utm_campaign=welcome_e2_2026`
- **Note:** Verify product feed `Best_Selling_No_Clearance` exists under Content → Feeds. If named differently, edit the Liquid `{% if feeds.Best_Selling_No_Clearance %}` block in the template HTML.

### Step 6 — Time Delay
- **Wait:** 2 days

### Step 7 — Conditional Split
- **Condition:** Same as Step 4 — `Placed Order` at least once since starting this flow
- **YES branch:** → exit
- **NO branch:** → continue to Step 8

### Step 8 — Send Email (Email 3)
- **Template:** `BC - Welcome Email 3 - Last Nudge`
- **Subject line:** `{{ first_name|default:'Still here' }} — 3 reasons NZ shops at Bargain Chemist`
- **Preview text:** `Price beat guarantee, free shipping, trusted pharmacists since 1984.`
- **From name:** `Bargain Chemist`
- **From email:** `hello@bargainchemist.co.nz`
- **Reply-to:** `hello@bargainchemist.co.nz`
- **Smart Sending:** ON
- **Add UTM tracking:** ON
  - `utm_source=klaviyo`
  - `utm_medium=email`
  - `utm_campaign=welcome_e3_2026`

### Step 9 — End of flow
- (No action; flow naturally completes)

---

## 5. Flow-level settings

Click the flow's settings cog in Klaviyo:

| Setting | Value | Why |
|---------|-------|-----|
| **Smart Sending** (flow level) | ON | Backstop in case any individual email override is OFF |
| **Quiet Hours** | 8 AM – 9 PM Pacific/Auckland | Avoid late-night sends to NZ subscribers |
| **Action exclusion** | None | We rely on the per-step Conditional Splits |
| **Email re-send** | OFF | Default — don't re-send to repeat triggers within 30 days |

---

## 6. Pre-launch checklist

Run all of these before flipping to LIVE:

- [ ] All 4 templates uploaded (run the PowerShell deploy script)
- [ ] Each email previewed with a test profile (uses `{{ first_name }}` correctly)
- [ ] Email 2 product feed renders (3 best-sellers visible, prices show in NZD)
- [ ] All "Shop Now" CTAs go to `bargainchemist.co.nz/collections/all`
- [ ] Footer renders with `{{ organization.name }}` and `{{ organization.full_address }}` populated
- [ ] Unsubscribe link works (preview with test email)
- [ ] UTM tracking visible on a clicked link (preview source URL)
- [ ] Conditional splits show "Placed Order since starting this flow" — NOT "in last X days"
- [ ] Flow filter "has not been in flow in last 30 days" is set
- [ ] Existing `SehWRt` is **still in DRAFT** (don't accidentally activate both)

---

## 7. Activation

When the checklist is green:

1. Set `Welcome Series 2026 - No Coupon` to **LIVE**
2. Confirm `SehWRt` is **DRAFT** (so no double-send)
3. Send yourself a test trigger (submit the website form with a test email)
4. Monitor inbox for Email 1 within ~5 minutes
5. Wait 24h to confirm Email 2 fires (use a test profile that hasn't ordered)

---

## 8. Reporting (set this up after 14 days of live data)

Track these in Klaviyo → Analytics → Custom Report:

| Metric | Target (per Klaviyo benchmark) |
|--------|-------------------------------|
| Email 1 open rate | 40–55% |
| Email 1 click rate | 4–8% |
| Email 1 placed order rate | 2–4% |
| Series total revenue per recipient | $3.34+ |
| Series conversion rate | 8–12% |

If Email 2 / Email 3 conversion < 1%, A/B test subject lines (curiosity vs benefit framing).

---

## 9. Rollback plan

If the new flow underperforms after 30 days:

1. Set `Welcome Series 2026 - No Coupon` to **DRAFT**
2. Set `SehWRt` to **LIVE** (after fixing its coupon splits per the no-coupon strategy)
3. Log the postmortem in `memory/decisions-log.md`

---

## File locations

- Templates: `.claude/bargain-chemist/templates/welcome-email-{1,2,3}.html`
- Deployment script: `.claude/bargain-chemist/scripts/klaviyo-deploy-templates.ps1`
- Visual diagram: `.claude/bargain-chemist/templates/welcome-flow-diagram.png`
- This spec: `.claude/bargain-chemist/templates/welcome-flow-build-spec.md`
