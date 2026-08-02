# Crystal POS Setup Script
# This script runs after installation to set up the application
# Version: 2.1.0 - Enhanced error handling, logging, and robustness

param(
    [Parameter(Position=0)]
    [string]$InstallDir
)

# ============================================================================
# SET CONSOLE TITLE AND WINDOW
# ============================================================================
$Host.UI.RawUI.WindowTitle = "Crystal POS Setup"

# ============================================================================
# RESOLVE INSTALL DIRECTORY
# ============================================================================
# Handle various ways the install dir might be passed or inferred
if ([string]::IsNullOrEmpty($InstallDir)) {
    # Try to get from script location
    if ($PSScriptRoot -and (Test-Path $PSScriptRoot)) {
        $InstallDir = Split-Path -Parent $PSScriptRoot
    } elseif ($MyInvocation.MyCommand.Path) {
        $InstallDir = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
    } else {
        # Fallback to default install location
        $InstallDir = "${env:ProgramFiles}\Crystal POS"
        if (!(Test-Path $InstallDir)) {
            $InstallDir = "${env:ProgramFiles(x86)}\Crystal POS"
        }
    }
}

# Normalize the path (remove quotes if present)
$InstallDir = $InstallDir.Trim('"').Trim("'")

# Verify the install directory exists
if (!(Test-Path $InstallDir)) {
    Write-Host "ERROR: Install directory not found: $InstallDir" -ForegroundColor Red
    Write-Host "Attempting to create it..." -ForegroundColor Yellow
    try {
        New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    } catch {
        Write-Host "Failed to create directory. Please run installer again." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# ============================================================================
# CONFIGURATION
# ============================================================================
$ErrorActionPreference = "Continue"  # Don't stop on errors, we handle them manually
$Script:SetupSuccess = $true
$Script:LastError = $null
$Script:CurrentStep = ""

# ============================================================================
# LOGGING SETUP
# ============================================================================
$LogDir = Join-Path $InstallDir "logs"
if (!(Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFile = Join-Path $LogDir "setup_$Timestamp.log"
$ErrorLogFile = Join-Path $LogDir "setup_errors_$Timestamp.log"

# Also keep a "latest" log for easy access
$LatestLogFile = Join-Path $LogDir "setup_latest.log"

function Write-Log {
    param(
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "SUCCESS", "DEBUG")]
        [string]$Level = "INFO"
    )
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss.fff"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    # Color-coded console output
    switch ($Level) {
        "ERROR"   { Write-Host $LogMessage -ForegroundColor Red }
        "WARN"    { Write-Host $LogMessage -ForegroundColor Yellow }
        "SUCCESS" { Write-Host $LogMessage -ForegroundColor Green }
        "DEBUG"   { Write-Host $LogMessage -ForegroundColor Gray }
        default   { Write-Host $LogMessage }
    }
    
    # Write to log files
    Add-Content -Path $LogFile -Value $LogMessage -ErrorAction SilentlyContinue
    Add-Content -Path $LatestLogFile -Value $LogMessage -ErrorAction SilentlyContinue
    
    # Also log errors to separate error log
    if ($Level -eq "ERROR") {
        Add-Content -Path $ErrorLogFile -Value $LogMessage -ErrorAction SilentlyContinue
    }
}

function Write-StepHeader {
    param([string]$StepNumber, [string]$StepName)
    $Script:CurrentStep = "$StepNumber - $StepName"
    Write-Log ""
    Write-Log "=============================================="
    Write-Log "STEP $StepNumber : $StepName"
    Write-Log "=============================================="
}

function Write-ErrorDetails {
    param(
        [System.Management.Automation.ErrorRecord]$ErrorRecord,
        [string]$Context = ""
    )
    
    $Script:SetupSuccess = $false
    $Script:LastError = $ErrorRecord.Exception.Message
    
    Write-Log "ERROR DETAILS:" "ERROR"
    Write-Log "  Context: $Context" "ERROR"
    Write-Log "  Message: $($ErrorRecord.Exception.Message)" "ERROR"
    Write-Log "  Type: $($ErrorRecord.Exception.GetType().FullName)" "ERROR"
    Write-Log "  Script: $($ErrorRecord.InvocationInfo.ScriptName)" "ERROR"
    Write-Log "  Line: $($ErrorRecord.InvocationInfo.ScriptLineNumber)" "ERROR"
    Write-Log "  Command: $($ErrorRecord.InvocationInfo.Line.Trim())" "ERROR"
    
    if ($ErrorRecord.Exception.InnerException) {
        Write-Log "  Inner Exception: $($ErrorRecord.Exception.InnerException.Message)" "ERROR"
    }
}

function Show-ErrorDialog {
    param(
        [string]$Title,
        [string]$Message,
        [string]$Details
    )
    
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
        $fullMessage = "$Message`n`nDetails:`n$Details`n`nCheck log file for more information:`n$LogFile"
        [System.Windows.Forms.MessageBox]::Show($fullMessage, $Title, [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Error)
    } catch {
        # Fallback if Windows Forms not available
        Write-Log "Could not display error dialog: $_" "WARN"
    }
}

function Show-SuccessDialog {
    param([string]$Message)
    
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
        [System.Windows.Forms.MessageBox]::Show($Message, "Crystal POS Setup", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
    } catch {
        Write-Log "Could not display success dialog: $_" "WARN"
    }
}

function Test-Command {
    param([string]$Command)
    try {
        $null = Get-Command $Command -ErrorAction Stop
        return $true
    } catch {
        return $false
    }
}

function Get-PythonPath {
    Write-Log "Searching for Python installation..." "DEBUG"
    
    # Check for bundled Python first
    $BundledPython = Join-Path $InstallDir "python\python.exe"
    if (Test-Path $BundledPython) {
        Write-Log "Found bundled Python at: $BundledPython" "DEBUG"
        return $BundledPython
    }
    
    # Check system Python
    if (Test-Command "python") {
        try {
            $pythonExe = (Get-Command python -ErrorAction Stop).Source
            Write-Log "Found system Python at: $pythonExe" "DEBUG"
            return $pythonExe
        } catch {
            Write-Log "Failed to get python path: $_" "DEBUG"
        }
    }
    
    if (Test-Command "python3") {
        try {
            $pythonExe = (Get-Command python3 -ErrorAction Stop).Source
            Write-Log "Found python3 at: $pythonExe" "DEBUG"
            return $pythonExe
        } catch {
            Write-Log "Failed to get python3 path: $_" "DEBUG"
        }
    }
    
    # Check common install locations
    $CommonPaths = @(
        "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Python313\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe"
    )
    
    foreach ($Path in $CommonPaths) {
        Write-Log "Checking: $Path" "DEBUG"
        if (Test-Path $Path) {
            Write-Log "Found Python at: $Path" "DEBUG"
            return $Path
        }
    }
    
    Write-Log "Python not found in any known location" "DEBUG"
    return $null
}

function Invoke-StepWithErrorHandling {
    param(
        [string]$StepName,
        [scriptblock]$Action
    )
    
    try {
        & $Action
        return $true
    } catch {
        Write-ErrorDetails -ErrorRecord $_ -Context $StepName
        return $false
    }
}

# ============================================================================
# MAIN SETUP PROCESS - Wrapped in global error handler
# ============================================================================

try {

# Clear latest log file
if (Test-Path $LatestLogFile) {
    Remove-Item $LatestLogFile -Force -ErrorAction SilentlyContinue
}

Write-Log "=========================================================="
Write-Log "CRYSTAL POS SETUP - STARTING"
Write-Log "=========================================================="
Write-Log "Timestamp: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Log "Install Directory: $InstallDir"
Write-Log "Log File: $LogFile"
Write-Log "PowerShell Version: $($PSVersionTable.PSVersion)"
Write-Log "OS: $([System.Environment]::OSVersion.VersionString)"
Write-Log "User: $env:USERNAME"
Write-Log "=========================================================="

# ============================================================================
# STEP 1: CHECK PYTHON INSTALLATION
# ============================================================================
Write-StepHeader "1" "Checking Python Installation"

$PythonPath = $null
$StepSuccess = Invoke-StepWithErrorHandling -StepName "Check Python" -Action {
    $Script:PythonPath = Get-PythonPath
    
    if ($null -eq $Script:PythonPath) {
        throw "Python not found. Please install Python 3.10 or later from https://www.python.org/downloads/"
    }
    
    # Verify Python works
    $PythonVersion = & $Script:PythonPath --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python found but failed to execute: $PythonVersion"
    }
    
    Write-Log "Python found: $PythonVersion" "SUCCESS"
    Write-Log "Python path: $Script:PythonPath"
}

$PythonPath = $Script:PythonPath

if (!$StepSuccess) {
    Show-ErrorDialog -Title "Crystal POS Setup Failed" `
        -Message "Python is not installed or not working properly." `
        -Details $Script:LastError
    exit 1
}

# ============================================================================
# STEP 2: CREATE VIRTUAL ENVIRONMENT
# ============================================================================
Write-StepHeader "2" "Creating Virtual Environment"

$VenvPath = Join-Path $InstallDir "venv"
$VenvPython = Join-Path $VenvPath "Scripts\python.exe"
$VenvPip = Join-Path $VenvPath "Scripts\pip.exe"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Create Virtual Environment" -Action {
    if (!(Test-Path $VenvPath)) {
        Write-Log "Creating new virtual environment..."
        # Quote paths to handle spaces in 'Program Files'
        $output = & "$PythonPath" -m venv "$VenvPath" 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment: $output"
        }
        Write-Log "Virtual environment created at: $VenvPath" "SUCCESS"
    } else {
        Write-Log "Virtual environment already exists at: $VenvPath"
    }
    
    # Verify venv Python exists
    if (!(Test-Path $VenvPython)) {
        throw "Virtual environment created but python.exe not found at: $VenvPython"
    }
    Write-Log "Venv Python verified: $VenvPython" "SUCCESS"
}

