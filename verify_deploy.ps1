# verify_deploy.ps1 — Post-deploy smoke test for PandasAI (Render backend + Vercel frontend)
# Usage:  .\verify_deploy.ps1 -BackendUrl https://pandasai-backend.onrender.com -FrontendUrl https://pandas-ai.vercel.app
# Exit 0 = all checks pass. Exit 1 = one or more failed.

param(
    [Parameter(Mandatory=$true)][string]$BackendUrl,
    [Parameter(Mandatory=$true)][string]$FrontendUrl
)

$ErrorActionPreference = "Stop"
$fail = 0
function Check($name, $ok, $detail) {
    if ($ok) { Write-Host "[PASS] $name — $detail" -ForegroundColor Green }
    else { Write-Host "[FAIL] $name — $detail" -ForegroundColor Red; $script:fail = 1 }
}

# Trim trailing slash
$BackendUrl = $BackendUrl.TrimEnd('/')
$FrontendUrl = $FrontendUrl.TrimEnd('/')

Write-Host "`n=== PandasAI Deploy Verification ===" -ForegroundColor Cyan
Write-Host "Backend:  $BackendUrl"
Write-Host "Frontend: $FrontendUrl`n"

# 1. Backend /health
try {
    $h = Invoke-RestMethod "$BackendUrl/health" -TimeoutSec 30
    Check "Backend /health" ($h.status -eq "ok") "status=$($h.status) version=$($h.version)"
} catch { Check "Backend /health" $false $_.Exception.Message }

# 2. Backend /examples (should return 22 few-shot examples)
try {
    $ex = Invoke-RestMethod "$BackendUrl/examples" -TimeoutSec 30
    $n = if ($ex.examples) { $ex.examples.Count } elseif ($ex) { $ex.Count } else { 0 }
    Check "Backend /examples" ($n -ge 20) "$n examples returned"
} catch { Check "Backend /examples" $false $_.Exception.Message }

# 3. Backend /generate (real end-to-end, tests LLM key + rate limiter)
try {
    $body = @{ description = "group by city and sum sales, sort descending"; schema_hint = "columns: city(str), sales(float)" } | ConvertTo-Json
    $g = Invoke-RestMethod "$BackendUrl/generate" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 60
    $provider = $g.provider
    $valid = $g.is_valid
    Check "Backend /generate" ($valid -eq $true) "provider=$provider is_valid=$valid tokens=$($g.tokens_used)"
} catch { Check "Backend /generate" $false $_.Exception.Message }

# 4. Frontend loads (HTTP 200 + contains expected text)
try {
    $resp = Invoke-WebRequest $FrontendUrl -TimeoutSec 30 -UseBasicParsing
    $hasApp = $resp.Content -match "pandas|PandasAI|Generate"
    Check "Frontend loads" ($resp.StatusCode -eq 200 -and $hasApp) "HTTP $($resp.StatusCode) content-match=$hasApp"
} catch { Check "Frontend loads" $false $_.Exception.Message }

# 5. CORS preflight (frontend -> backend)
try {
    $preflight = Invoke-WebRequest "$BackendUrl/generate" -Method Options -Headers @{ Origin = $FrontendUrl; "Access-Control-Request-Method" = "POST" } -TimeoutSec 15 -UseBasicParsing
    $corsOk = $preflight.Headers["Access-Control-Allow-Origin"] -ne $null
    Check "CORS preflight" $corsOk "Allow-Origin header present=$corsOk"
} catch { Check "CORS preflight" $false "preflight failed (may be OK if Render handles CORS middleware)" }

Write-Host ""
if ($fail -eq 0) { Write-Host "=== ALL CHECKS PASSED — deploy is live and functional ===" -ForegroundColor Green }
else { Write-Host "=== ONE OR MORE CHECKS FAILED — review above ===" -ForegroundColor Red }
exit $fail
