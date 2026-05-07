# Klaviyo: Create the "Welcome Series 2026 - No Coupon" flow via API (BETA endpoint)
# Leaves SehWRt (existing draft) completely untouched.
#
# REQUIREMENTS:
#   - .env.local has KLAVIYO_PRIVATE_KEY=<key with flows:write scope>
#   - klaviyo-deploy-templates.ps1 has been run AND succeeded (templates uploaded)
#   - You have the 4 template IDs (printed by the deploy script + saved to
#     .claude/bargain-chemist/snapshots/<date>/deployed-templates.json)
#
# WHAT THIS DOES:
#   - Calls POST /api/flows/ with revision header 2024-10-15.pre (beta)
#   - Builds the full flow definition from scratch:
#       Trigger (List - Website Form)
#         -> 5 min delay
#         -> Email 1 (Welcome to the Family)
#         -> 1 day delay
#         -> Conditional split (Placed Order? -> exit if YES)
#         -> Email 2 (Best Sellers)
#         -> 2 day delay
#         -> Conditional split (Placed Order? -> exit if YES)
#         -> Email 3 (Last Nudge)
#   - Created flow lands in DRAFT status (Klaviyo default for newly-created flows)
#
# CAVEATS (per Klaviyo docs):
#   - Beta API: not for prod, schema may shift. We only use it for one-shot creation.
#   - Once created, flow structure CANNOT be edited via API. To change: delete + recreate, or edit in UI.
#   - Rate limit: 100 flow creates/day. We use 1.

$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'   # Fixes PS 5.1 slow upload bug
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

# --- Load env ---
if (-not (Test-Path .env.local)) { Write-Error "ERROR: .env.local not found"; exit 1 }
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}
if (-not $env:KLAVIYO_PRIVATE_KEY) { Write-Error "ERROR: KLAVIYO_PRIVATE_KEY not set"; exit 1 }

# --- Locate the deployed-templates.json ---
$Date = Get-Date -Format 'yyyy-MM-dd'
$DeployedFile = ".claude/bargain-chemist/snapshots/$Date/deployed-templates.json"
if (-not (Test-Path $DeployedFile)) {
    Write-Error "ERROR: $DeployedFile not found. Run klaviyo-deploy-templates.ps1 first."
    exit 1
}
$Deployed = Get-Content $DeployedFile -Raw | ConvertFrom-Json

function Get-TemplateId([string]$Name) {
    $hit = $Deployed | Where-Object { $_.name -eq $Name }
    if (-not $hit) { Write-Error "ERROR: template '$Name' not found in deployed-templates.json"; exit 1 }
    return $hit.id
}

$Tpl1 = Get-TemplateId 'BC - Welcome Email 1 - Welcome to the Family'
$Tpl2 = Get-TemplateId 'BC - Welcome Email 2 - Best Sellers'
$Tpl3 = Get-TemplateId 'BC - Welcome Email 3 - Last Nudge'

Write-Host "Using templates:" -ForegroundColor Cyan
Write-Host "  E1 = $Tpl1"
Write-Host "  E2 = $Tpl2"
Write-Host "  E3 = $Tpl3"

# --- Trigger: which list ID? Pull from existing SehWRt or override below ---
# OPTION A: Set this manually if you know the Website Form list ID:
$WebsiteFormListId = $env:KLAVIYO_WEBSITE_FORM_LIST_ID  # Set this in .env.local for clarity
if (-not $WebsiteFormListId) {
    Write-Host ""
    Write-Host "WARNING: KLAVIYO_WEBSITE_FORM_LIST_ID not set in .env.local." -ForegroundColor Yellow
    Write-Host "         Add it (find the list ID in Klaviyo - Lists & Segments - click the list - URL contains the ID)" -ForegroundColor Yellow
    Write-Host "         Aborting create. Add the variable and re-run." -ForegroundColor Yellow
    exit 1
}

