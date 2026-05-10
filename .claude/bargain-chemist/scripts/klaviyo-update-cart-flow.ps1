# Klaviyo: conservative updates to RPQXaa cart-abandonment flow (Phase 1).
#
# Changes (low risk, terminal-only):
#   1. Verify Email 2 status is now live (post user-toggle)
#   2. Set proper custom_tracking_params on Email 1 and Email 2
#      (utm_source=klaviyo, utm_medium=email, utm_campaign=cart_abandon_eN_2026)
#      - Fixes Shopify attribution (currently uses Klaviyo's default {flow_name})
#
# NOT in this script (intentionally) - these need separate decisions:
#   - Subject line / preview-text changes (recommend A/B test first, not a blind swap)
#   - CheckoutURL button injection (requires new Family B global templates first)
#   - Email 3 addition (requires UI work - Klaviyo API can't add new actions)
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-update-cart-flow.ps1 -Mode verify
#   .\.claude\bargain-chemist\scripts\klaviyo-update-cart-flow.ps1 -Mode apply

param(
    [ValidateSet('verify','apply')]
    [string]$Mode = 'verify'
)

$ErrorActionPreference = 'Continue'

$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if (-not $curl) { Write-Error 'curl.exe not found'; exit 1 }

if (-not (Test-Path .env.local)) { Write-Error 'ERROR: .env.local not found'; exit 1 }
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}
if (-not $env:KLAVIYO_PRIVATE_KEY) { Write-Error 'ERROR: KLAVIYO_PRIVATE_KEY not set'; exit 1 }

$Date    = Get-Date -Format 'yyyy-MM-dd'
$OutDir  = ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$TempDir = Join-Path $env:TEMP "klaviyo-cart-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

function Invoke-KlaviyoCurl {
    param([string]$Method, [string]$Url, [string]$BodyJson, [string]$RespFile, [string]$Revision = '2025-10-15')
    $headers = @(
        '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
        '-H', "revision: $Revision",
        '-H', 'Accept: application/vnd.api+json'
    )
    $extra = @()
    if ($BodyJson) {
        $bodyFile = Join-Path $TempDir "body-$([guid]::NewGuid().ToString('N').Substring(0,6)).json"
        [System.IO.File]::WriteAllText($bodyFile, $BodyJson, [System.Text.UTF8Encoding]::new($false))
        $extra = @('-H', 'Content-Type: application/vnd.api+json', '--data-binary', "@$bodyFile")
    }
    $args = @('--silent','--show-error','--max-time','60','--write-out','%{http_code}','--output',$RespFile,'-X',$Method) + $headers + $extra + @($Url)
    return (& curl.exe @args)
}

# Plan: action ID -> (label, utm_campaign value)
$Plan = @(
    [pscustomobject]@{ ActionId='98627502'; Label='E1 - Cart Abandon Email 1'; UtmCampaign='cart_abandon_e1_2026' }
    [pscustomobject]@{ ActionId='98628345'; Label='E2 - Cart Abandon Email 2'; UtmCampaign='cart_abandon_e2_2026' }
)

Write-Host ""
Write-Host "=== Mode: $Mode ===" -ForegroundColor Cyan

foreach ($p in $Plan) {
    Write-Host ""
    Write-Host "[$($p.ActionId)] $($p.Label)" -ForegroundColor Cyan

    # GET current
    $getResp = Join-Path $TempDir "get-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'GET' -Url "https://a.klaviyo.com/api/flow-actions/$($p.ActionId)/" -RespFile $getResp
    if ($code -ne '200') {
        Write-Host "  GET failed HTTP $code" -ForegroundColor Red
        if (Test-Path $getResp) { Get-Content $getResp -Raw | Write-Host -ForegroundColor DarkYellow }
        continue
    }
    $current = Get-Content $getResp -Raw | ConvertFrom-Json
    $defn = $current.data.attributes.definition
    $msg  = $defn.data.message

    Write-Host "  current data.status:           $($defn.data.status)"
    Write-Host "  current subject_line:          $($msg.subject_line)"
    Write-Host "  current add_tracking_params:   $($msg.add_tracking_params)"
    if ($msg.custom_tracking_params) {
        Write-Host "  current custom_tracking_params:" -ForegroundColor DarkGray
        $msg.custom_tracking_params | ForEach-Object { Write-Host "    - $($_.param) = $($_.value)" -ForegroundColor DarkGray }
    } else {
        Write-Host "  current custom_tracking_params: NONE (using Klaviyo defaults - bad for Shopify attribution)" -ForegroundColor Yellow
    }

    if ($Mode -eq 'verify') { continue }

    # PATCH: set custom_tracking_params (and confirm status:live for safety)
    # UtmParam schema: { param: '<utm_key>', value: '<static_value>' }
    # Verified via 400 error from Klaviyo API on 2026-05-07
    $newUtm = @(
        [ordered]@{ param='utm_source';   value='klaviyo' }
        [ordered]@{ param='utm_medium';   value='email' }
        [ordered]@{ param='utm_campaign'; value=$p.UtmCampaign }
    )
    $msg | Add-Member -NotePropertyName custom_tracking_params -NotePropertyValue $newUtm -Force
    $defn.data.message = $msg

    # Always force status to live (in case still draft after user toggle)
    if ($defn.data.status -ne 'live') {
        Write-Host "  -> bumping data.status from '$($defn.data.status)' to 'live'" -ForegroundColor Yellow
        $defn.data.status = 'live'
    }

    $defnJson  = $defn | ConvertTo-Json -Depth 30 -Compress
    $patchBody = "{`"data`":{`"type`":`"flow-action`",`"id`":`"$($p.ActionId)`",`"attributes`":{`"definition`":$defnJson}}}"

    $patchResp = Join-Path $TempDir "patch-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'PATCH' -Url "https://a.klaviyo.com/api/flow-actions/$($p.ActionId)/" -BodyJson $patchBody -RespFile $patchResp

    if ($code -eq '200') {
        $after = Get-Content $patchResp -Raw | ConvertFrom-Json
        $am = $after.data.attributes.definition.data.message
        Write-Host "  OK PATCH 200" -ForegroundColor Green
        Write-Host "  -> data.status:                $($after.data.attributes.definition.data.status)"
        if ($am.custom_tracking_params) {
            Write-Host "  -> custom_tracking_params:" -ForegroundColor Green
            $am.custom_tracking_params | ForEach-Object { Write-Host "    - $($_.param) = $($_.value)" -ForegroundColor Green }
        }
        Copy-Item $patchResp -Destination "$OutDir/cart-flow-action-$($p.ActionId)-after.json" -Force
    } else {
        Write-Host "  FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $patchResp) { Get-Content $patchResp -Raw | Write-Host -ForegroundColor DarkYellow }
    }
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Verify in Klaviyo: https://www.klaviyo.com/flow/RPQXaa/edit"
Write-Host ""
Write-Host "Phase 2 (when you're ready):"
Write-Host "  - Add Email 3 (UI: drag in delay + send-email after Email 2)"
Write-Host "  - Migrate to Family B templates with CheckoutURL button"
Write-Host "  - A/B test Email 1 subject line"

Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
