# Klaviyo Back In Stock Form (Shopify)

A drop-in back-in-stock form for the Bargain Chemist Shopify Plus theme.
Captures email + optional SMS, fires Klaviyo's `Subscribed to Back in Stock`
metric, and registers the visitor against the Shopify variant so Klaviyo
sends the notification when inventory returns.

## What it talks to

- **Klaviyo company / public API key:** `XCgiqg`
- **Klaviyo list (optional opt-in):** `Back In Stock Send Update` (`RhChwn`)
- **Trigger metric:** `Subscribed to Back in Stock` (`USbQRB`)
- **Flow it powers:** `[Z] Back in Stock` (`Ysj7sg`)
- **API:** `POST https://a.klaviyo.com/client/back-in-stock-subscriptions/?company_id=XCgiqg`
  (Klaviyo's public client endpoint — no secret key needed)

## Files

| File | Drop into theme path |
| --- | --- |
| `snippets/klaviyo-back-in-stock.liquid` | `snippets/klaviyo-back-in-stock.liquid` |
| `assets/klaviyo-back-in-stock.js` | `assets/klaviyo-back-in-stock.js` |
| `assets/klaviyo-back-in-stock.css` | `assets/klaviyo-back-in-stock.css` |

## Install

1. **Upload files.** In the Shopify admin, go to **Online Store → Themes →
   ⋯ → Edit code** on a duplicate of the live theme and add the three
   files at the paths above.
2. **Render the snippet on the product template.** Open
   `sections/main-product.liquid` (or whichever section renders the buy
   box) and add this line just below the Add-to-Cart button block:

   ```liquid
   {%- render 'klaviyo-back-in-stock', product: product, current_variant: product.selected_or_first_available_variant -%}
   ```

   The snippet renders itself only when the selected variant is
   unavailable, so it's safe to leave on every product page.
3. **(Optional) Hook into your variant picker.** If your theme dispatches
   a custom event when shoppers change variant, the form re-targets
   automatically. The script listens for both `variant:change` and
   `variantChange` events with `event.detail.variant` (or the variant
   directly in `event.detail`). If your theme uses a different event,
   add a tiny shim at the bottom of your variant script:

   ```js
   document.dispatchEvent(new CustomEvent('variant:change', { detail: { variant: newVariant } }));
   ```
4. **Preview.** Visit a product whose selected variant is sold out. The
   form should appear, accept an email, and show `You're on the list…`.
5. **Verify in Klaviyo.** Profile → Activity feed should show a
   `Subscribed to Back in Stock` event with a `Variant` ID matching
   `$shopify:::$default:::<variant_id>`. Your existing `[Z] Back in
   Stock` flow already filters on this metric, so it'll send when the
   variant restocks.
6. **Publish the theme** when you're happy.

## Notes

- The endpoint accepts unauthenticated browser requests using your
  public company ID — the same token Klaviyo's onsite forms use.
- The list opt-in checkbox writes to `Back In Stock Send Update`
  (`RhChwn`). It's set to **double opt-in** in Klaviyo, so subscribers
  receive a confirmation email before being added. If you'd rather
  capture them on a single-opt-in list, change the
  `data-klaviyo-list-id` attribute on the script tag in the snippet.
- NZ phone numbers entered without a country code are auto-prefixed
  with `+64` to satisfy Klaviyo's E.164 requirement.
- The script is `defer`-loaded and adds no dependencies.
