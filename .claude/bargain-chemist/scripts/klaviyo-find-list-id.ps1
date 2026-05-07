# Finds the trigger list ID of an existing flow and appends it to .env.local.
# Default: reads from SehWRt (the existing Welcome Series Website draft).
# Uses curl.exe (PS 5.1 HTTP cmdlets hang on this machine - see memory/terminal-scripting-notes.md).

param(
    [string]$FlowId = 'SehWRt',
    [string]$EnvVar = 'KLAVIYO_WEBSITE_FORM_LIST_ID'
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

$Url = "https://a.klaviyo.com/api/flows/$FlowId/?additional-fields%5Bflow%5D=definition"
Write-Host "Fetching $Url ..." -ForegroundColor Cyan

$TempDir = Join-Path $env:TEMP "klaviyo-list-$([guid]::NewGuid().ToString('N').Substring(0,8))"
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
$respFile = Join-Path $TempDir 'resp.json'

$curlArgs = @(
    '--silent', '--show-error',
    '--max-time', '30',
    '--write-out', '%{http_code}',
    '--output', $respFile,
    '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
    '-H', 'revision: 2024-10-15.pre',
    '-H', 'Accept: application/vnd.api+json',
    $Url
)
$httpCode = & curl.exe @curlArgs

if ($httpCode -ne '200') {
    Write-Host "FAIL HTTP $httpCode" -ForegroundColor Red
    if (Test-Path $respFile) { Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow }
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item env:KLAVIYO_PRIVATE_KEY
    exit 1
}

try {
    $json = Get-Content $respFile -Raw | ConvertFrom-Json
    $defn = $json.data.attributes.definition
    if (-not $defn) {
        Write-Host "ERROR: definition not in response. Raw response:" -ForegroundColor Red
        Get-Content $respFile -Raw | Write-Host -ForegroundColor DarkYellow
        exit 1
    }

    $listId = $null
    foreach ($t in $defn.triggers) {
        if ($t.type -eq 'list' -and $t.list_id) { $listId = $t.list_id; break }
        if ($t.list -and $t.list.id)            { $listId = $t.list.id; break }
        if ($t.id)                              { $listId = $t.id;      break }
    }

    if (-not $listId) {
        Write-Host "WARNING: No list ID found in triggers. Full triggers JSON:" -ForegroundColor Yellow
        $defn.triggers | ConvertTo-Json -Depth 8 | Write-Host -ForegroundColor DarkYellow
        Write-Host ""
        Write-Host "Try running with a different flow ID, or set $EnvVar manually in .env.local." -ForegroundColor Yellow
        exit 1
    }

    Write-Host "Found list ID: $listId" -ForegroundColor Green

    # Append (or update) .env.local
    $existing = Get-Content .env.local
    if ($existing -match "^$EnvVar=") {
        $existing = $existing -replace "^$EnvVar=.*$", "$EnvVar=$listId"
        $existing | Set-Content .env.local -Encoding utf8
        Write-Host "Updated $EnvVar in .env.local" -ForegroundColor Green
    } else {
        Add-Content -Path .env.local -Value "$EnvVar=$listId"
        Write-Host "Appended $EnvVar to .env.local" -ForegroundColor Green
    }
} finally {
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item env:KLAVIYO_PRIVATE_KEY
}
