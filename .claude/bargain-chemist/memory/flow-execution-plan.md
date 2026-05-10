# Flow Execution Plan — Existing State vs. Desired State

**Date**: 2026-05-06
**Purpose**: For each flow that needs work — current state, desired state, gap, execution steps, dependencies, expected impact.

> ⚠️ **Constraint**: Without Klaviyo MCP `templates:read` scope I cannot see email body HTML. The "current state" sections describe **structure + performance only**. Content review is a per-flow dependency that needs you to either (a) expand MCP scope, or (b) send screenshots of each email message.

---

## SEQUENCE OF WORK (priority order)

| # | Flow / Action | Why now | Blocking dependencies | Estimated revenue lift (90d) |
|---|---------------|---------|------------------------|-------------------------------|
| 1 | **Fix UTM attribution** (Klaviyo settings) | Without it nothing else is measurable | None — you make change in Klaviyo UI | $0 (enables measurement) |
| 2 | **Compliance gate hardcoded** | Before any new content goes out | Pharmacy registration #, lead pharmacist name | $0 (de-risks future) |
| 3 | **Welcome Series Website — investigate + activate** | Highest leverage flow currently in DRAFT, 537 recipients hitting it already | Need to see Email content (screenshots OR MCP scope) | +$2.5–4k/quarter |
| 4 | **Order Confirmation — add marketing element + activate** | 0% conversion currently; +2200% lift possible | Need product-rec block decision | +$1–2k/quarter |
| 5 | **Cart Abandonment — add Email 3** | Live, performing, Email 3 = +50% rev per benchmark | Content draft | +$8–10k/quarter |
| 6 | **Replenishment — diagnose trigger** | Live but 0 recipients; H&B = 35–50% of flow revenue lives here | Need to see flow trigger config | +$10–15k/quarter potential |
| 7 | **Browse Abandonment Triple Pixel — fix over-firing** | Largest recipient pool (8,175), worst performance | Trigger config check | +$2–3k/quarter |
| 8 | **Sunset flow — build from scratch** | Doesn't exist; required for deliverability | Definition of "unengaged" | $0 direct, prevents -10–20% future loss |
| 9 | **Win-back — diagnose trigger** | 1 recipient in 90d = misconfigured | Trigger config check | +$1–2k/quarter |
| 10 | **Triple Pixel duplicates — kill or activate** | Running parallel = audience overlap + fatigue | Decide which to keep | Reduces fatigue (-fatigue → +open rate over time) |

**Total estimated quarterly lift if executed**: **+$25–35k/quarter** = **$100–140k/year** of incremental email-attributed revenue, taking BC from 3.1% of revenue → ~5–6% of revenue from email. Still well below H&B benchmark of 20–30% — there's a longer tail.

---

## 1. UTM ATTRIBUTION (you execute, 5 min)

| | Current | Desired |
|---|---------|---------|
| Klaviyo `addTrackingParams` | ✓ on | ✓ on |
| Klaviyo `customTrackingParams` | `[]` empty | populated with `utm_source=klaviyo`, `utm_medium={{channel}}`, `utm_campaign={{name|slugify}}` |
| Shopify "klaviyo" referrer | absent | shows real $ within 24-48h of first tagged send |

**Gap**: standard UTM values not configured.
**Execution**: see `utm-attribution-fix.md` for exact steps. You make this change in Klaviyo UI.
**Verification**: 24h after first send, query Shopify referrer breakdown. Compare Klaviyo flow attribution ($48k/90d) to Shopify "klaviyo" referrer (should converge).

---

## 2. COMPLIANCE GATE (you + me)

| | Current | Desired |
|---|---------|---------|
| Compliance review process | Ad-hoc; some flows paused after issues hit | Pre-send checklist; AI scan against POM/restricted word list; human sign-off for medicines |
| POM word list hardcoded | Not in any system | In `.claude/bargain-chemist/memory/compliance-scan-2026-05-06.md` (already there) |
| Footer compliance baseline | Unknown; can't read templates | Pharmacy registration # + pharmacist name + disclaimer in every email footer |
| Solus campaign approval | Direct from supplier copy | Pharmacist review on every Solus before send |

**Gap**: compliance is reactive, not preventive.
**Execution**:
1. You confirm pharmacy registration # + lead pharmacist name → I add to `business-context.md`
2. I'll write a `/compliance-check` slash command that takes campaign/flow content and scans for POM names + therapeutic claims, returns pass/fail
3. You add a human approval step before every Solus campaign send
4. ANZA TAPS pre-vetting for major campaigns ($150–300, 5–10 days)

