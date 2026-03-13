import { drizzle } from "drizzle-orm/node-postgres";
import pg from "pg";
import {
  pgTable, uuid, text, numeric, integer, boolean,
  date, timestamp, uniqueIndex,
} from "drizzle-orm/pg-core";

const { Pool } = pg;

if (!process.env.DATABASE_URL) {
  throw new Error("DATABASE_URL environment variable is required.");
}

// ─── Schema ───────────────────────────────────────────────────────────────

export const productsTable = pgTable("products", {
  id: uuid("id").primaryKey().defaultRandom(),
  name: text("name").notNull(),
  brand: text("brand"),
  category: text("category").notNull(),
  subcategory: text("subcategory"),
  barcode: text("barcode"),
  unitSize: text("unit_size"),
  unitMeasure: text("unit_measure"),
  unitQuantity: numeric("unit_quantity"),
  imageUrl: text("image_url"),
  caloriesPer100g: numeric("calories_per_100g"),
  proteinPer100g: numeric("protein_per_100g"),
  fatPer100g: numeric("fat_per_100g"),
  carbsPer100g: numeric("carbs_per_100g"),
  fiberPer100g: numeric("fiber_per_100g"),
  sugarPer100g: numeric("sugar_per_100g"),
  sodiumPer100g: numeric("sodium_per_100g"),
  nutriScore: text("nutri_score"),
  novaGroup: integer("nova_group"),
  allergens: text("allergens").array(),
  offBarcode: text("off_barcode"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
  updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
});

export const retailerProductsTable = pgTable(
  "retailer_products",
  {
    id: uuid("id").primaryKey().defaultRandom(),
    productId: uuid("product_id").references(() => productsTable.id),
    retailer: text("retailer").notNull(),
    retailerSku: text("retailer_sku"),
    retailerName: text("retailer_name"),
    retailerUrl: text("retailer_url"),
    currentPrice: numeric("current_price"),
    wasPrice: numeric("was_price"),
    unitPrice: numeric("unit_price"),
    unitPriceString: text("unit_price_string"),
    isOnSpecial: boolean("is_on_special").default(false),
    specialType: text("special_type"),
    specialEndDate: date("special_end_date"),
    inStock: boolean("in_stock").default(true),
    imageUrl: text("image_url"),
    lastScrapedAt: timestamp("last_scraped_at", { withTimezone: true }),
    createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
    updatedAt: timestamp("updated_at", { withTimezone: true }).notNull().defaultNow(),
  },
  (t) => [
    uniqueIndex("idx_retailer_products_retailer_sku").on(t.retailer, t.retailerSku),
  ]
);

export const priceHistoryTable = pgTable("price_history", {
  id: uuid("id").primaryKey().defaultRandom(),
  retailerProductId: uuid("retailer_product_id")
    .notNull()
    .references(() => retailerProductsTable.id),
  price: numeric("price").notNull(),
  wasPrice: numeric("was_price"),
  isOnSpecial: boolean("is_on_special").default(false),
  recordedAt: timestamp("recorded_at", { withTimezone: true }).notNull().defaultNow(),
});

// ─── Types ─────────────────────────────────────────────────────────────────

export type InsertProduct = typeof productsTable.$inferInsert;
export type InsertRetailerProduct = typeof retailerProductsTable.$inferInsert;

// ─── Connection ────────────────────────────────────────────────────────────

export const pool = new Pool({ connectionString: process.env.DATABASE_URL });
export const db = drizzle(pool, {
  schema: { productsTable, retailerProductsTable, priceHistoryTable },
});
