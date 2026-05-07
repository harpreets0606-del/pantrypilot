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

## Production context shape (verified from live Checkout Started events)

The actual `event_properties` payload:

```json
{
  "$value": 99.99,           // cart subtotal (numeric) — access via |lookup:'$value'
  "$event_id": "...",
  "$currency_code": "NZD",
  "Item Count": 1,
  "Items": ["...", "..."],   // array of product titles
  "Total Discounts": "0.00",
  "$extra": {
    "token": "...",          // for cart recovery URL construction (Shopify)
    "line_items": [...],     // full cart contents incl. line_price
    "full_landing_site": "...",
    "referring_site": "..."
  },
  "Source Name": "web",
  "Customer Locale": "en-NZ",
  "Discount Codes": []
}
```

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