**Dependencies**: pharmacy registration #, lead pharmacist name. Without these I cannot draft compliant footer language.

---

## 3. WELCOME SERIES WEBSITE — investigate + activate

### Current state (from API)
- Status: **DRAFT** since 2026-03-03; updated as recently as 2026-05-04
- Trigger: Added to List
- Length: 6+ emails (Email 1 + Email 2 + Email 6 visible in performance — gaps in 3, 4, 5)
- Performance (90d, 537 recipients hitting it despite draft):
  - Email 1: 54.8% open / 15.07% click / 3.65% conv / **$3.30 RPR** ← strong, near top quartile
  - Email 2: 44.2% open / 9.7% click / 0.6% conv / $0.50 RPR ← steep drop
  - Email 6: 42.8% open / 4.6% click / 1.32% conv / $0.64 RPR
- Aggregate: 48.13% open / 10.45% click / 2.05% conv / $1.68 RPR / $902 revenue

### Desired state
- Status: **LIVE**
- Length: **3–4 emails** (best practice; reduces fatigue, lifts per-email RPR)
- Sequence (NO COUPONS — see `no-coupon-strategy.md`):
  - Email 1 (immediate): Welcome + brand intro (100% Kiwi-owned, Price Beat 10%, free ship $79+)
  - Email 2 (+24h): Best-sellers (product feed) + reviews + Price Beat reassurance
  - Email 3 (+3d): "3 reasons NZ shops with us" + find-a-store + free-shipping reminder
- Filter: hasn't purchased in last 90d
- Exit: Placed Order
- Sender: `hello@bargainchemist.co.nz` (consistent)
- Per-benchmark target: 8–12% conversion / $3.34 RPR

### Gap analysis
| Aspect | Current | Desired | Gap |
|--------|---------|---------|-----|
| Status | Draft | Live | ⚠️ activate |
| Length | 6+ | 3–4 | trim |
| Email 1 open + click | 54.8% / 15.07% | 50% / 8–10% | ✓ exceeds |
| Email 1 conv | 3.65% | 8–12% | -50% |
| Cohort RPR | $1.68 | $3.34 | -50% |
| Sender consistency | Unknown | hello@ for marketing | needs check |
| Brand positioning visible | Unknown | Kiwi-owned, price-beat, free ship | content audit needed |
| Compliance | Unknown | Pharmacy reg + pharmacist + disclaimer | content audit needed |

### Execution
**Phase 1 — Investigation (depends on you):**
- A) Send me screenshots of all 6 email messages (subject + body)
- B) Tell me the specific blocker — is there an unsaved Email 3, missing image, wrong incentive?

**Phase 2 — Once content visible:**
- I write a 3-email rewrite using confirmed brand voice + positioning
- I write subject lines optimised for parallel-structure brand pattern
- I propose conditional split: did-vs-didn't open Email 1 → different Email 2 path
- You paste rewrites into Klaviyo, set live

**Phase 3 — Validate:**
- Run for 4 weeks
- Compare 28d post-launch performance to the current 537-recipient baseline
- **Falsifiable prediction**: $1.68 RPR → $2.50+ RPR within 28 days = +50% revenue lift on this flow

### Dependencies
- Email content visibility (screenshots or MCP scope)
- Confirmed compliance approver
- UTM tagging fix (so we can measure the post-launch lift)

---

## 4. ORDER CONFIRMATION — add marketing element + activate

### Current state
- Status: **DRAFT** (Klaviyo flow VJui9n / report ID Smp9WN)
- Trigger: Metric (Placed Order)
- Performance: 136 recipients, 57.4% open ✓, 0.74% click, **0% conversion**

### Desired state
- Status: **LIVE**
- Email 1 (immediate, transactional): order confirmation + ONE marketing element (recommended: "Your next-favourite picks" 3-product recommendation block based on order)
- Industry data: +2200% conversion lift vs pure transactional; +14.6% open lift; +64.7% click lift
- Per-benchmark target: 1.4% conversion (transactional+marketing hybrid)
- For Bargain Chemist scale (296 orders/day), at 1.4% = 4 conversions/day = ~360 incremental orders/quarter

### Gap analysis
| Aspect | Current | Desired | Gap |
|--------|---------|---------|-----|
| Status | Draft | Live | ⚠️ |
| Marketing element | Unknown (likely none) | 1 product-rec block | **+1 block** |
| Conversion | 0% | 1.4% | huge |
| Compliance footer | Unknown | Pharmacy reg + disclaimer | content audit |
| Cross-sell logic | Unknown | Use Boost recommendations or Klaviyo's AI-Recommended Products | choose source |