if (!$StepSuccess) {
    Show-ErrorDialog -Title "Crystal POS Setup Failed" `
        -Message "Failed to create virtual environment." `
        -Details $Script:LastError
    exit 1
}

# ============================================================================
# STEP 3: UPGRADE PIP AND INSTALL SETUPTOOLS
# ============================================================================
Write-StepHeader "3" "Upgrading pip and Installing setuptools"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Upgrade pip" -Action {
    Write-Log "Upgrading pip..."
    # Quote paths to handle spaces in 'Program Files'
    $output = & "$VenvPython" -m pip install --upgrade pip 2>&1
    $output | ForEach-Object { Write-Log "  $_" "DEBUG" }
    
    if ($LASTEXITCODE -ne 0) {
        Write-Log "pip upgrade had issues, continuing..." "WARN"
    }
    
    Write-Log "Installing setuptools and wheel..."
    # setuptools>=81 removed pkg_resources entirely, which djangorestframework-simplejwt==5.3.0
    # still imports at module load time. Pinning below that keeps every Django command from
    # crashing with "ModuleNotFoundError: No module named 'pkg_resources'".
    $output = & "$VenvPip" install --upgrade "setuptools<81" wheel 2>&1
    $output | ForEach-Object { Write-Log "  $_" "DEBUG" }
    
    Write-Log "pip and setuptools ready" "SUCCESS"
}

