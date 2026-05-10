# Dumps every Klaviyo template referenced by any flow's send-email actions
# (live OR draft). Reads flow definitions from
# .claude/bargain-chemist/snapshots/<date>/all-flows/*.json and pulls the
# unique set of template IDs to .../snapshots/<date>/templates/<id>.json
#
# Idempotent: re-running overwrites existing files. Skips templates already
# pulled in this run.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-dump-all-templates.ps1

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

if (-not (Test-Path .env.local)) { Write-Error '.env.local not found'; exit 1 }
$KEY = ((Get-Content .env.local | Where-Object { $_ -match '^KLAVIYO_PRIVATE_KEY=' }) -split '=',2)[1].Trim()
if (-not $KEY) { Write-Error 'KLAVIYO_PRIVATE_KEY not set'; exit 1 }

$Date    = Get-Date -Format 'yyyy-MM-dd'
$FlowDir = ".claude/bargain-chemist/snapshots/$Date/all-flows"
$OutDir  = ".claude/bargain-chemist/snapshots/$Date/templates"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# Collect unique template IDs from all flow definitions
$tids = New-Object System.Collections.Generic.HashSet[string]
$flows = Get-ChildItem $FlowDir -Filter '*.json' | Where-Object { $_.Name -ne '_flow-list.json' }
Write-Host ("=== Scanning {0} flow files for template IDs ===" -f $flows.Count) -ForegroundColor Cyan

foreach ($f in $flows) {
    try {
        $j = Get-Content $f.FullName -Raw | ConvertFrom-Json
    } catch { continue }
    $defn = $j.data.attributes.definition
    if (-not $defn) { continue }
    foreach ($a in $defn.actions) {
        if ($a.type -eq 'send-email') {
            $tid = $a.data.message.template_id
            if ($tid) { [void]$tids.Add($tid) }
        }
    }
}
Write-Host ("  Found {0} unique template IDs" -f $tids.Count) -ForegroundColor DarkGray

Write-Host ''
Write-Host '=== Pulling templates ===' -ForegroundColor Cyan
$ok=0; $fail=0
foreach ($tid in $tids) {
    $out = "$OutDir/$tid.json"
    $code = & curl.exe --silent --max-time 30 `
        --write-out '%{http_code}' --output $out `
        -H "Authorization: Klaviyo-API-Key $KEY" `
        -H 'revision: 2024-10-15' `
        -H 'Accept: application/vnd.api+json' `
        "https://a.klaviyo.com/api/templates/$tid/"
    $size = (Get-Item $out).Length
    if ($code -eq '200') {
        Write-Host ("  [{0}] HTTP 200  {1,7} bytes" -f $tid, $size) -ForegroundColor Green
        $ok++
    } else {
        Write-Host ("  [{0}] HTTP {1}  {2}" -f $tid, $code, $size) -ForegroundColor Red
        $fail++
    }
}

Write-Host ''
Write-Host ("=== DONE: {0} ok, {1} failed ===" -f $ok, $fail) -ForegroundColor Cyan
Write-Host ''
Write-Host 'Now commit + push:' -ForegroundColor DarkGray
Write-Host '  git add .claude/bargain-chemist/snapshots/' -ForegroundColor DarkGray
Write-Host "  git commit -m 'Bulk template dump for full audit'" -ForegroundColor DarkGray
Write-Host '  git push origin claude/klaviyo-access-integration-g7txQ' -ForegroundColor DarkGray

Remove-Item env:KLAVIYO_PRIVATE_KEY -ErrorAction SilentlyContinue
