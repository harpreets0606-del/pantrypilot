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
    "Content-Type"  = "application/json"
    "Accept"        = "application/json"
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
    $account = Invoke-Klav "GET" "/accounts/"
    Write-Host "Connected to Klaviyo account: $($account.data[0].id)" -ForegroundColor Green
} catch {
    Write-Host "Could not connect - check your API key or IP allowlist in Klaviyo Settings." -ForegroundColor Red
    exit 1
}

foreach ($flow in $FLOWS) {
    Write-Host ""
    Write-Host "--- $($flow.name) ($($flow.id)) ---" -ForegroundColor Yellow

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
            if ($msg.attributes.status -eq "live") {
                Write-Host "  Setting message $($msg.id) to Draft..." -ForegroundColor DarkYellow
                $body = @{
                    data = @{
                        type       = "flow-message"
                        id         = $msg.id
                        attributes = @{ status = "draft" }
                    }
                }
                Invoke-Klav "PATCH" "/flow-messages/$($msg.id)/" $body | Out-Null
                Write-Host "  Message $($msg.id) set to Draft" -ForegroundColor Green
            }
        }

        Write-Host "  Creating new message with template $NEW_TEMPLATE..." -ForegroundColor DarkYellow
        $newMsg = @{
            data = @{
                type       = "flow-message"
                attributes = @{
                    status     = "live"
                    definition = @{
                        channel = "email"
                        content = @{
                            subject      = $SUBJECT
                            preview_text = $PREVIEW
                        }
                    }
                }
                relationships = @{
                    "flow-action" = @{ data = @{ type = "flow-action"; id = $action.id } }
                    template      = @{ data = @{ type = "template";    id = $NEW_TEMPLATE } }
                }
            }
        }
        $created = Invoke-Klav "POST" "/flow-messages/" $newMsg
        Write-Host "  New message created: $($created.data.id) - Live" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Done! Check both flows in Klaviyo to confirm the new template is live." -ForegroundColor Cyan