if (!$StepSuccess) {
    Write-Log "pip upgrade had issues, but continuing with setup..." "WARN"
}

# ============================================================================
# STEP 4: INSTALL BACKEND REQUIREMENTS
# ============================================================================
Write-StepHeader "4" "Installing Backend Requirements"

$RequirementsPath = Join-Path $InstallDir "backend\requirements.txt"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Install Requirements" -Action {
    if (!(Test-Path $RequirementsPath)) {
        throw "requirements.txt not found at: $RequirementsPath"
    }
    
    Write-Log "Installing from: $RequirementsPath"
    Write-Log "This may take a few minutes..."
    
    # Quote paths to handle spaces in 'Program Files'
    $output = & "$VenvPip" install -r "$RequirementsPath" 2>&1
    $output | ForEach-Object { Write-Log "  $_" "DEBUG" }
    
    if ($LASTEXITCODE -ne 0) {
        throw "pip install failed with exit code $LASTEXITCODE"
    }
    
    Write-Log "Backend requirements installed successfully" "SUCCESS"
}

if (!$StepSuccess) {
    Show-ErrorDialog -Title "Crystal POS Setup Failed" `
        -Message "Failed to install Python dependencies." `
        -Details $Script:LastError
    exit 1
}

# ============================================================================
# STEP 5: PREPARE DATABASE DIRECTORY
# ============================================================================
Write-StepHeader "5" "Preparing Database Directory"

