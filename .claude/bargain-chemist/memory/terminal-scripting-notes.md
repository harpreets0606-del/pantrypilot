# Terminal scripting notes — for Bargain Chemist deployment

*Working notes captured during this session. Updated whenever we discover something that breaks or surprises.*

## Environment

- **User's machine:** Windows 10/11
- **Shell:** Windows PowerShell **5.1** (the built-in one, not PS 7+)
  - Confirmed by behaviour: PowerShell 5.1 is the one with the `Invoke-WebRequest` progress-bar performance bug
- **Repo path:** `C:\Users\HarpreetSingh\pantrypilot`
- **Working branch:** `claude/klaviyo-access-integration-g7txQ` (per system instructions); user may also be on parallel agent branches like `claude/fetch-klaviyo-flows-zRRFH`
- **Encoding:** PS 5.1 `Out-File -Encoding utf8` writes UTF-8 **with BOM**. `Set-Content -Encoding utf8` does the same. To get clean UTF-8 we'd need `[System.IO.File]::WriteAllText($path, $content, [System.Text.UTF8Encoding]::new($false))` or use PS 7's `-Encoding utf8NoBOM`.

## Hard-won fixes

### -2. NEVER use `$NN` (digit literals like `$79`) inside double-quoted PowerShell strings

**Symptom:** Output text loses chunks like `$79`, leaving garbled phrases like `Free shipping over .`
**Cause:** PowerShell parses `$<digits>` in double quotes as automatic positional variables (`$1` ... `$9` ... `$79`). They're undefined in normal scripts → expand to empty string. The trailing period eats whatever's left.
**Example:**
```powershell
"Free shipping over $79."   # becomes: "Free shipping over ."  (BROKEN)
```
**Fix:** Use single-quoted strings for any literal containing `$<digits>`:
```powershell
'Free shipping over $79.'   # correct
```
Or backtick-escape:
```powershell
"Free shipping over `$79."  # correct
```
**Caught in:** `klaviyo-deploy-cart-flow.ps1` Plan hashtable (Preview text) — broke E2 preview deployment 2026-05-07. Fixed by switching the Plan strings to single-quote, doubling internal apostrophes (`it''s`), and escaping the printout at the end.

**Rule for future scripts:** when a script has user-facing copy strings, default to single quotes. Use double quotes only when you genuinely need PS variable interpolation (e.g. `"$($p.ActionId)"`).

---

### -1. NEVER write non-ASCII characters in `.ps1` files (without UTF-8 BOM)

**Symptom:** Script fails to parse with errors like "Missing closing '}'", "Unexpected token", or weird `â€"` strings appearing in error messages.
**Cause:** PowerShell 5.1 reads `.ps1` files as Windows-1252 by default. Any UTF-8 multi-byte char (em-dash, en-dash, smart quotes) gets mojibake'd into garbage that breaks string parsing.
**Fix (mandatory for any .ps1 we write):**
1. Stick to ASCII-only in script content. Use `-` instead of em/en-dash. Use straight quotes only.
2. If non-ASCII is unavoidable, save the file with a UTF-8 BOM (bytes `0xEF 0xBB 0xBF` at start).

**Status:** Applied 2026-05-07. All 10 PS scripts audited; 3 had em-dashes — fixed via BOM + ASCII replacement. Going forward: write ASCII-only by default.

---

### 0. WHEN PS 5.1 HTTP HANGS - JUST USE curl.exe

**This is the lesson of the session.** Don't waste time trying to fix PS 5.1's HTTP cmdlets when they hang. Windows 10 1803+ ships `curl.exe` (real curl, not the PS alias) at `C:\Windows\System32\curl.exe`. It uses a completely different HTTP stack and doesn't have any of these issues.

**Pattern for any Klaviyo API write from PowerShell:**
```powershell
# 1. Build body in PS, write to temp file
$body = $obj | ConvertTo-Json -Depth 10 -Compress
$bodyFile = Join-Path $env:TEMP "kv-$([guid]::NewGuid().ToString('N').Substring(0,8)).json"
[System.IO.File]::WriteAllText($bodyFile, $body, [System.Text.UTF8Encoding]::new($false))

# 2. Shell out to curl.exe
$respFile = "$bodyFile.resp"
$httpCode = & curl.exe `
    --silent --show-error `
    --max-time 60 `
    --write-out '%{http_code}' `
    --output $respFile `
    -X POST `
    -H "Authorization: Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)" `
    -H 'revision: 2024-10-15' `
    -H 'Accept: application/vnd.api+json' `
    -H 'Content-Type: application/vnd.api+json' `
    --data-binary "@$bodyFile" `
    'https://a.klaviyo.com/api/templates/'

# 3. Parse response
if ($httpCode -in '200','201') {
    $json = Get-Content $respFile -Raw | ConvertFrom-Json
    # use $json.data.id etc
} else {
    Write-Host "FAIL HTTP $httpCode"
    Get-Content $respFile -Raw | Write-Host
}
```

**Status:** Applied to `klaviyo-deploy-templates.ps1` and `klaviyo-create-welcome-flow.ps1` after `Invoke-WebRequest` AND `Invoke-RestMethod` BOTH hung indefinitely on the same machine (2026-05-07, fix v3 — final).

**Default to this pattern from the start. Don't try Invoke-WebRequest/RestMethod first.**

---

### 1. `Invoke-WebRequest` hangs on POST — PS 5.1 multi-cause issue
**Symptom:** Script prints a header line, then hangs forever (or 30+ seconds per call) on the actual POST. `Ctrl+C` doesn't always stop it — must close the window.
**Cause(s):** PS 5.1 has multiple compounding bugs around `Invoke-WebRequest`:
1. Hidden progress bar that synchronously stalls large requests by 10-100x
2. TLS 1.2 not always default — Klaviyo requires it
3. `Invoke-WebRequest` itself has known hang issues with body POSTs even with `-UseBasicParsing`
**Fix (all four required):**
```powershell
$ProgressPreference = 'SilentlyContinue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)
$json = Invoke-RestMethod -Uri $url `
                          -Headers $Headers `
                          -Method Post `
                          -Body $bodyBytes `
                          -ContentType 'application/vnd.api+json' `
                          -TimeoutSec 60 `
                          -DisableKeepAlive
