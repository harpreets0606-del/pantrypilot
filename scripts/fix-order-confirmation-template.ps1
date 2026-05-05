# Fix Order Confirmation template + inspect Post-Purchase and Back in Stock
# Run: .\scripts\fix-order-confirmation-template.ps1

$KLAV_KEY      = "pk_XCgiqg_6f9d304481501e6aef41ce91b33d767564"
$REVISION      = "2024-10-15"
$BASE          = "https://a.klaviyo.com/api"

$FLOW_ID       = "Smp9WN"   # [Z] Order Confirmation
$NEW_TEMPLATE  = "QRdbLf"   # [Z] Order Confirmation - v2 (with CTA)
$NEW_SUBJECT   = "Your Bargain Chemist order #{{ event.OrderId }} is confirmed!"
$NEW_PREVIEW   = "We are packing it now - here is everything you need to know."

$Headers = @{
    "Authorization" = "Klaviyo-API-Key $KLAV_KEY"
    "revision"      = $REVISION
    "Content-Type"  = "application/vnd.api+json"
    "Accept"        = "application/vnd.api+json"
}

function Invoke-Klav($Method, $Path, $Body = $null) {
    $uri    = "$BASE$Path"
    $params = @{ Uri = $uri; Method = $Method; Headers = $Headers; ErrorAction = "Stop" }
    if ($Body) { $params["Body"] = ($Body | ConvertTo-Json -Depth 10) }
    try   { return Invoke-RestMethod @params }
    catch {
        $code = $_.Exception.Response.StatusCode
        $msg  = $_.ErrorDetails.Message
        Write-Host "  ERROR $Method $Path => $code : $msg" -ForegroundColor Red
        throw
    }
}

# ── Part 1: Fix Order Confirmation ────────────────────────────────────────────
Write-Host ""
Write-Host "Part 1: Fix Order Confirmation Template" -ForegroundColor Cyan
Write-Host ("-" * 50)

# Pause flow
Write-Host "  Pausing flow $FLOW_ID..." -ForegroundColor DarkYellow
Invoke-Klav "PATCH" "/flows/$FLOW_ID/" @{
    data = @{ type = "flow"; id = $FLOW_ID; attributes = @{ status = "manual" } }
} | Out-Null
Write-Host "  Flow paused" -ForegroundColor Green

# Get flow actions
$actions = (Invoke-Klav "GET" "/flows/$FLOW_ID/flow-actions/").data
Write-Host "  Found $($actions.Count) action(s)"

foreach ($action in $actions) {
    if ($action.attributes.action_type -ne "SEND_EMAIL") {
        Write-Host "  Skipping [$($action.attributes.action_type)]"
        continue
    }

    Write-Host "  Email action: $($action.id)" -ForegroundColor Yellow
    $messages = (Invoke-Klav "GET" "/flow-actions/$($action.id)/flow-messages/").data

    foreach ($msg in $messages) {
        $mid    = $msg.id
        $status = $msg.attributes.status
        Write-Host "    Message $mid — current status: $status"

        # Set to draft if needed
        if ($status -ne "draft") {
            Write-Host "    Setting to draft..." -ForegroundColor DarkYellow
            Invoke-Klav "PATCH" "/flow-messages/$mid/" @{
                data = @{ type = "flow-message"; id = $mid; attributes = @{ status = "draft" } }
            } | Out-Null
            Write-Host "    Draft" -ForegroundColor Green
        }

        # Update template + subject + preview
        Write-Host "    Assigning template $NEW_TEMPLATE..." -ForegroundColor DarkYellow
        Invoke-Klav "PATCH" "/flow-messages/$mid/" @{
            data = @{
                type          = "flow-message"
                id            = $mid
                attributes    = @{
                    definition = @{
                        channel = "email"
                        content = @{
                            subject      = $NEW_SUBJECT
                            preview_text = $NEW_PREVIEW
                        }
                    }
                }
                relationships = @{
                    template = @{ data = @{ type = "template"; id = $NEW_TEMPLATE } }
                }
            }
        } | Out-Null
        Write-Host "    Template updated" -ForegroundColor Green

        # Set back to live
        Write-Host "    Setting to live..." -ForegroundColor DarkYellow
        Invoke-Klav "PATCH" "/flow-messages/$mid/" @{
            data = @{ type = "flow-message"; id = $mid; attributes = @{ status = "live" } }
        } | Out-Null
        Write-Host "    Message $mid is live with new template" -ForegroundColor Green
    }
}

# Resume flow
Write-Host "  Resuming flow..." -ForegroundColor DarkYellow
Invoke-Klav "PATCH" "/flows/$FLOW_ID/" @{
    data = @{ type = "flow"; id = $FLOW_ID; attributes = @{ status = "live" } }
} | Out-Null
Write-Host "  Flow is live" -ForegroundColor Green
Write-Host "  Edit: https://www.klaviyo.com/flow/$FLOW_ID/edit" -ForegroundColor Cyan

# ── Part 2: Inspect zero-recipient flows ──────────────────────────────────────
Write-Host ""
Write-Host "Part 2: Inspect Zero-Recipient Flows" -ForegroundColor Cyan
Write-Host ("-" * 50)

$inspect = @(
    @{ id = "RDJQYM"; name = "[Z] Post-Purchase Series" },
    @{ id = "Ysj7sg"; name = "[Z] Back in Stock" }
)

foreach ($f in $inspect) {
    Write-Host ""
    Write-Host "  --- $($f.name) ($($f.id)) ---" -ForegroundColor Yellow

    $flow    = Invoke-Klav "GET" "/flows/$($f.id)/"
    $trigger = $flow.data.attributes.triggerType
    Write-Host "  Trigger type: $trigger"

    $actions = (Invoke-Klav "GET" "/flows/$($f.id)/flow-actions/?page[size]=50").data
    Write-Host "  Actions: $($actions.Count)"

    foreach ($action in $actions) {
        $atype = $action.attributes.action_type
        $aid   = $action.id
        Write-Host "    [$atype] id=$aid"

        if ($atype -eq "TIME_DELAY") {
            Write-Host "      Settings: $($action.attributes.settings | ConvertTo-Json -Depth 3 -Compress)"
        }
        if ($atype -eq "CONDITIONAL_SPLIT" -or $atype -eq "TRIGGER_SPLIT") {
            Write-Host "      Condition: $($action.attributes.settings | ConvertTo-Json -Depth 8 -Compress)"
        }
        if ($atype -eq "SEND_EMAIL") {
            $msgs = (Invoke-Klav "GET" "/flow-actions/$aid/flow-messages/").data
            foreach ($m in $msgs) {
                Write-Host "      msg=$($m.id) | status=$($m.attributes.status) | $($m.attributes.name)"
                $defn = $m.attributes.definition
                if ($defn) {
                    Write-Host "      subject: $($defn.content.subject)"
                }
            }
        }
    }
}

Write-Host ""
Write-Host "Done." -ForegroundColor Cyan
