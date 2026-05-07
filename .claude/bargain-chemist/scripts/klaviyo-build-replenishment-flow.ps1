# Build the new Replenishment V2 flow via the Klaviyo Create-Flow beta API
# (POST /api/flows, revision: 2024-10-15.pre).
#
# Architecture:
#   Trigger: Ordered Product (UWP7cZ), no trigger filter
#   Action 1 (entry): conditional-split - did the trigger event include a
#     restricted product (_pharmacy-only, _pharmacist-only, _prescription)
#     in its Categories list? If YES, exit. If NO, continue to category
#     routing.
#   Then 5 sequential conditional-splits: Vitamins -> Skincare -> Hair
#   Care -> Oral Care -> Baby & Family. First match wins.
#   Universal fallback after Baby Care NO branch.
#
# All emails created in DRAFT status. Flow created with default status
# (manual). User smoke tests in UI, then flips emails to live and the flow
# overall to live.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-build-replenishment-flow.ps1

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

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
$IdsFile = ".claude/bargain-chemist/snapshots/$Date/replenishment-template-ids.json"
if (-not (Test-Path $IdsFile)) { Write-Error "Template IDs not found: $IdsFile - run klaviyo-deploy-replenishment-templates.ps1 first"; exit 1 }
$Ids = Get-Content $IdsFile -Raw | ConvertFrom-Json

# Resolve template IDs via Where-Object - avoids PS5.1 hashtable coercion quirk
function Get-TplId([string]$key) {
    $row = $Ids | Where-Object { $_.Key -eq $key } | Select-Object -First 1
    if (-not $row) { Write-Error "Missing template ID for: $key"; exit 1 }
    if ([string]::IsNullOrWhiteSpace($row.TemplateId)) { Write-Error "Empty TemplateId for key: $key"; exit 1 }
    return $row.TemplateId
}
$tplVitamins = Get-TplId 'vitamins'
$tplSkincare = Get-TplId 'skincare'
$tplHaircare = Get-TplId 'haircare'
$tplOralcare = Get-TplId 'oralcare'
$tplBabycare = Get-TplId 'babycare'
$tplFallback = Get-TplId 'fallback'
Write-Host '  Loaded template IDs:' -ForegroundColor DarkGray
Write-Host ("    vitamins  -> {0}" -f $tplVitamins) -ForegroundColor DarkGray
Write-Host ("    skincare  -> {0}" -f $tplSkincare) -ForegroundColor DarkGray
Write-Host ("    haircare  -> {0}" -f $tplHaircare) -ForegroundColor DarkGray
Write-Host ("    oralcare  -> {0}" -f $tplOralcare) -ForegroundColor DarkGray
Write-Host ("    babycare  -> {0}" -f $tplBabycare) -ForegroundColor DarkGray
Write-Host ("    fallback  -> {0}" -f $tplFallback) -ForegroundColor DarkGray

$AuthHeader = "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
$MetricId   = 'UWP7cZ'   # Ordered Product

# Helper to build a category conditional-split (checks Categories contains "CAT=...")
function New-CategorySplit {
    param([string]$tempId, [string]$catTag, [string]$nextTrue, [string]$nextFalse)
    return @{
        temporary_id = $tempId
        type         = 'conditional-split'
        data         = @{
            profile_filter = @{
                condition_groups = @(@{
                    conditions = @(@{
                        type             = 'profile-metric'
                        metric_id        = $MetricId
                        measurement      = 'count'
                        measurement_filter = @{ type = 'numeric'; operator = 'greater-than'; value = 0 }
                        timeframe_filter   = @{ type = 'date'; operator = 'flow-start' }
                        metric_filters     = @(@{
                            property = 'Categories'
                            filter   = @{ type = 'string'; operator = 'contains'; value = $catTag }
                        })
                    })
                })
            }
        }
        links = @{ next_if_true = $nextTrue; next_if_false = $nextFalse }
    }
}

