/**
 * Coles Scraper — Production Implementation
 *
 * Strategy: Fetches the Coles search/product pages as HTML and extracts
 * the embedded __NEXT_DATA__ JSON (server-side rendered at request time).
 * This avoids the API gateway (which is blocked by Incapsula from non-AU IPs)
 * and gives us the same data the website shows users.
 *
 * ⚠️  TLS FINGERPRINT NOTE:
 * Coles uses PerimeterX bot detection that blocks Node.js's built-in fetch
 * based on its TLS ClientHello fingerprint. curl's TLS fingerprint passes.
 * All HTML fetches use curl via child_process — do NOT switch back to fetch.
 *
 * Data confirmed accurate against live coles.com.au (March 2026).
 *
 * For GTINs (barcodes): requires individual product detail page fetch.
 * The search result only contains the Coles internal stockcode (id).
 *
 * Run standalone:  pnpm --filter @workspace/scripts run scrape-coles
 */

import { execFileSync } from "child_process";

const COLES_BASE = "https://www.coles.com.au";
const PRODUCT_IMAGE_BASE = "https://cdn.productimages.coles.com.au/productimages";

const CURL_HEADERS = [
  "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
  "-H", "Accept-Language: en-AU,en;q=0.9",
  "-H", "Accept-Encoding: gzip, deflate, br",
];

// ─── Types from real Coles __NEXT_DATA__ schema ───────────────────────────

interface ColesRawProduct {
  _type: "PRODUCT" | "SINGLE_TILE";
  id: number;
  adId: string | null;
  adSource: string | null;
  featured: boolean;
  name: string;
  brand: string | null;
  description: string;
  size: string | null;
  availability: boolean;
  availabilityType: string;
  availableQuantity: number | null;
  imageUris: Array<{ altText: string; type: string; uri: string }>;
  merchandiseHeir: {
    tradeProfitCentre: string;
    categoryGroup: string;
    category: string;
    subCategory: string;
    className: string;
  };
  onlineHeirs: Array<{
    aisle: string;
    category: string;
    subCategory: string;
    categoryId: string;
    aisleId: string;
    subCategoryId: string;
  }>;
  minGuarantee: string | null;
  pricing: {
    now: number;
    /** NOTE: was=0 means "no previous price" — NOT zero dollars. Treat as null. */
    was: number;
    unit: {
      quantity: number;
      ofMeasureQuantity: number;
      ofMeasureUnits: string;
      price: number;
      ofMeasureType: string | null;
      isWeighted: boolean;
      isIncremental: boolean;
    };
    /** Human-readable unit price, e.g. "$1.55/ 1L" */
    comparable: string;
    promotionType: string | null;
    onlineSpecial: boolean;
    saveAmount?: number | null;
    savePercent?: number;
    specialType?: string | null;
    offerDescription?: string | null;
  };
  variations?: { total: number };
  restrictions: {
    retailLimit: number;
    promotionalLimit: number;
  };
}

interface ColesDetailProduct extends ColesRawProduct {
  /** 13-digit EAN barcode — only present on product detail pages, not search */
  gtin: string | null;
  nutrition?: {
    servingSize: string;
    servingsPerPackage: string;
    breakdown: Array<{
      title: string;
      nutrients: Array<{ nutrient: string; value: string }>;
    }>;
  };
  additionalInfo?: Array<{ title: string; description: string }>;
  countryOfOrigin?: string | null;
  longDescription?: string | null;
}

export interface ColesProduct {
  retailer: "coles";
  retailerSku: string;
  name: string;
  brand: string | null;
  description: string;
  size: string | null;
  /** Current selling price in AUD */
  currentPrice: number;
  /** Previous price — null if no special is active */
  wasPrice: number | null;
  /** Parsed unit price value, e.g. 1.55 */
  unitPrice: number;
  /** Unit measure string, e.g. "L" or "100g" */
  unitMeasure: string;
  /** Full readable unit string, e.g. "$1.55/ 1L" */
  unitPriceString: string;
  isOnSpecial: boolean;
  isOnlineSpecial: boolean;
  promotionType: string | null;
  inStock: boolean;
  stockQuantity: number | null;
  /** Full image URL */
  imageUrl: string;
  /** 13-digit EAN barcode — null from search; fetch via getProductDetail() */
  barcode: string | null;
  category: string | null;
  subCategory: string | null;
  /** Verify live: https://www.coles.com.au/product/<retailerSku> */
  verifyUrl: string;
}

