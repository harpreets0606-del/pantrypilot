#!/usr/bin/env bash
# Klaviyo deep-fetch script — pulls flow structures, flow messages, and templates
# that the MCP cannot access. Output saved as JSON files in snapshots/<date>/.
#
# Usage:
#   1. Ensure .env.local has KLAVIYO_PRIVATE_KEY=<your_full_scope_key>
#   2. From repo root:  bash .claude/bargain-chemist/scripts/klaviyo-fetch.sh
#   3. Commit the snapshot directory + push.
#
# Requires: curl, jq, bash 4+
set -euo pipefail

# Load env
if [ -f .env.local ]; then
  set -a; source .env.local; set +a
fi
if [ -z "${KLAVIYO_PRIVATE_KEY:-}" ]; then
  echo "ERROR: KLAVIYO_PRIVATE_KEY not set in .env.local" >&2
  exit 1
fi

REVISION="2024-10-15"
DATE=$(date +%Y-%m-%d)
OUT=".claude/bargain-chemist/snapshots/$DATE"
mkdir -p "$OUT/flows" "$OUT/flow-messages" "$OUT/templates" "$OUT/lists" "$OUT/segments" "$OUT/forms"

# Helper — runs a GET, saves response, prints status
fetch() {
  local label="$1"
  local url="$2"
  local outfile="$3"
  local code
  code=$(curl -sS -o "$outfile" -w "%{http_code}" \
    -H "Authorization: Klaviyo-API-Key $KLAVIYO_PRIVATE_KEY" \
    -H "revision: $REVISION" \
    -H "Accept: application/vnd.api+json" \
    "$url")
  if [ "$code" = "200" ]; then
    echo "  ✓ $label  →  $outfile"
  else
    echo "  ✗ $label  HTTP $code  →  $outfile (check body for error)"
  fi
}

echo ""
echo "=== Phase 1: Priority flows (with structure + messages + templates) ==="
echo ""

# --- Welcome Series Website (TOP PRIORITY) ---
echo "[1/4] Welcome Series Website (SehWRt) — DRAFT but receiving recipients"
fetch "Flow structure"      "https://a.klaviyo.com/api/flows/SehWRt/?include=flow-actions" "$OUT/flows/SehWRt-welcome-website.json"
# Known message IDs from earlier reports
fetch "Email 1 (U2HQmW)"    "https://a.klaviyo.com/api/flow-messages/U2HQmW/?include=template" "$OUT/flow-messages/U2HQmW-welcome-email1.json"
fetch "Email 2 (QYfRCd)"    "https://a.klaviyo.com/api/flow-messages/QYfRCd/?include=template" "$OUT/flow-messages/QYfRCd-welcome-email2.json"
fetch "Email 6 (VJwtx3)"    "https://a.klaviyo.com/api/flow-messages/VJwtx3/?include=template" "$OUT/flow-messages/VJwtx3-welcome-email6.json"

echo ""
echo "[2/4] Welcome Series No Coupon (TsC8GZ) — LIVE"
fetch "Flow structure"      "https://a.klaviyo.com/api/flows/TsC8GZ/?include=flow-actions" "$OUT/flows/TsC8GZ-welcome-nocoupon.json"
fetch "Email 1 (UC2XAR)"    "https://a.klaviyo.com/api/flow-messages/UC2XAR/?include=template" "$OUT/flow-messages/UC2XAR-welcome-nocoupon-email1.json"

echo ""
echo "[3/4] Order Confirmation (VJui9n) — DRAFT 0% conversion"
fetch "Flow structure"      "https://a.klaviyo.com/api/flows/VJui9n/?include=flow-actions" "$OUT/flows/VJui9n-order-confirmation.json"
fetch "Post-Purchase Email 1 (XJENuf)" "https://a.klaviyo.com/api/flow-messages/XJENuf/?include=template" "$OUT/flow-messages/XJENuf-order-confirm-email1.json"

echo ""
echo "[4/4] Cart Abandonment (RPQXaa) — LIVE best performer"
fetch "Flow structure"      "https://a.klaviyo.com/api/flows/RPQXaa/?include=flow-actions" "$OUT/flows/RPQXaa-cart-abandon.json"
fetch "Email 1 (TCgQED)"    "https://a.klaviyo.com/api/flow-messages/TCgQED/?include=template" "$OUT/flow-messages/TCgQED-cart-email1.json"
fetch "Email 2 (TpkzDd)"    "https://a.klaviyo.com/api/flow-messages/TpkzDd/?include=template" "$OUT/flow-messages/TpkzDd-cart-email2.json"

echo ""
echo "=== Phase 2: Sample template (visual baseline) ==="
fetch "Fragrance Clearance template (TK24Zf)" "https://a.klaviyo.com/api/templates/TK24Zf/" "$OUT/templates/TK24Zf-fragrance-clearance.json"
fetch "Trilogy Solus template (VLUx6Y)"        "https://a.klaviyo.com/api/templates/VLUx6Y/"  "$OUT/templates/VLUx6Y-trilogy-solus.json"
fetch "Codral Solus template (SYRWve)"         "https://a.klaviyo.com/api/templates/SYRWve/"  "$OUT/templates/SYRWve-codral-solus.json"

echo ""
echo "=== Phase 3: Audit gap fills ==="
fetch "Lists with profile counts"     "https://a.klaviyo.com/api/lists/?additional-fields%5Blist%5D=profile_count" "$OUT/lists/all-lists-with-counts.json"
fetch "Segments with profile counts"  "https://a.klaviyo.com/api/segments/?additional-fields%5Bsegment%5D=profile_count&page%5Bsize%5D=100" "$OUT/segments/all-segments-with-counts.json"
fetch "Forms"                          "https://a.klaviyo.com/api/forms/?page%5Bsize%5D=50" "$OUT/forms/all-forms.json"
fetch "Sample profile (predictive)"    "https://a.klaviyo.com/api/profiles/?additional-fields%5Bprofile%5D=predictive_analytics&page%5Bsize%5D=1" "$OUT/sample-profile-predictive.json"

echo ""
echo "=== DONE ==="
echo "Snapshot saved to: $OUT"
echo ""
echo "Next steps:"
echo "  1. Quick sanity check: cat $OUT/flows/SehWRt-welcome-website.json | jq '.data.attributes.name'"
echo "  2. If everything looks OK:"
echo "       git add $OUT"
echo "       git commit -m 'Klaviyo snapshot $DATE'"
echo "       git push"
echo "  3. Tell Claude: 'snapshot pushed' — Claude will read and analyse."
