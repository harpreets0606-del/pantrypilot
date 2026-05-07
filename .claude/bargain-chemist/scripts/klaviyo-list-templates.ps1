# Klaviyo: list every email template in the account.
# Saves to snapshots/<date>/templates-library.json + prints a summary table.
#
# Usage (from repo root):
#   .\.claude\bargain-chemist\scripts\klaviyo-list-templates.ps1

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
$TempDir = Join-Path $env:TEMP "klaviyo-list-tpl-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

$All = @()
$cursor = $null
$page = 0
do {
    $page++
    $url = 'https://a.klaviyo.com/api/templates/?fields%5Btemplate%5D=name,editor_type,created,updated&page%5Bsize%5D=100&sort=-updated'
    if ($cursor) { $url = $url + '&page%5Bcursor%5D=' + [uri]::EscapeDataString($cursor) }

    $respFile = Join-Path $TempDir "page-$page.json"
    $code = & curl.exe `
        --silent --show-error `
        --max-time 60 `
        --write-out '%{http_code}' `
        --output $respFile `
        -H "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)" `
        -H 'revision: 2024-10-15' `
        -H 'Accept: application/vnd.api+json' `
        $url

    if ($code -ne '200') {
        Write-Host "FAIL HTTP $code on page $page" -ForegroundColor Red
        if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
        break
    }

    $j = Get-Content $respFile -Raw | ConvertFrom-Json
    foreach ($t in $j.data) {
        $All += [pscustomobject]@{
            id          = $t.id
            name        = $t.attributes.name
            editor_type = $t.attributes.editor_type
            created     = $t.attributes.created
            updated     = $t.attributes.updated
        }
    }

    # Pagination — Klaviyo returns links.next as a full URL with cursor
    $cursor = $null
    if ($j.links.next) {
        # Extract cursor from the next URL
        if ($j.links.next -match 'page%5Bcursor%5D=([^&]+)') { $cursor = [uri]::UnescapeDataString($Matches[1]) }
    }
} while ($cursor)

Write-Host ""
Write-Host "=== $($All.Count) templates found in account ===" -ForegroundColor Cyan
Write-Host ""

# Save raw
$All | ConvertTo-Json -Depth 5 | Out-File -FilePath "$OutDir/templates-library.json" -Encoding utf8

# Print sorted by updated desc, with type breakdown
Write-Host "By editor type:" -ForegroundColor Cyan
$All | Group-Object editor_type | ForEach-Object { Write-Host "  $($_.Name): $($_.Count)" }
Write-Host ""

Write-Host "Most recently updated 30:" -ForegroundColor Cyan
$All | Select-Object -First 30 | Format-Table id, editor_type, @{N='updated';E={$_.updated.Substring(0,10)}}, name -AutoSize

Write-Host ""
Write-Host "Full list saved to: $OutDir/templates-library.json"
Write-Host "Commit + push that file so Claude can analyse:"
Write-Host "  git add $OutDir/templates-library.json"
Write-Host "  git commit -m 'Snapshot template library'"
Write-Host "  git push origin HEAD:claude/klaviyo-access-integration-g7txQ"

Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item env:KLAVIYO_PRIVATE_KEY
