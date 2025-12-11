# Crystal POS Frontend Launcher
# Opens the frontend in the default browser

param(
    [string]$InstallDir = (Split-Path -Parent $PSScriptRoot),
    [string]$BackendUrl = "http://localhost:8000"
)

$FrontendDist = Join-Path $InstallDir "frontend\dist"
$IndexFile = Join-Path $FrontendDist "index.html"

Write-Host "=========================================="
Write-Host "Opening Crystal POS Frontend"
Write-Host "=========================================="

# Check if backend is running
try {
    $Response = Invoke-WebRequest -Uri "$BackendUrl/api/" -TimeoutSec 3 -UseBasicParsing -ErrorAction Stop
    Write-Host "Backend is running at $BackendUrl"
} catch {
    Write-Host "WARNING: Backend may not be running at $BackendUrl"
    Write-Host "Please start the backend first using start-backend.ps1"
}

# Open frontend
if (Test-Path $IndexFile) {
    Write-Host "Opening frontend..."
    Start-Process $BackendUrl
} else {
    Write-Host "ERROR: Frontend files not found at $FrontendDist"
    Write-Host "Please verify installation."
}