```
Key changes from `Invoke-WebRequest`:
- **Use `Invoke-RestMethod`** — cleaner, no hidden parsing, returns the parsed object directly (no `.Content`)
- **Send body as UTF-8 bytes** — string body can hang on large POSTs in PS 5.1
- **`-DisableKeepAlive`** — forces fresh connection; keep-alive can hang with some endpoints
- **`-TimeoutSec`** is essential; default can be effectively infinite
**Status:** Applied to `klaviyo-find-list-id.ps1`, `klaviyo-deploy-templates.ps1`, `klaviyo-create-welcome-flow.ps1` (2026-05-07, second pass after first fix didn't fully resolve).

### 2. `Out-File` saves JSON as one-byte-per-line decimal codes
**Symptom:** Output JSON files are unreadable; opening them shows numbers like `123\n34\n100...`
**Cause:** `Out-File` was being passed an array of bytes (from `Invoke-WebRequest.RawContentStream` or similar) instead of a string, and PS 5.1 happily wrote each int on its own line.
**Fix:** Use `$resp.Content` (string) not `.RawContentStream`, and pipe via `Out-File -Encoding utf8` OR write with `[System.IO.File]::WriteAllText`. If you've already got malformed files, decode them in Python:
```python
text = ''.join(chr(int(line)) for line in open(path) if line.strip().isdigit())
```
**Status:** Original `klaviyo-fetch.ps1` had this bug; the deploy/create scripts use `.Content` directly so OK.

### 3. Execution Policy blocks scripts
**Symptom:** Running a `.ps1` file shows red error: "running scripts is disabled on this system" or "is not digitally signed".
**Cause:** Default Windows execution policy is Restricted or RemoteSigned with downloaded scripts treated as unsigned.
**Fix (per session, no admin needed):**
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### 4. `bash` not present on Windows
**Confirmed:** `where.exe bash` returns nothing. Don't write `.sh` scripts for this user — write `.ps1`.

### 5. Branch confusion when multiple Claude agents run in parallel
**Symptom:** `git push origin <branch>` fails with "src refspec does not match any" because user is on a different local branch.
**Cause:** A separate Claude agent worked on a parallel branch (e.g. `claude/fetch-klaviyo-flows-zRRFH`) and the user's HEAD is on that one, not the integration branch.
**Fix:**
```powershell
git branch --show-current      # diagnose
git push origin <local-name>:<remote-name>   # push current branch under different name
# OR
git checkout <correct-branch>
```

### 6. Merge conflicts in `snapshots/` after `git pull`
**Symptom:** Many `CONFLICT (add/add)` lines on JSON files in `.claude/bargain-chemist/snapshots/`.
**Cause:** Both local and remote independently created the same snapshot files (separate Claude agents pulling same Klaviyo data).
**Fix:** Snapshot data is reproducible — always take the remote version:
```powershell
git checkout --theirs .claude/bargain-chemist/snapshots/
git add .claude/bargain-chemist/snapshots/
git commit -m "Resolve snapshot conflicts - take remote"
```

## API conventions for Klaviyo scripts

- Always include three headers:
  ```
  Authorization: Klaviyo-API-Key <key>
  revision: 2024-10-15        (or 2024-10-15.pre for beta endpoints like POST /api/flows/)
  Accept: application/vnd.api+json
  Content-Type: application/vnd.api+json   (only on writes)
  ```
- Request body wrapping: `{ "data": { "type": "<resource>", "attributes": { ... } } }`
- Always `-UseBasicParsing -TimeoutSec 60`
- Always set `$ProgressPreference = 'SilentlyContinue'`
- Save the request body to `snapshots/<date>/` for debugging before sending
- On error, capture and save the response body — Klaviyo's error JSON is usually very specific

## Standard script skeleton

```powershell
$ErrorActionPreference = 'Continue'
$ProgressPreference    = 'SilentlyContinue'

# Load .env.local
if (-not (Test-Path .env.local)) { Write-Error 'no .env.local'; exit 1 }
Get-Content .env.local | ForEach-Object {
    if ($_ -match '^\s*([^#=]+)\s*=\s*(.+)\s*$') {
        Set-Item "env:$($Matches[1].Trim())" $Matches[2].Trim()
    }
}

$Headers = @{
    'Authorization' = "Klaviyo-API-Key $($env:KLAVIYO_PRIVATE_KEY)"
    'revision'      = '2024-10-15'
    'Accept'        = 'application/vnd.api+json'
}

# ... API call(s) with -UseBasicParsing -TimeoutSec 60 ...

Remove-Item env:KLAVIYO_PRIVATE_KEY   # clean up at end
```

## What goes in this file

Whenever we hit a Windows/PowerShell/Klaviyo terminal gotcha, append it here. **Do NOT** write a one-off fix and forget it — the next session will trip on the same thing. Add:
- Symptom (one line)
- Cause (one line)
- Fix (code snippet)
- Date discovered + which script(s) it affected
