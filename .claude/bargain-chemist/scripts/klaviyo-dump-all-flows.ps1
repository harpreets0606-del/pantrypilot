# Dump every unarchived flow's full definition into one snapshot dir.
# Used for the comprehensive content audit (subjects, previews, structure,
# trigger filters, profile filters, all in one place).
#
# Output: .claude/bargain-chemist/snapshots/<date>/all-flows/<FlowId>.json
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-dump-all-flows.ps1

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

$Date   = Get-Date -Format 'yyyy-MM-dd'
$OutDir = ".claude/bargain-chemist/snapshots/$Date/all-flows"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$AuthHeader = "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"

# Step 1: list every unarchived flow
Write-Host '=== STEP 1: List unarchived flows ===' -ForegroundColor Cyan
$ListFile = "$OutDir/_flow-list.json"
$ListUrl  = 'https://a.klaviyo.com/api/flows/?fields%5Bflow%5D=name,status,trigger_type,created,updated&filter=equals(archived,false)&page%5Bsize%5D=50'

$listArgs = @(
    '--silent', '--show-error',
    '--max-time', '30',
    '--write-out', '%{http_code}',
    '--output', $ListFile,
    '-H', $AuthHeader,
    '-H', 'revision: 2024-10-15',
    '-H', 'Accept: application/vnd.api+json',
    $ListUrl
)
$httpCode = & curl.exe @listArgs
if ($httpCode -ne '200') {
    Write-Host "FAIL listing flows  HTTP $httpCode" -ForegroundColor Red
    if (Test-Path $ListFile) { Get-Content $ListFile -Raw | Write-Host -ForegroundColor DarkYellow }
    Remove-Item env:KLAVIYO_PRIVATE_KEY
    exit 1
}

$list = Get-Content $ListFile -Raw | ConvertFrom-Json
$flows = $list.data
Write-Host "Found $($flows.Count) unarchived flows" -ForegroundColor Green
Write-Host ''

# Step 2: dump each flow's definition
Write-Host '=== STEP 2: Dump definitions ===' -ForegroundColor Cyan
$ok   = 0
$fail = 0
foreach ($f in $flows) {
    $id     = $f.id
    $name   = $f.attributes.name
    $status = $f.attributes.status
    $outFile = "$OutDir/$id.json"
    $url = "https://a.klaviyo.com/api/flows/$id/?additional-fields%5Bflow%5D=definition"

    $args = @(
        '--silent', '--show-error',
        '--max-time', '30',
        '--write-out', '%{http_code}',
        '--output', $outFile,
        '-H', $AuthHeader,
        '-H', 'revision: 2024-10-15.pre',
        '-H', 'Accept: application/vnd.api+json',
        $url
    )
    $code = & curl.exe @args

    if ($code -eq '200') {
        $size = (Get-Item $outFile).Length
        Write-Host ("  [{0,-6}] {1,-50} {2,8} bytes  status={3}" -f $id, $name, $size, $status) -ForegroundColor Green
        $ok++
    } else {
        Write-Host ("  [{0,-6}] {1,-50} HTTP {2}" -f $id, $name, $code) -ForegroundColor Red
        $fail++
    }
}

Write-Host ''
Write-Host "=== DONE ===" -ForegroundColor Cyan
Write-Host "  $ok ok, $fail failed"
Write-Host ''
Write-Host "Now commit + push:"
Write-Host "  git add $OutDir" -ForegroundColor Cyan
Write-Host "  git commit -m 'Bulk dump all unarchived flows for content audit'" -ForegroundColor Cyan
Write-Host "  git push origin claude/klaviyo-access-integration-g7txQ" -ForegroundColor Cyan

Remove-Item env:KLAVIYO_PRIVATE_KEY