### Execution
**Phase 1**: I write the marketing-element block: 3 product recs + 1 review snippet + secondary CTA "Find your local store" (drives Click & Collect lift) + value props strip (Kiwi-owned, free ship $79+, price-beat).
**Phase 2**: You insert into Klaviyo, link to Boost or Klaviyo product feed.
**Phase 3**: Set live. Monitor 4 weeks. **Falsifiable prediction**: 1%+ conversion lift = ~250 incremental orders × $58 AOV = $14k/quarter.

### Dependencies
- Decide product recommendation source (Boost integration is already wired up; Klaviyo native works too)
- Visibility into current confirmation template (or write fresh)

---

## 5. CART ABANDONMENT (RPQXaa) — add Email 3

### Current state
- Status: LIVE
- Length: 2 emails
- Performance: 8,743 recipients, $20,144 revenue, $2.31 RPR

### Desired state (NO COUPONS — see `no-coupon-strategy.md`)
- Length: **3 emails**
- Email 1: 1h after add-to-cart — cart reminder + Price Beat (currently working — keep)
- Email 2: 24h after — social proof + reviews + free-shipping threshold reminder (content review)
- Email 3 (NEW): 72h after — last-chance scarcity + free-shipping nudge ("Your cart is $X away from free shipping")
- Per-benchmark: 3-email = 6.5× revenue of 1-email; even adding email 3 to existing 2-email = +50% revenue
- **Free-shipping nudge**: AOV $58 vs $79 threshold = $21 to free ship. Email 3 hook: "Your cart is $X away from free shipping — complete your order"

### Gap & execution
- Add Email 3 (template `BC — Cart Abandonment Email 3 — Last Chance (72h)`); two subject variants: (a) urgency framing, (b) free-shipping framing
- A/B test the variants for 4 weeks
- **Falsifiable prediction**: $20k → $30k/quarter = +$10k

### Dependencies
- Content draft + design support
- Cart-value calculation in template (Klaviyo Liquid: `{{ event.extra.value }}` or similar)

---

## 6. REPLENISHMENT (V4cZMd) — diagnose trigger

### Current state
- Status: LIVE since 2026-05-05 (1 day old)
- 0 recipients in 90d (because too new)
- Trigger: Metric — but configuration unknown

### Desired state
For H&B replenishment, the standard pattern:
- Trigger: Placed Order with `replenishment_eligible_category = true`
- Filter: hasn't ordered same product class in last X days
- Email sent 5–7 days BEFORE expected runout
- Cycle by category: vitamins ~30d, oral care ~60d, fragrance ~90d, skincare ~60d
- For Bargain Chemist's top sellers — Elevit (90 tabs = 90d), GO Healthy (varies), Oracoat Xylimelts (40-pack ~30d), supplements generally ~30–60d

### Gap & execution
**Phase 1 — Audit trigger (you):**
- Open `[Z] Replenishment - Reorder Reminders` in Klaviyo
- Tell me: trigger metric, profile filter, delay, conditional splits
- Or send a screenshot of the flow structure

**Phase 2 — Refine:**
- I propose category-specific delays
- We add product-class custom property to Shopify product feed
- Audience: ALL customers who placed order > X days ago

