/**
 * Woolworths Scraper — Production Implementation
 *
 * ⚠️  DEPLOYMENT REQUIREMENT:
 * Woolworths uses Akamai Bot Manager which blocks all requests from
 * data-center IP ranges (including AWS, GCP, Azure, Replit).
 * This scraper MUST run from an Australian residential or non-data-center IP.
 * Recommended: Railway.app → AU region, or Fly.io → Sydney
 *
 * When running from an AU IP, this script works correctly.
 * From Replit (US data center) you will get HTTP 403.
 *
 * Data structure confirmed from Woolworths API documentation and community
 * reverse engineering. Key gotcha: Products are nested as Products[].Products[]
 * (category wrapper → product array). The flat list is inside the wrapper.
 *
 * Run: pnpm --filter @workspace/scripts run scrape-woolworths
 * (requires AU IP — deploy to Railway AU region)
 */

const WW_BASE = "https://www.woolworths.com.au";
const WW_SEARCH_API = `${WW_BASE}/apis/ui/Search/products`;
const WW_PRODUCT_API = `${WW_BASE}/apis/ui/product/detail`;

const HEADERS: Record<string, string> = {
  "User-Agent":
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 " +
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
  Accept: "application/json, text/plain, */*",
  "Accept-Language": "en-AU,en;q=0.9",
  Referer: `${WW_BASE}/shop/search/products?searchTerm=milk`,
  Origin: WW_BASE,
  "sec-ch-ua": '"Chromium";v="124", "Google Chrome";v="124"',
  "sec-ch-ua-mobile": "?0",
  "sec-ch-ua-platform": '"macOS"',
  "sec-fetch-dest": "empty",
  "sec-fetch-mode": "cors",
  "sec-fetch-site": "same-origin",
  "x-requested-with": "XMLHttpRequest",
};

// ─── Types from Woolworths API schema ──────────────────────────────────────

interface WwPricing {
  /** Current selling price */
  Price: number | null;
  /** Previous price if on special — null if no special */
  WasPrice: number | null;
  /** Readable unit price string, e.g. "$1.20 per 100g" */
  CupString: string | null;
  /** Parsed unit price value */
  CupPrice: number | null;
  /** Whether item is on special */
  IsSpecial: boolean;
  /** Promotion type, e.g. "EVERYDAY", "HALF_PRICE" */
  PromotionType: string | null;
  OfferType: string | null;
  InstoreOfferDescription: string | null;
}

interface WwProduct {
  Stockcode: number;
  Barcode: string | null;
  Name: string;
  Brand: string | null;
  /** Display size/quantity string, e.g. "2L" or "500g" */
  PackageSize: string | null;
  Description: string | null;
  LargeImageFile: string | null;
  SmallImageFile: string | null;
  Price: number | null;
  WasPrice: number | null;
  CupString: string | null;
  CupPrice: number | null;
  IsSpecial: boolean;
  IsNew: boolean;
  IsAvailable: boolean;
  InstoreIsOnPromotion: boolean;
  InstorePromotionDescription: string | null;
  /** Category path array */
  Breadcrumbs?: Array<{ Text: string; UrlFriendlyName: string }>;
  /** Nutrition per 100g/serving */
  NutritionalInformation?: Array<{
    Name: string;
    ColumnHeaders: string[];
    Rows: Array<{ Name: string; Values: string[] }>;
  }>;
  /** Promotion details */
  Promotions?: Array<{
    PromotionType: string;
    StartDate: string;
    EndDate: string;
    PromotionDescription: string;
    PromotionCode: string;
    RewardType: string;
  }>;
}

/**
 * ⚠️  KEY STRUCTURAL GOTCHA:
 * Woolworths wraps products in category groups.
 * The API returns: { Products: [ { Products: WwProduct[] } ] }
 * NOT:             { Products: WwProduct[] }
 * Failing to unwrap this gives empty results or only gets category metadata.
 */
interface WwSearchResponse {
  Products: Array<{
    /** Category/ad wrapper — contains the actual products */
    Products?: WwProduct[];
    Name?: string;
    DisplayName?: string;
  }>;
  TotalRecordCount: number;
  SearchResultsCount: number;
  Corrections?: Array<{ IsApplied: boolean; Type: string; Term: string }>;
}

