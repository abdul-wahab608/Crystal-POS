# Crystal POS Installer Build Script
# This script builds the complete installer package

param(
    [switch]$SkipFrontendBuild,
    [switch]$SkipBackendCheck,
    [string]$InnoSetupPath = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$InstallerDir = $PSScriptRoot
$DistDir = Join-Path $ProjectRoot "dist\installer"

Write-Host "=========================================="
Write-Host "Crystal POS Installer Build Script"
Write-Host "=========================================="
Write-Host ""

# Step 1: Verify project structure
Write-Host "Step 1: Verifying project structure..."
$RequiredPaths = @(
    (Join-Path $ProjectRoot "backend\manage.py"),
    (Join-Path $ProjectRoot "backend\requirements.txt"),
    (Join-Path $ProjectRoot "frontend\package.json")
)

foreach ($Path in $RequiredPaths) {
    if (!(Test-Path $Path)) {
        Write-Host "ERROR: Required file not found: $Path"
        exit 1
    }
}
Write-Host "Project structure verified."

# Step 2: Build frontend
if (!$SkipFrontendBuild) {
    Write-Host ""
    Write-Host "Step 2: Building frontend..."
    Push-Location (Join-Path $ProjectRoot "frontend")
    
    # Check if node_modules exists
    if (!(Test-Path "node_modules")) {
        Write-Host "Installing npm dependencies..."
        npm install
    }
    
    # Build Vue app
    Write-Host "Running npm build..."
    npm run build
    
    if (!(Test-Path "dist\index.html")) {
        Write-Host "ERROR: Frontend build failed. dist\index.html not found."
        Pop-Location
        exit 1
    }
    
    Pop-Location
    Write-Host "Frontend build complete."
} else {
    Write-Host ""
    Write-Host "Step 2: Skipping frontend build."
}

# Step 3: Create dist directory
Write-Host ""
Write-Host "Step 3: Preparing distribution directory..."
if (!(Test-Path $DistDir)) {
    New-Item -ItemType Directory -Path $DistDir -Force | Out-Null
}

# Step 4: Check for Inno Setup
Write-Host ""
Write-Host "Step 4: Checking for Inno Setup compiler..."

# Try common Inno Setup paths
$InnoPaths = @(
    $InnoSetupPath,
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe",
    "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
)

$InnoCompiler = $null
foreach ($Path in $InnoPaths) {
    if (Test-Path $Path) {
        $InnoCompiler = $Path
        break
    }
}

if ($null -eq $InnoCompiler) {
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "Inno Setup not found!"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "To build the installer, you need Inno Setup 6 installed."
    Write-Host "Download from: https://jrsoftware.org/isdl.php"
    Write-Host ""
    Write-Host "After installing, run this script again, or run manually:"
    Write-Host "  ISCC.exe `"$InstallerDir\CrystalPOS.iss`""
    Write-Host ""
    Write-Host "Alternatively, you can use the portable version:"
    Write-Host "  1. Download ISCC.exe from the Inno Setup website"
    Write-Host "  2. Place it in the installer/ folder"
    Write-Host "  3. Run: .\build-installer.ps1"
    Write-Host "=========================================="
    
    # Check for portable ISCC in installer folder
    $PortableISCC = Join-Path $InstallerDir "ISCC.exe"
    if (Test-Path $PortableISCC) {
        $InnoCompiler = $PortableISCC
        Write-Host "Found portable ISCC.exe in installer folder."
    } else {
        exit 1
    }
}

Write-Host "Inno Setup found at: $InnoCompiler"

# Step 5: Build installer
Write-Host ""
Write-Host "Step 5: Building installer..."
$IssFile = Join-Path $InstallerDir "CrystalPOS.iss"

if (!(Test-Path $IssFile)) {
    Write-Host "ERROR: Inno Setup script not found: $IssFile"
    exit 1
}

& $InnoCompiler $IssFile

# Step 6: Verify output
Write-Host ""
Write-Host "Step 6: Verifying installer..."
$InstallerExe = Get-ChildItem -Path $DistDir -Filter "CrystalPOS-Setup-*.exe" | Sort-Object LastWriteTime -Descending | Select-Object -First 1

if ($InstallerExe) {
    Write-Host ""
    Write-Host "=========================================="
    Write-Host "BUILD SUCCESSFUL!"
    Write-Host "=========================================="
    Write-Host ""
    Write-Host "Installer created:"
    Write-Host "  $($InstallerExe.FullName)"
    Write-Host ""
    Write-Host "File size: $([math]::Round($InstallerExe.Length / 1MB, 2)) MB"
    Write-Host ""
    Write-Host "You can now distribute this installer to clients."
    Write-Host "=========================================="
} else {
    Write-Host "ERROR: Installer file not found in $DistDir"
    exit 1
}

exit 0
