# Pauses the OLD Replenishment flow (V4cZMd) by setting status to "manual".
# This stops auto-triggering for new orders. Fully reversible (PATCH back
# to "live" any time). Safe to run before V2 build.
#
# Verification: post-PATCH GET on the flow confirms new status.
#
# Usage:
#   .\.claude\bargain-chemist\scripts\klaviyo-pause-replenishment-v1.ps1

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

$FlowId    = 'V4cZMd'
$AuthHeader = "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
$PatchUrl  = "https://a.klaviyo.com/api/flows/$FlowId/"

$Body = @{
    data = @{
        type       = 'flow'
        id         = $FlowId
        attributes = @{ status = 'manual' }
    }
} | ConvertTo-Json -Depth 10 -Compress

$BodyFile = [System.IO.Path]::GetTempFileName()
[System.IO.File]::WriteAllText($BodyFile, $Body, [System.Text.UTF8Encoding]::new($false))

Write-Host '=== STEP 1: PATCH flow status to manual ===' -ForegroundColor Cyan
$RespFile = [System.IO.Path]::GetTempFileName()
$patchArgs = @(
    '--silent', '--show-error',
    '--max-time', '30',
    '--write-out', '%{http_code}',
    '--output', $RespFile,
    '-X', 'PATCH',
    '-H', $AuthHeader,
    '-H', 'revision: 2024-10-15',
    '-H', 'Accept: application/vnd.api+json',
    '-H', 'Content-Type: application/vnd.api+json',
    '--data-binary', "@$BodyFile",
    $PatchUrl
)
$httpCode = & curl.exe @patchArgs
if ($httpCode -eq '200') {
    Write-Host "OK  HTTP 200 - flow $FlowId set to manual" -ForegroundColor Green
} else {
    Write-Host "FAIL  HTTP $httpCode" -ForegroundColor Red
    if (Test-Path $RespFile) { Get-Content $RespFile -Raw | Write-Host -ForegroundColor DarkYellow }
    Remove-Item $BodyFile, $RespFile -ErrorAction SilentlyContinue
    Remove-Item env:KLAVIYO_PRIVATE_KEY
    exit 1
}
Remove-Item $BodyFile, $RespFile -ErrorAction SilentlyContinue

Write-Host ''
Write-Host '=== STEP 2: Verify status ===' -ForegroundColor Cyan
$VerifyFile = [System.IO.Path]::GetTempFileName()
$getArgs = @(
    '--silent', '--show-error',
    '--max-time', '30',
    '--output', $VerifyFile,
    '-H', $AuthHeader,
    '-H', 'revision: 2024-10-15',
    '-H', 'Accept: application/vnd.api+json',
    "https://a.klaviyo.com/api/flows/$FlowId/"
)
& curl.exe @getArgs | Out-Null
$verify = Get-Content $VerifyFile -Raw | ConvertFrom-Json
$newStatus = $verify.data.attributes.status
Remove-Item $VerifyFile -ErrorAction SilentlyContinue

if ($newStatus -eq 'manual') {
    Write-Host "Verified: status = $newStatus" -ForegroundColor Green
} else {
    Write-Host "WARNING: expected 'manual', got '$newStatus'" -ForegroundColor Red
}

Write-Host ''
Write-Host 'Old replenishment flow is paused. New entries no longer trigger.' -ForegroundColor Cyan
Write-Host 'Profiles already mid-flow continue through their existing path.' -ForegroundColor DarkGray
Write-Host 'To unpause: re-PATCH with status=live (or run a reverse script).' -ForegroundColor DarkGray

Remove-Item env:KLAVIYO_PRIVATE_KEY
