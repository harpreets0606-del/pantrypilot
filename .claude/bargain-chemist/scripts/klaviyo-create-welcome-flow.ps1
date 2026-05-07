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
# Action references use temporary_id; Klaviyo replaces with real IDs in response.

$FlowDef = [ordered]@{
    triggers = @(
        @{
            type = 'list'
            list_id = $WebsiteFormListId
        }
    )
    profile_filter = @{
        # Re-entry guard: skip if been in this flow in last 30 days
        condition_groups = @(
            @{
                conditions = @(
                    @{
                        type = 'profile-property-condition'
                        # Klaviyo evaluates "has not been in flow X in last N days" as a flow filter, not profile filter.
                        # Leave this empty here — set the in-flow re-entry guard manually if Klaviyo's API exposes it.
                    }
                )
            }
        )
    }
    actions = @(
        # Step 1: 5 minute delay
        [ordered]@{
            temporary_id = 'delay-1'
            type = 'time-delay'
            data = @{ unit = 'minutes'; value = 5 }
            links = @{ next = 'email-1' }
        },
        # Step 2: Email 1
        [ordered]@{
            temporary_id = 'email-1'
            type = 'send-email'
            data = @{
                template_id          = $Tpl1
                subject              = "Welcome to Bargain Chemist, {{ first_name|default:'there' }}"
                preview_text         = "NZ's most trusted pharmacy - and your best price starts now."
                from_email           = 'hello@bargainchemist.co.nz'
                from_label           = 'Bargain Chemist'
                reply_to_email       = 'hello@bargainchemist.co.nz'
                smart_sending        = $true
                add_tracking_params  = $true
                custom_tracking_params = @(
                    @{ type = 'static'; value = 'klaviyo'; name = 'utm_source' },
                    @{ type = 'static'; value = 'email';    name = 'utm_medium' },
                    @{ type = 'static'; value = 'welcome_e1_2026'; name = 'utm_campaign' }
                )
            }
            links = @{ next = 'delay-2' }
        },
        # Step 3: 1 day delay
        [ordered]@{
            temporary_id = 'delay-2'
            type = 'time-delay'
            data = @{ unit = 'days'; value = 1 }
            links = @{ next = 'split-1' }
        },
        # Step 4: Conditional split - Placed Order since starting flow?
        [ordered]@{
            temporary_id = 'split-1'
            type = 'conditional-split'
            data = @{
                condition_groups = @(
                    @{
                        conditions = @(
                            @{
                                type = 'metric-condition'
                                metric_filter = @{
                                    metric_name = 'Placed Order'
                                    measurement = 'count'
                                    operator = 'greater-than-or-equal'
                                    value = 1
                                    timeframe = 'since-flow-start'
                                }
                            }
                        )
                    }
                )
            }
            links = @{
                'true'  = $null      # YES -> exit (no further action)
                'false' = 'email-2'  # NO -> continue
            }
        },
        # Step 5: Email 2
        [ordered]@{
            temporary_id = 'email-2'
            type = 'send-email'
            data = @{
                template_id          = $Tpl2
                subject              = "{{ first_name|default:'There' }}, here's what's flying off our shelves"
                preview_text         = "NZ's best-selling vitamins, skincare and pharmacy essentials - see what Kiwis love."
                from_email           = 'hello@bargainchemist.co.nz'
                from_label           = 'Bargain Chemist'
                reply_to_email       = 'hello@bargainchemist.co.nz'
                smart_sending        = $true
                add_tracking_params  = $true
                custom_tracking_params = @(
                    @{ type = 'static'; value = 'klaviyo'; name = 'utm_source' },
                    @{ type = 'static'; value = 'email';    name = 'utm_medium' },
                    @{ type = 'static'; value = 'welcome_e2_2026'; name = 'utm_campaign' }
                )
            }
            links = @{ next = 'delay-3' }
        },
        # Step 6: 2 day delay
        [ordered]@{
            temporary_id = 'delay-3'
            type = 'time-delay'
            data = @{ unit = 'days'; value = 2 }
            links = @{ next = 'split-2' }
        },
        # Step 7: Conditional split #2
        [ordered]@{
            temporary_id = 'split-2'
            type = 'conditional-split'
            data = @{
                condition_groups = @(
                    @{
                        conditions = @(
                            @{
                                type = 'metric-condition'
                                metric_filter = @{
                                    metric_name = 'Placed Order'
                                    measurement = 'count'
                                    operator = 'greater-than-or-equal'
                                    value = 1
                                    timeframe = 'since-flow-start'
                                }
                            }
                        )
                    }
                )
            }
            links = @{
                'true'  = $null
                'false' = 'email-3'
            }
        },
        # Step 8: Email 3
        [ordered]@{
            temporary_id = 'email-3'
            type = 'send-email'
            data = @{
                template_id          = $Tpl3
                subject              = "{{ first_name|default:'Still here' }} - 3 reasons NZ shops at Bargain Chemist"
                preview_text         = "Price beat guarantee, free shipping, trusted pharmacists since 1984."
                from_email           = 'hello@bargainchemist.co.nz'
                from_label           = 'Bargain Chemist'
                reply_to_email       = 'hello@bargainchemist.co.nz'
                smart_sending        = $true
                add_tracking_params  = $true
                custom_tracking_params = @(
                    @{ type = 'static'; value = 'klaviyo'; name = 'utm_source' },
                    @{ type = 'static'; value = 'email';    name = 'utm_medium' },
                    @{ type = 'static'; value = 'welcome_e3_2026'; name = 'utm_campaign' }
                )
            }
            links = @{ next = $null }   # End of flow
        }
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
    $resp = Invoke-WebRequest -Uri 'https://a.klaviyo.com/api/flows/' `
                              -Headers $Headers `
                              -Method Post `
                              -Body $Body `
                              -ErrorAction Stop `
                              -UseBasicParsing
    $json = $resp.Content | ConvertFrom-Json
    $flowId = $json.data.id
    Write-Host ""
    Write-Host "  SUCCESS - flow created" -ForegroundColor Green
    Write-Host "  Flow ID:  $flowId" -ForegroundColor Green
    Write-Host "  Edit URL: https://www.klaviyo.com/flow/$flowId/edit" -ForegroundColor Green
    Write-Host ""
    Write-Host "Saving response to: .claude/bargain-chemist/snapshots/$Date/created-flow-response.json"
    $resp.Content | Out-File -FilePath ".claude/bargain-chemist/snapshots/$Date/created-flow-response.json" -Encoding utf8

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
