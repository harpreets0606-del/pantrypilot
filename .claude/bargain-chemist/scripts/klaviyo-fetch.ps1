# Klaviyo deep-fetch — PowerShell version
# Pulls flow structures, flow messages, and templates the MCP cannot access.
# Output saved as JSON files in .claude/bargain-chemist/snapshots/<date>/
#
# Usage (from repo root):
#   1. Ensure .env.local has:  KLAVIYO_PRIVATE_KEY=<your_full_scope_key>
#   2. Run:  .\.claude\bargain-chemist\scripts\klaviyo-fetch.ps1
#   3. Review output, then:  git add .claude/bargain-chemist/snapshots/ ; git commit -m "Klaviyo snapshot" ; git push

$ErrorActionPreference = 'Continue'

# Load .env.local
if (-not (Test-Path .env.local)) {
    Write-Error "ERROR: .env.local not found at repo root. Create it with: KLAVIYO_PRIVATE_KEY=<key>"
    exit 1
}
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}
if (-not $env:KLAVIYO_PRIVATE_KEY) {
    Write-Error "ERROR: KLAVIYO_PRIVATE_KEY not set in .env.local"
    exit 1
}

$Revision = '2024-10-15'
$Date = Get-Date -Format 'yyyy-MM-dd'
$Out = ".claude/bargain-chemist/snapshots/$Date"
foreach ($sub in 'flows','flow-messages','templates','lists','segments','forms') {
    New-Item -ItemType Directory -Force -Path "$Out/$sub" | Out-Null
}

$Headers = @{
    'Authorization' = "Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
    'revision'      = $Revision
    'Accept'        = 'application/vnd.api+json'
}

function Fetch {
    param(
        [string]$Label,
        [string]$Url,
        [string]$OutFile
    )
    try {
        $resp = Invoke-WebRequest -Uri $Url -Headers $Headers -Method Get -ErrorAction Stop
        $resp.Content | Out-File -FilePath $OutFile -Encoding utf8
        Write-Host "  OK  $Label  ->  $OutFile" -ForegroundColor Green
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        $body = ''
        if ($_.Exception.Response) {
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($stream)
                $body = $reader.ReadToEnd()
            } catch {}
        }
        Write-Host "  FAIL $Label  HTTP $code" -ForegroundColor Red
        if ($body) {
            $body | Out-File -FilePath "$OutFile.error" -Encoding utf8
            Write-Host "       Error body saved to $OutFile.error" -ForegroundColor DarkYellow
        }
    }
}

Write-Host ""
Write-Host "=== Phase 1: Priority flows (structure + messages + templates) ===" -ForegroundColor Cyan

Write-Host ""
Write-Host "[1/4] Welcome Series Website (SehWRt) - DRAFT but receiving recipients"
Fetch "Flow structure"     "https://a.klaviyo.com/api/flows/SehWRt/?include=flow-actions" "$Out/flows/SehWRt-welcome-website.json"
Fetch "Email 1 (U2HQmW)"   "https://a.klaviyo.com/api/flow-messages/U2HQmW/?include=template" "$Out/flow-messages/U2HQmW-welcome-email1.json"
Fetch "Email 2 (QYfRCd)"   "https://a.klaviyo.com/api/flow-messages/QYfRCd/?include=template" "$Out/flow-messages/QYfRCd-welcome-email2.json"
Fetch "Email 6 (VJwtx3)"   "https://a.klaviyo.com/api/flow-messages/VJwtx3/?include=template" "$Out/flow-messages/VJwtx3-welcome-email6.json"

Write-Host ""
Write-Host "[2/4] Welcome Series No Coupon (TsC8GZ) - LIVE"
Fetch "Flow structure"     "https://a.klaviyo.com/api/flows/TsC8GZ/?include=flow-actions" "$Out/flows/TsC8GZ-welcome-nocoupon.json"
Fetch "Email 1 (UC2XAR)"   "https://a.klaviyo.com/api/flow-messages/UC2XAR/?include=template" "$Out/flow-messages/UC2XAR-welcome-nocoupon-email1.json"

Write-Host ""
Write-Host "[3/4] Order Confirmation (VJui9n) - DRAFT 0% conversion"
Fetch "Flow structure"     "https://a.klaviyo.com/api/flows/VJui9n/?include=flow-actions" "$Out/flows/VJui9n-order-confirmation.json"
Fetch "Post-Purchase Email 1 (XJENuf)" "https://a.klaviyo.com/api/flow-messages/XJENuf/?include=template" "$Out/flow-messages/XJENuf-order-confirm-email1.json"

Write-Host ""
Write-Host "[4/4] Cart Abandonment (RPQXaa) - LIVE best performer"
Fetch "Flow structure"     "https://a.klaviyo.com/api/flows/RPQXaa/?include=flow-actions" "$Out/flows/RPQXaa-cart-abandon.json"
Fetch "Email 1 (TCgQED)"   "https://a.klaviyo.com/api/flow-messages/TCgQED/?include=template" "$Out/flow-messages/TCgQED-cart-email1.json"
Fetch "Email 2 (TpkzDd)"   "https://a.klaviyo.com/api/flow-messages/TpkzDd/?include=template" "$Out/flow-messages/TpkzDd-cart-email2.json"

Write-Host ""
Write-Host "=== Phase 2: Sample templates (visual baseline) ===" -ForegroundColor Cyan
Fetch "Fragrance Clearance template (TK24Zf)" "https://a.klaviyo.com/api/templates/TK24Zf/" "$Out/templates/TK24Zf-fragrance-clearance.json"
Fetch "Trilogy Solus template (VLUx6Y)"        "https://a.klaviyo.com/api/templates/VLUx6Y/" "$Out/templates/VLUx6Y-trilogy-solus.json"
Fetch "Codral Solus template (SYRWve)"         "https://a.klaviyo.com/api/templates/SYRWve/" "$Out/templates/SYRWve-codral-solus.json"

Write-Host ""
Write-Host "=== Phase 3: Audit gap fills ===" -ForegroundColor Cyan
Fetch "Lists with profile counts"     "https://a.klaviyo.com/api/lists/?additional-fields%5Blist%5D=profile_count" "$Out/lists/all-lists-with-counts.json"
Fetch "Segments with profile counts"  "https://a.klaviyo.com/api/segments/?additional-fields%5Bsegment%5D=profile_count&page%5Bsize%5D=100" "$Out/segments/all-segments-with-counts.json"
Fetch "Forms"                          "https://a.klaviyo.com/api/forms/?page%5Bsize%5D=50" "$Out/forms/all-forms.json"
Fetch "Sample profile (predictive)"    "https://a.klaviyo.com/api/profiles/?additional-fields%5Bprofile%5D=predictive_analytics&page%5Bsize%5D=1" "$Out/sample-profile-predictive.json"

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "Snapshot directory: $Out"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  git add $Out"
Write-Host "  git commit -m 'Klaviyo snapshot $Date'"
Write-Host "  git push"
Write-Host ""
Write-Host "If any FAILs above, paste the .error file contents to Claude."

Remove-Item env:KLAVIYO_PRIVATE_KEY
