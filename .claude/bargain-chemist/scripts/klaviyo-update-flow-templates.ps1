# Klaviyo: PATCH the live (flow-cloned) templates of YdejKf in place.
# Pushes updated HTML from .claude/bargain-chemist/templates/ into the existing
# template IDs assigned to the Welcome Series 2026 flow. Changes go live immediately.
#
# Usage (from repo root):
#   .\.claude\bargain-chemist\scripts\klaviyo-update-flow-templates.ps1
#
# Mapping (verified via YdejKf-with-full-definition.json on 2026-05-07):
#   E1 = VMMpC9  <- welcome-email-1.html
#   E2 = Tnktv3  <- welcome-email-2.html
#   E3 = QWTxmV  <- welcome-email-3.html
#
# Uses curl.exe + manual JSON escape (per memory/terminal-scripting-notes.md).

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

# Manual JSON string escaper (PS 5.1 ConvertTo-Json hangs on long HTML)
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

$Date    = Get-Date -Format 'yyyy-MM-dd'
$OutDir  = ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$TempDir = Join-Path $env:TEMP "klaviyo-update-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

# Read template mapping (run klaviyo-discover-flow-template-ids.ps1 first to generate this)
$mapFile = ".claude/bargain-chemist/snapshots/$Date/flow-template-mapping.json"
if (-not (Test-Path $mapFile)) {
    Write-Host "ERROR: $mapFile not found." -ForegroundColor Red
    Write-Host "Run klaviyo-discover-flow-template-ids.ps1 first to fetch the real template IDs." -ForegroundColor Yellow
    exit 1
}
$Mapping = Get-Content $mapFile -Raw | ConvertFrom-Json
$Updates = $Mapping | ForEach-Object {
    @{ TemplateId = $_.template_id; File = $_.local_file; Label = $_.label }
}

Write-Host ""
Write-Host "=== Updating live flow templates for YdejKf ===" -ForegroundColor Cyan

$Idx = 0
foreach ($u in $Updates) {
    $Idx++
    Write-Host ""
    Write-Host "[$Idx/$($Updates.Count)] PATCH template $($u.TemplateId) ($($u.Label))" -ForegroundColor Cyan

    if (-not (Test-Path $u.File)) {
        Write-Host "  FAIL  $($u.File) not found" -ForegroundColor Red
        continue
    }

    $html = Get-Content $u.File -Raw -Encoding UTF8
    Write-Host "  HTML: $([math]::Round($html.Length/1KB,1)) KB" -ForegroundColor DarkGray

    $htmlJson = ConvertTo-JsonString $html
    $body = '{"data":{"type":"template","id":"' + $u.TemplateId + '","attributes":{"html":' + $htmlJson + '}}}'

    $bodyFile = Join-Path $TempDir "body-$($u.TemplateId).json"
    [System.IO.File]::WriteAllText($bodyFile, $body, [System.Text.UTF8Encoding]::new($false))
    $respFile = Join-Path $TempDir "resp-$($u.TemplateId).json"

    $curlArgs = @(
        '--silent', '--show-error',
        '--max-time', '60',
        '--write-out', '%{http_code}',
        '--output', $respFile,
        '-X', 'PATCH',
        '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
        '-H', 'revision: 2024-10-15',
        '-H', 'Accept: application/vnd.api+json',
        '-H', 'Content-Type: application/vnd.api+json',
        '--data-binary', "@$bodyFile",
        "https://a.klaviyo.com/api/templates/$($u.TemplateId)/"
    )
    $httpCode = & curl.exe @curlArgs

    if ($httpCode -eq '200') {
        Write-Host "  OK    template $($u.TemplateId) updated (HTTP 200)" -ForegroundColor Green
        Write-Host "        Edit: https://www.klaviyo.com/email-editor/$($u.TemplateId)/edit" -ForegroundColor DarkGray
    } else {
        Write-Host "  FAIL  HTTP $httpCode" -ForegroundColor Red
        if (Test-Path $respFile) {
            $errBody = Get-Content $respFile -Raw
            Write-Host "  $errBody" -ForegroundColor DarkYellow
            $errFile = "$OutDir/template-update-error-$($u.TemplateId).json"
            $errBody | Out-File -FilePath $errFile -Encoding utf8
        }
    }
}

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host "Open the flow in Klaviyo to verify - changes are LIVE immediately:"
Write-Host "  https://www.klaviyo.com/flow/YdejKf/edit"

Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
