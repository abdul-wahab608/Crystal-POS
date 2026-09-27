# Crystal POS Backend Server Launcher
# Starts the Django backend server

param(
    [string]$InstallDir = (Split-Path -Parent $PSScriptRoot),
    [int]$Port = 8010
)

$ErrorActionPreference = "Stop"

# Paths
$VenvPython = Join-Path $InstallDir "python\python.exe"
$ManagePy = Join-Path $InstallDir "backend\manage.py"
$LogDir = Join-Path $InstallDir "logs"
$DataDir = Join-Path $InstallDir "data"
$DbPath = Join-Path $DataDir "db.sqlite3"

# Set database path environment variable
$env:DJANGO_DB_PATH = $DbPath

# Prevent the bundled interpreter from reading packages out of a same-version
# system Python's user site-packages instead of its own bundled ones (see setup.ps1)
$env:PYTHONNOUSERSITE = "1"

# Create directories
@($LogDir, $DataDir) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Check if bundled runtime exists
if (!(Test-Path $VenvPython)) {
    Write-Host "ERROR: Bundled Python runtime not found. Please reinstall Crystal POS."
    exit 1
}

# Check if port is in use (only an active Listen counts - stale TIME_WAIT/CLOSE_WAIT
# connections left over from a since-exited process must not trigger a kill here)
$PortInUse = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue
if ($PortInUse) {
    Write-Host "Port $Port is already in use. Stopping existing process..."
    $Process = Get-Process -Id $PortInUse.OwningProcess -ErrorAction SilentlyContinue
    if ($Process) {
        Stop-Process -Id $Process.Id -Force
        Start-Sleep -Seconds 1
    }
}

Write-Host "=========================================="
Write-Host "Starting Crystal POS Backend Server"
Write-Host "=========================================="
Write-Host "Server URL: http://localhost:$Port"
Write-Host "API Base:   http://localhost:$Port/api/"
Write-Host "Admin:      http://localhost:$Port/admin/"
Write-Host "Database:   $DbPath"
Write-Host "=========================================="
Write-Host ""

# Set working directory
Push-Location (Join-Path $InstallDir "backend")

# Run server (quote paths to handle spaces in 'Program Files')
& "$VenvPython" "$ManagePy" runserver "0.0.0.0:$Port"

Pop-Location
