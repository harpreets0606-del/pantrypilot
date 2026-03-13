/**
 * Coles API Sync — uses the official BFF JSON API instead of HTML scraping.
 *
 * The BFF endpoint returns the same product structure as the HTML __NEXT_DATA__
 * scraper but works reliably from any IP using the subscription key.
 *
 * Endpoint: https://www.coles.com.au/api/bff/products/search
 * Auth:     ?subscription-key=<COLES_SUBSCRIPTION_KEY>
 *
 * Uses curl (not Node fetch) to pass PerimeterX TLS fingerprint checks.
 * 5-second delays between requests — far more conservative than needed.
 *
 * Run: pnpm --filter @workspace/scripts run coles-api-sync
 */

import { execFileSync } from "child_process";
import { db, pool } from "./db.js";
import { productsTable, retailerProductsTable, priceHistoryTable } from "./db.js";
import type { InsertProduct, InsertRetailerProduct } from "./db.js";
import { eq, and, sql } from "drizzle-orm";

const COLES_BFF_SEARCH = "https://www.coles.com.au/api/bff/products/search";
const STORE_ID = "0584";
const SUBSCRIPTION_KEY = process.env.COLES_SUBSCRIPTION_KEY;

if (!SUBSCRIPTION_KEY) {
  console.error("COLES_SUBSCRIPTION_KEY env var is required");
  process.exit(1);
}

// ── Remaining search terms (eggs–pork already done) ───────────────────────
const SEARCH_TERMS = [
  // Meat & Seafood (continued)
  "chicken breast", "salmon", "tuna",
  // Pantry staples
  "pasta", "rice", "flour", "sugar", "oats", "cereal",
  "olive oil", "vegetable oil", "tomato sauce", "baked beans",
  // Drinks
  "coffee", "tea", "orange juice", "sparkling water",
  // Frozen
  "frozen peas", "frozen pizza", "ice cream",
  // Household
  "toilet paper", "dishwashing liquid", "laundry detergent",
];

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// ── Types (same as ColesRawProduct in scraper-coles.ts) ───────────────────

interface BffProduct {
  _type: "PRODUCT" | "SINGLE_TILE";
  id: number;
  name: string;
  brand: string | null;
  description: string;
  size: string | null;
  availability: boolean;
  availableQuantity: number | null;
  imageUris: Array<{ altText: string; type: string; uri: string }>;
  merchandiseHeir: {
    tradeProfitCentre: string;
    categoryGroup: string;
    category: string;
    subCategory: string;
  };
  onlineHeirs: Array<{
    aisle: string;
    category: string;
    subCategory: string;
  }>;
  pricing: {
    now: number;
    was: number;
    unit: { quantity: number; ofMeasureQuantity: number; ofMeasureUnits: string; price: number };
    comparable: string;
    promotionType: string | null;
    onlineSpecial: boolean;
    specialType?: string | null;
  };
}

interface BffResponse {
  noOfResults: number;
  start: number;
  pageSize: number;
  keyword: string;
  results: BffProduct[];
}

const PRODUCT_IMAGE_BASE = "https://cdn.productimages.coles.com.au/productimages";

// ── Coles product mapper ───────────────────────────────────────────────────

function mapBffProduct(raw: BffProduct) {
  const pr = raw.pricing;
  if (!pr || pr.now == null) return null;
  const wasPrice = pr.was && pr.was > 0 && pr.was !== pr.now ? pr.was : null;
  const isOnSpecial = wasPrice !== null || pr.onlineSpecial || pr.promotionType === "SPECIAL";

  const comparable = pr.comparable ?? "";
  const unitMatch = comparable.match(/\$([0-9.]+)\s*\/\s*[0-9.]*\s*(.+)/);
  const unitPrice = unitMatch ? parseFloat(unitMatch[1]) : pr.unit?.price ?? 0;
  const unitMeasure = unitMatch ? unitMatch[2].trim() : pr.unit?.ofMeasureUnits ?? "";

  const imageUri = raw.imageUris?.[0]?.uri ?? "";
  const imageUrl = imageUri ? `${PRODUCT_IMAGE_BASE}${imageUri}` : "";
  const online = raw.onlineHeirs?.[0];

  return {
    retailerSku: String(raw.id),
    name: raw.name,
    brand: raw.brand,
    description: raw.description,
    size: raw.size,
    currentPrice: pr.now,
    wasPrice,
    unitPrice,
    unitMeasure,
    unitPriceString: comparable,
    isOnSpecial,
    promotionType: pr.promotionType,
    inStock: raw.availability,
    imageUrl,
    barcode: null as string | null,
    category: online?.category ?? null,
    subCategory: online?.subCategory ?? null,
    verifyUrl: `https://www.coles.com.au/product/${raw.id}`,
  };
}

