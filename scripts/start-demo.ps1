param([switch]$NoBrowser, [switch]$AppOnly)
$ErrorActionPreference = 'Stop'
$demoRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$demoPython = Join-Path $demoRoot '.venv\Scripts\python.exe'
$demoN8n = Join-Path $demoRoot '.runtime\n8n\node_modules\n8n\package.json'
$demoN8nLauncher = Join-Path $demoRoot 'scripts\start-n8n.ps1'
$demoAppUrl = 'http://127.0.0.1:8001'
$demoN8nUrl = 'http://127.0.0.1:5678'
function Test-DemoReady([string]$Uri, [string]$Service) {
    try {
        $response = Invoke-WebRequest -Uri $Uri -UseBasicParsing -TimeoutSec 2
        $payload = $response.Content | ConvertFrom-Json
        if ($Service -eq 'aap') { return $payload.service -eq 'aap-prototype' -and $payload.database -eq 'ready' }
        return $payload.status -eq 'ok'
    } catch { return $false }
}
function Assert-FreePort([int]$Port) {
    $listener = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
    if ($listener) { throw "Port $Port is occupied by an unready service. Stop that service before retrying; this launcher never kills existing processes." }
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
if (-not $AppOnly -and -not (Test-DemoReady "$demoN8nUrl/healthz" 'n8n')) {
    if (-not (Test-Path -LiteralPath $demoN8n)) { Write-Warning 'Pinned n8n is missing. AAP can still show saved evidence and explicitly selected DEMO_FALLBACK.' }
    elseif ((Get-Content -LiteralPath $demoN8n -Raw | ConvertFrom-Json).version -ne '2.41.6') { throw 'n8n version differs from pinned 2.41.6; no automatic upgrade.' }
    else {
        Assert-FreePort 5678
        $null = Start-Process -FilePath 'powershell.exe' -ArgumentList @('-NoProfile','-File',('"' + $demoN8nLauncher + '"')) -WorkingDirectory $demoRoot -WindowStyle Hidden -PassThru
        Write-Host 'Starting pinned local n8n in the background.'
    }
} elseif (-not $AppOnly) { Write-Host 'n8n already healthy; reusing it.' }
$demoDeadline = [DateTime]::UtcNow.AddSeconds(90)
do {
    $demoAppReady = Test-DemoReady "$demoAppUrl/health" 'aap'
    $demoN8nReady = -not $AppOnly -and (Test-DemoReady "$demoN8nUrl/healthz" 'n8n')
    if ($demoAppReady -and ($AppOnly -or $demoN8nReady -or -not (Test-Path -LiteralPath $demoN8n))) { break }
    Start-Sleep -Seconds 1
} while ([DateTime]::UtcNow -lt $demoDeadline)
if (-not $demoAppReady) { throw 'AAP not ready. Check the local Python environment and occupied ports. No evaluation was dispatched.' }
Write-Host "AAP ready: $demoAppUrl/"
Write-Host "Saved evidence: $demoAppUrl/runs"
if ($demoN8nReady) { Write-Host "n8n ready: $demoN8nUrl (provider quota is not checked)" }
else { Write-Warning 'n8n unavailable or intentionally skipped. Inspect saved runs, or explicitly select DEMO_FALLBACK. LIVE_MODEL never silently falls back.' }
Write-Host 'No model request, credential change or workspace reset was performed.'
if (-not $NoBrowser) { Start-Process "$demoAppUrl/" }