# Helper to build a "restricted product" exit split (exits if customer's order has any restricted item)
function New-RestrictedSplit {
    param([string]$tempId, [string]$nextFalse)
    return @{
        temporary_id = $tempId
        type         = 'conditional-split'
        data         = @{
            profile_filter = @{
                condition_groups = @(
                    @{ conditions = @(@{
                        type             = 'profile-metric'
                        metric_id        = $MetricId
                        measurement      = 'count'
                        measurement_filter = @{ type = 'numeric'; operator = 'greater-than'; value = 0 }
                        timeframe_filter   = @{ type = 'date'; operator = 'flow-start' }
                        metric_filters     = @(@{
                            property = 'Categories'
                            filter   = @{ type = 'string'; operator = 'contains'; value = '_pharmacy-only' }
                        })
                    })},
                    @{ conditions = @(@{
                        type             = 'profile-metric'
                        metric_id        = $MetricId
                        measurement      = 'count'
                        measurement_filter = @{ type = 'numeric'; operator = 'greater-than'; value = 0 }
                        timeframe_filter   = @{ type = 'date'; operator = 'flow-start' }
                        metric_filters     = @(@{
                            property = 'Categories'
                            filter   = @{ type = 'string'; operator = 'contains'; value = '_pharmacist-only' }
                        })
                    })},
                    @{ conditions = @(@{
                        type             = 'profile-metric'
                        metric_id        = $MetricId
                        measurement      = 'count'
                        measurement_filter = @{ type = 'numeric'; operator = 'greater-than'; value = 0 }
                        timeframe_filter   = @{ type = 'date'; operator = 'flow-start' }
                        metric_filters     = @(@{
                            property = 'Categories'
                            filter   = @{ type = 'string'; operator = 'contains'; value = '_prescription' }
                        })
                    })}
                )
            }
        }
        # Klaviyo OR-conjuncts when condition_groups has multiple groups - any match = TRUE
        # If ANY restricted is present -> exit (next_if_true=null), else proceed
        links = @{ next_if_true = $null; next_if_false = $nextFalse }
    }
}

# Helper: time-delay action (days only, with all weekdays)
function New-DayDelay {
    param([string]$tempId, [int]$days, [string]$nextId)
    return @{
        temporary_id = $tempId
        type         = 'time-delay'
        data         = @{
            unit                  = 'days'
            value                 = $days
            secondary_value       = $null
            timezone              = 'profile'
            delay_until_weekdays  = @('monday','tuesday','wednesday','thursday','friday','saturday','sunday')
        }
        links = @{ next = $nextId }
    }
}

# Helper: send-email action
function New-Email {
    param(
        [string]$tempId, [string]$tplId, [string]$messageName,
        [string]$subject, [string]$preview, [string]$utmContent
    )
    return @{
        temporary_id = $tempId
        type         = 'send-email'
        data         = @{
            message = @{
                name                  = $messageName
                from_email            = 'hello@bargainchemist.co.nz'
                from_label            = 'Bargain Chemist'
                reply_to_email        = 'orders@bargainchemist.co.nz'
                cc_email              = $null
                bcc_email             = $null
                subject_line          = $subject
                preview_text          = $preview
                template_id           = $tplId
                smart_sending_enabled = $true
                transactional         = $false
                add_tracking_params   = $true
                custom_tracking_params = @(
                    @{ param = 'utm_source';   value = 'klaviyo' },
                    @{ param = 'utm_medium';   value = 'email' },
                    @{ param = 'utm_campaign'; value = 'replenishment-v2' },
                    @{ param = 'utm_content';  value = $utmContent }
                )
                additional_filters    = $null
            }
            status = 'draft'
        }
        links = @{ next = $null }
    }
}

# === Build all actions ===
$actions = @()

# Entry: restricted-product exit gate
$actions += New-RestrictedSplit -tempId 'split-restricted' -nextFalse 'split-vitamins'

# Vitamins
$actions += New-CategorySplit -tempId 'split-vitamins' -catTag 'CAT=Vitamins' -nextTrue 'delay-vitamins' -nextFalse 'split-skincare'
$actions += New-DayDelay      -tempId 'delay-vitamins' -days 60 -nextId 'email-vitamins'
$actions += New-Email         -tempId 'email-vitamins' -tplId $tplVitamins `
    -messageName '[Z] Replenishment - E1 Vitamins' `
    -subject "Time to top up your vitamins, {{ first_name|default:'there' }}" `
    -preview "Daily wellness works best when you don't run out. Free shipping over `$79." `
    -utmContent 'e1-vitamins'

