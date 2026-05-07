# No-Coupon Strategy — HARD CONSTRAINT
*Locked 2026-05-07 by user directive*

## Rule

**Bargain Chemist email/SMS strategy MUST NOT use coupons, promo codes, discount codes, vouchers, or "% off" offers in any flow, campaign, automation, template, or copy recommendation.**

This applies to:
- Welcome series (no signup discount)
- Cart abandonment (no recovery code)
- Browse abandonment (no incentive code)
- Post-purchase / cross-sell (no thank-you code)
- Win-back / lapsed (no return-customer code)
- VIP / loyalty (no member-only code)
- Birthday / anniversary (no gift code)
- Any campaign

## What we lean on instead

The brand competes on **EDLP (Everyday Low Pricing)**, not promo cycles. The persuasion levers are:

1. **Price Beat Guarantee** — "Find it cheaper at any NZ pharmacy and we'll beat it by 10%" — this IS the offer; it's a permanent policy, not a promo.
2. **Free shipping over $79** — threshold nudge, not a code.
3. **Trust / longevity** — "Trusted NZ pharmacists since 1984", **30+ stores nationwide**.
4. **Product feed / social proof** — best sellers, reviews, scarcity (low stock).
5. **Reminder / urgency** — "Your cart's still here", "Items selling fast".
6. **Convenience** — find-a-store, click & collect, repeat-order ease.
7. **Education** — pharmacist advice, condition-led content, seasonal health.

## Banned phrases / constructs

Do not produce any copy, subject line, or template containing:
- "Use code XXXXX"
- "Enter code at checkout"
- "Code: XXXXX"
- "X% off your first order"
- "$X off your next purchase"
- "Welcome discount"
- "Promo code"
- "Voucher inside"
- "Coupon attached"
- Any merge tag like `{{ coupon_code }}` or dynamic-coupon Liquid block
- Any Klaviyo "Coupon" content block

## Permitted phrases

- "Free shipping on orders over $79"
- "Price beat guarantee — beat any NZ pharmacy by 10%"
- "Lowest pharmacy prices in NZ"
- "EDLP" → translate customer-facing as "everyday low prices" (never the acronym)
- "Last chance — your cart's waiting" (urgency, no code)
- "Top up to unlock free shipping" (threshold nudge)

## Implications for memory + playbooks

The following files contained coupon-based recommendations and have been corrected:
- `memory/klaviyo-best-practices.md` — welcome series + cart abandonment recipes updated to no-coupon variants
- `memory/hypotheses.md` — VIP test reframed (free-shipping threshold drop vs. free gift)
- `memory/flow-execution-plan.md` — Cart Email 3 variants updated to free-ship + scarcity (no escalated coupon)
- `playbooks/churn-investigation.md` — winback test reframed (free shipping / pharmacist concierge, not 15% off)

## When the user asks for a discount-based campaign

If the user explicitly requests a coupon-based campaign in the future, **stop and confirm** before drafting. Do not silently override this constraint. Possible reasons the user might override (only if they say so):
- Specific seasonal exception
- Supplier-funded promotion
- Compliance test (NOT a real send)

Default behaviour: **assume no coupons. Always.**
