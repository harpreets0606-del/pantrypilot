# Klaviyo template deployment - PowerShell version
# Uploads the 4 Welcome / Cart Abandonment HTML templates from .claude/bargain-chemist/templates/
# Returns the new template IDs so you can paste them into the flow actions.
#
# Usage (from repo root, on Windows machine with .env.local present):
#   .\.claude\bargain-chemist\scripts\klaviyo-deploy-templates.ps1
#
# Outputs a summary file at .claude/bargain-chemist/snapshots/<date>/deployed-templates.json
# with template IDs + names + Klaviyo edit URLs.

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'   # Fixes PS 5.1 slow upload bug

# Load .env.local
if (-not (Test-Path .env.local)) {
    Write-Error "ERROR: .env.local not found at repo root."
    exit 1
}
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}
if (-not $env:KLAVIYO_PRIVATE_KEY) {
    Write-Error "ERROR: KLAVIYO_PRIVATE_KEY not set in .env.local"
    exit 1
}

$Revision = '2024-10-15'
$Date     = Get-Date -Format 'yyyy-MM-dd'
$OutDir   = ".claude/bargain-chemist/snapshots/$Date"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Headers = @{
    'Authorization' = "Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
    'revision'      = $Revision
    'Accept'        = 'application/vnd.api+json'
    'Content-Type'  = 'application/vnd.api+json'
}

# Templates to deploy: name + html file path
$Templates = @(
    @{ Name = 'BC - Welcome Email 1 - Welcome to the Family';        File = '.claude/bargain-chemist/templates/welcome-email-1.html' },
    @{ Name = 'BC - Welcome Email 2 - Best Sellers';                 File = '.claude/bargain-chemist/templates/welcome-email-2.html' },
    @{ Name = 'BC - Welcome Email 3 - Last Nudge';                   File = '.claude/bargain-chemist/templates/welcome-email-3.html' },
    @{ Name = 'BC - Cart Abandonment Email 3 - Last Chance (72h)';   File = '.claude/bargain-chemist/templates/cart-abandon-email-3.html' }
)

$Results = @()

Write-Host ""
Write-Host "=== Deploying 4 templates to Klaviyo (account XCgiqg) ===" -ForegroundColor Cyan
Write-Host ""

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
    Write-Host "  HTML size: $([math]::Round($html.Length/1KB,1)) KB - sending POST..." -ForegroundColor DarkGray

    $body = @{
        data = @{
            type = 'template'
            attributes = @{
                name        = $t.Name
                editor_type = 'CODE'
                html        = $html
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress

    try {
        $resp = Invoke-WebRequest -Uri 'https://a.klaviyo.com/api/templates/' `
                                  -Headers $Headers `
                                  -Method Post `
                                  -Body $body `
                                  -ErrorAction Stop `
                                  -UseBasicParsing `
                                  -TimeoutSec 60
        $json = $resp.Content | ConvertFrom-Json
        $tid  = $json.data.id
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
    } catch {
        $code = $_.Exception.Response.StatusCode.value__
        $errBody = ''
        if ($_.Exception.Response) {
            try {
                $stream = $_.Exception.Response.GetResponseStream()
                $reader = New-Object System.IO.StreamReader($stream)
                $errBody = $reader.ReadToEnd()
            } catch {}
        }
        Write-Host "  FAIL  $($t.Name)  HTTP $code" -ForegroundColor Red
        if ($errBody) { Write-Host "        $errBody" -ForegroundColor DarkYellow }
    }
}

# Save summary
$summaryFile = "$OutDir/deployed-templates.json"
$Results | ConvertTo-Json -Depth 5 | Out-File -FilePath $summaryFile -Encoding utf8

Write-Host ""
Write-Host "=== DONE ===" -ForegroundColor Green
Write-Host ""
Write-Host "Summary saved to: $summaryFile"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Open Klaviyo - Content - Templates - find the 4 'BC -' templates"
Write-Host "  2. Preview each with a test profile"
Write-Host "  3. Build the new flow per .claude/bargain-chemist/templates/welcome-flow-build-spec.md"
Write-Host "     (assign each template to its email step)"
Write-Host ""

Remove-Item env:KLAVIYO_PRIVATE_KEY