# --- Build the flow definition ---
# Schema mirrored from SehWRt-with-full-definition.json (canonical).
# NOTE: linear flow (no conditional splits) for the API-creation pass. After the
# flow lands in DRAFT, add the two "Placed Order? -> exit" splits in the Klaviyo UI
# (we don't have a verified ConditionalBranchActionData schema).

$WeekDays = @('monday','tuesday','wednesday','thursday','friday','saturday','sunday')

function New-EmailMessage([string]$Name, [string]$Subject, [string]$Preview, [string]$TemplateId) {
    return [ordered]@{
        name                  = $Name
        from_email            = 'hello@bargainchemist.co.nz'
        from_label            = 'Bargain Chemist'
        reply_to_email        = $null
        cc_email              = $null
        bcc_email             = $null
        subject_line          = $Subject
        preview_text          = $Preview
        template_id           = $TemplateId
        smart_sending_enabled = $true
        transactional         = $false
        add_tracking_params   = $true
        custom_tracking_params = $null
        additional_filters    = $null
    }
}

function New-Delay([string]$TempId, [string]$Unit, [int]$Value, [string]$NextId) {
    $data = [ordered]@{
        unit            = $Unit
        value           = $Value
        secondary_value = $null
        timezone        = 'profile'
    }
    # delay_until_weekdays only valid when unit is 'days'
    if ($Unit -eq 'days') { $data['delay_until_weekdays'] = $WeekDays }
    return [ordered]@{
        temporary_id = $TempId
        type         = 'time-delay'
        data         = $data
        links        = @{ next = $NextId }
    }
}

function New-EmailAction([string]$TempId, $Message, $NextId) {
    return [ordered]@{
        temporary_id = $TempId
        type         = 'send-email'
        data         = [ordered]@{
            message = $Message
            status  = 'draft'
        }
        links = @{ next = $NextId }
    }
}

$Msg1 = New-EmailMessage `
    'Welcome Email 1 - Welcome to the Family' `
    "Welcome to Bargain Chemist, {{ first_name|default:'there' }}" `
    "NZ's most trusted pharmacy - and your best price starts now." `
    $Tpl1
$Msg2 = New-EmailMessage `
    'Welcome Email 2 - Best Sellers' `
    "{{ first_name|default:'There' }}, here's what's flying off our shelves" `
    "NZ's best-selling vitamins, skincare and pharmacy essentials - see what Kiwis love." `
    $Tpl2
$Msg3 = New-EmailMessage `
    'Welcome Email 3 - Last Nudge' `
    "{{ first_name|default:'Still here' }} - 3 reasons NZ shops at Bargain Chemist" `
    "Price beat guarantee, free shipping, trusted pharmacists since 1984." `
    $Tpl3

$FlowDef = [ordered]@{
    triggers = @(
        [ordered]@{ type = 'list'; id = $WebsiteFormListId }
    )
    profile_filter  = $null
    entry_action_id = 'delay-1'
    actions = @(
        New-Delay        'delay-1' 'minutes' 5 'email-1'
        New-EmailAction  'email-1' $Msg1     'delay-2'
        New-Delay        'delay-2' 'days'    1 'email-2'
        New-EmailAction  'email-2' $Msg2     'delay-3'
        New-Delay        'delay-3' 'days'    2 'email-3'
        New-EmailAction  'email-3' $Msg3     $null
    )
}

$Body = @{
    data = @{
        type = 'flow'
        attributes = @{
            name       = 'Welcome Series 2026 - No Coupon'
            definition = $FlowDef
        }
    }
} | ConvertTo-Json -Depth 20

# Save the request body for debugging / inspection
$ReqFile = ".claude/bargain-chemist/snapshots/$Date/create-flow-request.json"
$Body | Out-File -FilePath $ReqFile -Encoding utf8
Write-Host ""
Write-Host "Request body saved to: $ReqFile" -ForegroundColor DarkGray

