# Discover the REAL template IDs for each flow-message in YdejKf.
# The IDs that appear in flow definition's `template_id` field are message-internal
# references; the actual Templates API IDs come from the flow-message relationship.
#
# This script:
#   1. GETs each flow-message with ?include=template
#   2. Extracts the real template ID
#   3. Saves a mapping file the update script can read

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

# Flow message IDs from YdejKf-with-full-definition.json (the .data.message.id field)
$Messages = @(
    @{ MessageId = 'TZmw7E'; Label = 'E1 - Welcome to the Family'; LocalFile = '.claude/bargain-chemist/templates/welcome-email-1.html' },
    @{ MessageId = 'RzUzYy'; Label = 'E2 - Best Sellers';          LocalFile = '.claude/bargain-chemist/templates/welcome-email-2.html' },
    @{ MessageId = 'WXcevZ'; Label = 'E3 - Last Nudge';            LocalFile = '.claude/bargain-chemist/templates/welcome-email-3.html' }
)

$Results = @()
$TempDir = Join-Path $env:TEMP "klaviyo-discover-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

Write-Host ""
Write-Host "=== Discovering real template IDs for YdejKf flow messages ===" -ForegroundColor Cyan

foreach ($m in $Messages) {
    Write-Host ""
    Write-Host "GET flow-message $($m.MessageId) ($($m.Label))" -ForegroundColor Cyan

    $respFile = Join-Path $TempDir "fm-$($m.MessageId).json"
    $curlArgs = @(
        '--silent', '--show-error',
        '--max-time', '30',
        '--write-out', '%{http_code}',
        '--output', $respFile,
        '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
        '-H', 'revision: 2024-10-15',
        '-H', 'Accept: application/vnd.api+json',
        "https://a.klaviyo.com/api/flow-messages/$($m.MessageId)/?include=template"
    )
    $httpCode = & curl.exe @curlArgs

    if ($httpCode -ne '200') {
        Write-Host "  FAIL HTTP $httpCode" -ForegroundColor Red
        if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
        continue
    }

    $json = Get-Content $respFile -Raw | ConvertFrom-Json
    $tplId = $null
    if ($json.data.relationships.template.data) { $tplId = $json.data.relationships.template.data.id }
    if (-not $tplId -and $json.included) {
        foreach ($inc in $json.included) {
            if ($inc.type -eq 'template') { $tplId = $inc.id; break }
        }
    }

    if ($tplId) {
        Write-Host "  Real template ID: $tplId" -ForegroundColor Green
        # Save full message for inspection
        Copy-Item $respFile -Destination "$OutDir/flow-message-$($m.MessageId).json" -Force
        $Results += [pscustomobject]@{
            message_id  = $m.MessageId
            label       = $m.Label
            template_id = $tplId
            local_file  = $m.LocalFile
        }
    } else {
        Write-Host "  WARNING: no template relationship found" -ForegroundColor Yellow
    }
}

# Save mapping
$mapFile = "$OutDir/flow-template-mapping.json"
$Results | ConvertTo-Json -Depth 5 | Out-File -FilePath $mapFile -Encoding utf8

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "Mapping saved to: $mapFile"
Write-Host ""
Write-Host "Now run klaviyo-update-flow-templates.ps1 - it will use this mapping."

Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
