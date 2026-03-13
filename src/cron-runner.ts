/**
 * PantryPilot — Fly.io Cron Runner
 *
 * Keeps the process alive and runs the price sync daily at 2am AEST (Sydney).
 * Fly.io Sydney region (syd) gives us an Australian IP so Woolworths + Coles
 * bot detection passes through correctly.
 */

import { main as runPriceSync } from "./price-sync.js";

const AEST_HOUR = 2;

function msUntilNext2amSydney(): number {
  const now = new Date();
  const sydney = new Date(now.toLocaleString("en-AU", { timeZone: "Australia/Sydney" }));
  const next = new Date(sydney);
  next.setHours(AEST_HOUR, 0, 0, 0);
  if (next <= sydney) next.setDate(next.getDate() + 1);
  return next.getTime() - sydney.getTime();
}

async function scheduleNext() {
  const ms = msUntilNext2amSydney();
  const hrs = (ms / 3_600_000).toFixed(1);
  console.log(`[cron] Next price sync in ${hrs}h (2am AEST)`);

  setTimeout(async () => {
    console.log("[cron] Starting scheduled price sync...");
    try {
      await runPriceSync();
      console.log("[cron] Price sync complete.");
    } catch (err) {
      console.error("[cron] Price sync failed:", err);
    }
    scheduleNext();
  }, ms);
}

console.log("[cron] PantryPilot price sync scheduler started — Sydney region");
scheduleNext();
