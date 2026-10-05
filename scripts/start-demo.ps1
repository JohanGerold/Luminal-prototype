param([switch]$NoBrowser, [switch]$AppOnly, [switch]$Restart)
$ErrorActionPreference = 'Stop'
$demoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$demoPython = Join-Path $demoRoot '.venv\Scripts\python.exe'
$demoN8n = Join-Path $demoRoot '.runtime\n8n\node_modules\n8n\package.json'
$demoN8nLauncher = Join-Path $demoRoot 'scripts\start-n8n.ps1'
$demoAppUrl = 'http://127.0.0.1:8001'
$demoN8nUrl = 'http://127.0.0.1:5678'
$demoEnv = Join-Path $demoRoot '.env'
$demoProvider = if (Test-Path -LiteralPath $demoEnv) { (Get-Content -LiteralPath $demoEnv | Where-Object { $_ -match '^AAP_LIVE_PROVIDER=' } | Select-Object -First 1) -replace '^AAP_LIVE_PROVIDER=', '' } else { '' }
$demoProvider = if ($demoProvider) { $demoProvider.Trim().ToLower() } else { 'groq' }
# groq and direct-ollama run the agent loop inside AAP, so n8n is neither started nor required.
$demoDirect = $demoProvider -in @('groq', 'direct-ollama')
$demoSkipN8n = $AppOnly -or $demoDirect
function Test-DemoReady([string]$Uri, [string]$Service) {
    try {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 2
        $payload = $response.Content | ConvertFrom-Json
        if ($Service -eq 'aap') { return $payload.service -eq 'aap-prototype' -and $payload.database -eq 'ready' }
        return $payload.status -eq 'ok'
    } catch { return $false }
}
function Stop-DemoPort([int]$Port) {
    $listeners = @(Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue)
    foreach ($processId in @($listeners | Select-Object -ExpandProperty OwningProcess -Unique)) {
        $process = Get-Process -Id $processId -ErrorAction SilentlyContinue
        if ($process) {
            Write-Host "Stopping prototype service on port $Port (PID $processId)."
            Stop-Process -Id $processId -Force
        }
    }
    $deadline = [DateTime]::UtcNow.AddSeconds(10)
    while ((Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) -and [DateTime]::UtcNow -lt $deadline) {
        Start-Sleep -Milliseconds 250
    }
    if (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue) {
        throw "Prototype port $Port did not close; no new service was started."
    }
}
function Assert-FreePort([int]$Port) {
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listener) { throw "Port $Port is occupied by an unready service. Stop that service before retrying; this launcher never kills existing processes." }
}
if ($Restart) {
    Stop-DemoPort 8001
    if (-not $demoSkipN8n) { Stop-DemoPort 5678 }
}
if (-not (Test-Path -LiteralPath $demoPython)) { throw 'Python environment missing. Run uv sync --locked once from the prototype repository.' }
if (-not (Test-Path -LiteralPath (Join-Path $demoRoot '.env'))) { throw 'Local .env missing. Follow the existing n8n setup guide; never paste secrets into this script.' }
if (-not (Test-DemoReady "$demoAppUrl/health" 'aap')) {
    Assert-FreePort 8001
    Push-Location $demoRoot
    try {
        & $demoPython manage.py migrate --noinput
        if ($LASTEXITCODE -ne 0) { throw 'Django migration failed; app not started.' }
        & $demoPython manage.py seed_demo
        if ($LASTEXITCODE -ne 0) { throw 'Demo catalog seeding failed; app not started.' }
    } finally { Pop-Location }
    $null = Start-Process -FilePath $demoPython -ArgumentList @('manage.py','serve_demo') -WorkingDirectory $demoRoot -WindowStyle Hidden -PassThru
    Write-Host 'Starting local AAP in the background.'
} else { Write-Host 'AAP already healthy; reusing it.' }
if (-not $demoSkipN8n -and -not (Test-DemoReady "$demoN8nUrl/healthz" 'n8n')) {
    if (-not (Test-Path -LiteralPath $demoN8n)) { Write-Warning 'Pinned n8n is missing. AAP can still show saved evidence and explicitly selected DEMO_FALLBACK.' }
    elseif ((Get-Content -LiteralPath $demoN8n -Raw | ConvertFrom-Json).version -ne '2.41.6') { throw 'n8n version differs from pinned 2.41.6; no automatic upgrade.' }
    else {
        Assert-FreePort 5678
        $null = Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-File',('"' + $demoN8nLauncher + '"')) -WorkingDirectory $demoRoot -WindowStyle Hidden -PassThru
        Write-Host 'Starting pinned local n8n in the background.'
    }
} elseif (-not $demoSkipN8n) { Write-Host 'n8n already healthy; reusing it.' }
# A cold native n8n start has exceeded 90 seconds on the presentation machine.
$demoDeadline = [DateTime]::UtcNow.AddSeconds(180)
do {
    $demoAppReady = Test-DemoReady "$demoAppUrl/health" 'aap'
    $demoN8nReady = -not $demoSkipN8n -and (Test-DemoReady "$demoN8nUrl/healthz" 'n8n')
    if ($demoAppReady -and ($demoSkipN8n -or $demoN8nReady -or -not (Test-Path -LiteralPath $demoN8n))) { break }
    Start-Sleep -Seconds 1
} while ([DateTime]::UtcNow -lt $demoDeadline)
if (-not $demoAppReady) { throw 'AAP not ready. Check the local Python environment and occupied ports. No evaluation was dispatched.' }
if (-not $AppOnly -and $demoProvider -in @('ollama', 'direct-ollama')) {
    $demoOllamaUrl = 'http://127.0.0.1:11434'
    $demoOllamaUp = { try { $null = Invoke-WebRequest -Uri "$demoOllamaUrl/api/version" -UseBasicParsing -TimeoutSec 2; $true } catch { $false } }
    if (-not (& $demoOllamaUp)) {
        $demoOllamaExe = Join-Path $env:LOCALAPPDATA 'Programs\Ollama\ollama.exe'
        if (Test-Path -LiteralPath $demoOllamaExe) {
            $null = Start-Process -FilePath $demoOllamaExe -ArgumentList 'serve' -WindowStyle Hidden -PassThru
            $ollamaDeadline = [DateTime]::UtcNow.AddSeconds(30)
            while (-not (& $demoOllamaUp) -and [DateTime]::UtcNow -lt $ollamaDeadline) { Start-Sleep -Milliseconds 500 }
        }
    }
    if (& $demoOllamaUp) {
        # Load the model into GPU memory now so the first live run does not pay the cold-load cost.
        # An empty generate request only loads weights; it runs no evaluation and touches no files.
        try {
            $null = Invoke-RestMethod -Uri "$demoOllamaUrl/api/generate" -Method Post -ContentType 'application/json' -TimeoutSec 180 `
                -Body '{"model":"qwen3:8b","keep_alive":"60m","options":{"num_ctx":8192}}'
            Write-Host "Ollama ready: qwen3:8b loaded for LIVE_MODEL."
        } catch { Write-Warning 'Ollama is running but qwen3:8b could not be loaded. Run: ollama pull qwen3:8b' }
    } else { Write-Warning 'Ollama is not running. LIVE_MODEL will fail until it starts; DEMO_FALLBACK remains available.' }
}
Write-Host "AAP ready: $demoAppUrl/"
Write-Host "Saved evidence: $demoAppUrl/runs"
if ($demoN8nReady) {
    # n8n can report healthy before (or without) registering a published webhook. An unauthenticated
    # empty POST returns 403 once the live workflow is registered and 404 while it is not; it never runs the agent.
    $demoWebhookPath = if ($demoProvider -eq 'gemini') { 'aap-filesystem-agent' } else { 'aap-filesystem-agent-ollama' }
    $demoWebhookDeadline = [DateTime]::UtcNow.AddSeconds(45)
    do {
        try { $null = Invoke-WebRequest -Uri "$demoN8nUrl/webhook/$demoWebhookPath" -Method Post -Body '{}' -ContentType 'application/json' -UseBasicParsing -TimeoutSec 5; $demoWebhookCode = 200 }
        catch { $demoWebhookCode = if ($_.Exception.Response) { [int]$_.Exception.Response.StatusCode } else { 0 } }
        if ($demoWebhookCode -ne 404) { break }
        Start-Sleep -Seconds 2
    } while ([DateTime]::UtcNow -lt $demoWebhookDeadline)
    if ($demoWebhookCode -eq 403) { Write-Host "n8n ready: $demoN8nUrl (live workflow /webhook/$demoWebhookPath registered for $demoProvider)" }
    else { Write-Warning "n8n is up but /webhook/$demoWebhookPath is not registered (HTTP $demoWebhookCode). Run start.bat again; if it persists, see n8n/README.md. LIVE_MODEL runs will fail until then." }
}
elseif ($demoProvider -eq 'groq' -and -not $AppOnly) {
    # Only checks that a key is present; the value is never printed or sent anywhere by the launcher.
    $demoGroqKey = Get-Content -LiteralPath $demoEnv | Where-Object { $_ -match '^AAP_GROQ_API_KEY=.{20,}' }
    if ($demoGroqKey) { Write-Host 'Live model: Groq cloud (openai/gpt-oss-120b). n8n and the local GPU are not used.' }
    else { Write-Warning 'AAP_GROQ_API_KEY is missing from .env. LIVE_MODEL runs will fail with MODEL_AUTH_FAILED until it is added.' }
}
elseif ($demoProvider -eq 'direct-ollama' -and -not $AppOnly) { Write-Host 'n8n not needed: direct-ollama runs the agent loop inside AAP against local Ollama.' }
else { Write-Warning 'n8n unavailable or intentionally skipped. Inspect saved runs, or explicitly select DEMO_FALLBACK. LIVE_MODEL never silently falls back.' }
Write-Host 'No evaluation, credential change or workspace reset was performed.'
if (-not $NoBrowser) { Start-Process "$demoAppUrl/" }
