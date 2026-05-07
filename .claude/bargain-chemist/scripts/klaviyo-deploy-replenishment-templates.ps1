# Deploy 6 Replenishment templates to Klaviyo as global owned templates.
# Reads the master HTML and substitutes per-category placeholders, then
# POSTs each as a new template. Captures the resulting template IDs into
# .claude/bargain-chemist/snapshots/<date>/replenishment-template-ids.json
# so the UI flow build (next step) can reference them.
#
# Re-running this script will create NEW templates each run (Klaviyo
# templates are not idempotent on name). Only run once unless intentionally
# replacing.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-deploy-replenishment-templates.ps1

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

$MasterPath = '.claude/bargain-chemist/templates/replenishment-master.html'
if (-not (Test-Path $MasterPath)) { Write-Error "Master template not found: $MasterPath"; exit 1 }
$Master = Get-Content $MasterPath -Raw

# Per-category configs. Editing here changes what gets uploaded.
$Categories = @(
    @{
        Key                = 'vitamins'
        Name               = '[Z] Replenishment - E1 Vitamins'
        Eyebrow            = 'VITAMINS REPLENISHMENT'
        H1                 = "Time to top up your vitamins, {{ first_name|default:'there' }}"
        Subhead            = "Daily wellness works best when you don't run out."
        IntroDays          = 60
        CategoryLabel      = 'vitamins'
        CtaLabel           = 'Shop Vitamins'
        CollectionHandle   = 'vitamins-supplements'
        ValuePropLine      = 'Consistency is the whole point - keep your routine going.'
    },
    @{
        Key                = 'skincare'
        Name               = '[Z] Replenishment - E2 Skincare'
        Eyebrow            = 'SKINCARE REPLENISHMENT'
        H1                 = "Your skincare routine misses you, {{ first_name|default:'you' }}"
        Subhead            = 'Skin loves consistency - keep your routine going.'
        IntroDays          = 45
        CategoryLabel      = 'skincare'
        CtaLabel           = 'Shop Skincare'
        CollectionHandle   = 'skin-care'
        ValuePropLine      = "Top up before you run dry - same great Bargain Chemist price."
    },
    @{
        Key                = 'haircare'
        Name               = '[Z] Replenishment - E3 Hair Care'
        Eyebrow            = 'HAIR CARE REPLENISHMENT'
        H1                 = "{{ first_name|default:'Hey' }}, ready for a hair care top-up?"
        Subhead            = 'Shampoo, conditioner and styling - the daily go-tos.'
        IntroDays          = 60
        CategoryLabel      = 'hair care'
        CtaLabel           = 'Shop Hair Care'
        CollectionHandle   = 'hair-care'
        ValuePropLine      = "Everything you need from NZ's best pharmacy prices."
    },
    @{
        Key                = 'oralcare'
        Name               = '[Z] Replenishment - E4 Oral Care'
        Eyebrow            = 'ORAL CARE REPLENISHMENT'
        H1                 = "Your oral care kit needs a refresh, {{ first_name|default:'there' }}"
        Subhead            = 'Toothpaste, floss and mouthwash - daily essentials.'
        IntroDays          = 30
        CategoryLabel      = 'oral care'
        CtaLabel           = 'Shop Oral Care'
        CollectionHandle   = 'oral-hygiene-care'
        ValuePropLine      = "Daily mouth care - the basics, ready when you are."
    },
    @{
        Key                = 'babycare'
        Name               = '[Z] Replenishment - E5 Baby & Family'
        Eyebrow            = 'BABY ESSENTIALS REPLENISHMENT'
        H1                 = "Time to restock the baby essentials, {{ first_name|default:'there' }}"
        Subhead            = 'Nappy creams, wipes and the daily basics.'
        IntroDays          = 30
        CategoryLabel      = 'baby essentials'
        CtaLabel           = 'Shop Baby & Family'
        CollectionHandle   = 'baby-care'
        ValuePropLine      = "All at NZ's lowest pharmacy prices."
    },
    @{
        Key                = 'fallback'
        Name               = '[Z] Replenishment - E6 Fallback (Your Favourites)'
        Eyebrow            = 'YOUR FAVOURITES'
        H1                 = "Time to restock your favourites, {{ first_name|default:'there' }}"
        Subhead            = "Whatever you ordered last - back at NZ's best prices."
        IntroDays          = 45
        CategoryLabel      = 'favourites'
        CtaLabel           = 'Shop Your Last Order'
        CollectionHandle   = 'all-products'
        ValuePropLine      = 'Same great prices, free shipping over $79, Price Beat 10%.'
    }
)

