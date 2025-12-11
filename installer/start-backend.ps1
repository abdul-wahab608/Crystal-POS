# Crystal POS Backend Server Launcher
# Starts the Django backend server

param(
    [string]$InstallDir = (Split-Path -Parent $PSScriptRoot),
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

# Paths
$VenvPython = Join-Path $InstallDir "venv\Scripts\python.exe"
$ManagePy = Join-Path $InstallDir "backend\manage.py"
$LogDir = Join-Path $InstallDir "logs"
$DataDir = Join-Path $InstallDir "data"
$DbPath = Join-Path $DataDir "db.sqlite3"

# Set database path environment variable
$env:DJANGO_DB_PATH = $DbPath

# Create directories
@($LogDir, $DataDir) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Check if venv exists
if (!(Test-Path $VenvPython)) {
    Write-Host "ERROR: Virtual environment not found. Please run setup.ps1 first."
    exit 1
}

# Check if port is in use
$PortInUse = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
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