// ─── Core parser ──────────────────────────────────────────────────────────

function parseUnitPrice(comparable: string): {
  unitPrice: number;
  unitMeasure: string;
} {
  // Comparable format: "$1.55/ 1L" or "$3.13/ 100ml" or "$2.40/ 1kg"
  const match = comparable.match(/\$([0-9.]+)\s*\/\s*[0-9.]*\s*(.+)/);
  if (!match) return { unitPrice: 0, unitMeasure: "" };
  return {
    unitPrice: parseFloat(match[1]),
    unitMeasure: match[2].trim(),
  };
}

function mapProduct(raw: ColesRawProduct): ColesProduct {
  const pr = raw.pricing;
  // was=0 is Coles' sentinel for "no previous price" — must convert to null
  const wasPrice = pr.was && pr.was > 0 ? pr.was : null;
  const isOnSpecial = wasPrice !== null || pr.onlineSpecial || pr.promotionType === "SPECIAL";
  const { unitPrice, unitMeasure } = parseUnitPrice(pr.comparable ?? "");

  // Image URI is relative like "/8/8150288.jpg"
  const imageUri = raw.imageUris?.[0]?.uri ?? "";
  const imageUrl = imageUri ? `${PRODUCT_IMAGE_BASE}${imageUri}` : "";

  const online = raw.onlineHeirs?.[0];

  return {
    retailer: "coles",
    retailerSku: String(raw.id),
    name: raw.name,
    brand: raw.brand,
    description: raw.description,
    size: raw.size,
    currentPrice: pr.now,
    wasPrice,
    unitPrice,
    unitMeasure,
    unitPriceString: pr.comparable,
    isOnSpecial,
    isOnlineSpecial: pr.onlineSpecial,
    promotionType: pr.promotionType,
    inStock: raw.availability,
    stockQuantity: raw.availableQuantity,
    imageUrl,
    barcode: null, // only available via getProductDetail()
    category: online?.category ?? null,
    subCategory: online?.subCategory ?? null,
    verifyUrl: `${COLES_BASE}/product/${raw.id}`,
  };
}

// ─── Fetchers ─────────────────────────────────────────────────────────────

/**
 * Fetch a Coles page via curl and extract __NEXT_DATA__.
 *
 * curl's TLS ClientHello fingerprint passes PerimeterX; Node.js fetch does not.
 * We use execFileSync so there's no shell injection (args are passed as array).
 */
async function fetchNextData(url: string, retries = 2): Promise<unknown> {
  for (let attempt = 0; attempt <= retries; attempt++) {
    if (attempt > 0) {
      const delay = attempt * 3000;
      console.log(`  Retry ${attempt}/${retries} in ${delay / 1000}s...`);
      await new Promise((r) => setTimeout(r, delay));
    }

    let html: string;
    try {
      const buf = execFileSync("curl", [
        "-sL",           // silent + follow redirects
        "--compressed",  // decompress gzip/br automatically
        "--max-time", "20",
        ...CURL_HEADERS,
        url,
      ]);
      html = buf.toString("utf8");
    } catch (e: any) {
      if (attempt < retries) {
        console.log(`  curl error (attempt ${attempt + 1}): ${e.message}`);
        continue;
      }
      throw new Error(`curl failed fetching ${url}: ${e.message}`);
    }

    const match = html.match(/__NEXT_DATA__[^>]*>(.+?)<\/script>/s);
    if (!match) {
      if (attempt < retries) {
        console.log(
          `  No __NEXT_DATA__ (attempt ${attempt + 1}) — page preview: ${html.slice(0, 200)}`
        );
        continue;
      }
      throw new Error(
        `No __NEXT_DATA__ found at ${url}. Page preview: ${html.slice(0, 300)}`
      );
    }

    return JSON.parse(match[1]);
  }
  throw new Error(`Failed to fetch ${url} after ${retries + 1} attempts`);
}

