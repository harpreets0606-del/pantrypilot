# Klaviyo Segment Fix Guide — Manual UI Edits

> The Klaviyo MCP does not expose a segment-update tool. The 4 fixes below must be applied via the Klaviyo UI. Each item includes the exact URL, the change, the reasoning, and the predicted impact so you can sanity-check after.

## Fix 1 — `WkwEvG` (High AOV $100+ → $45 rebuild)

**Why it's broken:** currently returns 0 profiles. Property names (`$value`, `Collections`) are correct — root cause is Klaviyo's unreliable `metricFilters` AND across a numeric property and an array property within a single condition.

**URL:** https://www.klaviyo.com/lists/WkwEvG/edit

**Change — rebuild as 3 separate condition groups (all AND'd):**

```
Group 1: Has Placed Order at least once in last 1095 days
         WHERE $value > 45

Group 2: Has Placed Order at least once in last 1095 days
         WHERE Collections contains any of: _retail

Group 3: Has consented to receive marketing on email channel
```

**Predicted result:** 0 → ~8,000–15,000 profiles
- If <1,000: drop threshold to $30 (lower than CM minimum is bad)
- If >25,000: raise to $60 (too broad to be a "high AOV" signal)

---

## Fix 2 — `VQ8Sz4` (New Customers: `count = 1` → `count > 0` on 30d)

**Why it's slightly off:** `count equals 1 in 30d` excludes any new customer who placed a 2nd order within their first 30 days. We want all customers whose **lifetime total = 1** AND who bought in last 30d.

**URL:** https://www.klaviyo.com/lists/VQ8Sz4/edit

**Change — first condition only:**

```
BEFORE: Placed Order count equals 1 in last 30 days WHERE _retail
AFTER:  Placed Order count greater than 0 in last 30 days WHERE _retail
```

(Leave the 1095d `equals 1` condition unchanged — that's what enforces lifetime-first-time.)

**Predicted result:** 1,539 → ~1,600–1,800 (5–15% lift)

---

## Fix 3 — `YdzNmz` (Unengaged 180D: add Received Email condition)

**Why it's slightly off:** currently a subscriber who's never been emailed (because they signed up recently) counts as "unengaged" because they trivially have 0 Opens, 0 Clicks. False-positive sunset risk.

**URL:** https://www.klaviyo.com/lists/YdzNmz/edit

**Change — add a 7th condition group:**

```
Group 7 (NEW): Has Received Email at least once in last 180 days
```

Search "Received Email" in the metric picker — built-in Klaviyo metric.

**Predicted result:** 34,248 → ~25,000–32,000 (3,000–9,000 false positives removed)

---

## Fix 4 — Clone `RTzA5N` to retail-only sibling

**Why it's worth a sibling:** the existing RTzA5N has no Collections filter on `Viewed Product`, so GLP-1 and pharmacy-only product viewers are included. Fine for email re-engagement, problematic if used as a Google Ads retail-remarketing audience.

**URL to clone from:** https://www.klaviyo.com/lists/RTzA5N

**Action:** Klaviyo UI → segment menu → Duplicate. Name the duplicate `BC — Browse Abandoners 30d (retail)`. Edit the duplicate:

```
Group 1: Viewed Product count > 0 in last 30 days WHERE Collections contains _retail
Group 2: Placed Order count = 0 in last 30 days WHERE Collections contains _retail
Group 3: subscribed (unchanged)
```

**Predicted result:** new segment ID, ~600–1,000 profiles. Use new sibling for Google Ads retail remarketing; keep original RTzA5N for organic email use.

---

## After all 4 fixes are done

Tell me "fixes complete" — I'll batch-pull all segments with live profile counts and report:
- ✅ / ❌ per fix vs. predicted impact
- New segment ID for the cloned Browse Abandoners
- Green-light decision for the 5-email Customer Match test

## Backlog (deferred, lower priority)

- **X2pdkD GLP-1 SKU refresh** — hard-coded 8-product list, current count 24. New GLP-1 SKUs (Ozempic, Saxenda variants) won't match. Re-audit against Shopify catalog before any usage. (Never sync to Google Ads regardless.)
