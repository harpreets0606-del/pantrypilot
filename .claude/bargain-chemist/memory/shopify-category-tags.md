# Shopify Category Tags — Verified List

Pulled live from Shopify Admin API (`productTags` query) on 2026-05-07.
Source: bargain-chemist.myshopify.com.

This is the canonical taxonomy for top-level product categories on
the Bargain Chemist store. The `CAT=` prefix denotes a top-level
category tag. Smart collections use these in their TAG=EQUALS rules.

## Tag systems in use (in priority order)

1. **`CAT=<Name>`** — primary top-level category taxonomy. Use this for
   trigger/conditional-split filters in Klaviyo flows.
2. **`SUBCAT=<Name>`** — subcategory tier under CAT.
3. **`BRAND=<Name>`** — brand identifier. Don't use for category-based
   audience splits.
4. **`CONCERN=<Name>`** — need-state (e.g. `CONCERN=Energy & Fatigue`).
5. **`INGREDIENTS=<Name>`** — single-ingredient identifier.
6. **`PRODTYPE=<Name>`** — product-type granular tag.
7. **`Type_<Name>` / `Category: <Name>` / `Brand: <Name>`** — legacy formats
   from older imports. Still present on some products but being phased out;
   do NOT design new flows around these.

## Restricted-product tags (must exclude from promotional flows)

- `_pharmacy-only` — pharmacy-only medicines (e.g. some antihistamines,
  Omeprazole)
- `_pharmacist-only` — pharmacist-only medicines (e.g. higher-strength
  topicals)
- `_prescription` — prescription-only (e.g. Wegovy, Saxenda)

These three tags must be checked via NOT-CONTAINS in any trigger filter or
trigger-split for promotional content. ASA Therapeutic Code requires no
price promotion or aspirational marketing of restricted medicines.

## Complete `CAT=` tag list (verified 2026-05-07)

Listed alphabetically as returned by the API. Unusual / data-quality
issues are flagged.

### Health & Wellness

- `CAT=Allergies Hayfever & Sinus`
- `CAT=Allergy` ⚠️ duplicate of above — likely older; verify which is
  canonical before using
- `CAT=Anti-Nauseants`
- `CAT=Antioxidant`
- `CAT=Bladder Control & Incontinence`
- `CAT=Body Health`
- `CAT=Bone Health`
- `CAT=Brain Health`
- `CAT=Cold & Flu`
- `CAT=Cold Sore Treatments`
- `CAT=Comfort & wellness`
- `CAT=COVID-19 Tests`
- `CAT=Ear Care & Treatments`
- `CAT=Energy Sleep & Fatigue`
- `CAT=Everyday Health`
- `CAT=Eye Care & Treatments`
- `CAT=Eye Health`
- `CAT=Foot Care`
- `CAT=Gut Health Detox & Digestion`
- `CAT=Haemorrhoids`
- `CAT=Heart & Circulation`
- `CAT=Immune Support`
- `CAT=Joints & Mobility`
- `CAT=Liver Health`
- `CAT=Medical Aids`
- `CAT=Medical Equipment`
- `CAT=Mum Health`
- `CAT=Muscle Relief & Support`
- `CAT=Optic Care`
- `CAT=Pain Relief`
- `CAT=Respiratory Health`
- `CAT=Sleeping Aids`
- `CAT=Smoking Deterrents`
- `CAT=Stomach & Bowel Treatments`
- `CAT=Stress & Anxiety`
- `CAT=Thyroid & Iodine Support`
- `CAT=Urinary Tract Health`
- `CAT=Urinary Tract Infections (UTI)`

### Vitamins & Supplements (single nutrients + categories)

- `CAT=Apple Cider Vinegar`
- `CAT=Ashwagandha`
- `CAT=Calcium`
- `CAT=Collagen`
- `CAT=Electrolyte Replacement`
- `CAT=Essential Oils`
- `CAT=Extracts` ⚠️ also `CAT=Extract & Others`, `CAT=Extracts & Other`,
  `CAT=Extracts & Others` — pick one canonical
