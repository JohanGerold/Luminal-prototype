$ErrorActionPreference = 'Stop'
$prototypeRoot = Split-Path -Parent $PSScriptRoot
$n8nEntry = Join-Path $prototypeRoot '.runtime\n8n\node_modules\n8n\bin\n8n'
if (-not (Test-Path -LiteralPath $n8nEntry)) {
    throw 'Pinned local n8n is missing. Complete P-00 installation first.'
}
$env:N8N_USER_FOLDER = Join-Path $prototypeRoot '.runtime\n8n-state'
$env:N8N_LISTEN_ADDRESS = '127.0.0.1'
$env:N8N_HOST = '127.0.0.1'
$env:N8N_PORT = '5678'
$env:N8N_PROTOCOL = 'http'
$env:N8N_EDITOR_BASE_URL = 'http://127.0.0.1:5678'
$env:N8N_WEBHOOK_URL = 'http://127.0.0.1:5678/'
$env:N8N_SECURE_COOKIE = 'false'
$env:N8N_DIAGNOSTICS_ENABLED = 'false'
$env:N8N_VERSION_NOTIFICATIONS_ENABLED = 'false'
$env:N8N_TEMPLATES_ENABLED = 'false'
& node $n8nEntry start
exit $LASTEXITCODE
