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
$VenvPython = Join-Path $InstallDir "venv\Scripts\python.exe"
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

# Verify Python/venv exists
if (!(Test-Path $VenvPython)) {
    Show-ErrorDialog -Title "Crystal POS Error" -Message "Python virtual environment not found.`n`nExpected: $VenvPython`n`nPlease reinstall Crystal POS."
    exit 1
}

# Check if backend is already running
$ExistingBackend = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($ExistingBackend) {
    Write-Host "Backend server already running on port 8000"
} else {
    # Start backend server
    Write-Host "Starting Crystal POS Backend Server..."
    
    # Use quoted paths in argument string to handle spaces in 'Program Files'
    $BackendProcess = Start-Process -FilePath $VenvPython `
        -ArgumentList "`"$ManagePy`" runserver 0.0.0.0:8000" `
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
        $Response = Invoke-WebRequest -Uri "http://localhost:8000/api/health/" -TimeoutSec 5 -UseBasicParsing
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
Start-Process "http://localhost:8000"

Write-Host ""
Write-Host "=========================================="
Write-Host "Crystal POS is now running!"
Write-Host "=========================================="
Write-Host "Application:  http://localhost:8000/"
Write-Host "Backend API:  http://localhost:8000/api/"
Write-Host ""
Write-Host "Default login: admin / admin123"
Write-Host "=========================================="
Write-Host ""
# Exit silently - backend runs in background
exit 0
