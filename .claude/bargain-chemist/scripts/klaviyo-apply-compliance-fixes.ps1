# Applies 4 compliance fixes to live-flow templates via PATCH /api/templates/{id}/
#
# Templates fixed:
#   W2Sbja  Ysj7sg E1 (Back in Stock)         - removed 3 ASA fear phrases
#   QRewz9  RPQXaa E2 (Cart Abandonment)      - removed "selling fast" + "Don't miss out"
#   XgqKFQ  YdejKf E3 (Welcome Series 2026)   - removed "don't miss" in headline
#   SJwrxf  V9XmEm E1 (Flu Season)            - rebuilt minimal footer to full ASA footer
#
# Each PATCH is preceded by a snapshot of the live HTML (rollback safety).
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-apply-compliance-fixes.ps1

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

if (-not (Test-Path .env.local)) { Write-Error '.env.local not found'; exit 1 }
$KEY = ((Get-Content .env.local | Where-Object { $_ -match '^KLAVIYO_PRIVATE_KEY=' }) -split '=',2)[1].Trim()
if (-not $KEY) { Write-Error 'KLAVIYO_PRIVATE_KEY not set'; exit 1 }

$Date    = Get-Date -Format 'yyyy-MM-dd'
$BackupDir = ".claude/bargain-chemist/snapshots/$Date/templates/before-compliance-fix"
New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null

$fixes = @(
    @{ Id='W2Sbja'; Label='Ysj7sg E1 (Back in Stock)';      Note='Removed: sold out / don''t miss / limited stock' },
    @{ Id='QRewz9'; Label='RPQXaa E2 (Cart Abandonment)';   Note='Removed: selling fast / Don''t miss out' },
    @{ Id='XgqKFQ'; Label='YdejKf E3 (Welcome Series 2026)';Note='Removed: don''t miss in headline' },
    @{ Id='SJwrxf'; Label='V9XmEm E1 (Flu Season)';         Note='Rebuilt footer: + $79 + address + always-read-label + healthcare-pro' }
)

$ok = 0; $fail = 0
foreach ($f in $fixes) {
    $tid = $f.Id
    Write-Host ""
    Write-Host "=== $tid  $($f.Label) ===" -ForegroundColor Cyan
    Write-Host "  $($f.Note)" -ForegroundColor DarkGray

    # 1. Snapshot pre-change live state
    $beforeFile = Join-Path (Get-Location).Path "$BackupDir/$tid.json"
    & curl.exe --silent --max-time 30 `
        -H "Authorization: Klaviyo-API-Key $KEY" `
        -H 'revision: 2024-10-15' `
        -H 'Accept: application/vnd.api+json' `
        --output $beforeFile `
        "https://a.klaviyo.com/api/templates/$tid/"
    Write-Host "  Backup saved: $beforeFile" -ForegroundColor DarkGray

    # 2. Read fixed HTML
    $fixedFile = ".claude/bargain-chemist/templates/fixes/$tid.html"
    if (-not (Test-Path $fixedFile)) {
        Write-Host "  ERROR: fixed HTML not found at $fixedFile" -ForegroundColor Red
        $fail++; continue
    }
    $html = Get-Content $fixedFile -Raw

    # 3. Build PATCH body
    $body = @{
        data = @{
            type       = 'template'
            id         = $tid
            attributes = @{ html = $html }
        }
    } | ConvertTo-Json -Depth 10 -Compress

    $bodyFile = [System.IO.Path]::GetTempFileName()
    [System.IO.File]::WriteAllText($bodyFile, $body, [System.Text.UTF8Encoding]::new($false))
    $respFile = Join-Path (Get-Location).Path "$BackupDir/$tid-patch-response.json"

    # 4. PATCH
    $code = & curl.exe --silent --show-error --max-time 30 `
        --write-out '%{http_code}' --output $respFile `
        -X PATCH `
        -H "Authorization: Klaviyo-API-Key $KEY" `
        -H 'revision: 2024-10-15' `
        -H 'Accept: application/vnd.api+json' `
        -H 'Content-Type: application/vnd.api+json' `
        --data-binary "@$bodyFile" `
        "https://a.klaviyo.com/api/templates/$tid/"

    if ($code -eq '200') {
        Write-Host "  HTTP 200 OK" -ForegroundColor Green
        $ok++
    } else {
        Write-Host "  HTTP $code  FAIL" -ForegroundColor Red
        Write-Host "  Response: $respFile" -ForegroundColor DarkGray
        $fail++
    }
    Remove-Item $bodyFile -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=== DONE: $ok ok, $fail failed ===" -ForegroundColor Cyan

if ($ok -gt 0) {
    Write-Host ""
    Write-Host "Re-pull templates to verify fixes landed:" -ForegroundColor DarkGray
    Write-Host "  .\.claude\bargain-chemist\scripts\klaviyo-dump-all-templates.ps1" -ForegroundColor DarkGray
    Write-Host ""
    Write-Host "Then commit:" -ForegroundColor DarkGray
    Write-Host "  git add .claude/bargain-chemist/" -ForegroundColor DarkGray
    Write-Host "  git commit -m 'Apply ASA compliance fixes to 4 live-flow templates'" -ForegroundColor DarkGray
    Write-Host "  git push origin claude/klaviyo-access-integration-g7txQ" -ForegroundColor DarkGray
}

Remove-Item env:KLAVIYO_PRIVATE_KEY -ErrorAction SilentlyContinue
