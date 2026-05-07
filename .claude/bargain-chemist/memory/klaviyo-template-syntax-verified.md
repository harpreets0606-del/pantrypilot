# Klaviyo Template Syntax — Verified via render-probe (2026-05-08)

Empirical results from POSTing test HTML to `/api/template-render` (revision 2025-10-15) with production-like contexts. **Every entry below has been live-verified — do not assume from Django/Jinja docs.**

## Render endpoint

- **URL:** `POST /api/template-render/`
- **Required:** `data.type = "template"`, `data.attributes.id = <existing template id>` (it does NOT accept inline `html` field — must reference an existing template)
- **Workflow for testing draft HTML:** snapshot existing owned template → PATCH it with test HTML → render → restore via PATCH → repeat. (See `scripts/klaviyo_render_probe.py`.)

## Verified WORKING

| Syntax | Notes |
|---|---|
| `{{ first_name }}` | Direct profile field |
| `{{ first_name\|default:'there' }}` | `default` filter works |
| `{{ event.value }}` | Works ONLY when context contains plain `value` key |
| `{{ event\|lookup:'$value' }}` | **Use this for $-prefixed event properties** — works in production where actual key is `$value` |
| `{% if event\|lookup:'$value' < 79 %}` | `lookup` filter inside `if` is supported |
| `{% with v=event\|lookup:'$value' %}{% if v < 79 %}...{% endif %}{% endwith %}` | `with` block works |
| `{{ organization.full_address }}` | Requires `organization` in context |
| `{% unsubscribe 'Click here' %}` | Klaviyo template tag — renders unsubscribe link |
| Numeric comparison operators `<`, `>`, `<=`, `>=`, `==` | All work in `{% if %}` |
| Nested `{% if %}{% else %}{% if %}...{% endif %}{% endif %}` | Works |
| `{% if %}{% elif %}{% else %}{% endif %}` | **Verified working** (probe-elif 2026-05-08): 3-way conditional rendered correctly with $value=20/50/120 |

## Verified BROKEN / DO NOT USE

| Syntax | Why |
|---|---|
| `{{ event.$value }}` | Django parser can't handle `$` inside dotted-name identifier — `Unable to render` 400 |
| `{% if event.$value < 79 %}` | Same — `$` in identifier breaks lexer |
| `\|float` | Jinja2-only filter, not in Django/Klaviyo. Falls through as literal text → garbled output. |
| `\|round(2)` | Jinja2-only. Use `\|floatformat:2` (Django) instead. |
| Arithmetic in templates: `{{ (79 - x)\|round(2) }}` | Django doesn't allow expression syntax. No native `sub`/multiply. Workarounds: `\|add:-N` (subtraction by adding negative), or compute server-side. |

## Production context shape (verified from live Checkout Started events 2026-05-08)

Pulled 3 real Checkout Started events (metric VvcTue) via klaviyo_get_events MCP. Field meanings:

```json
{
  "$value": 99.99,           // cart subtotal (numeric) — access via |lookup:'$value'
  "$event_id": "...",
  "$currency_code": "NZD",
  "Item Count": 1,
  "Items": ["...", "..."],   // array of product titles
  "Total Discounts": "0.00",
  "$extra": {
    "token": "...",          // raw Shopify cart token
    "line_items": [...],     // full cart contents incl. line_price
    "full_landing_site": "http://bargain-chemist.myshopify.com/products/<handle>?...",  // ⚠️  the product/page customer was on BEFORE checkout — NOT the cart recovery URL. Trap. Empirically: always points to a /products/<handle> page, never the cart.
    "checkout_url": "https://www.bargainchemist.co.nz/.../checkouts/ac/<token>/recover?key=...&locale=en-NZ",  // ✅ THE cart recovery URL — use this for "Return to checkout" CTAs in abandoned-checkout flows
    "responsive_checkout_url": "...",  // ✅ Same value as checkout_url in all 3 sample events. Either works.
    "referring_site": "https://www.google.com/",   // upstream traffic source
    "webhook_id": "..."
  },
  "Source Name": "web",
  "Customer Locale": "en-NZ",
  "Discount Codes": []
}
```

**FIELD-CHOICE TRAP (verified 2026-05-08):** for the "Return to checkout" link in abandoned-checkout templates, use `event.extra.checkout_url`, NOT `event.extra.full_landing_site`. The latter sounds right but contains the product page. This was discovered when test sends from Y84ruV v3 went to product pages instead of saved carts. Fix logged in decisions-log 2026-05-08.

**For order-completed events** (filtered out of Y84ruV by profile_filter): `checkout_url` becomes an order-status authenticate URL (`/orders/.../authenticate?key=...`). Doesn't matter for cart-abandon flows since the profile_filter excludes these profiles, but worth knowing if the field is ever used in other flow types.

**Klaviyo's auto-strip behaviour at runtime:** UNVERIFIED. Render endpoint does NOT auto-strip `$` from event keys (probe test 14 was inconclusive — context had both `$value` and `value`). For production safety, **always use `|lookup:'$value'`**, not `event.value`.

## Pattern: 3-way cart-value tier conditional (verified)

```django
{% if event|lookup:'$value' < 30 %}
  [ Tier A: small impulse cart ]
{% elif event|lookup:'$value' < 79 %}
  [ Tier B: gap-actionable cart ]
{% else %}
  [ Tier C: free-ship qualified cart ]
{% endif %}
```

elif verified working via probe (2026-05-08, all 3 tiers rendered correctly).

## Workflow for any future template change

1. **Build** new HTML.
2. **Snapshot** existing owned template (rollback file).
3. **PATCH** owned template with new HTML (no live impact — live flow uses the CLONE, not the owned global).
4. **POST `/api/template-render`** with N test contexts covering every conditional branch.
5. **Check rendered output** for: literal `{% %}` / `{{ }}` leftovers, expected per-context phrases, leftover broken legacy code.
6. **If any check fails** → PATCH back to rollback HTML. Done; live unaffected.
7. **If all pass** → re-assign flow-action to owned template (forces re-clone with new HTML). Live now reflects new content.
8. **Verify new clone** has no leftover broken code.

Reference scripts:
- `scripts/klaviyo_render_probe.py` — generic render syntax probe
- `scripts/klaviyo_rebuild_email1_branded.py` — surgical edit pattern with render-test + rollback
