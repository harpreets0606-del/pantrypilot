# Klaviyo end-to-end cart-abandonment flow content deploy.
#
# What it does (single run, three phases):
#   PHASE 1 - Create global Cart E1 + Cart E2 templates if they do not exist.
#             PATCH global Cart E3 (Sq6pt2) with latest HTML.
#   PHASE 2 - PATCH RPQXaa flow-actions:
#               - 98627502 (Email 1)  -> new template_id, new subject, new preview
#               - 98628345 (Email 2)  -> new template_id, new subject, new preview
#               (Email 3 is added via UI separately)
#   PHASE 3 - Verify by GET on each action and report.
#
# Templates owned globally (we PATCH directly, idempotent):
#   - Sq6pt2  Cart Abandonment Email 3 - Last Chance (already deployed)
#   - <new>   Cart Abandonment Email 1 - You Forgot Something (this script creates if missing)
#   - <new>   Cart Abandonment Email 2 - Don't Miss Out
#
# Subject lines + preview text - locked in Plan below.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-deploy-cart-flow.ps1

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
$TempDir = Join-Path $env:TEMP "klaviyo-deploy-cart-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# Manual JSON string escaper for HTML bodies (PS 5.1 ConvertTo-Json hangs on long HTML)
function ConvertTo-JsonString([string]$s) {
    $sb = New-Object System.Text.StringBuilder
    [void]$sb.Append('"')
    foreach ($c in $s.ToCharArray()) {
        switch ($c) {
            '\' { [void]$sb.Append('\\') }
            '"' { [void]$sb.Append('\"') }
            "`b" { [void]$sb.Append('\b') }
            "`f" { [void]$sb.Append('\f') }
            "`n" { [void]$sb.Append('\n') }
            "`r" { [void]$sb.Append('\r') }
            "`t" { [void]$sb.Append('\t') }
            default {
                $i = [int]$c
                if ($i -lt 32) { [void]$sb.AppendFormat('\u{0:x4}', $i) }
                else { [void]$sb.Append($c) }
            }
        }
    }
    [void]$sb.Append('"')
    return $sb.ToString()
}

