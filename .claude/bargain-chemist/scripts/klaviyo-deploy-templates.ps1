# Klaviyo template deployment - PowerShell + curl.exe
# Bypasses PS 5.1 Invoke-WebRequest/Invoke-RestMethod HTTP bugs by shelling out to curl.exe
# (built into Windows 10/11 since 1803).
#
# Usage (from repo root):
#   .\.claude\bargain-chemist\scripts\klaviyo-deploy-templates.ps1
#
# Outputs: .claude/bargain-chemist/snapshots/<date>/deployed-templates.json with template IDs.

$ErrorActionPreference = 'Continue'

# --- Verify curl.exe ---
$curl = Get-Command curl.exe -ErrorAction SilentlyContinue
if (-not $curl) {
    Write-Error "ERROR: curl.exe not found. Windows 10 1803+ should have it. Run 'where.exe curl' to debug."
    exit 1
}
Write-Host "Using: $($curl.Source)" -ForegroundColor DarkGray

# --- Load .env.local ---
if (-not (Test-Path .env.local)) { Write-Error 'ERROR: .env.local not found'; exit 1 }
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}
if (-not $env:KLAVIYO_PRIVATE_KEY) { Write-Error 'ERROR: KLAVIYO_PRIVATE_KEY not set'; exit 1 }

$Date = Get-Date -Format 'yyyy-MM-dd'
$OutDir = ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Templates = @(
    @{ Name = 'BC - Welcome Email 1 - Welcome to the Family';        File = '.claude/bargain-chemist/templates/welcome-email-1.html' },
    @{ Name = 'BC - Welcome Email 2 - Best Sellers';                 File = '.claude/bargain-chemist/templates/welcome-email-2.html' },
    @{ Name = 'BC - Welcome Email 3 - Last Nudge';                   File = '.claude/bargain-chemist/templates/welcome-email-3.html' },
    @{ Name = 'BC - Cart Abandonment Email 3 - Last Chance (72h)';   File = '.claude/bargain-chemist/templates/cart-abandon-email-3.html' }
)

$Results = @()
$TempDir = Join-Path $env:TEMP "klaviyo-deploy-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

Write-Host ""
Write-Host "=== Deploying 4 templates to Klaviyo via curl.exe (account XCgiqg) ===" -ForegroundColor Cyan

$Idx = 0
foreach ($t in $Templates) {
    $Idx++
    Write-Host ""
    Write-Host "[$Idx/$($Templates.Count)] Uploading: $($t.Name)" -ForegroundColor Cyan

    if (-not (Test-Path $t.File)) {
        Write-Host "  FAIL  file not found at $($t.File)" -ForegroundColor Red
        continue
    }

    $html = Get-Content $t.File -Raw -Encoding UTF8
    Write-Host "  HTML size: $([math]::Round($html.Length/1KB,1)) KB" -ForegroundColor DarkGray

    # Build JSON body
    $bodyObj = @{
        data = @{
            type = 'template'
            attributes = @{
                name        = $t.Name
                editor_type = 'CODE'
                html        = $html
            }
        }
    }
    $body = $bodyObj | ConvertTo-Json -Depth 10 -Compress

    # Write body to temp file for curl --data-binary @file
    $bodyFile = Join-Path $TempDir "body-$Idx.json"
    [System.IO.File]::WriteAllText($bodyFile, $body, [System.Text.UTF8Encoding]::new($false))
    $respFile = Join-Path $TempDir "resp-$Idx.json"

    # Run curl.exe
    Write-Host "  POST -> https://a.klaviyo.com/api/templates/" -ForegroundColor DarkGray
    $curlArgs = @(
        '--silent', '--show-error',
        '--max-time', '60',
        '--write-out', '%{http_code}',
        '--output', $respFile,
        '-X', 'POST',
        '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
        '-H', 'revision: 2024-10-15',
        '-H', 'Accept: application/vnd.api+json',
        '-H', 'Content-Type: application/vnd.api+json',
        '--data-binary', "@$bodyFile",
        'https://a.klaviyo.com/api/templates/'
    )
    $httpCode = & curl.exe @curlArgs

    if ($httpCode -eq '201' -or $httpCode -eq '200') {
        $respJson = Get-Content $respFile -Raw | ConvertFrom-Json
        $tid = $respJson.data.id
        $editUrl = "https://www.klaviyo.com/email-editor/$tid/edit"
        Write-Host "  OK    $($t.Name)" -ForegroundColor Green
        Write-Host "        ID:   $tid" -ForegroundColor DarkGray
        Write-Host "        Edit: $editUrl" -ForegroundColor DarkGray
        $Results += [pscustomobject]@{
            name      = $t.Name
            id        = $tid
            edit_url  = $editUrl
            file      = $t.File
            deployed  = (Get-Date -Format o)
        }
    } else {
        Write-Host "  FAIL  HTTP $httpCode" -ForegroundColor Red
        if (Test-Path $respFile) {
            $errBody = Get-Content $respFile -Raw
            Write-Host "  $errBody" -ForegroundColor DarkYellow
            $errFile = "$OutDir/template-error-$Idx.json"
            $errBody | Out-File -FilePath $errFile -Encoding utf8
            Write-Host "  Error saved to $errFile" -ForegroundColor DarkYellow
        }
    }
}

# Save summary
$summaryFile = "$OutDir/deployed-templates.json"
if ($Results.Count -gt 0) {
    $Results | ConvertTo-Json -Depth 5 | Out-File -FilePath $summaryFile -Encoding utf8
    Write-Host ""
    Write-Host "=== DONE ===" -ForegroundColor Green
    Write-Host "Summary saved to: $summaryFile"
} else {
    Write-Host ""
    Write-Host "=== NO TEMPLATES DEPLOYED ===" -ForegroundColor Red
}

# Cleanup
Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