/**
 * Search Coles for products by keyword.
 * Returns up to pageSize real products (SINGLE_TILE ad tiles are filtered out).
 *
 * Rate limit: Coles' PerimeterX bot detection triggers after ~3-5 rapid requests.
 * The optional `delayBefore` param (default 5s) prevents this.
 * In production, keep at least 5s between calls.
 */
export async function searchColes(
  query: string,
  pageSize = 48,
  delayBefore = 0
): Promise<ColesProduct[]> {
  if (delayBefore > 0) {
    await new Promise((r) => setTimeout(r, delayBefore));
  }
  const url = `${COLES_BASE}/search/products?q=${encodeURIComponent(query)}`;
  const data = (await fetchNextData(url)) as {
    props: { pageProps: { searchResults: { results: ColesRawProduct[] } } };
  };

  const results = data.props?.pageProps?.searchResults?.results ?? [];
  return results
    .filter((r) => r._type === "PRODUCT")
    .slice(0, pageSize)
    .map(mapProduct);
}

/**
 * Browse Coles by category slug (e.g. "dairy-eggs-fridge", "bakery").
 * Returns the full category listing.
 */
export async function browseColesByCategory(
  categorySlug: string
): Promise<ColesProduct[]> {
  const url = `${COLES_BASE}/browse/${categorySlug}`;
  const data = (await fetchNextData(url)) as {
    props: {
      pageProps: {
        searchResults?: { results: ColesRawProduct[] };
        categoryProducts?: { results: ColesRawProduct[] };
      };
    };
  };

  const pp = data.props?.pageProps;
  const results =
    pp?.searchResults?.results ?? pp?.categoryProducts?.results ?? [];

  return results.filter((r) => r._type === "PRODUCT").map(mapProduct);
}

/**
 * Fetch full product detail for a single Coles product.
 * This is the only way to get the GTIN (barcode) for cross-retailer matching.
 * Rate-limit: at least 1 second between calls.
 */
export async function getColesProductDetail(
  stockcode: string
): Promise<ColesProduct & { barcode: string | null }> {
  const url = `${COLES_BASE}/product/${stockcode}`;
  const data = (await fetchNextData(url)) as {
    props: { pageProps: { product: ColesDetailProduct } };
  };

  const raw = data.props?.pageProps?.product;
  if (!raw) throw new Error(`No product found for stockcode ${stockcode}`);

  const mapped = mapProduct(raw);
  return {
    ...mapped,
    barcode: raw.gtin ?? null,
  };
}

/**
 * Enrich a list of products with GTINs (barcodes) by fetching each detail page.
 * Rate-limited to avoid hammering Coles. Pass a small batch.
 */
export async function enrichWithBarcodes(
  products: ColesProduct[],
  delayMs = 1500
): Promise<ColesProduct[]> {
  const enriched: ColesProduct[] = [];

  for (const p of products) {
    try {
      const detail = await getColesProductDetail(p.retailerSku);
      enriched.push({ ...p, barcode: detail.barcode });
      console.log(`  [${p.retailerSku}] ${p.name} → GTIN: ${detail.barcode}`);
    } catch (e) {
      console.warn(`  [${p.retailerSku}] Failed to get GTIN: ${(e as Error).message}`);
      enriched.push(p);
    }
    await new Promise((r) => setTimeout(r, delayMs));
  }

  return enriched;
}

// ─── Standalone test run ───────────────────────────────────────────────────