function Invoke-KlaviyoCurl {
    param([string]$Method, [string]$Url, [string]$BodyJson, [string]$RespFile, [string]$Revision = '2024-10-15')
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

# Plan: action -> (file, owned global template ID or NULL if needs create, name for new template, subject, preview, utm campaign)
$Plan = @(
    [pscustomobject]@{
        ActionId      = '98627502'
        Label         = 'E1 - Cart Abandon Email 1'
        File          = '.claude/bargain-chemist/templates/cart-abandon-email-1.html'
        OwnedTemplate = $null   # to be created
        TemplateName  = 'BC - Cart Abandonment Email 1 - You Forgot Something'
        Subject       = "{{ first_name|default:'Hey' }}, you forgot something at Bargain Chemist"
        Preview       = "Your cart's saved at NZ's lowest pharmacy prices - Price Beat 10% included."
        UtmCampaign   = 'cart_abandon_e1_2026'
    }
    [pscustomobject]@{
        ActionId      = '98628345'
        Label         = 'E2 - Cart Abandon Email 2'
        File          = '.claude/bargain-chemist/templates/cart-abandon-email-2.html'
        OwnedTemplate = $null
        TemplateName  = "BC - Cart Abandonment Email 2 - Don't Miss Out"
        Subject       = "{{ first_name|default:'Still here' }}? Your cart's waiting at NZ's lowest prices"
        Preview       = "Items selling fast - protected by Price Beat Guarantee. Free shipping over $79."
        UtmCampaign   = 'cart_abandon_e2_2026'
    }
)

# E3 is owned-global Sq6pt2, just PATCH HTML (no flow-action work in this script - E3 not in flow yet)
$E3 = [pscustomobject]@{
    OwnedTemplate = 'Sq6pt2'
    File          = '.claude/bargain-chemist/templates/cart-abandon-email-3.html'
    Label         = 'E3 - Last Chance (global, awaiting UI flow add)'
}

# ============================================================
# PHASE 1: Create / update global templates
# ============================================================
Write-Host ""
Write-Host "=== PHASE 1: Create / update global cart-abandon templates ===" -ForegroundColor Cyan

foreach ($p in $Plan) {
    Write-Host ""
    Write-Host "[$($p.Label)] " -NoNewline -ForegroundColor Cyan
    if (-not (Test-Path $p.File)) {
        Write-Host "FAIL local file missing: $($p.File)" -ForegroundColor Red
        continue
    }
    $html = Get-Content $p.File -Raw -Encoding UTF8
    Write-Host "HTML size $([math]::Round($html.Length/1KB,1)) KB" -ForegroundColor DarkGray

    $htmlJson = ConvertTo-JsonString $html
    $nameJson = ConvertTo-JsonString $p.TemplateName

    # Always create a NEW global template (idempotent in the sense that we just track the latest ID)
    $body = '{"data":{"type":"template","attributes":{"name":' + $nameJson + ',"editor_type":"CODE","html":' + $htmlJson + '}}}'

    $respFile = Join-Path $TempDir "tpl-create-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'POST' -Url 'https://a.klaviyo.com/api/templates/' -BodyJson $body -RespFile $respFile
    if ($code -in '200','201') {
        $resp = Get-Content $respFile -Raw | ConvertFrom-Json
        $tplId = $resp.data.id
        $p.OwnedTemplate = $tplId
        Write-Host "  Created global template: $tplId" -ForegroundColor Green
    } else {
        Write-Host "  Create FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
    }
}

# Phase 1b: PATCH the existing E3 global template
Write-Host ""
Write-Host "[$($E3.Label)] PATCH global template $($E3.OwnedTemplate)" -ForegroundColor Cyan
if (Test-Path $E3.File) {
    $html3 = Get-Content $E3.File -Raw -Encoding UTF8
    $htmlJson = ConvertTo-JsonString $html3
    $body3 = '{"data":{"type":"template","id":"' + $E3.OwnedTemplate + '","attributes":{"html":' + $htmlJson + '}}}'
    $respFile = Join-Path $TempDir "tpl-patch-e3.json"
    $code = Invoke-KlaviyoCurl -Method 'PATCH' -Url "https://a.klaviyo.com/api/templates/$($E3.OwnedTemplate)/" -BodyJson $body3 -RespFile $respFile
    if ($code -eq '200') { Write-Host "  PATCH OK" -ForegroundColor Green }
    else {
        Write-Host "  PATCH FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
    }
} else {
    Write-Host "  SKIP - $($E3.File) not found" -ForegroundColor Yellow
}

# Save the deployed template IDs for E1 and E2
$DeployedFile = "$OutDir/cart-flow-deployed-templates.json"
$Plan | Select-Object ActionId,Label,OwnedTemplate,TemplateName | ConvertTo-Json -Depth 5 | Out-File -FilePath $DeployedFile -Encoding utf8
Write-Host ""
Write-Host "Deployed template IDs saved to $DeployedFile" -ForegroundColor DarkGray

# ============================================================
# PHASE 2: PATCH flow-actions (subject, preview, template_id, UTMs)
# ============================================================
Write-Host ""
Write-Host "=== PHASE 2: Update flow-actions in RPQXaa ===" -ForegroundColor Cyan

foreach ($p in $Plan) {
    if (-not $p.OwnedTemplate) {
        Write-Host "[$($p.Label)] SKIP - no template ID (Phase 1 failed)" -ForegroundColor Yellow
        continue
    }
    Write-Host ""
    Write-Host "[$($p.ActionId)] $($p.Label)" -ForegroundColor Cyan

    # GET current
    $getResp = Join-Path $TempDir "fa-get-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'GET' -Url "https://a.klaviyo.com/api/flow-actions/$($p.ActionId)/" -RespFile $getResp -Revision '2025-10-15'
    if ($code -ne '200') {
        Write-Host "  GET failed HTTP $code" -ForegroundColor Red
        if (Test-Path $getResp) { Get-Content $getResp -Raw | Write-Host -ForegroundColor DarkYellow }
        continue
    }
    $current = Get-Content $getResp -Raw | ConvertFrom-Json
    $defn = $current.data.attributes.definition
    $msg  = $defn.data.message

    # Mutate: template_id, subject_line, preview_text, custom_tracking_params
    $msg.template_id  = $p.OwnedTemplate
    $msg.subject_line = $p.Subject
    $msg.preview_text = $p.Preview
    $newUtm = @(
        [ordered]@{ param='utm_source'  ; value='klaviyo' }
        [ordered]@{ param='utm_medium'  ; value='email' }
        [ordered]@{ param='utm_campaign'; value=$p.UtmCampaign }
    )
    $msg | Add-Member -NotePropertyName custom_tracking_params -NotePropertyValue $newUtm -Force
    $defn.data.message = $msg
    if ($defn.data.status -ne 'live') { $defn.data.status = 'live' }

    $defnJson  = $defn | ConvertTo-Json -Depth 30 -Compress
    $patchBody = "{`"data`":{`"type`":`"flow-action`",`"id`":`"$($p.ActionId)`",`"attributes`":{`"definition`":$defnJson}}}"

    $patchResp = Join-Path $TempDir "fa-patch-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'PATCH' -Url "https://a.klaviyo.com/api/flow-actions/$($p.ActionId)/" -BodyJson $patchBody -RespFile $patchResp -Revision '2025-10-15'

    if ($code -eq '200') {
        $after = Get-Content $patchResp -Raw | ConvertFrom-Json
        $am = $after.data.attributes.definition.data.message
        Write-Host "  PATCH OK" -ForegroundColor Green
        Write-Host "  -> template_id:  $($am.template_id) (Klaviyo cloned from $($p.OwnedTemplate))"
        Write-Host "  -> subject:      $($am.subject_line)"
        Write-Host "  -> preview:      $($am.preview_text)"
        if ($am.custom_tracking_params) {
            $am.custom_tracking_params | ForEach-Object { Write-Host "  -> $($_.param) = $($_.value)" -ForegroundColor DarkGreen }
        }
        Copy-Item $patchResp -Destination "$OutDir/cart-flow-action-$($p.ActionId)-deployed.json" -Force
    } else {
        Write-Host "  PATCH FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $patchResp) { Get-Content $patchResp -Raw | Write-Host -ForegroundColor DarkYellow }
    }
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Verify in Klaviyo: https://www.klaviyo.com/flow/RPQXaa/edit"
Write-Host ""
Write-Host "Email 3 setup (when you're ready):"
Write-Host "  1. UI: drag in Time Delay (2 days) + Send Email after Email 2"
Write-Host "  2. Assign template: BC - Cart Abandonment Email 3 - Last Chance (Sq6pt2)"
Write-Host "  3. Set subject:    Last chance, {{ first_name|default:'there' }} - your cart is expiring"
Write-Host "  4. Set preview:    Don't let NZ's best pharmacy prices slip away. Free shipping over $79."

Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
