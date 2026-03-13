/**
 * PantryPilot — Price Sync Pipeline
 *
 * Scrapes Woolworths and Coles for common grocery categories,
 * upserts products + retailer_products into PostgreSQL, and
 * records price_history whenever a price changes.
 *
 * Designed to run as a Railway Cron Job (daily at 2am AEST).
 * Idempotent — re-running never creates duplicate rows.
 *
 * Architecture:
 *   1. Scrape each search term from Woolworths + Coles
 *   2. For each product: upsert products table (by barcode or new row)
 *   3. Upsert retailer_products by (retailer, retailer_sku)
 *   4. If price changed → insert price_history row
 */

import { db, pool, productsTable, retailerProductsTable, priceHistoryTable } from "./db.js";
import type { InsertProduct, InsertRetailerProduct } from "./db.js";
import { eq, and, sql } from "drizzle-orm";
import { searchWoolworths, type WoolworthsProduct } from "./scraper-woolworths.js";
import { searchColes, type ColesProduct } from "./scraper-coles.js";

// ─── Search terms covering core grocery categories ─────────────────────────

const SEARCH_TERMS = [
  // Dairy
  "milk", "butter", "cheese", "yogurt", "cream", "eggs",
  // Bakery
  "bread", "sourdough", "wraps", "crackers",
  // Meat
  "chicken breast", "beef mince", "pork", "salmon", "tuna",
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

// ─── Rate limiting helpers ─────────────────────────────────────────────────

const delay = (ms: number) => new Promise((r) => setTimeout(r, ms));

// ─── Category inference from search term ──────────────────────────────────

function inferCategory(term: string): string {
  const t = term.toLowerCase();
  if (["milk", "butter", "cheese", "yogurt", "cream", "eggs"].some((k) => t.includes(k)))
    return "dairy";
  if (["bread", "sourdough", "wraps", "crackers"].some((k) => t.includes(k)))
    return "bakery";
  if (["chicken", "beef", "pork", "lamb", "salmon", "tuna"].some((k) => t.includes(k)))
    return "meat-seafood";
  if (["pasta", "rice", "flour", "sugar", "oats", "cereal", "oil", "sauce", "beans"].some((k) => t.includes(k)))
    return "pantry";
  if (["coffee", "tea", "juice", "water"].some((k) => t.includes(k)))
    return "drinks";
  if (["frozen", "ice cream"].some((k) => t.includes(k)))
    return "frozen";
  if (["toilet paper", "dishwashing", "laundry", "detergent"].some((k) => t.includes(k)))
    return "household";
  return "general";
}

// ─── Product upsert: find-or-create in the canonical products table ────────

async function findOrCreateProduct(
  retailer: string,
  retailerSku: string,
  data: {
    name: string;
    brand: string | null;
    category: string;
    barcode: string | null;
    unitSize: string | null;
    imageUrl: string | null;
  }
): Promise<string> {
  // 1. Try matching by barcode (cross-retailer canonical product)
  if (data.barcode) {
    const existing = await db
      .select({ id: productsTable.id })
      .from(productsTable)
      .where(eq(productsTable.barcode, data.barcode))
      .limit(1);
    if (existing.length > 0) return existing[0]!.id;
  }

  // 2. Try matching via existing retailer_products row for this SKU
  const existingRetailerProduct = await db
    .select({ productId: retailerProductsTable.productId })
    .from(retailerProductsTable)
    .where(
      and(
        eq(retailerProductsTable.retailer, retailer),
        eq(retailerProductsTable.retailerSku, retailerSku)
      )
    )
    .limit(1);

  if (existingRetailerProduct.length > 0 && existingRetailerProduct[0]!.productId) {
    return existingRetailerProduct[0]!.productId;
  }

  // 3. Insert new canonical product row
  const newProduct: InsertProduct = {
    name: data.name,
    brand: data.brand,
    category: data.category,
    barcode: data.barcode,
    unitSize: data.unitSize,
    imageUrl: data.imageUrl,
  };

  const inserted = await db
    .insert(productsTable)
    .values(newProduct)
    .returning({ id: productsTable.id });

  return inserted[0]!.id;
}

// ─── Retailer product upsert + price history ──────────────────────────────

async function upsertRetailerProduct(
  productId: string,
  data: InsertRetailerProduct & { retailer: string; retailerSku: string }
): Promise<{ priceChanged: boolean; oldPrice: number | null }> {
  const existing = await db
    .select({
      id: retailerProductsTable.id,
      currentPrice: retailerProductsTable.currentPrice,
    })
    .from(retailerProductsTable)
    .where(
      and(
        eq(retailerProductsTable.retailer, data.retailer),
        eq(retailerProductsTable.retailerSku, data.retailerSku!)
      )
    )
    .limit(1);

  const now = new Date();

  if (existing.length === 0) {
    await db.insert(retailerProductsTable).values({
      ...data,
      productId,
      lastScrapedAt: now,
    });
    return { priceChanged: true, oldPrice: null };
  }

  const oldPrice = existing[0]!.currentPrice
    ? parseFloat(existing[0]!.currentPrice)
    : null;
  const newPrice = data.currentPrice ? parseFloat(String(data.currentPrice)) : null;
  const priceChanged = oldPrice !== newPrice;

  await db
    .update(retailerProductsTable)
    .set({
      productId,
      retailerName: data.retailerName,
      retailerUrl: data.retailerUrl,
      currentPrice: data.currentPrice,
      wasPrice: data.wasPrice,
      unitPrice: data.unitPrice,
      unitPriceString: data.unitPriceString,
      isOnSpecial: data.isOnSpecial,
      inStock: data.inStock,
      imageUrl: data.imageUrl,
      lastScrapedAt: now,
      updatedAt: now,
    })
    .where(eq(retailerProductsTable.id, existing[0]!.id));

  return { priceChanged, oldPrice };
}

// ─── Record price history ─────────────────────────────────────────────────

async function recordPriceHistory(
  retailer: string,
  retailerSku: string,
  price: number,
  wasPrice: number | null,
  isOnSpecial: boolean
) {
  const rp = await db
    .select({ id: retailerProductsTable.id })
    .from(retailerProductsTable)
    .where(
      and(
        eq(retailerProductsTable.retailer, retailer),
        eq(retailerProductsTable.retailerSku, retailerSku)
      )
    )
    .limit(1);

  if (rp.length === 0) return;

  await db.insert(priceHistoryTable).values({
    retailerProductId: rp[0]!.id,
    price: String(price),
    wasPrice: wasPrice ? String(wasPrice) : null,
    isOnSpecial,
  });
}

// ─── Process a batch of scraped products ──────────────────────────────────

async function processBatch(
  retailer: string,
  products: Array<{
    name: string;
    brand: string | null;
    barcode: string | null;
    retailerSku: string;
    retailerUrl: string | null;
    currentPrice: number | null;
    wasPrice: number | null;
    unitPrice: number | null;
    unitPriceString: string | null;
    isOnSpecial: boolean;
    inStock: boolean;
    imageUrl: string | null;
    packageSize: string | null;
  }>,
  category: string
): Promise<{ inserted: number; updated: number; priceChanges: number }> {
  let inserted = 0;
  let updated = 0;
  let priceChanges = 0;

  for (const p of products) {
    try {
      const productId = await findOrCreateProduct(retailer, p.retailerSku, {
        name: p.name,
        brand: p.brand,
        category,
        barcode: p.barcode,
        unitSize: p.packageSize,
        imageUrl: p.imageUrl,
      });

      const rpData: InsertRetailerProduct & { retailer: string; retailerSku: string } = {
        retailer,
        retailerSku: p.retailerSku,
        retailerName: p.name,
        retailerUrl: p.retailerUrl,
        currentPrice: p.currentPrice ? String(p.currentPrice) : null,
        wasPrice: p.wasPrice ? String(p.wasPrice) : null,
        unitPrice: p.unitPrice ? String(p.unitPrice) : null,
        unitPriceString: p.unitPriceString,
        isOnSpecial: p.isOnSpecial,
        inStock: p.inStock,
        imageUrl: p.imageUrl,
      };

      const { priceChanged, oldPrice } = await upsertRetailerProduct(productId, rpData);

      if (priceChanged && p.currentPrice !== null) {
        await recordPriceHistory(
          retailer,
          p.retailerSku,
          p.currentPrice,
          p.wasPrice,
          p.isOnSpecial
        );
        priceChanges++;
        if (oldPrice === null) {
          inserted++;
        } else {
          updated++;
        }
      } else {
        updated++;
      }
    } catch (err: any) {
      console.error(`  ⚠️  ${retailer} SKU ${p.retailerSku} — ${err.message}`);
    }
  }

  return { inserted, updated, priceChanges };
}

// ─── Normalisers ──────────────────────────────────────────────────────────

function normaliseWoolworths(p: WoolworthsProduct) {
  return {
    name: p.name,
    brand: p.brand ?? null,
    barcode: p.barcode ?? null,
    retailerSku: p.retailerSku,
    retailerUrl: p.verifyUrl,
    currentPrice: p.currentPrice ?? null,
    wasPrice: p.wasPrice ?? null,
    unitPrice: p.unitPrice ?? null,
    unitPriceString: p.cupString ?? null,
    isOnSpecial: p.isOnSpecial,
    inStock: p.inStock,
    imageUrl: p.imageUrl ?? null,
    packageSize: p.packageSize ?? null,
  };
}

function normaliseColes(p: ColesProduct) {
  return {
    name: p.name,
    brand: p.brand ?? null,
    barcode: p.barcode ?? null,
    retailerSku: p.retailerSku,
    retailerUrl: p.verifyUrl,
    currentPrice: p.currentPrice ?? null,
    wasPrice: p.wasPrice ?? null,
    unitPrice: p.unitPrice ?? null,
    unitPriceString: p.unitPriceString ?? null,
    isOnSpecial: p.isOnSpecial,
    inStock: p.inStock,
    imageUrl: p.imageUrl ?? null,
    packageSize: p.size ?? null,
  };
}

// ─── Main sync loop ────────────────────────────────────────────────────────

export async function main() {
  console.log("=".repeat(72));
  console.log("  PANTRYPILOT — PRICE SYNC PIPELINE");
  console.log(`  ${new Date().toISOString()}`);
  console.log("=".repeat(72));
  console.log(`  Search terms: ${SEARCH_TERMS.length}`);
  console.log(`  Retailers:    Woolworths, Coles\n`);

  const totals = {
    woolworths: { products: 0, inserted: 0, updated: 0, priceChanges: 0, errors: 0 },
    coles: { products: 0, inserted: 0, updated: 0, priceChanges: 0, errors: 0 },
  };

  for (let i = 0; i < SEARCH_TERMS.length; i++) {
    const term = SEARCH_TERMS[i]!;
    const category = inferCategory(term);

    console.log(`\n[${i + 1}/${SEARCH_TERMS.length}] "${term}" (${category})`);

    // ── Woolworths ──
    try {
      process.stdout.write("  Woolworths... ");
      const { products, total } = await searchWoolworths(term, 1, 36);
      const normalised = products.map(normaliseWoolworths);
      const { inserted, updated, priceChanges } = await processBatch(
        "woolworths",
        normalised,
        category
      );
      totals.woolworths.products += products.length;
      totals.woolworths.inserted += inserted;
      totals.woolworths.updated += updated;
      totals.woolworths.priceChanges += priceChanges;
      console.log(
        `${products.length}/${total} products (${inserted} new, ${updated} updated, ${priceChanges} price changes)`
      );
    } catch (err: any) {
      console.log(`❌ ${err.message.slice(0, 100)}`);
      totals.woolworths.errors++;
    }

    await delay(2000);

    // ── Coles ──
    try {
      process.stdout.write("  Coles...      ");
      const products = await searchColes(term, 48, 0);
      const normalised = products.map(normaliseColes);
      const { inserted, updated, priceChanges } = await processBatch(
        "coles",
        normalised,
        category
      );
      totals.coles.products += products.length;
      totals.coles.inserted += inserted;
      totals.coles.updated += updated;
      totals.coles.priceChanges += priceChanges;
      console.log(
        `${products.length} products (${inserted} new, ${updated} updated, ${priceChanges} price changes)`
      );
    } catch (err: any) {
      console.log(`❌ ${err.message.slice(0, 100)}`);
      totals.coles.errors++;
    }

    // 10s between search terms — keeps Coles PerimeterX happy
    if (i < SEARCH_TERMS.length - 1) {
      await delay(10000);
    }
  }

  // ── Final summary ──
  console.log(`\n${"=".repeat(72)}`);
  console.log("  SYNC COMPLETE");
  console.log("=".repeat(72));

  const [productCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(productsTable);
  const [rpCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(retailerProductsTable);
  const [phCount] = await db
    .select({ count: sql<number>`count(*)::int` })
    .from(priceHistoryTable);

  console.log(`\n  Woolworths:`);
  console.log(`    Products scraped:  ${totals.woolworths.products}`);
  console.log(`    New products:      ${totals.woolworths.inserted}`);
  console.log(`    Price updates:     ${totals.woolworths.priceChanges}`);
  if (totals.woolworths.errors > 0) console.log(`    Errors:            ${totals.woolworths.errors}`);

  console.log(`\n  Coles:`);
  console.log(`    Products scraped:  ${totals.coles.products}`);
  console.log(`    New products:      ${totals.coles.inserted}`);
  console.log(`    Price updates:     ${totals.coles.priceChanges}`);
  if (totals.coles.errors > 0) console.log(`    Errors:            ${totals.coles.errors}`);

  console.log(`\n  Database totals:`);
  console.log(`    products:          ${productCount?.count ?? 0} rows`);
  console.log(`    retailer_products: ${rpCount?.count ?? 0} rows`);
  console.log(`    price_history:     ${phCount?.count ?? 0} rows`);
  console.log();

  await pool.end();
}

main().catch((err) => {
  console.error("Fatal:", err);
  pool.end().finally(() => process.exit(1));
});