// ── BFF API caller via curl ────────────────────────────────────────────────

function searchColesApi(term: string, pageSize = 48): BffProduct[] {
  const params = new URLSearchParams({
    storeId: STORE_ID,
    searchTerm: term,
    start: "0",
    pageSize: String(pageSize),
    "subscription-key": SUBSCRIPTION_KEY!,
  });

  const url = `${COLES_BFF_SEARCH}?${params}`;

  const buf = execFileSync("curl", [
    "-sL",
    "--compressed",
    "--max-time", "20",
    "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "-H", "Accept: application/json",
    "-H", "Accept-Language: en-AU,en;q=0.9",
    "-H", `Referer: https://www.coles.com.au/search?q=${encodeURIComponent(term)}`,
    url,
  ]);

  const data = JSON.parse(buf.toString("utf8")) as BffResponse;
  return (data.results ?? []).filter((r) => r._type === "PRODUCT");
}

// ── DB helpers ────────────────────────────────────────────────────────────

function inferCategory(term: string): string {
  const t = term.toLowerCase();
  if (["milk", "butter", "cheese", "yogurt", "cream", "eggs"].some((k) => t.includes(k))) return "dairy";
  if (["bread", "sourdough", "wraps", "crackers"].some((k) => t.includes(k))) return "bakery";
  if (["chicken", "beef", "pork", "lamb", "salmon", "tuna"].some((k) => t.includes(k))) return "meat-seafood";
  if (["pasta", "rice", "flour", "sugar", "oats", "cereal", "oil", "sauce", "beans"].some((k) => t.includes(k))) return "pantry";
  if (["coffee", "tea", "juice", "water"].some((k) => t.includes(k))) return "drinks";
  if (["frozen", "ice cream"].some((k) => t.includes(k))) return "frozen";
  if (["toilet paper", "dishwashing", "laundry"].some((k) => t.includes(k))) return "household";
  return "general";
}

async function findOrCreateProduct(retailerSku: string, data: {
  name: string; brand: string | null; category: string; barcode: string | null;
  unitSize: string | null; imageUrl: string | null;
}): Promise<string> {
  const existingRp = await db.select({ productId: retailerProductsTable.productId })
    .from(retailerProductsTable)
    .where(and(eq(retailerProductsTable.retailer, "coles"), eq(retailerProductsTable.retailerSku, retailerSku)))
    .limit(1);
  if (existingRp.length > 0 && existingRp[0]!.productId) return existingRp[0]!.productId;

  const inserted = await db.insert(productsTable).values({
    name: data.name, brand: data.brand, category: data.category,
    barcode: data.barcode, unitSize: data.unitSize, imageUrl: data.imageUrl,
  } as InsertProduct).returning({ id: productsTable.id });
  return inserted[0]!.id;
}

async function upsertRetailerProduct(productId: string, data: {
  retailerSku: string; name: string; verifyUrl: string; currentPrice: number;
  wasPrice: number | null; unitPrice: number; unitPriceString: string;
  isOnSpecial: boolean; inStock: boolean; imageUrl: string;
}) {
  const existing = await db.select({ id: retailerProductsTable.id, currentPrice: retailerProductsTable.currentPrice })
    .from(retailerProductsTable)
    .where(and(eq(retailerProductsTable.retailer, "coles"), eq(retailerProductsTable.retailerSku, data.retailerSku)))
    .limit(1);

  const now = new Date();
  const rpInsert: InsertRetailerProduct & { retailer: string; retailerSku: string } = {
    retailer: "coles", retailerSku: data.retailerSku, retailerName: data.name,
    retailerUrl: data.verifyUrl, currentPrice: String(data.currentPrice),
    wasPrice: data.wasPrice ? String(data.wasPrice) : null,
    unitPrice: String(data.unitPrice), unitPriceString: data.unitPriceString,
    isOnSpecial: data.isOnSpecial, inStock: data.inStock, imageUrl: data.imageUrl,
  };

  if (existing.length === 0) {
    await db.insert(retailerProductsTable).values({ ...rpInsert, productId, lastScrapedAt: now });
    await db.insert(priceHistoryTable).values({
      retailerProductId: (await db.select({ id: retailerProductsTable.id }).from(retailerProductsTable)
        .where(and(eq(retailerProductsTable.retailer, "coles"), eq(retailerProductsTable.retailerSku, data.retailerSku))).limit(1))[0]!.id,
      price: String(data.currentPrice),
      wasPrice: data.wasPrice ? String(data.wasPrice) : null,
      isOnSpecial: data.isOnSpecial,
    });
    return "new";
  }

  const oldPrice = existing[0]!.currentPrice ? parseFloat(existing[0]!.currentPrice) : null;
  if (oldPrice !== data.currentPrice) {
    await db.insert(priceHistoryTable).values({
      retailerProductId: existing[0]!.id,
      price: String(data.currentPrice),
      wasPrice: data.wasPrice ? String(data.wasPrice) : null,
      isOnSpecial: data.isOnSpecial,
    });
  }
  await db.update(retailerProductsTable).set({
    productId, retailerName: data.name, retailerUrl: data.verifyUrl,
    currentPrice: String(data.currentPrice), wasPrice: data.wasPrice ? String(data.wasPrice) : null,
    unitPrice: String(data.unitPrice), unitPriceString: data.unitPriceString,
    isOnSpecial: data.isOnSpecial, inStock: data.inStock, imageUrl: data.imageUrl,
    lastScrapedAt: now, updatedAt: now,
  }).where(eq(retailerProductsTable.id, existing[0]!.id));
  return oldPrice !== data.currentPrice ? "price-changed" : "updated";
}

