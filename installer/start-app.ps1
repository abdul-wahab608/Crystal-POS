# Crystal POS Application Launcher
# Starts both backend server and opens frontend

param(
    [string]$InstallDir = (Split-Path -Parent $PSScriptRoot)
)

# Error dialog function
Add-Type -AssemblyName System.Windows.Forms

function Show-ErrorDialog {
    param([string]$Title, [string]$Message)
    [System.Windows.Forms.MessageBox]::Show($Message, $Title, [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
}

$ErrorActionPreference = "SilentlyContinue"

# Paths
$VenvPython = Join-Path $InstallDir "python\python.exe"
$ManagePy = Join-Path $InstallDir "backend\manage.py"
$FrontendDist = Join-Path $InstallDir "frontend\dist"
$LogDir = Join-Path $InstallDir "logs"
$DataDir = Join-Path $InstallDir "data"
$DbPath = Join-Path $DataDir "db.sqlite3"
$BackendLog = Join-Path $LogDir "backend.log"
$BackendErrorLog = Join-Path $LogDir "backend_error.log"

# Create directories
@($LogDir, $DataDir) | ForEach-Object {
    if (!(Test-Path $_)) {
        New-Item -ItemType Directory -Path $_ -Force | Out-Null
    }
}

# Set database path environment variable
$env:DJANGO_DB_PATH = $DbPath

# Prevent the bundled interpreter from reading packages out of a same-version
# system Python's user site-packages instead of its own bundled ones (see setup.ps1)
$env:PYTHONNOUSERSITE = "1"

# Verify Python/venv exists
if (!(Test-Path $VenvPython)) {
    Show-ErrorDialog -Title "Crystal POS Error" -Message "Bundled Python runtime not found.`n`nExpected: $VenvPython`n`nPlease reinstall Crystal POS."
    exit 1
}

# Check if backend is already running (TIME_WAIT/CLOSE_WAIT leftovers from an
# unrelated process that recently held the port don't count as "running")
$ExistingBackend = Get-NetTCPConnection -LocalPort 8010 -State Listen -ErrorAction SilentlyContinue
if ($ExistingBackend) {
    Write-Host "Backend server already running on port 8010"
} else {
    # Start backend server
    Write-Host "Starting Crystal POS Backend Server..."
    
    # Use quoted paths in argument string to handle spaces in 'Program Files'
    $BackendProcess = Start-Process -FilePath $VenvPython `
        -ArgumentList "`"$ManagePy`" runserver 0.0.0.0:8010" `
        -WorkingDirectory (Join-Path $InstallDir "backend") `
        -WindowStyle Hidden `
        -PassThru `
        -RedirectStandardOutput $BackendLog `
        -RedirectStandardError $BackendErrorLog
    
    # Wait for backend to start
    Write-Host "Waiting for backend to initialize..."
    Start-Sleep -Seconds 4
    
    # Verify backend is running
    $BackendRunning = $false
    try {
        $Response = Invoke-WebRequest -Uri "http://localhost:8010/api/health/" -TimeoutSec 5 -UseBasicParsing
        if ($Response.StatusCode -eq 200) {
            $BackendRunning = $true
            Write-Host "Backend server started successfully!"
        }
    } catch {
        # Check if process exited
        if ($BackendProcess.HasExited) {
            $ErrorContent = ""
            if (Test-Path $BackendErrorLog) {
                $ErrorContent = Get-Content $BackendErrorLog -Raw -ErrorAction SilentlyContinue
            }
            Show-ErrorDialog -Title "Crystal POS Error" -Message "Backend server failed to start.`n`nCheck logs at:`n$BackendErrorLog`n`nError: $ErrorContent"
            exit 1
        }
        Write-Host "Backend may still be starting..."
    }
}

# Open frontend in default browser
Write-Host "Opening Crystal POS in your browser..."
Start-Process "http://localhost:8010"

Write-Host ""
Write-Host "=========================================="
Write-Host "Crystal POS is now running!"
Write-Host "=========================================="
Write-Host "Application:  http://localhost:8010/"
Write-Host "Backend API:  http://localhost:8010/api/"
Write-Host ""
Write-Host "Default login: admin / admin123"
Write-Host "=========================================="
Write-Host ""
# Exit silently - backend runs in background
exit 0
