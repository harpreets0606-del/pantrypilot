# Klaviyo end-to-end content deploy - updates flow YdejKf email HTML via API.
#
# Workflow:
#   1. PATCH each owned global template (RjiNUy/SuHDNq/UPxjA8) with the latest local HTML
#   2. PATCH each flow-action to re-assign the template (Klaviyo clones again,
#      picking up the just-updated HTML)
#   3. Verify the new clone IDs and report
#
# This is the WORKING end-to-end path discovered after deep API research:
#   - PATCH /api/templates/{owned_id}     (we own these, PATCH works)
#   - PATCH /api/flow-actions/{id}        (revision 2025-10-15, GA endpoint)
#
# Why this works: cloned-on-assign is fixed Klaviyo behaviour. By updating our
# global template FIRST, then re-assigning, the new clone reflects the latest HTML.
#
# Usage (from repo root):
#   .\.claude\bargain-chemist\scripts\klaviyo-deploy-content.ps1

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
$TempDir = Join-Path $env:TEMP "klaviyo-deploy-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# Manual JSON string escaper - avoids PS 5.1 ConvertTo-Json hang
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

# Mapping: flow-action ID -> (label, owned global template ID, local HTML file)
$Plan = @(
    [pscustomobject]@{ ActionId='105917207'; Label='E1 - Welcome';      OwnedTemplate='RjiNUy'; LocalFile='.claude/bargain-chemist/templates/welcome-email-1.html' }
    [pscustomobject]@{ ActionId='105917209'; Label='E2 - Best Sellers'; OwnedTemplate='SuHDNq'; LocalFile='.claude/bargain-chemist/templates/welcome-email-2.html' }
    [pscustomobject]@{ ActionId='105917211'; Label='E3 - Last Nudge';   OwnedTemplate='UPxjA8'; LocalFile='.claude/bargain-chemist/templates/welcome-email-3.html' }
)

Write-Host ""
Write-Host "=== Phase 1: Update global templates with latest local HTML ===" -ForegroundColor Cyan

foreach ($p in $Plan) {
    Write-Host ""
    Write-Host "[$($p.OwnedTemplate)] Update global template ($($p.Label))" -ForegroundColor Cyan
    if (-not (Test-Path $p.LocalFile)) {
        Write-Host "  FAIL local file not found: $($p.LocalFile)" -ForegroundColor Red
        continue
    }
    $html = Get-Content $p.LocalFile -Raw -Encoding UTF8
    Write-Host "  HTML: $([math]::Round($html.Length/1KB,1)) KB" -ForegroundColor DarkGray

    $htmlJson = ConvertTo-JsonString $html
    $body = '{"data":{"type":"template","id":"' + $p.OwnedTemplate + '","attributes":{"html":' + $htmlJson + '}}}'

    $respFile = Join-Path $TempDir "tpl-patch-$($p.OwnedTemplate).json"
    $code = Invoke-KlaviyoCurl -Method 'PATCH' -Url "https://a.klaviyo.com/api/templates/$($p.OwnedTemplate)/" -BodyJson $body -RespFile $respFile

    if ($code -eq '200') {
        Write-Host "  OK PATCH 200" -ForegroundColor Green
    } else {
        Write-Host "  FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
    }
}

Write-Host ""
Write-Host "=== Phase 2: Re-assign templates to flow-actions (forces fresh clones) ===" -ForegroundColor Cyan

foreach ($p in $Plan) {
    Write-Host ""
    Write-Host "[$($p.ActionId)] Re-assign $($p.Label) to template $($p.OwnedTemplate)" -ForegroundColor Cyan

    # GET current action
    $getResp = Join-Path $TempDir "fa-get-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'GET' -Url "https://a.klaviyo.com/api/flow-actions/$($p.ActionId)/" -RespFile $getResp -Revision '2025-10-15'
    if ($code -ne '200') {
        Write-Host "  GET failed HTTP $code" -ForegroundColor Red
        if (Test-Path $getResp) { Get-Content $getResp -Raw | Write-Host -ForegroundColor DarkYellow }
        continue
    }
    $current = Get-Content $getResp -Raw | ConvertFrom-Json
    $defn = $current.data.attributes.definition
    $oldTpl = $defn.data.message.template_id
    Write-Host "  current template_id: $oldTpl" -ForegroundColor DarkGray
    $defn.data.message.template_id = $p.OwnedTemplate

    $defnJson  = $defn | ConvertTo-Json -Depth 30 -Compress
    $patchBody = "{`"data`":{`"type`":`"flow-action`",`"id`":`"$($p.ActionId)`",`"attributes`":{`"definition`":$defnJson}}}"

    $patchResp = Join-Path $TempDir "fa-patch-$($p.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'PATCH' -Url "https://a.klaviyo.com/api/flow-actions/$($p.ActionId)/" -BodyJson $patchBody -RespFile $patchResp -Revision '2025-10-15'

    if ($code -eq '200') {
        $after = Get-Content $patchResp -Raw | ConvertFrom-Json
        $newTpl = $after.data.attributes.definition.data.message.template_id
        Write-Host "  OK reassigned. Live template_id is now: $newTpl" -ForegroundColor Green
        Copy-Item $patchResp -Destination "$OutDir/flow-action-$($p.ActionId)-deployed.json" -Force
    } else {
        Write-Host "  FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $patchResp) {
            $errBody = Get-Content $patchResp -Raw
            Write-Host $errBody -ForegroundColor DarkYellow
        }
    }
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "Verify at: https://www.klaviyo.com/flow/YdejKf/edit"
Write-Host ""
Write-Host "From now on, to update content:"
Write-Host "  1. Edit .claude/bargain-chemist/templates/welcome-email-X.html"
Write-Host "  2. Run this script. That's it."

Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