- `CAT=Fish Oil`
- `CAT=Flaxseed Oil`
- `CAT=Garlic Extract`
- `CAT=Greens & Superfoods`
- `CAT=Hair Skin & Nails`
- `CAT=Hemp Seed Oil`
- `CAT=Iron`
- `CAT=Krill Oil`
- `CAT=Magnesium`
- `CAT=Manuka & Bee Products`
- `CAT=Manuka Honey`
- `CAT=Minerals`
- `CAT=Multimineral`
- `CAT=Multivitamin`
- `CAT=Oils`
- `CAT=Omega-3`
- `CAT=Potassium`
- `CAT=Pre & Probiotic`
- `CAT=Sodium`
- `CAT=Specialty Tea`
- `CAT=Spirulina`
- `CAT=Sports Nutrition`
- `CAT=Turmeric`
- `CAT=Vitamin A`
- `CAT=Vitamin B`
- `CAT=Vitamin C`
- `CAT=Vitamin D`
- `CAT=Vitamin E`
- `CAT=Vitamins`
- `CAT=Zinc`

### Skin / Body / Personal Care

- `CAT=Body Treatments`
- `CAT=Cotton Balls Buds & Pads`
- `CAT=Deodorants`
- `CAT=Feminine Products`
- `CAT=Hand & Body`
- `CAT=Self-Tanning`
- `CAT=Shaving & Personal Grooming`
- `CAT=Skin Care`
- `CAT=Sun Care`
- `CAT=Talcum Powder`

### Hair

- `CAT=Hair Accessories`
- `CAT=Hair Care`
- `CAT=Hair Dye`

### Oral

- `CAT=Oral Hygiene & Care`

### Cosmetics & Fragrance

- `CAT=Brows`
- `CAT=Eyebrow & Eyelash Tint`
- `CAT=Eyes`
- `CAT=Face`
- `CAT=fragrance mist` ⚠️ inconsistent casing
- `CAT=Fragrance Sets`
- `CAT=Home Fragrance`
- `CAT=Lips`
- `CAT=Makeup Accessories`
- `CAT=Makeup Brushes`
- `CAT=Manicures & Nail Care`
- `CAT=Men's Fragrance`
- `CAT=Pimple Patch`
- `CAT=Unisex fragrance` ⚠️ inconsistent casing
- `CAT=Women's Fragrance`

### Children & Family

- `CAT=Baby Care`
- `CAT=Children's Health`
- `CAT=Children's Toys`

### First Aid & Medical Supplies

- `CAT=First Aid`
- `CAT=Gauze`
- `CAT=Hot Water Bottles & Wheat Bags`
- `CAT=Topical Ointments & Spray` ⚠️ also `CAT=Topical Ointments & Sprays`
  — pick one

### Sex / Reproductive

- `CAT=Sexual Health & Family Planning`

### Lifestyle & Travel

- `CAT=Batteries & Electronics`
- `CAT=Cleaning`
- `CAT=Clothing`
- `CAT=Easter`
- `CAT=Insect Repellent`
- `CAT=Kitchen`
- `CAT=Laundry`
- `CAT=Linen`
- `CAT=Luggage Straps Tags & Locks`
- `CAT=Neck Pillow`
- `CAT=Pantry & Groceries`
- `CAT=Passport Holders & Wallets`
- `CAT=Pet Care`
- `CAT=Shopping Bags`
- `CAT=Sleep Masks`
- `CAT=Sports & Recreation`
- `CAT=Stationary` ⚠️ typo of "Stationery"
- `CAT=Sun Care Deals`
- `CAT=Toilet Paper & Facial Tissues`
- `CAT=Travel Bags & Containers`
- `CAT=Travel Socks`
- `CAT=Travelling`

### Weight Management

- `CAT=Weight Management Nutrition` (meal-replacement nutrition: Optifast,
  Optislim, Ensure)
