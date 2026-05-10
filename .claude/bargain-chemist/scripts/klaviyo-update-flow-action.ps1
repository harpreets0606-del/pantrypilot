# Update flow-action via PATCH /api/flow-actions/{id} (revision 2025-10-15).
# This is the WORKING endpoint for updating flow message content -
# bypasses the broken PATCH /api/templates/{cloned_id} bug entirely.
#
# Strategy:
#   1. GET current flow-action definition (whole opaque blob)
#   2. Mutate the message fields (template_id, subject_line, preview_text)
#   3. PATCH back the modified definition
#
# Per Klaviyo Python SDK source (FlowActionUpdateQueryResourceObjectAttributes):
#   body = {
#     "data": {
#       "type": "flow-action",
#       "id": "<action_id>",
#       "attributes": { "definition": {...the entire action definition...} }
#     }
#   }
#
# Param: -Mode allows two strategies:
#   "swap-to-global"  -> repoint each action's message.template_id to our owned templates
#                        (RjiNUy/SuHDNq/UPxjA8). Then we can iterate via /api/templates PATCH.
#   "verify"          -> just dump current action state for inspection (no writes)

param(
    [ValidateSet('swap-to-global','verify')]
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
$TempDir = Join-Path $env:TEMP "klaviyo-fa-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# Flow action IDs from YdejKf-with-full-definition.json
# Mapping: flow-action ID -> (label, our owned global template ID)
$Actions = @(
    [pscustomobject]@{ ActionId='105917207'; Label='E1 - Welcome';      OwnedTemplate='RjiNUy' },
    [pscustomobject]@{ ActionId='105917209'; Label='E2 - Best Sellers'; OwnedTemplate='SuHDNq' },
    [pscustomobject]@{ ActionId='105917211'; Label='E3 - Last Nudge';   OwnedTemplate='UPxjA8' }
)

function Invoke-KlaviyoCurl {
    param([string]$Method, [string]$Url, [string]$BodyJson, [string]$RespFile)
    $headers = @(
        '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
        '-H', 'revision: 2025-10-15',
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

Write-Host ""
Write-Host "=== Mode: $Mode ===" -ForegroundColor Cyan

foreach ($a in $Actions) {
    Write-Host ""
    Write-Host "[$($a.ActionId)] $($a.Label)" -ForegroundColor Cyan

    # Step 1: GET current action
    $getResp = Join-Path $TempDir "get-$($a.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'GET' -Url "https://a.klaviyo.com/api/flow-actions/$($a.ActionId)/" -RespFile $getResp
    if ($code -ne '200') {
        Write-Host "  GET failed HTTP $code" -ForegroundColor Red
        if (Test-Path $getResp) { Get-Content $getResp -Raw | Write-Host -ForegroundColor DarkYellow }
        continue
    }
    $current = Get-Content $getResp -Raw | ConvertFrom-Json
    Copy-Item $getResp -Destination "$OutDir/flow-action-$($a.ActionId)-before.json" -Force

    $defn = $current.data.attributes.definition
    if (-not $defn) {
        Write-Host "  WARN: no definition in GET response" -ForegroundColor Yellow
        continue
    }
    $msg = $defn.data.message
    Write-Host "  current template_id: $($msg.template_id)"
    Write-Host "  current subject:     $($msg.subject_line)"

    if ($Mode -eq 'verify') {
        Write-Host "  (verify mode - no PATCH)" -ForegroundColor DarkGray
        continue
    }

    # Step 2: Mutate the definition
    $msg.template_id = $a.OwnedTemplate
    Write-Host "  -> setting template_id to OUR owned template: $($a.OwnedTemplate)" -ForegroundColor Yellow

    # Step 3: Build PATCH body
    $defnJson = $defn | ConvertTo-Json -Depth 30 -Compress
    $patchBody = "{`"data`":{`"type`":`"flow-action`",`"id`":`"$($a.ActionId)`",`"attributes`":{`"definition`":$defnJson}}}"

    # Save the patch body for debugging
    $patchBody | Out-File -FilePath "$OutDir/flow-action-$($a.ActionId)-patch-body.json" -Encoding utf8

    $patchResp = Join-Path $TempDir "patch-$($a.ActionId).json"
    $code = Invoke-KlaviyoCurl -Method 'PATCH' -Url "https://a.klaviyo.com/api/flow-actions/$($a.ActionId)/" -BodyJson $patchBody -RespFile $patchResp

    if ($code -eq '200') {
        Write-Host "  OK PATCH 200" -ForegroundColor Green
        Copy-Item $patchResp -Destination "$OutDir/flow-action-$($a.ActionId)-after.json" -Force
        $after = Get-Content $patchResp -Raw | ConvertFrom-Json
        $newTpl = $after.data.attributes.definition.data.message.template_id
        Write-Host "  new template_id (post-PATCH): $newTpl" -ForegroundColor $(if ($newTpl -eq $a.OwnedTemplate) {'Green'} else {'Yellow'})
        if ($newTpl -ne $a.OwnedTemplate) {
            Write-Host "  WARN: Klaviyo re-cloned the template (new ID)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  FAIL HTTP $code" -ForegroundColor Red
        if (Test-Path $patchResp) {
            $errBody = Get-Content $patchResp -Raw
            $errFile = "$OutDir/flow-action-$($a.ActionId)-error.json"
            $errBody | Out-File -FilePath $errFile -Encoding utf8
            Write-Host $errBody -ForegroundColor DarkYellow
        }
    }
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
