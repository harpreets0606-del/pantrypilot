# Dump full flow definition (incl. actions structure) to a snapshot file.
# We use this to learn the canonical schema for the beta create-flow API,
# since the docs are blocked and the API errors only tell us what's wrong, not what's right.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-dump-flow-definition.ps1 [-FlowId <id>]

param(
    [string]$FlowId = 'SehWRt'
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

$Date   = Get-Date -Format 'yyyy-MM-dd'
$OutDir = ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$OutFile = "$OutDir/$FlowId-with-full-definition.json"

$Url = "https://a.klaviyo.com/api/flows/$FlowId/?additional-fields%5Bflow%5D=definition"
Write-Host "Fetching $Url" -ForegroundColor Cyan
Write-Host "Saving to: $OutFile" -ForegroundColor DarkGray

$curlArgs = @(
    '--silent', '--show-error',
    '--max-time', '30',
    '--write-out', '%{http_code}',
    '--output', $OutFile,
    '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
    '-H', 'revision: 2024-10-15.pre',
    '-H', 'Accept: application/vnd.api+json',
    $Url
)
$httpCode = & curl.exe @curlArgs

if ($httpCode -eq '200') {
    $size = (Get-Item $OutFile).Length
    Write-Host "OK  HTTP 200  -  saved $size bytes" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now commit + push so Claude can read the schema:"
    Write-Host "  git add $OutFile" -ForegroundColor Cyan
    Write-Host "  git commit -m 'Snapshot SehWRt full definition for schema reference'" -ForegroundColor Cyan
    Write-Host "  git push origin <your-branch>" -ForegroundColor Cyan
} else {
    Write-Host "FAIL  HTTP $httpCode" -ForegroundColor Red
    if (Test-Path $OutFile) { Get-Content $OutFile -Raw | Write-Host -ForegroundColor DarkYellow }
}

Remove-Item env:KLAVIYO_PRIVATE_KEY