$Date    = Get-Date -Format 'yyyy-MM-dd'
$OutDir  = ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$IdsFile = "$OutDir/replenishment-template-ids.json"

$AuthHeader = "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
$results    = @()

foreach ($cat in $Categories) {
    Write-Host ('=== ' + $cat.Key + ' ===') -ForegroundColor Cyan
    $html = $Master
    $html = $html.Replace('__EYEBROW__',           $cat.Eyebrow)
    $html = $html.Replace('__H1__',                $cat.H1)
    $html = $html.Replace('__SUBHEAD__',           $cat.Subhead)
    $html = $html.Replace('__INTRO_DAYS__',        [string]$cat.IntroDays)
    $html = $html.Replace('__CATEGORY_LABEL__',    $cat.CategoryLabel)
    $html = $html.Replace('__CTA_LABEL__',         $cat.CtaLabel)
    $html = $html.Replace('__COLLECTION_HANDLE__', $cat.CollectionHandle)
    $html = $html.Replace('__VALUE_PROP_LINE__',   $cat.ValuePropLine)

    # Sanity: any unsubstituted placeholders left?
    $remaining = [regex]::Matches($html, '__[A-Z_]+__')
    if ($remaining.Count -gt 0) {
        Write-Host ('  WARN unsubstituted placeholders: ' + ($remaining.Value -join ', ')) -ForegroundColor Yellow
    }

    $body = @{
        data = @{
            type       = 'template'
            attributes = @{
                name        = $cat.Name
                editor_type = 'CODE'
                html        = $html
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress

    $bodyFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($bodyFile, $body, [System.Text.UTF8Encoding]::new($false))
    $respFile = [System.IO.Path]::GetTempFileName()

    $postArgs = @(
        '--silent', '--show-error',
        '--max-time', '30',
        '--write-out', '%{http_code}',
        '--output', $respFile,
        '-X', 'POST',
        '-H', $AuthHeader,
        '-H', 'revision: 2024-10-15',
        '-H', 'Accept: application/vnd.api+json',
        '-H', 'Content-Type: application/vnd.api+json',
        '--data-binary', "@$bodyFile",
        'https://a.klaviyo.com/api/templates/'
    )
    $httpCode = & curl.exe @postArgs

    if ($httpCode -eq '201') {
        $resp = Get-Content $respFile -Raw | ConvertFrom-Json
        $tid  = $resp.data.id
        Write-Host ('  OK  HTTP 201  template_id = ' + $tid) -ForegroundColor Green
        $results += [PSCustomObject]@{
            Key             = $cat.Key
            Name            = $cat.Name
            TemplateId      = $tid
            CollectionHandle= $cat.CollectionHandle
            IntroDays       = $cat.IntroDays
        }
    } else {
        Write-Host ('  FAIL HTTP ' + $httpCode) -ForegroundColor Red
        if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
    }

    Remove-Item $bodyFile, $respFile -ErrorAction SilentlyContinue
}

Write-Host ''
$results | Format-Table Key, TemplateId, Name -AutoSize

# Save IDs for next step (UI flow build references these template IDs)
$results | ConvertTo-Json -Depth 10 | Set-Content -Path $IdsFile -Encoding UTF8
Write-Host ('Template IDs saved to: ' + $IdsFile) -ForegroundColor Cyan
Write-Host ''
Write-Host 'NEXT STEP: build the flow structure in Klaviyo UI using these' -ForegroundColor Cyan
Write-Host 'template IDs. See:' -ForegroundColor Cyan
Write-Host '  .claude/bargain-chemist/playbooks/replenishment-v2-ui-build.md' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Then commit + push:' -ForegroundColor DarkGray
Write-Host ('  git add ' + $IdsFile) -ForegroundColor DarkGray
Write-Host "  git commit -m 'Snapshot replenishment-v2 template IDs'" -ForegroundColor DarkGray
Write-Host '  git push origin claude/klaviyo-access-integration-g7txQ' -ForegroundColor DarkGray

Remove-Item env:KLAVIYO_PRIVATE_KEY
