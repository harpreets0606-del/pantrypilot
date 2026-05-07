# Klaviyo API — what's actually possible (verified 2026-05-07)

*Replaces the incorrect assumption made in this session that flows are read-only via API. Verified against Klaviyo developer docs.*

## Liquid filter chaining gotcha - VERIFIED 2026-05-07

Klaviyo's Liquid parser **breaks** on `replace` (two-arg) chained inline with another filter:
```
{{ event|lookup:'URL'|replace:'a','b'|default:'fallback' }}   ❌ "Could not parse some characters"
```
The parser tokenises the comma between replace's two args as a filter-chain delimiter.

**Workarounds:**
1. Drop the replace and rely on Shopify primary-domain 301 redirect (preferred for our case — myshopify.com URLs auto-redirect to bargainchemist.co.nz):
   ```
   {{ event|lookup:'URL'|default:'https://www.bargainchemist.co.nz/cart' }}
   ```
2. If replace is essential, do it via `{% assign %}` first, then output the var separately. (Untested in Klaviyo — may also fail.)

**Affected files:** cart-abandon-email-1/2/3.html line 57-66 (link href + button href). Fixed by removing replace 2026-05-07.

## "Added to Cart" event payload (Shopify integration) - VERIFIED via real event 2026-05-07

Inspected via `klaviyo_get_events` filter `metric_id=S4jKYD`. Key fields available in `event_properties` for Shopify "Added to Cart" events:

| Field name (case-sensitive) | Liquid access | Example |
|-----------------------------|---------------|---------|
| `Product Name` | `{{ event\|lookup:'Product Name' }}` | UMBRO Action Deodorant Body Spray 150ml |
| `Price` | `{{ event\|lookup:'Price' }}` | 3 (number) |
| `Quantity` | `{{ event\|lookup:'Quantity' }}` | 1 |
| `URL` | `{{ event\|lookup:'URL' }}` | bargain-chemist.myshopify.com/products/... |
| **`ImageURL`** (one word, camelCase) | `{{ event\|lookup:'ImageURL' }}` | https://cdn.shopify.com/... |
| `CompareAtPrice` | `{{ event\|lookup:'CompareAtPrice' }}` | 7.99 |
| `Brand` | `{{ event\|lookup:'Brand' }}` | UMBRO |
| `Categories` | array | [Personal Care, Deodorants, ...] |
| `Variant SKU` | with space | 9009932 |
| `ProductID` | one word | 7810292744329 |
| `VariantID` | one word | 42842887389321 |
| `Product Type` | with space | Personal Care |
| `$value` | total cart value | 3 |
| `$currency` | NZD | |

**CRITICAL trap I fell into 2026-05-07:** field name is `ImageURL` (one word, camelCase) — NOT `Image URL` with space. I used the wrong key initially in the cart-abandon templates, image fell back to default. The flow's own trigger filter even uses `ImageURL` (visible in flow definition dump).

**URL field returns the myshopify admin domain.** For customer-facing links, always wrap with replace filter:
```liquid
{{ event|lookup:'URL'|replace:'bargain-chemist.myshopify.com','www.bargainchemist.co.nz' }}
```

**Verification source:** snapshot at `.claude/bargain-chemist/snapshots/2026-05-07/` includes raw event payloads from MCP `klaviyo_get_events`.

## Universal Content API (deep-research finding 2026-05-07)

| Operation | Endpoint | Verb | Status |
|-----------|----------|------|--------|
| Create universal content block | `/api/universal-content/` | POST | ✅ Stable (GA) |
| Get universal content | `/api/universal-content/{id}/` | GET | ✅ Stable |
| **Update universal content** | `/api/universal-content/{id}/` | PATCH | ✅ Stable — **propagates to all templates using the block** |
| Delete universal content | `/api/universal-content/{id}/` | DELETE | ✅ Stable |

