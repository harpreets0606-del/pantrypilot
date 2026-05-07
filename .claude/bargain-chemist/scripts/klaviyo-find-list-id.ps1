# Finds the trigger list ID of an existing flow and appends it to .env.local.
# Default: reads from SehWRt (the existing Welcome Series Website draft).

param(
    [string]$FlowId = 'SehWRt',
    [string]$EnvVar = 'KLAVIYO_WEBSITE_FORM_LIST_ID'
)

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if (-not (Test-Path .env.local)) { Write-Error "ERROR: .env.local not found"; exit 1 }
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}
if (-not $env:KLAVIYO_PRIVATE_KEY) { Write-Error "ERROR: KLAVIYO_PRIVATE_KEY not set"; exit 1 }

$Headers = @{
    'Authorization' = "Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
    'revision'      = '2024-10-15.pre'
    'Accept'        = 'application/vnd.api+json'
}

$Url = "https://a.klaviyo.com/api/flows/$FlowId/?additional-fields%5Bflow%5D=definition"
Write-Host "Fetching $Url ..." -ForegroundColor Cyan

try {
    $resp = Invoke-WebRequest -Uri $Url -Headers $Headers -Method Get -UseBasicParsing -ErrorAction Stop
    $json = $resp.Content | ConvertFrom-Json
    $defn = $json.data.attributes.definition
    if (-not $defn) { Write-Error "ERROR: definition not in response (does your key have flows:read?)"; exit 1 }

    $listId = $null
    foreach ($t in $defn.triggers) {
        if ($t.type -eq 'list' -and $t.list_id) { $listId = $t.list_id; break }
        if ($t.list -and $t.list.id)            { $listId = $t.list.id; break }
    }

    if (-not $listId) {
        Write-Host "WARNING: Trigger is not a list trigger. Full triggers:" -ForegroundColor Yellow
        $defn.triggers | ConvertTo-Json -Depth 8 | Write-Host
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
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Write-Host "FAIL HTTP $code" -ForegroundColor Red
    if ($_.Exception.Response) {
        $stream = $_.Exception.Response.GetResponseStream()
        $reader = New-Object System.IO.StreamReader($stream)
        Write-Host $reader.ReadToEnd() -ForegroundColor DarkYellow
    }
}

Remove-Item env:KLAVIYO_PRIVATE_KEY