**Phase 3 — Activate:**
- Slow ramp (don't email all 22k customers at once)
- Per-benchmark: 8–15% conversion. For Bargain Chemist's repeat customer base (11,889/90d), even modestly tuned = $10–15k/quarter

### Dependencies
- Visibility into current trigger config
- Product property tagging in Shopify (replenishment cycle by product or category)

---

## 7. BROWSE ABANDONMENT TRIPLE PIXEL — fix over-firing

### Current state
- Status: DRAFT, but 8,175 recipients hitting it (largest recipient pool of any flow)
- Open rate **22.7% — half of benchmark**
- Conversion 0.45%, RPR $0.36

### Desired state
- Either: kill the Triple Pixel version, fall back to standard Browse Abandonment (RtiVC5 — also draft but performing 2× better at 44.9% open)
- Or: tighten the Triple Pixel trigger threshold so it doesn't fire on every micro-event

### Gap & execution
- Decision needed: which version to keep
- If keep TP: investigate Triple Pixel trigger conditions; maybe set a minimum dwell time / multi-event threshold
- If kill TP: archive flow, set standard Browse Abandonment live

### Dependencies
- Flow structure visibility
- Decision on Triple Pixel strategy generally

---

## 8. SUNSET FLOW — build from scratch

### Current state
- **Doesn't exist.** No flow handling unengaged subscribers.
- Implication: 6-month-unengaged subscribers continue receiving sends → reduce open rates, increase complaints → degrade sender reputation → degrade ALL email performance

### Desired state
- New flow `[Z] Sunset` 
- Trigger: profile in segment "Unengaged 180d" (no open, no click, no order in 180d)
- Length: 2–3 emails over 14 days
- Email 1: "We miss you — still want our emails?"
- Email 2: "Last chance — click to stay subscribed"
- Email 3 (final): "Goodbye for now"
- Action after flow: profile moved to "Suppressed - Sunset" segment, removed from main marketing sends

### Gap & execution
**Phase 1**: I draft the 3-email content
**Phase 2**: You build the flow structure in Klaviyo (or grant me MCP scope to do it)
**Phase 3**: Activate; monitor 30 days; expect ~70% of recipients silently exit, 5–10% reactivate

**Dependencies**: ability to create/modify flows via MCP, OR you build manually from my content drafts

---

## 9. WIN-BACK FLOW — diagnose

### Current state
- Status: LIVE since 2026-05-05
- 1 recipient in 90d (clearly misconfigured)

### Desired state
- Trigger: hasn't placed order in 90d AND was previously a customer
- Length: 3–4 emails escalating value (NO COUPONS): "we've missed you" + new arrivals → Price Beat reminder → free-shipping reminder + pharmacist concierge → "what would bring you back?" survey
- For Bargain Chemist: 51.7% return rate means 48.3% don't return — that's the addressable population

### Execution
- You verify trigger in Klaviyo, share with me
- I propose corrected trigger + content
- Per-benchmark: 20–40% reactivation rate

---

## 10. TRIPLE PIXEL DUPLICATES — decide

For each pair (Cart, Checkout, Browse), compare the standard `[Z]` flow to the `[Z] - Triple Pixel` version. Both are running in parallel which causes:
- Audience overlap (same person in both → 2 emails)
- Send fatigue
- Difficulty attributing performance lift to either trigger

### Decision matrix
| Pair | Standard ([Z]) | Triple Pixel | Verdict |
|------|----------------|---------------|---------|
| Added to Cart | RPQXaa LIVE — 41% open / $2.31 RPR | SnakeG DRAFT — 28% open / $1.81 RPR | **Keep standard, kill Triple Pixel** |
| Abandoned Checkout | Y84ruV LIVE — 45% open / $1.81 RPR | VMKAyS DRAFT — 32% open / $1.48 RPR | **Keep standard, kill Triple Pixel** |
| Browse Abandonment | RtiVC5 DRAFT — 45% open / $0.49 RPR | RSnNak DRAFT — 23% open / $0.36 RPR | **Activate standard, kill Triple Pixel** |

In all three cases, the Klaviyo standard event-based flow outperforms the Triple Whale-Pixel-based flow. Recommend killing all Triple Pixel duplicates.

---

## DEPENDENCIES SUMMARY

To execute this plan I need from you:

| Need | Why | Workaround if not available |
|------|-----|----------------------------|
| Klaviyo MCP `templates:read` scope expanded | Read flow message HTML, audit content + compliance | Send screenshots of each flow's emails |
| Klaviyo MCP `flow-actions:read` scope | Read flow structure (delays, splits, filters) | Send flow-export JSON OR screenshots of flow tree |
| Pharmacy registration # | Footer compliance | Use placeholder until provided |
| Lead pharmacist name | Footer compliance for medicine emails | Use placeholder |
| UTM fix done | Measurement of post-change lift | Use Klaviyo's own attribution as proxy |
| Decision on Triple Pixel strategy | Whether to keep or kill 4 duplicate flows | Default: kill (standard outperforms) |
| Decision on Solus compliance gate | Whether each Solus needs pharmacist review | Default: yes for medicine Solus |
| Brand colours / logo / template visual baseline | Brand voice template lockdown | Operate from confirmed positioning only; visual TBC |

---

## VALIDATION FRAMEWORK

Every change above gets logged to `decisions-log.md` with:
- Date executed
- Falsifiable prediction (specific metric + delta + timeframe)
- 28-day comparison to baseline
- Verdict (correct / partially / wrong)
- Learning

Without UTM attribution fixed, predictions will use Klaviyo's own RPR as the metric. Once UTM is fixed, we can validate via Shopify "klaviyo" referrer revenue too.