**Critical insight:** Updating a universal content block applies the change to every email template that references it. This is the right primitive for shared compliance blocks (legal footer, pharmacy reg #, pharmacist name) and value-props strip.

Updateable block types: `button`, `drop_shadow`, `horizontal_rule`, `html`, `image`, `spacer`, `text`.

For our compliance footer use case: create ONE `html` block with the full legal+unsubscribe footer including pharmacy registration, pharmacist name, address macros. Reference it in every email template via `<div data-klaviyo-universal-block="block_id">&nbsp;</div>`. Future updates to compliance fields = single PATCH, propagates everywhere.

## Editor types (verified)

| editor_type | Create via API | Update HTML via API |
|-------------|----------------|---------------------|
| `CODE` (pure HTML) | ✅ | ✅ for owned globals; ❌ for flow-cloned (404 bug) |
| `USER_DRAGGABLE` (hybrid) | ✅ | ✅ |
| `SYSTEM_DRAGGABLE` (native drag-drop) | ❌ Not allowed | ✅ definition field only |

Klaviyo's flow editor and email designer create SYSTEM_DRAGGABLE templates by default. Templates we POST via API are CODE.

## Templates

| Operation | Endpoint | Verb | Status |
|-----------|----------|------|--------|
| Create email template (HTML) | `/api/templates/` | POST | ✅ Stable |
| Get template (global) | `/api/templates/{id}/` | GET | ✅ Stable |
| Update template (global) | `/api/templates/{id}/` | PATCH | ✅ Stable for global templates |
| **PATCH a flow-cloned template** | `/api/templates/{id}/` | PATCH | ❌ **BROKEN — known bug** |
| Delete template | `/api/templates/{id}/` | DELETE | ✅ Stable |
| Render template | `/api/template-render/` | POST | ✅ Stable |
| Clone template | `/api/template-clone/` | POST | ✅ Stable |
| Get template for flow message | `/api/flow-messages/{id}/template/` | GET | ✅ Stable |

### CONFIRMED WORKING WORKFLOW (verified 2026-05-07)

For updating flow message HTML content via API:

1. **Phase 1**: `PATCH /api/templates/{owned_id}/` — update our owned global template with new HTML. The "owned" templates are the ones we created via `POST /api/templates/` and stored their IDs (e.g. `RjiNUy`, `SuHDNq`, `UPxjA8` for welcome series). PATCH on these works fine.
2. **Phase 2**: `PATCH /api/flow-actions/{action_id}/` (revision `2025-10-15`) — re-assign the same global template to force Klaviyo to clone it again, picking up the just-updated HTML.

The clone-on-assign is fixed Klaviyo behaviour — every assignment creates a fresh internal copy. **You cannot update those internal copies directly.** But you can force a re-clone by re-assigning, which picks up your latest global template HTML.

Script: `scripts/klaviyo-deploy-content.ps1` — runs both phases end-to-end. Workflow is now:
```
Edit local HTML file → Run klaviyo-deploy-content.ps1 → Live in flow.
```

### Earlier session conclusion was incomplete

I previously declared "flow-cloned template content cannot be updated via API." **That was wrong.** The Templates API PATCH on cloned IDs IS broken, but Klaviyo released a separate working endpoint:

**`PATCH /api/flow-actions/{id}/`** — revision `2025-10-15` (GA, not beta!)

This updates a flow action's full definition INCLUDING `data.message.{template_id, subject_line, preview_text, from_email, smart_sending_enabled, etc.}`. Verified via:
- Klaviyo API changelog [21.0.0] revision 2025-10-15
- Python SDK source `flow_action_update_query_resource_object_attributes.py` confirms shape
- SDK method: `klaviyo.Flows.update_flow_action(id, body)`
- Endpoint URL pattern in SDK: `/api/flow-actions/{id}` PATCH

**Body shape (verified from SDK):**
```json
{
  "data": {
    "type": "flow-action",
    "id": "<flow_action_id>",
    "attributes": {
      "definition": { ... opaque dict mirroring GET response ... }
    }
  }
}
```
The `definition` is the full action structure (type, data, links). For send-email actions this includes the `data.message` object.

**Lesson: stop concluding "impossible" without checking the latest revision.** Klaviyo ships new endpoints quarterly under new revision headers. Always check the changelog for the revision matching the current date before declaring something unsupported.

---

### The DEPRECATED workaround (PATCH /api/templates/{id} on flow-cloned IDs)

When you assign a global template to a flow message, Klaviyo creates an internal cloned copy. That copy:
- Returns a real-looking template ID (e.g. `VMMpC9`)
- Is reachable via `GET /api/flow-messages/{id}/?include=template`
- Returns 200 on `GET /api/templates/{cloned_id}/`
- **Returns 404 on `PATCH /api/templates/{cloned_id}/`** with `"Template with id 'X' does not exist"`
- Same behaviour with beta revision header `2024-10-15.pre`
- Same behaviour for campaign-message cloned templates

**This is a Klaviyo platform bug, NOT a config issue.** Don't try to PATCH flow-cloned templates from a script — it will always 404. Multiple community threads since 2024 confirm Klaviyo hasn't fixed it.

**Workarounds:**
1. **Manual paste in Klaviyo UI** (fastest for one-off edits) — open `https://www.klaviyo.com/email-editor/{cloned_id}/edit`, paste new HTML, save. Goes live in flow immediately.
2. **Update the global template, then re-assign it in the flow editor** — Klaviyo will re-clone, picking up your changes. UI action required either way.
3. **Treat templates as immutable inside flows** — for any non-trivial content change, plan to delete + recreate the flow rather than fight the API.

### Implication for our deployment workflow

- Initial flow build via API: ✅ works (templates get cloned but that's fine for first-time)
- Iterating on copy/HTML: ❌ has to happen in the Klaviyo UI for now
- We will NOT add a "re-deploy template content" PowerShell script — it can't work until Klaviyo fixes this bug

**Scope:** `templates:write`. The Klaviyo MCP token in this session **does not have it** (returns 401). The user's PowerShell key in `.env.local` **does** — that's how we'll deploy.

## Flows — IMPORTANT CORRECTION

**Earlier in this session I incorrectly stated the Klaviyo API does not support creating flows. That was wrong.** A beta endpoint exists.

| Operation | Endpoint | Verb | Status |
|-----------|----------|------|--------|
| List flows | `/api/flows/` | GET | ✅ Stable |
| Get flow + definition | `/api/flows/{id}/?additional-fields[flow]=definition` | GET | ✅ Stable |
| Get flow actions | `/api/flows/{id}/flow-actions/` | GET | ✅ Stable |
| Get flow message | `/api/flow-messages/{id}/` | GET | ✅ Stable |
| **Create flow (full definition)** | `/api/flows/` | **POST** | 🟡 **Beta** |
| Update flow status (draft↔live↔manual) | `/api/flows/{id}/` | PATCH | ✅ Stable |
| **Update flow definition (steps/branches)** | — | — | ❌ **Not supported** |
| Delete flow | `/api/flows/{id}/` | DELETE | ✅ Stable |

### Create Flow — operational details

- **Beta revision header:** `revision: 2024-10-15.pre` (note the `.pre` — beta)
- **Scope:** `flows:write`
- **Rate limits:** Burst 1/s, Steady 15/min, Daily **100/day**
- **Klaviyo's own warning:** "Beta APIs are not intended for production use" — but they're stable enough for one-shot flow creation, which is our use case
- **Identifier convention:** new actions inside the definition use `temporary_id` (string of your choice). Klaviyo replaces these with real IDs in the response.
- **Constraint 1:** A/B test actions are **not** supported via API
- **Constraint 2:** Once created, a flow's **structure cannot be updated** via API. To change steps, you must DELETE + re-CREATE (or edit in UI).
- **Recommended workflow (from Klaviyo docs):** build a reference flow in UI → GET it with `?additional-fields[flow]=definition` → mutate the JSON → POST as a new flow.

### Actions schema — VERIFIED from SehWRt-with-full-definition.json (2026-05-07)

Top-level `data.attributes.definition`:
```json
{
  "triggers": [ { "type": "list", "id": "<list_id>" } ],
  "profile_filter": null,
  "entry_action_id": "<temporary_id of first action>",
  "actions": [ ... ]
}
```

**Trigger:** `{"type": "list", "id": "<list_id>"}` — uses `id`, NOT `list_id`.

**time-delay action:**
```json
{
  "temporary_id": "delay-1",
  "type": "time-delay",
  "data": {
    "unit": "minutes" | "hours" | "days" | "weeks",
    "value": <int>,
    "secondary_value": null,
    "timezone": "profile" | "utc" | "<account-tz>",
    "delay_until_weekdays": ["monday","tuesday",...]   // ONLY if unit is "days"
  },
  "links": { "next": "<temporary_id>" }
}
```
**Constraint (verified by API error 2026-05-07):** `delay_until_weekdays` and `delay_until_time` are ONLY valid when `unit` is `"days"`. For minutes/hours/weeks, omit them entirely. Setting them on a non-day delay returns `400 invalid`.

**UtmParam schema** (for `data.message.custom_tracking_params[]` in flow-actions):
```json
{ "param": "utm_source", "value": "klaviyo" }
```
Required field: `param` (the UTM key name). Optional/required: `value` (static string). Fields `name` and `type` are NOT valid (returns 400). Verified via API error on 2026-05-07.

**send-email action:**
```json
{
  "temporary_id": "email-1",
  "type": "send-email",
  "data": {
    "message": {
      "name": "Welcome Email 1",
      "from_email": "hello@bargainchemist.co.nz",
      "from_label": "Bargain Chemist",
      "reply_to_email": null,
      "cc_email": null,
      "bcc_email": null,
      "subject_line": "...",            // ← NOT "subject"
      "preview_text": "...",
      "template_id": "<template_id>",
      "smart_sending_enabled": true,    // ← NOT "smart_sending"
      "transactional": false,
      "add_tracking_params": true,
      "custom_tracking_params": null,
      "additional_filters": null
    },
    "status": "draft"
  },
  "links": { "next": "<temporary_id>" | null }
}
```

**conditional-split action — schema NOT YET VERIFIED.** Errors confirmed:
- `data.profile_filter` is required (object, not array)
- `data.condition_groups` is INVALID (was the wrong guess)
- `links.next_if_true` and `links.next_if_false` are required (NOT `true`/`false`)
- Action type for splits is conditional-branch, distinct from boolean-branch

**TODO when we need conditional splits via API:** create one in UI with the desired filter, dump it via `klaviyo-dump-flow-definition.ps1`, copy schema. Until then, build linear flow and add splits in UI manually.

### Practical implication for Bargain Chemist

We **can** create the new "Welcome Series 2026 - No Coupon" flow entirely via API:

1. Run `klaviyo-deploy-templates.ps1` → get 4 template IDs
2. Fetch `SehWRt` with `?additional-fields[flow]=definition` → get its full action tree as a starting skeleton
3. Mutate the JSON: drop the 3 coupon splits, swap template IDs to the new ones, set subjects/previews/UTMs
4. POST to `/api/flows/` with `revision: 2024-10-15.pre` header → flow is created in DRAFT
5. Existing `SehWRt` left untouched in DRAFT

This is what we'll do.

## Other API capabilities verified

- Profiles: full CRUD ✅
- Lists: full CRUD ✅
- Segments: read + create + delete ✅ (definitions are also editable)
- Campaigns: full CRUD ✅
- Coupons: read + create + delete (we don't use these)
- Events: write (POST `/api/events/`) ✅
- Catalogs: full CRUD ✅
- Forms: read-only ⚠️ (no write API for forms)

## Sources

- [Klaviyo Flows API overview](https://developers.klaviyo.com/en/reference/flows_api_overview)
- [Klaviyo Create Flow (beta)](https://developers.klaviyo.com/en/v2024-10-15/reference/create_and_retrieve_flows)
- [Klaviyo developer community thread](https://community.klaviyo.com/developer-group-64/create-new-flow-using-api-5162)

## My mistake — for the record

When the user asked "can you set up the flows with conditions through terminal too" my first response was that flow structure is API-impossible. That was wrong. The user pushed back twice and made me actually check the docs. The lesson logged: **always verify API limits via vendor docs / search before declaring something impossible**, especially when the user has explicit reason to believe otherwise. Added to `decisions-log.md`.