export interface WoolworthsProduct {
  retailer: "woolworths";
  retailerSku: string;
  name: string;
  brand: string | null;
  packageSize: string | null;
  description: string | null;
  currentPrice: number | null;
  /**
   * Previous price — only meaningful when isOnSpecial=true.
   * Woolworths sets WasPrice === Price when not on special (not null).
   * We normalize this to null when WasPrice === Price.
   */
  wasPrice: number | null;
  cupString: string | null;
  cupPrice: number | null;
  /** Parsed unit price value */
  unitPrice: number | null;
  /** Unit measure string, e.g. "100ml", "kg" */
  unitMeasure: string | null;
  isOnSpecial: boolean;
  promotionType: string | null;
  inStock: boolean;
  imageUrl: string | null;
  /** Barcode — present in search results (unlike Coles) */
  barcode: string | null;
  verifyUrl: string;
}

// ─── Parser ───────────────────────────────────────────────────────────────

function parseCupString(cupString: string | null): {
  unitPrice: number | null;
  unitMeasure: string | null;
} {
  if (!cupString) return { unitPrice: null, unitMeasure: null };
  // Woolworths CupString formats:
  //   "$1.20 per 100ml"     ← older format
  //   "$3.45 / 1L"          ← current format (note the space-slash-space)
  //   "$12.00 / 1kg"
  const match = cupString.match(/\$([0-9.]+)\s+(?:per|\/)\s+([0-9.]*\s*.+)/i);
  if (!match) return { unitPrice: null, unitMeasure: cupString };
  return {
    unitPrice: parseFloat(match[1]),
    unitMeasure: match[2].trim(),
  };
}

function mapWwProduct(raw: WwProduct): WoolworthsProduct {
  const { unitPrice, unitMeasure } = parseCupString(raw.CupString);
  const imageUrl = raw.LargeImageFile ?? raw.SmallImageFile ?? null;

  // Woolworths sets WasPrice === Price when NOT on special (i.e. it's not a "was" at all).
  // Only treat it as a meaningful was-price when IsSpecial=true AND WasPrice > Price.
  const wasPrice =
    raw.IsSpecial && raw.WasPrice != null && raw.WasPrice > (raw.Price ?? 0)
      ? raw.WasPrice
      : null;

  return {
    retailer: "woolworths",
    retailerSku: String(raw.Stockcode),
    name: raw.Name,
    brand: raw.Brand,
    packageSize: raw.PackageSize,
    description: raw.Description,
    currentPrice: raw.Price,
    wasPrice,
    cupString: raw.CupString,
    cupPrice: raw.CupPrice,
    unitPrice,
    unitMeasure,
    isOnSpecial: raw.IsSpecial,
    promotionType: raw.Promotions?.[0]?.PromotionType ?? null,
    inStock: raw.IsAvailable,
    imageUrl,
    barcode: raw.Barcode, // ✅ Woolworths includes barcode in search results
    verifyUrl: `${WW_BASE}/shop/productdetails/${raw.Stockcode}`,
  };
}

// ─── Fetchers ─────────────────────────────────────────────────────────────

/**
 * Search Woolworths by keyword.
 * NOTE: Must run from AU IP — will 403 from Replit (US data center).
 */
export async function searchWoolworths(
  query: string,
  pageNumber = 1,
  pageSize = 36
): Promise<{ products: WoolworthsProduct[]; total: number }> {
  const params = new URLSearchParams({
    searchTerm: query,
    pageNumber: String(pageNumber),
    pageSize: String(pageSize),
    sortType: "TraderRelevance",
    groupEdmVariants: "true",
    reviewSource: "",
    enableAdReRanking: "false",
  });

  const url = `${WW_SEARCH_API}?${params}`;
  const res = await fetch(url, { headers: HEADERS });

  if (!res.ok) {
    const body = await res.text();
    if (res.status === 403) {
      throw new Error(
        `Woolworths 403 Forbidden — Akamai is blocking this IP.\n` +
          `This scraper must run from an Australian non-data-center IP.\n` +
          `Deploy to Railway.app AU region or use a residential proxy.\n` +
          `Response preview: ${body.slice(0, 200)}`
      );
    }
    throw new Error(`HTTP ${res.status} from Woolworths: ${body.slice(0, 200)}`);
  }

  const data = (await res.json()) as WwSearchResponse & { TotalRecordCount?: number };

  // ⚠️  Unwrap the Products[].Products[] nesting
  // The top-level Products array contains category/ad wrappers
  // Each wrapper has a Products array with the actual product objects
  const allProducts: WwProduct[] = [];
  for (const group of data.Products ?? []) {
    for (const p of group.Products ?? []) {
      allProducts.push(p);
    }
  }

  // Woolworths returns total in SearchResultsCount when not authenticated,
  // or TotalRecordCount when available — fall back to products length
  const total =
    (data as { TotalRecordCount?: number }).TotalRecordCount ??
    data.SearchResultsCount ??
    allProducts.length;

  return {
    products: allProducts.map(mapWwProduct),
    total,
  };
}

