# Bargain Chemist - Browse Abandonment Flow Updater (PowerShell)
# Run from your pantrypilot folder: .\scripts\update-browse-abandonment-flow.ps1

$KLAV_KEY     = "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564"
$REVISION     = "2024-10-15"
$NEW_TEMPLATE = "YuWLyf"
$SUBJECT      = "Still thinking about it{% if first_name %}, {{ first_name }}{% endif %}?"
$PREVIEW      = "The item you were checking out is still available - and we will beat any competitor's price."
$BASE         = "https://a.klaviyo.com/api"

$FLOWS = @(
    @{ id = "RtiVC5"; name = "[Z] Browse Abandonment" },
    @{ id = "RSnNak"; name = "[Z] Browse Abandonment - Triple Pixel" }
)

$Headers = @{
    "Authorization" = "Klaviyo-API-Key $KLAV_KEY"
    "revision"      = $REVISION
    "Content-Type"  = "application/vnd.api+json"
    "Accept"        = "application/vnd.api+json"
}

function Invoke-Klav($Method, $Path, $Body = $null) {
    $uri = "$BASE$Path"
    $params = @{ Uri = $uri; Method = $Method; Headers = $Headers; ErrorAction = "Stop" }
    if ($Body) { $params["Body"] = ($Body | ConvertTo-Json -Depth 10) }
    try {
        $response = Invoke-RestMethod @params
        return $response
    } catch {
        $err = $_.Exception.Response
        Write-Host "  ERROR $Method $Path => $($err.StatusCode)" -ForegroundColor Red
        throw
    }
}

Write-Host ""
Write-Host "Bargain Chemist - Browse Abandonment Flow Updater" -ForegroundColor Cyan
Write-Host "Verifying Klaviyo connection..."

try {
    $check = Invoke-Klav "GET" "/flows/$($FLOWS[0].id)/"
    Write-Host "Connected to Klaviyo - flow found: $($check.data.id)" -ForegroundColor Green
} catch {
    Write-Host "Could not connect - check your API key or IP allowlist in Klaviyo Settings." -ForegroundColor Red
    exit 1
}

foreach ($flow in $FLOWS) {
    Write-Host ""
    Write-Host "--- $($flow.name) ($($flow.id)) ---" -ForegroundColor Yellow

    # Pause the flow so messages become editable
    Write-Host "  Pausing flow..." -ForegroundColor DarkYellow
    Invoke-Klav "PATCH" "/flows/$($flow.id)/" @{
        data = @{
            type       = "flow"
            id         = $flow.id
            attributes = @{ status = "manual" }
        }
    } | Out-Null
    Write-Host "  Flow paused" -ForegroundColor Green

    $actions = (Invoke-Klav "GET" "/flows/$($flow.id)/flow-actions/").data
    Write-Host "  Found $($actions.Count) action(s)"

    foreach ($action in $actions) {
        if ($action.attributes.action_type -ne "SEND_EMAIL") {
            Write-Host "  Skipping: $($action.attributes.action_type)"
            continue
        }

        Write-Host "  Email action: $($action.id)"

        $messages = (Invoke-Klav "GET" "/flow-actions/$($action.id)/flow-messages/").data
        Write-Host "  Found $($messages.Count) message(s)"

        foreach ($msg in $messages) {
            Write-Host "  Message $($msg.id) - status: $($msg.attributes.status)"

            # Step 1: set to draft so we can update it
            if ($msg.attributes.status -eq "live") {
                Write-Host "  Setting to Draft..." -ForegroundColor DarkYellow
                Invoke-Klav "PATCH" "/flow-messages/$($msg.id)/" @{
                    data = @{
                        type       = "flow-message"
                        id         = $msg.id
                        attributes = @{ status = "draft" }
                    }
                } | Out-Null
                Write-Host "  Set to Draft" -ForegroundColor Green
            }

            # Step 2: update template + content
            Write-Host "  Updating template to $NEW_TEMPLATE..." -ForegroundColor DarkYellow
            $updateBody = @{
                data = @{
                    type       = "flow-message"
                    id         = $msg.id
                    attributes = @{
                        definition = @{
                            channel = "email"
                            content = @{
                                subject      = $SUBJECT
                                preview_text = $PREVIEW
                            }
                        }
                    }
                    relationships = @{
                        template = @{ data = @{ type = "template"; id = $NEW_TEMPLATE } }
                    }
                }
            }
            Invoke-Klav "PATCH" "/flow-messages/$($msg.id)/" $updateBody | Out-Null
            Write-Host "  Template updated" -ForegroundColor Green

            # Step 3: set back to live
            Write-Host "  Setting back to Live..." -ForegroundColor DarkYellow
            Invoke-Klav "PATCH" "/flow-messages/$($msg.id)/" @{
                data = @{
                    type       = "flow-message"
                    id         = $msg.id
                    attributes = @{ status = "live" }
                }
            } | Out-Null
            Write-Host "  Message $($msg.id) is Live with new template" -ForegroundColor Green
        }
    }

    # Resume the flow
    Write-Host "  Resuming flow..." -ForegroundColor DarkYellow
    Invoke-Klav "PATCH" "/flows/$($flow.id)/" @{
        data = @{
            type       = "flow"
            id         = $flow.id
            attributes = @{ status = "live" }
        }
    } | Out-Null
    Write-Host "  Flow is Live" -ForegroundColor Green
}

Write-Host ""
Write-Host "Done! Check both flows in Klaviyo to confirm the new template is live." -ForegroundColor Cyan
