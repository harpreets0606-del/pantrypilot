# Template Activation Guide
*Generated 2026-05-07 — 4 templates ready to upload*

---

## How to create a template in Klaviyo (takes ~2 mins each)

1. Go to **Content → Templates → Create Template**
2. Choose **"Import HTML"** (or "Code your own")
3. Paste the HTML from the file listed below
4. Save with the exact template name shown
5. Then follow the flow-assignment steps

---

## Template 1 — Welcome Email 1 (Immediate send)

**File:** `.claude/bargain-chemist/templates/welcome-email-1.html`
**Template name:** `BC — Welcome Email 1 — Welcome to the Family`
**Subject line:** `Welcome to Bargain Chemist, {{ first_name|default:'there' }} 👋`
**Preview text:** `NZ's most trusted pharmacy — and your best price starts now.`

### Assign to flows:
- **Welcome Series Website (SehWRt)** → find Email 1 action (message ID `U2HQmW`) → Edit → "Change template" → select this template
- **Welcome Series No Coupon (TsC8GZ)** → find Email 1 action (message ID `UC2XAR`) → Edit → same

---

## Template 2 — Welcome Email 2 (Day 1)

**File:** `.claude/bargain-chemist/templates/welcome-email-2.html`
**Template name:** `BC — Welcome Email 2 — Best Sellers`
**Subject line:** `{{ first_name|default:'There' }}, here's what's flying off our shelves`
**Preview text:** `NZ's best-selling vitamins, skincare and pharmacy essentials — see what Kiwis love.`

### Assign to flows:
- **Welcome Series Website (SehWRt)** → find Email 2 action (message ID `QYfRCd`) → "Change template"

**Note on product feed:** This email uses `feeds.Best_Selling_No_Clearance`. Confirm that feed exists in Klaviyo under **Content → Feeds**. If the feed name is different, update the Liquid tag `{% if feeds.Best_Selling_No_Clearance %}` to match your actual feed name.

---

## Template 3 — Welcome Email 3 (Day 3 or Day 4)

**File:** `.claude/bargain-chemist/templates/welcome-email-3.html`
**Template name:** `BC — Welcome Email 3 — Last Nudge`
**Subject line:** `{{ first_name|default:'Still here' }} — 3 reasons NZ shops at Bargain Chemist`
**Preview text:** `Price beat guarantee, free shipping, trusted pharmacists since 1984.`

### Assign to flows:
- **Welcome Series Website (SehWRt)** → find Email 6 action (message ID `VJwtx3`) → "Change template"
- OR add a new SEND_EMAIL action if you want a 3rd position that doesn't exist yet

---

## Template 4 — Cart Abandonment Email 3 (72h last chance)

**File:** `.claude/bargain-chemist/templates/cart-abandon-email-3.html`
**Template name:** `BC — Cart Abandonment Email 3 — Last Chance (72h)`
**Subject line:** `Last chance — your cart's waiting 🛒`
**Preview text:** `Don't let NZ's best pharmacy prices slip away. Complete your order today.`

### Add to Cart Abandonment flow (RPQXaa):

The current flow ends at Email 2 (message `TpkzDd`, ~25.5h after Email 1).

**Steps to add Email 3:**
1. Open flow **RPQXaa** → Edit
2. After the last Email 2 send action, click **+** to add a new step
3. Add **Time Delay** → set to **46.5 hours** (so total from trigger = 72h)
   - In seconds: 167,400 — OR just set the delay to 2 days (to keep it round)
   - Recommended: **2 days from trigger** (Klaviyo's "wait until X days" option is cleanest)
4. Add **Send Email** action → assign the Cart Abandonment Email 3 template
5. Set **Subject:** `Last chance — your cart's waiting 🛒`
6. Set **From:** `hello@bargainchemist.co.nz` (match existing emails in the flow)
7. Keep flow status as **LIVE** after saving (this flow is already live — you're adding a branch, not changing existing ones)

---

## After uploading all templates

- Preview each one in Klaviyo's preview tool with a test profile
- Check the product feed renders (Email 2)
- Check `{{ event.extra.CheckoutURL }}` resolves in Cart Email 3
- For Welcome Series: when you're happy, change flow **SehWRt** status from DRAFT → LIVE

---

## Subject lines + preview text summary

| Email | Subject | Preview Text |
|-------|---------|--------------|
| Welcome E1 | `Welcome to Bargain Chemist, {{ first_name\|default:'there' }} 👋` | `NZ's most trusted pharmacy — and your best price starts now.` |
| Welcome E2 | `{{ first_name\|default:'There' }}, here's what's flying off our shelves` | `NZ's best-selling vitamins, skincare and pharmacy essentials — see what Kiwis love.` |
| Welcome E3 | `{{ first_name\|default:'Still here' }} — 3 reasons NZ shops at Bargain Chemist` | `Price beat guarantee, free shipping, trusted pharmacists since 1984.` |
| Cart E3 | `Last chance — your cart's waiting 🛒` | `Don't let NZ's best pharmacy prices slip away. Complete your order today.` |
