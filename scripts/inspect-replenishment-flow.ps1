# Inspect Replenishment Flow Structure
# Run: .\scripts\inspect-replenishment-flow.ps1

$KLAV_KEY = "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564"
$REVISION = "2024-10-15"
$FLOW_ID  = "XRUj2w"
$BASE     = "https://a.klaviyo.com/api"

$Headers = @{
    "Authorization" = "Klaviyo-API-Key $KLAV_KEY"
    "revision"      = $REVISION
    "Content-Type"  = "application/vnd.api+json"
    "Accept"        = "application/vnd.api+json"
}

function Invoke-Klav($Method, $Path) {
    $uri = "$BASE$Path"
    try {
        return Invoke-RestMethod -Uri $uri -Method $Method -Headers $Headers -ErrorAction Stop
    } catch {
        Write-Host "  ERROR $Method $Path => $($_.Exception.Response.StatusCode)" -ForegroundColor Red
        throw
    }
}

Write-Host ""
Write-Host "Inspecting flow: $FLOW_ID" -ForegroundColor Cyan

$actions = (Invoke-Klav "GET" "/flows/$FLOW_ID/flow-actions/?page[size]=100").data
Write-Host "Total actions: $($actions.Count)"
Write-Host ""

foreach ($action in $actions) {
    $type  = $action.attributes.action_type
    $id    = $action.id
    $attrs = $action.attributes

    Write-Host "--- Action: $id ---" -ForegroundColor Yellow
    Write-Host "  Type: $type"

    if ($type -eq "TIME_DELAY") {
        Write-Host "  Settings: $($attrs.settings | ConvertTo-Json -Depth 5 -Compress)" -ForegroundColor Cyan
    }

    if ($type -eq "CONDITIONAL_SPLIT") {
        Write-Host "  Condition: $($attrs.settings | ConvertTo-Json -Depth 10 -Compress)" -ForegroundColor Magenta
    }

    if ($type -eq "TRIGGER_SPLIT") {
        Write-Host "  Trigger Split: $($attrs.settings | ConvertTo-Json -Depth 10 -Compress)" -ForegroundColor Magenta
    }

    if ($type -eq "SEND_EMAIL") {
        $msgs = (Invoke-Klav "GET" "/flow-actions/$id/flow-messages/").data
        foreach ($msg in $msgs) {
            Write-Host "  Message: $($msg.id) - status: $($msg.attributes.status)"
        }
    }

    Write-Host ""
}

Write-Host "Done." -ForegroundColor Cyan