- `CAT=Weight Management Supplements` (non-prescription supplements)

⚠️ Prescription weight-loss medicines (Wegovy, Saxenda) do NOT carry these
tags — they are tagged with `_prescription`. Always exclude `_prescription`
in trigger filters.

### Health markers — broad

- `CAT=Concerns` ⚠️ also `CAT=Conerns` (typo)
- `CAT=Ear Plugs`
- `CAT=Men's Health`
- `CAT=Women's Health`
- `CAT=Breakfast Food`

### Sundry / breakage

- `CAT=` (empty value — leftover from a malformed import)
- `CAT= Dr. O and Sally Hans - BF` (campaign-specific tag, not a real
  category)
- `CAT= Hair Dye` (leading-space variant of `CAT=Hair Dye`)
- `CAT= Online only` (campaign-specific)
- `CAT+Minerals` (typo with `+` instead of `=` — orphan)
- `CAT=BF-Shave` (Black-Friday campaign-specific)
- `CAT=Elizabeth Arden` (brand mis-tagged as CAT)
- `CAT=oralB-Being` (mis-tagged)
- `CAT=Sun Care Deals` (campaign-specific)

These campaign / typo / orphan tags should NEVER be used as filters in
flows. Treat them as data-quality debt.

## Verified collection handles for replenishment / browse-abandon /
campaigns

Pulled via `collectionByHandle` query on 2026-05-07. Use these handles in
email CTAs.

| Purpose | Handle | Title | Products | Smart rule |
|---|---|---|---|---|
| Vitamins (broad) | `/collections/vitamins-supplements` | Vitamins & Supplements | 1759 | yes |
| Vitamins (narrow) | `/collections/vitamins` | Vitamins | 307 | `CAT=Vitamins` |
| Skin Care | `/collections/skin-care` | Skin Care | 1067 | yes |
| Sun Care | `/collections/sun-care` | Sun Care | 112 | yes |
| Hair Care | `/collections/hair-care` | Hair Care | 976 | yes |
| Oral Hygiene | `/collections/oral-hygiene-care` | Oral Hygiene & Care | 246 | yes |
| Baby Care | `/collections/baby-care` | Baby Care | 429 | yes |
| Baby (broad) | `/collections/baby` | Baby | 677 | possibly manual |
| Weight Loss Supps | `/collections/weight-management` | Weight Loss Supplements | 188 | yes |
| Weight Mgmt Nutrition | `/collections/weight-management-nutrition` | Weight Management Nutrition | 126 | yes |
| All products | `/collections/all-products` | All Products | 20051 | manual |

⚠️ Duplicate / unused:
- `skincare` — does not exist (404)
- `oral-care`, `oral-hygiene`, `haircare`, `baby` (in some forms) — verify before linking
- `skin-care-1` (2078 products, manual rule) is a duplicate of `skin-care`;
  ignore for email CTAs

## How to use this in flows

1. **Trigger filter (event property)** for `Ordered Product` (UWP7cZ) flows:
   ```
   AND group:
     event.Categories contains "CAT=Vitamins"  (or whichever bucket)
     event.Categories not contains "_pharmacy-only"
     event.Categories not contains "_pharmacist-only"
     event.Categories not contains "_prescription"
   ```
   Note: the `Categories` event property on `Ordered Product` is a
   line-item array. Multiple `CAT=` values may appear if the product is
   multi-categorised — `contains` matching works.

2. **Conditional-split** within a flow: use `event.Categories` (not profile
   metric) for the most accurate per-trigger routing.

3. **Profile-metric splits** (e.g. "has ordered Vitamins in last 90 days")
   use `Item Categories` property on the `Ordered Product` profile metric.

## Refresh policy

This list was pulled 2026-05-07. Re-run `productTags` query (start cursor
`CASZZZZZ`, paginate until `CAT=` prefix ends) every 90 days or whenever a
flow build references a tag.