# Skincare
$actions += New-CategorySplit -tempId 'split-skincare' -catTag 'CAT=Skin Care' -nextTrue 'delay-skincare' -nextFalse 'split-haircare'
$actions += New-DayDelay      -tempId 'delay-skincare' -days 45 -nextId 'email-skincare'
$actions += New-Email         -tempId 'email-skincare' -tplId $tplSkincare `
    -messageName '[Z] Replenishment - E2 Skincare' `
    -subject "Your skincare routine misses you, {{ first_name|default:'you' }}" `
    -preview 'Consistency is what skin loves most - top up before you run dry.' `
    -utmContent 'e2-skincare'

# Hair Care
$actions += New-CategorySplit -tempId 'split-haircare' -catTag 'CAT=Hair Care' -nextTrue 'delay-haircare' -nextFalse 'split-oralcare'
$actions += New-DayDelay      -tempId 'delay-haircare' -days 60 -nextId 'email-haircare'
$actions += New-Email         -tempId 'email-haircare' -tplId $tplHaircare `
    -messageName '[Z] Replenishment - E3 Hair Care' `
    -subject "{{ first_name|default:'Hey' }}, ready for a hair care top-up?" `
    -preview "Shampoo, conditioner, styling - everything you need from NZ's best prices." `
    -utmContent 'e3-haircare'

# Oral Care
$actions += New-CategorySplit -tempId 'split-oralcare' -catTag 'CAT=Oral Hygiene & Care' -nextTrue 'delay-oralcare' -nextFalse 'split-babycare'
$actions += New-DayDelay      -tempId 'delay-oralcare' -days 30 -nextId 'email-oralcare'
$actions += New-Email         -tempId 'email-oralcare' -tplId $tplOralcare `
    -messageName '[Z] Replenishment - E4 Oral Care' `
    -subject "Your oral care kit needs a refresh, {{ first_name|default:'there' }}" `
    -preview 'Toothpaste, mouthwash, floss - the daily basics, ready when you are.' `
    -utmContent 'e4-oralcare'

# Baby & Family
$actions += New-CategorySplit -tempId 'split-babycare' -catTag 'CAT=Baby Care' -nextTrue 'delay-babycare' -nextFalse 'delay-fallback'
$actions += New-DayDelay      -tempId 'delay-babycare' -days 30 -nextId 'email-babycare'
$actions += New-Email         -tempId 'email-babycare' -tplId $tplBabycare `
    -messageName '[Z] Replenishment - E5 Baby & Family' `
    -subject "Time to restock the baby essentials, {{ first_name|default:'there' }}" `
    -preview "Nappy creams, wipes and the everyday basics - all at NZ's lowest prices." `
    -utmContent 'e5-babycare'

# Universal fallback
$actions += New-DayDelay      -tempId 'delay-fallback' -days 45 -nextId 'email-fallback'
$actions += New-Email         -tempId 'email-fallback' -tplId $tplFallback `
    -messageName '[Z] Replenishment - E6 Fallback' `
    -subject "{{ first_name|default:'There' }}, time to restock your favourites?" `
    -preview "Whatever you ordered last time - restock it at the same great Bargain Chemist price." `
    -utmContent 'e6-fallback'

# === Assemble flow definition ===
$flowDef = @{
    triggers = @(@{
        type = 'metric'
        id   = $MetricId
        trigger_filter = $null
    })
    profile_filter   = $null
    entry_action_id  = 'split-restricted'
    actions          = $actions
}

$payload = @{
    data = @{
        type = 'flow'
        attributes = @{
            name       = '[Z] Replenishment - Category Based'
            definition = $flowDef
        }
    }
}

$bodyJson = $payload | ConvertTo-Json -Depth 100 -Compress