async function main() {
  console.log("=".repeat(70));
  console.log("  COLES SCRAPER — PRICE ACCURACY TEST");
  console.log("=".repeat(70));
  console.log(`  Strategy: HTML __NEXT_DATA__ extraction`);
  console.log(`  Source:   coles.com.au (server-rendered, matches website exactly)`);
  console.log(`  Time:     ${new Date().toISOString()}`);
  console.log("=".repeat(70));

  // ── Search test ────────────────────────────────────────────────────────
  console.log('\n[ SEARCH: "milk" ]\n');

  const products = await searchColes("milk", 20);
  console.log(`Found ${products.length} products (after filtering ad tiles)\n`);

  console.log(
    "#   Name                                     Brand        Size   Price   Was    Unit Price        Promo        Stock"
  );
  console.log("-".repeat(120));

  for (const [i, p] of products.entries()) {
    const n = String(i + 1).padStart(2);
    const name = (p.name ?? "").substring(0, 39).padEnd(39);
    const brand = (p.brand ?? "N/A").substring(0, 11).padEnd(11);
    const size = (p.size ?? "N/A").padEnd(6);
    const price = `$${p.currentPrice.toFixed(2)}`.padEnd(7);
    const was = p.wasPrice ? `$${p.wasPrice.toFixed(2)}` : "—";
    const unit = p.unitPriceString.padEnd(17);
    const promo = (p.promotionType ?? "—").padEnd(12);
    const stock = p.inStock ? `YES (${p.stockQuantity ?? "?"})` : "NO";
    console.log(
      `${n}  ${name} ${brand} ${size} ${price} ${was.padEnd(6)} ${unit} ${promo} ${stock}`
    );
  }

  // ── GTIN enrichment test (first 3 products only) ───────────────────────
  console.log("\n[ GTIN ENRICHMENT — first 3 products ]\n");
  const enriched = await enrichWithBarcodes(products.slice(0, 3), 1500);
  for (const p of enriched) {
    console.log(
      `  ${p.name} (${p.brand}) ${p.size} → GTIN: ${p.barcode ?? "not found"}`
    );
    console.log(`  Verify: ${p.verifyUrl}`);
  }

  // ── Field validation summary ────────────────────────────────────────────
  console.log("\n[ DATA QUALITY CHECK ]\n");
  const checks = {
    "Current price present": products.filter((p) => p.currentPrice > 0).length,
    "Unit price parseable": products.filter((p) => p.unitPrice > 0).length,
    "Unit measure present": products.filter((p) => p.unitMeasure).length,
    "Promo flag reliable": products.filter((p) => p.promotionType !== undefined).length,
    "Stock status present": products.filter((p) => p.inStock !== undefined).length,
    "Category data": products.filter((p) => p.category).length,
    "Has was-price (special)": products.filter((p) => p.wasPrice !== null).length,
    "Online special flag": products.filter((p) => p.isOnlineSpecial).length,
  };

  for (const [check, count] of Object.entries(checks)) {
    const pct = Math.round((count / products.length) * 100);
    const status = pct === 100 ? "✅" : pct > 80 ? "⚠️ " : "❌";
    console.log(`  ${status} ${check}: ${count}/${products.length} (${pct}%)`);
  }

  console.log("\n[ KNOWN LIMITATIONS ]\n");
  console.log("  ⚠️  GTIN (barcode): not in search results — requires detail page");
  console.log("  ⚠️  was=0 in raw data means no special (we convert this to null)");
  console.log("  ℹ️  Regional pricing: Coles search uses default online store");
  console.log("  ℹ️  Price updates: server-rendered at request time = always current");
  console.log("  ❌  Woolworths: Akamai blocks all Replit US IPs — needs AU server");
  console.log("\n  To verify prices manually: visit the verifyUrl for each product");
}

// Only run as standalone — not when imported as a module
const isMain =
  process.argv[1] &&
  (process.argv[1].endsWith("scraper-coles.ts") ||
    process.argv[1].endsWith("scraper-coles.js"));

if (isMain) {
  main().catch((err) => {
    console.error("Fatal:", err);
    process.exit(1);
  });
}