$Headers = @{
    'Authorization' = "Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
    'revision'      = '2024-10-15.pre'   # BETA header for create-flow
    'Accept'        = 'application/vnd.api+json'
    'Content-Type'  = 'application/vnd.api+json'
}

Write-Host ""
Write-Host "POST https://a.klaviyo.com/api/flows/ ..." -ForegroundColor Cyan

try {
    # Use curl.exe (sidesteps PS 5.1 HTTP stack bugs)
    $TempDir  = Join-Path $env:TEMP "klaviyo-flow-$([guid]::NewGuid().ToString('N').Substring(0,8))"
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    $bodyFile = Join-Path $TempDir 'body.json'
    $respFile = Join-Path $TempDir 'resp.json'
    [System.IO.File]::WriteAllText($bodyFile, $Body, [System.Text.UTF8Encoding]::new($false))

    $curlArgs = @(
        '--silent', '--show-error',
        '--max-time', '90',
        '--write-out', '%{http_code}',
        '--output', $respFile,
        '-X', 'POST',
        '-H', "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)",
        '-H', 'revision: 2024-10-15.pre',
        '-H', 'Accept: application/vnd.api+json',
        '-H', 'Content-Type: application/vnd.api+json',
        '--data-binary', "@$bodyFile",
        'https://a.klaviyo.com/api/flows/'
    )
    $httpCode = & curl.exe @curlArgs

    if ($httpCode -ne '201' -and $httpCode -ne '200') {
        Write-Host ""
        Write-Host "  FAIL  HTTP $httpCode" -ForegroundColor Red
        if (Test-Path $respFile) {
            $errBody = Get-Content $respFile -Raw
            $errFile = ".claude/bargain-chemist/snapshots/$Date/create-flow-error.json"
            $errBody | Out-File -FilePath $errFile -Encoding utf8
            Write-Host "  Error body saved to $errFile" -ForegroundColor DarkYellow
            Write-Host ""
            Write-Host $errBody -ForegroundColor DarkYellow
        }
        Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
        Remove-Item env:KLAVIYO_PRIVATE_KEY
        exit 1
    }

    $json = Get-Content $respFile -Raw | ConvertFrom-Json
    Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    $flowId = $json.data.id
    Write-Host ""
    Write-Host ""
    Write-Host "  SUCCESS - flow created" -ForegroundColor Green
    Write-Host "  Flow ID:  $flowId" -ForegroundColor Green
    Write-Host "  Edit URL: https://www.klaviyo.com/flow/$flowId/edit" -ForegroundColor Green
    Write-Host ""
    Write-Host "Saving response to: .claude/bargain-chemist/snapshots/$Date/created-flow-response.json"
    $json | ConvertTo-Json -Depth 20 | Out-File -FilePath ".claude/bargain-chemist/snapshots/$Date/created-flow-response.json" -Encoding utf8

    Write-Host ""
    Write-Host "Next: open the flow in Klaviyo, preview each email, then turn ON when ready."
    Write-Host "      SehWRt is unchanged."
} catch {
    $code = $_.Exception.Response.StatusCode.value__
    Write-Host ""
    Write-Host "  FAIL  HTTP $code" -ForegroundColor Red
    if ($_.Exception.Response) {
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $errBody = $reader.ReadToEnd()
            $errFile = ".claude/bargain-chemist/snapshots/$Date/create-flow-error.json"
            $errBody | Out-File -FilePath $errFile -Encoding utf8
            Write-Host "  Error body saved to $errFile" -ForegroundColor DarkYellow
            Write-Host ""
            Write-Host "Common causes:"
            Write-Host "  - API key missing flows:write scope (check Klaviyo - Settings - API Keys)"
            Write-Host "  - Beta endpoint schema changed (paste error JSON to Claude for diagnosis)"
            Write-Host "  - List ID wrong - verify KLAVIYO_WEBSITE_FORM_LIST_ID"
            Write-Host "  - Template IDs from deployed-templates.json don't match account"
        } catch {}
    }
}

Remove-Item env:KLAVIYO_PRIVATE_KEY