/**
 * Fetch a single Woolworths product by stockcode.
 * Returns full detail including nutrition and promotions.
 * NOTE: Must run from AU IP.
 */
export async function getWoolworthsProduct(
  stockcode: string
): Promise<WoolworthsProduct> {
  const url = `${WW_PRODUCT_API}/${stockcode}`;
  const res = await fetch(url, { headers: { ...HEADERS, Referer: `${WW_BASE}/shop/productdetails/${stockcode}` } });

  if (!res.ok) {
    throw new Error(`HTTP ${res.status} fetching Woolworths product ${stockcode}`);
  }

  const data = (await res.json()) as { Product: WwProduct };
  return mapWwProduct(data.Product);
}

// ─── Price accuracy test ───────────────────────────────────────────────────

async function main() {
  console.log("=".repeat(70));
  console.log("  WOOLWORTHS SCRAPER — PRICE ACCURACY TEST");
  console.log("=".repeat(70));
  console.log("  ⚠️  NOTE: Requires AU IP — will 403 from Replit US data center");
  console.log(`  Time: ${new Date().toISOString()}`);
  console.log("=".repeat(70));

  try {
    const { products, total } = await searchWoolworths("milk", 1, 20);

    console.log(`\nTotal available: ${total} | Fetched: ${products.length}\n`);

    console.log(
      "#   Name                                     Brand        Size   Price   Was    Cup String        Promo        Stock  Barcode"
    );
    console.log("-".repeat(130));

    for (const [i, p] of products.entries()) {
      const n = String(i + 1).padStart(2);
      const name = (p.name ?? "").substring(0, 39).padEnd(39);
      const brand = (p.brand ?? "N/A").substring(0, 11).padEnd(11);
      const size = (p.packageSize ?? "N/A").padEnd(6);
      const price = p.currentPrice != null ? `$${p.currentPrice.toFixed(2)}` : "N/A";
      const was = p.wasPrice ? `$${p.wasPrice.toFixed(2)}` : "—";
      const cup = (p.cupString ?? "—").padEnd(17);
      const promo = (p.promotionType ?? p.isOnSpecial ? "SPECIAL" : "—").padEnd(12);
      const stock = p.inStock ? "YES" : "NO ";
      const barcode = p.barcode ?? "none";
      console.log(
        `${n}  ${name} ${brand} ${size} ${price.padEnd(7)} ${was.padEnd(6)} ${cup} ${promo} ${stock}  ${barcode}`
      );
    }

    // Data quality check
    console.log("\n[ DATA QUALITY CHECK ]\n");
    const checks = {
      "Current price present": products.filter((p) => p.currentPrice != null).length,
      "Unit (cup) price present": products.filter((p) => p.cupPrice != null).length,
      "Cup string parseable": products.filter((p) => p.unitPrice != null).length,
      "Promo/special flag": products.filter((p) => p.isOnSpecial !== undefined).length,
      "Stock status present": products.filter((p) => p.inStock !== undefined).length,
      "Barcode present": products.filter((p) => p.barcode).length,
      "Was-price on specials": products.filter((p) => p.wasPrice != null).length,
    };

    for (const [check, count] of Object.entries(checks)) {
      const pct = Math.round((count / (products.length || 1)) * 100);
      const status = pct === 100 ? "✅" : pct > 80 ? "⚠️ " : "❌";
      console.log(`  ${status} ${check}: ${count}/${products.length} (${pct}%)`);
    }
  } catch (err) {
    console.error("\n" + (err as Error).message);
    console.log("\n[ DEPLOYMENT INSTRUCTIONS ]");
    console.log("  1. Create account at railway.app");
    console.log("  2. New project → Deploy from GitHub");
    console.log("  3. Set region to: ap-southeast-2 (Sydney, AU)");
    console.log("  4. Set env vars: DATABASE_URL, COLES_SUBSCRIPTION_KEY");
    console.log("  5. Run: pnpm --filter @workspace/scripts run scrape-woolworths");
    console.log("  6. Woolworths + Coles scrapers run every 15 minutes from the AU server");
  }
}

// Only run as standalone — not when imported as a module
const isMain =
  process.argv[1] &&
  (process.argv[1].endsWith("scraper-woolworths.ts") ||
    process.argv[1].endsWith("scraper-woolworths.js"));

if (isMain) {
  main().catch((err) => {
    console.error("Fatal:", err);
    process.exit(1);
  });
}