// ── Main ──────────────────────────────────────────────────────────────────

async function main() {
  console.log("=".repeat(72));
  console.log("  COLES API SYNC (BFF endpoint + subscription key)");
  console.log(`  ${new Date().toISOString()}`);
  console.log(`  Terms: ${SEARCH_TERMS.length} | Est. time: ~${Math.ceil(SEARCH_TERMS.length * 7 / 60)} minutes`);
  console.log("=".repeat(72));

  let totalNew = 0, totalUpdated = 0, totalErrors = 0;

  for (let i = 0; i < SEARCH_TERMS.length; i++) {
    const term = SEARCH_TERMS[i]!;
    const category = inferCategory(term);

    if (i > 0) await delay(5000); // 5s between requests

    process.stdout.write(`[${i + 1}/${SEARCH_TERMS.length}] "${term}" (${category})... `);

    try {
      const rawProducts = searchColesApi(term, 48);
      const products = rawProducts.map(mapBffProduct).filter((p): p is NonNullable<ReturnType<typeof mapBffProduct>> => p !== null);

      let termNew = 0, termUpdated = 0;

      for (const p of products) {
        try {
          const productId = await findOrCreateProduct(p.retailerSku, {
            name: p.name, brand: p.brand, category,
            barcode: p.barcode, unitSize: p.size, imageUrl: p.imageUrl,
          });
          const result = await upsertRetailerProduct(productId, {
            retailerSku: p.retailerSku, name: p.name, verifyUrl: p.verifyUrl,
            currentPrice: p.currentPrice, wasPrice: p.wasPrice,
            unitPrice: p.unitPrice, unitPriceString: p.unitPriceString,
            isOnSpecial: p.isOnSpecial, inStock: p.inStock, imageUrl: p.imageUrl,
          });
          if (result === "new") termNew++;
          else termUpdated++;
        } catch (err: any) {
          console.error(`\n  ⚠️  SKU ${p.retailerSku}: ${err.message.slice(0, 60)}`);
          totalErrors++;
        }
      }

      totalNew += termNew;
      totalUpdated += termUpdated;
      console.log(`${products.length} products (${termNew} new, ${termUpdated} updated)`);

    } catch (err: any) {
      console.log(`❌ ${err.message.slice(0, 100)}`);
      totalErrors++;
    }
  }

  const [pCount] = await db.select({ count: sql<number>`count(*)::int` }).from(productsTable);
  const [rpCount] = await db.select({ count: sql<number>`count(*)::int` }).from(retailerProductsTable);
  const [colesCount] = await db.select({ count: sql<number>`count(*)::int` })
    .from(retailerProductsTable).where(eq(retailerProductsTable.retailer, "coles"));
  const [wwCount] = await db.select({ count: sql<number>`count(*)::int` })
    .from(retailerProductsTable).where(eq(retailerProductsTable.retailer, "woolworths"));

  console.log(`\n${"=".repeat(72)}`);
  console.log("  SYNC COMPLETE");
  console.log(`  New Coles products:  ${totalNew}`);
  console.log(`  Updated:             ${totalUpdated}`);
  console.log(`  Errors:              ${totalErrors}`);
  console.log(`  DB products total:   ${pCount?.count ?? 0}`);
  console.log(`  Woolworths:          ${wwCount?.count ?? 0}`);
  console.log(`  Coles:               ${colesCount?.count ?? 0}`);
  console.log("=".repeat(72));

  await pool.end();
}

main().catch((err) => {
  console.error("Fatal:", err);
  pool.end().finally(() => process.exit(1));
});
