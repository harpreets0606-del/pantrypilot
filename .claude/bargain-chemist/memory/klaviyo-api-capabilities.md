# Klaviyo API — what's actually possible (verified 2026-05-07)

*Replaces the incorrect assumption made in this session that flows are read-only via API. Verified against Klaviyo developer docs.*

## Templates

| Operation | Endpoint | Verb | Status |
|-----------|----------|------|--------|
| Create email template (HTML) | `/api/templates/` | POST | ✅ Stable |
| Get template | `/api/templates/{id}/` | GET | ✅ Stable |
| Update template | `/api/templates/{id}/` | PATCH | ✅ Stable |
| Delete template | `/api/templates/{id}/` | DELETE | ✅ Stable |
| Render template | `/api/template-render/` | POST | ✅ Stable |
| Clone template | `/api/template-clone/` | POST | ✅ Stable |

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

### Actions schema (high level)

Each action in `data.attributes.definition.actions[]` has:
- `temporary_id` (string, your choice)
- `type` (`time-delay`, `send-email`, `conditional-split`, `update-profile-property`, `webhook`, etc.)
- `links` to next actions (referenced by `temporary_id`)
- `data` with type-specific settings:
  - `time-delay` → `unit`, `value`, `secondary_value`, `timezone`, `delay_until_time`, `delay_until_weekdays`
  - `send-email` → `template_id`, `subject`, `preview_text`, `from_email`, `from_label`, `reply_to_email`, `smart_sending`, `add_tracking_params`, etc.
  - `conditional-split` → criteria (events / metrics / properties)

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