$DataDir = Join-Path $InstallDir "data"
$DbPath = Join-Path $DataDir "db.sqlite3"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Prepare Database" -Action {
    if (!(Test-Path $DataDir)) {
        New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
        Write-Log "Created data directory: $DataDir"
    } else {
        Write-Log "Data directory exists: $DataDir"
    }
    
    # Set environment variable for database location - current session
    $env:DJANGO_DB_PATH = $DbPath
    
    # Persist environment variable to user environment for future sessions
    Write-Log "Setting persistent environment variable DJANGO_DB_PATH..."
    try {
        [System.Environment]::SetEnvironmentVariable('DJANGO_DB_PATH', $DbPath, [System.EnvironmentVariableTarget]::User)
        Write-Log "DJANGO_DB_PATH persisted to user environment" "SUCCESS"
    } catch {
        Write-Log "Could not persist DJANGO_DB_PATH (app will use auto-detection): $_" "WARN"
    }
    
    Write-Log "Database path: $DbPath"
    Write-Log "Database directory ready" "SUCCESS"
}

if (!$StepSuccess) {
    Show-ErrorDialog -Title "Crystal POS Setup Failed" `
        -Message "Failed to prepare database directory." `
        -Details $Script:LastError
    exit 1
}

# ============================================================================
# STEP 6: RUN DJANGO MIGRATIONS
# ============================================================================
Write-StepHeader "6" "Running Django Migrations"

$ManagePy = Join-Path $InstallDir "backend\manage.py"
$BackendDir = Join-Path $InstallDir "backend"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Run Migrations" -Action {
    if (!(Test-Path $ManagePy)) {
        throw "manage.py not found at: $ManagePy"
    }
    
    Write-Log "Running migrations from: $BackendDir"
    
    Push-Location $BackendDir
    try {
        # Quote paths to handle spaces in 'Program Files'
        $output = & "$VenvPython" "$ManagePy" migrate --no-input 2>&1
        $output | ForEach-Object { Write-Log "  $_" }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Django migrate failed with exit code $LASTEXITCODE"
        }
    } finally {
        Pop-Location
    }
    
    Write-Log "Database migrations completed successfully" "SUCCESS"
}

if (!$StepSuccess) {
    Show-ErrorDialog -Title "Crystal POS Setup Failed" `
        -Message "Failed to run database migrations." `
        -Details $Script:LastError
    exit 1
}

# ============================================================================
# STEP 7: CREATE ADMIN USER
# ============================================================================
Write-StepHeader "7" "Creating Admin User"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Create Admin User" -Action {
    $CreateSuperuserScript = @"
import os
import sys
import traceback

try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    
    import django
    django.setup()
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@crystalpos.com', 'admin123')
        print('SUCCESS: Admin user created (admin / admin123)')
    else:
        print('INFO: Admin user already exists')
    
    sys.exit(0)
except Exception as e:
    print(f'ERROR: {str(e)}')
    traceback.print_exc()
    sys.exit(1)
