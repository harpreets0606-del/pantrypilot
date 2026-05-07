# Replaces 6 broken Shopify CDN icon images in the Flu E2 template (YtcgUa)
# with styled emoji divs. The original images were never uploaded to Shopify
# Files, so they 404. This script PATCHes the template HTML directly.
#
# Reversible: snapshot of pre-change HTML is saved before PATCH.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-fix-flu-e2-icons.ps1

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'

if (-not (Test-Path .env.local)) { Write-Error '.env.local not found'; exit 1 }
$KEY = ((Get-Content .env.local | Where-Object { $_ -match '^KLAVIYO_PRIVATE_KEY=' }) -split '=',2)[1].Trim()
if (-not $KEY) { Write-Error 'KLAVIYO_PRIVATE_KEY not set'; exit 1 }

$TemplateId = 'YtcgUa'
$Auth       = "Authorization: Klaviyo-API-Key $KEY"
$Date       = Get-Date -Format 'yyyy-MM-dd'
$OutDir     = ".claude/bargain-chemist/snapshots/$Date/templates"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

# === Step 1: Pull current HTML ===
Write-Host "=== Step 1: Pull current $TemplateId ===" -ForegroundColor Cyan
$BeforeFile = Join-Path (Get-Location).Path "$OutDir/$TemplateId-before-emoji-fix.json"
& curl.exe --silent --max-time 30 `
    -H $Auth -H 'revision: 2024-10-15' -H 'Accept: application/vnd.api+json' `
    --output $BeforeFile `
    "https://a.klaviyo.com/api/templates/$TemplateId/"

$before = Get-Content $BeforeFile -Raw | ConvertFrom-Json
$html   = $before.data.attributes.html
Write-Host ("  Pulled. HTML length = {0} chars" -f $html.Length)

# === Step 2: Replace 6 image blocks with emoji divs ===
Write-Host ''
Write-Host '=== Step 2: Swap icons -> emoji ===' -ForegroundColor Cyan
# Build emoji from Unicode codepoints to avoid mojibake when PowerShell
# reads this file as a non-UTF-8 codepage (default on en-US Windows).
$VS16     = [char]0xFE0F  # variation selector (renders preceding char as emoji)
$swaps = @(
    @{ Icon='throat-icon';      Emoji=[char]::ConvertFromUtf32(0x1F375) },                  # 🍵
    @{ Icon='nasal-icon';       Emoji=([char]::ConvertFromUtf32(0x1F32C) + $VS16) },        # 🌬️
    @{ Icon='cold-flu-icon';    Emoji=[char]::ConvertFromUtf32(0x1F912) },                  # 🤒
    @{ Icon='probiotics-icon';  Emoji=[char]::ConvertFromUtf32(0x1F9A0) },                  # 🦠
    @{ Icon='pain-relief-icon'; Emoji=[char]::ConvertFromUtf32(0x1F48A) },                  # 💊
    @{ Icon='vitamins-icon';    Emoji=([char]::ConvertFromUtf32(0x2600) + $VS16) }          # ☀️
)

foreach ($s in $swaps) {
    $pattern = '<img[^>]*' + [regex]::Escape($s.Icon) + '\.png[^>]*/>'
    $replacement = '<div style="font-size:48px;line-height:1;margin:0 auto;text-align:center;font-family:Apple Color Emoji,Segoe UI Emoji,Noto Color Emoji,sans-serif;">' + $s.Emoji + '</div>'
    $newHtml = [regex]::Replace($html, $pattern, $replacement)
    if ($newHtml -eq $html) {
        Write-Host ("  WARN: pattern not matched for {0}" -f $s.Icon) -ForegroundColor Yellow
    } else {
        Write-Host ("  OK   {0,-20} -> {1}" -f $s.Icon, $s.Emoji) -ForegroundColor Green
    }
    $html = $newHtml
}

# === Step 2.5: Save fixed HTML for copy-paste fallback ===
$FixedHtmlFile = Join-Path (Get-Location).Path "$OutDir/$TemplateId-fixed.html"
[System.IO.File]::WriteAllText($FixedHtmlFile, $html, [System.Text.UTF8Encoding]::new($false))
Write-Host ("  Fixed HTML saved -> {0}" -f $FixedHtmlFile) -ForegroundColor DarkGray

# === Step 3: PATCH template ===
Write-Host ''
Write-Host '=== Step 3: PATCH template ===' -ForegroundColor Cyan

$body = @{
    data = @{
        type       = 'template'
        id         = $TemplateId
        attributes = @{ html = $html }
    }
} | ConvertTo-Json -Depth 10 -Compress

$BodyFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($BodyFile, $body, [System.Text.UTF8Encoding]::new($false))
$RespFile = Join-Path (Get-Location).Path "$OutDir/$TemplateId-patch-response.json"

$code = & curl.exe --silent --show-error --max-time 30 `
    --write-out '%{http_code}' --output $RespFile `
    -X PATCH `
    -H $Auth -H 'revision: 2024-10-15' `
    -H 'Accept: application/vnd.api+json' `
    -H 'Content-Type: application/vnd.api+json' `
    --data-binary "@$BodyFile" `
    "https://a.klaviyo.com/api/templates/$TemplateId/"

if ($code -eq '200') {
    Write-Host ("  OK   HTTP 200") -ForegroundColor Green
} else {
    Write-Host ("  FAIL HTTP $code (likely flow-attached template, not patchable)") -ForegroundColor Yellow
    Write-Host ''
    Write-Host '  FALLBACK: paste the fixed HTML into Klaviyo manually:' -ForegroundColor Cyan
    Write-Host ('    1. Open ' + 'https://www.klaviyo.com/email-editor/' + $TemplateId + '/edit')
    Write-Host '    2. Switch to Source / HTML view'
    Write-Host ('    3. Replace ALL contents with the file:')
    Write-Host ('       ' + $FixedHtmlFile) -ForegroundColor White
    Write-Host '    4. Save'
}
Remove-Item $BodyFile -ErrorAction SilentlyContinue

Write-Host ''
Write-Host 'Done. Preview the email in Klaviyo to verify emoji render correctly.' -ForegroundColor Cyan
Write-Host '  https://www.klaviyo.com/email-editor/YtcgUa/edit' -ForegroundColor DarkGray

Remove-Item env:KLAVIYO_PRIVATE_KEY -ErrorAction SilentlyContinue