# Save request body for debugging (absolute paths - System.IO has its own CWD)
$RepoRoot = (Get-Location).Path
$OutDir   = Join-Path $RepoRoot ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$ReqFile  = Join-Path $OutDir 'replenishment-v2-request.json'
[System.IO.File]::WriteAllText($ReqFile, ($payload | ConvertTo-Json -Depth 100), [System.Text.UTF8Encoding]::new($false))
Write-Host ("Request body saved: $ReqFile") -ForegroundColor DarkGray

# === POST /api/flows ===
Write-Host '=== POST /api/flows (revision 2024-10-15.pre, beta) ===' -ForegroundColor Cyan
$bodyFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($bodyFile, $bodyJson, [System.Text.UTF8Encoding]::new($false))
$RespFile = Join-Path $OutDir 'replenishment-v2-response.json'

$postArgs = @(
    '--silent', '--show-error',
    '--max-time', '60',
    '--write-out', '%{http_code}',
    '--output', $RespFile,
    '-X', 'POST',
    '-H', $AuthHeader,
    '-H', 'revision: 2024-10-15.pre',
    '-H', 'Accept: application/vnd.api+json',
    '-H', 'Content-Type: application/vnd.api+json',
    '--data-binary', "@$bodyFile",
    'https://a.klaviyo.com/api/flows/'
)
$httpCode = & curl.exe @postArgs
Remove-Item $bodyFile -ErrorAction SilentlyContinue

if ($httpCode -eq '201') {
    $resp = Get-Content $RespFile -Raw | ConvertFrom-Json
    $newFlowId = $resp.data.id
    Write-Host ("OK  HTTP 201  new flow id = $newFlowId") -ForegroundColor Green
    Write-Host ''
    Write-Host '=== Snapshotting full definition ===' -ForegroundColor Cyan
    $AllFlowsDir = Join-Path $OutDir 'all-flows'
    New-Item -ItemType Directory -Force -Path $AllFlowsDir | Out-Null
    $SnapFile = Join-Path $AllFlowsDir "$newFlowId.json"
    $getArgs = @(
        '--silent', '--show-error',
        '--max-time', '30',
        '--output', $SnapFile,
        '-H', $AuthHeader,
        '-H', 'revision: 2024-10-15.pre',
        '-H', 'Accept: application/vnd.api+json',
        "https://a.klaviyo.com/api/flows/$newFlowId/?additional-fields%5Bflow%5D=definition"
    )
    & curl.exe @getArgs | Out-Null
    Write-Host ("Snapshot: $SnapFile") -ForegroundColor Green
    Write-Host ''
    Write-Host "Flow $newFlowId is created in 'manual' status, all emails DRAFT." -ForegroundColor Cyan
    Write-Host 'Next:' -ForegroundColor Cyan
    Write-Host '  1. Open Klaviyo UI, find the new flow, smoke-test each email' -ForegroundColor Cyan
    Write-Host '  2. Flip each email status to live' -ForegroundColor Cyan
    Write-Host '  3. Toggle the flow itself to live' -ForegroundColor Cyan
    Write-Host '  4. (Optional) add a 45-day re-entry flow filter in the UI' -ForegroundColor Cyan
    Write-Host ''
    Write-Host 'Then commit and push:' -ForegroundColor DarkGray
    Write-Host "  git add $OutDir/all-flows/$newFlowId.json $ReqFile $RespFile" -ForegroundColor DarkGray
    Write-Host "  git commit -m 'Snapshot replenishment-v2 flow $newFlowId definition'" -ForegroundColor DarkGray
    Write-Host '  git push origin claude/klaviyo-access-integration-g7txQ' -ForegroundColor DarkGray
} else {
    Write-Host ("FAIL HTTP $httpCode") -ForegroundColor Red
    if (Test-Path $RespFile) {
        Write-Host '--- response body ---' -ForegroundColor DarkYellow
        Get-Content $RespFile -Raw | Write-Host -ForegroundColor DarkYellow
    }
    Write-Host ''
    Write-Host 'Request body left at:' $ReqFile -ForegroundColor DarkGray
    Write-Host 'Send the response body to Claude to debug. Schema iteration may be needed.' -ForegroundColor DarkGray
}

Remove-Item env:KLAVIYO_PRIVATE_KEY