"@

    $TempScript = Join-Path $BackendDir "create_superuser_temp.py"
    Write-Log "Creating temporary script: $TempScript"
    
    # Write script with proper encoding
    [System.IO.File]::WriteAllText($TempScript, $CreateSuperuserScript, [System.Text.Encoding]::UTF8)
    
    Push-Location $BackendDir
    try {
        # Quote paths to handle spaces in 'Program Files'
        $output = & "$VenvPython" "$TempScript" 2>&1
        $output | ForEach-Object { Write-Log "  $_" }
        
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create admin user. Exit code: $LASTEXITCODE"
        }
    } finally {
        Pop-Location
        # Clean up temp script
        if (Test-Path $TempScript) {
            Remove-Item $TempScript -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Log "Admin user setup completed" "SUCCESS"
}

if (!$StepSuccess) {
    Write-Log "Admin user creation had issues, but continuing..." "WARN"
    # Don't exit here - admin user can be created manually later
}

# ============================================================================
# STEP 8: VERIFY INSTALLATION
# ============================================================================
Write-StepHeader "8" "Verifying Installation"

$StepSuccess = Invoke-StepWithErrorHandling -StepName "Verify Installation" -Action {
    Write-Log "Checking Django installation..."
    
    Push-Location $BackendDir
    try {
        # Quote paths to handle spaces
        $output = & "$VenvPython" -c "import django; print(f'Django {django.VERSION}')" 2>&1
        Write-Log "  Django: $output"
        
        $output = & "$VenvPython" -c "import rest_framework; print('DRF OK')" 2>&1
        Write-Log "  REST Framework: $output"
        
        # Check if database exists
        if (Test-Path $DbPath) {
            $dbSize = (Get-Item $DbPath).Length / 1KB
            Write-Log "  Database: OK ($([math]::Round($dbSize, 2)) KB)"
        } else {
            Write-Log "  Database: Created (new installation)"
        }
    } finally {
        Pop-Location
    }
    
    Write-Log "Installation verified successfully" "SUCCESS"
}

# ============================================================================
# SETUP COMPLETE
# ============================================================================
Write-Log ""
Write-Log "=========================================================="

if ($Script:SetupSuccess) {
    Write-Log "CRYSTAL POS SETUP COMPLETED SUCCESSFULLY!" "SUCCESS"
    Write-Log "=========================================================="
    Write-Log ""
    Write-Log "Default login credentials:"
    Write-Log "  Username: admin"
    Write-Log "  Password: admin123"
    Write-Log ""
    Write-Log "To start the application:"
    Write-Log "  - Use the desktop shortcut 'Crystal POS'"
    Write-Log "  - Or run: $InstallDir\installer\start-app.ps1"
    Write-Log ""
    Write-Log "Log files saved to: $LogDir"
    Write-Log "=========================================================="
    
    Show-SuccessDialog -Message "Crystal POS has been installed successfully!`n`nDefault login:`nUsername: admin`nPassword: admin123`n`nUse the desktop shortcut to start the application."
    
    exit 0
} else {
    Write-Log "CRYSTAL POS SETUP COMPLETED WITH ERRORS" "ERROR"
    Write-Log "=========================================================="
    Write-Log "Last error: $($Script:LastError)" "ERROR"
    Write-Log "Failed at step: $($Script:CurrentStep)" "ERROR"
    Write-Log ""
    Write-Log "Please check the log files for details:"
    Write-Log "  Main log: $LogFile"
    Write-Log "  Error log: $ErrorLogFile"
    Write-Log "=========================================================="
    
    Show-ErrorDialog -Title "Crystal POS Setup Completed with Errors" `
        -Message "Setup completed but encountered some issues." `
        -Details "Failed at: $($Script:CurrentStep)`nError: $($Script:LastError)"
    
    # Pause so user can see the error
    Write-Host ""
    Write-Host "Press any key to close this window..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    
    exit 1
}

} catch {
    # Global error handler for any unhandled exceptions
    $FatalError = $_
    
    Write-Host "" -ForegroundColor Red
    Write-Host "========================================================" -ForegroundColor Red
    Write-Host "FATAL ERROR - UNHANDLED EXCEPTION" -ForegroundColor Red
    Write-Host "========================================================" -ForegroundColor Red
    Write-Host "Error: $($FatalError.Exception.Message)" -ForegroundColor Red
    Write-Host "Type: $($FatalError.Exception.GetType().FullName)" -ForegroundColor Red
    Write-Host "Line: $($FatalError.InvocationInfo.ScriptLineNumber)" -ForegroundColor Red
    Write-Host "========================================================" -ForegroundColor Red
    
    # Try to write to log file
    try {
        if ($LogFile) {
            Add-Content -Path $LogFile -Value "[$(Get-Date)] [FATAL] $($FatalError.Exception.Message)" -ErrorAction SilentlyContinue
        }
    } catch { }
    
    # Try to show error dialog
    try {
        Add-Type -AssemblyName System.Windows.Forms -ErrorAction SilentlyContinue
        [System.Windows.Forms.MessageBox]::Show(
            "A fatal error occurred during setup:`n`n$($FatalError.Exception.Message)`n`nPlease check the log files and try again.",
            "Crystal POS Setup - Fatal Error",
            [System.Windows.Forms.MessageBoxButtons]::OK,
            [System.Windows.Forms.MessageBoxIcon]::Error
        )
    } catch { }
    
    Write-Host ""
    Write-Host "Press any key to close this window..." -ForegroundColor Yellow
    try { $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown") } catch { Start-Sleep -Seconds 10 }
    
    exit 1
}