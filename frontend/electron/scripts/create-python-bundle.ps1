# Create Python Bundle for Installer
# This script creates a self-contained Python environment with all dependencies

Write-Host "`n=== Python Bundle Creator ===" -ForegroundColor Cyan
Write-Host "Creating self-contained Python environment with all Django dependencies`n" -ForegroundColor White

$ErrorActionPreference = "Stop"

# Paths
$scriptDir = $PSScriptRoot
$resourcesDir = Join-Path $scriptDir "..\resources"
$bundleDir = Join-Path $resourcesDir "python-bundle"
$backendDir = Join-Path $scriptDir "..\..\..\backend"
$requirementsFile = Join-Path $backendDir "requirements.txt"

# Create bundle directory
Write-Host "📁 Creating bundle directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null

# Create virtual environment
Write-Host "🐍 Creating Python virtual environment..." -ForegroundColor Yellow
$venvPath = Join-Path $bundleDir "python-env"
python -m venv $venvPath

# Activate and install dependencies
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow

& $activateScript
python -m pip install --upgrade pip --quiet
python -m pip install -r $requirementsFile --no-cache-dir

# Verify installation
Write-Host "`n✅ Verification:" -ForegroundColor Green
python --version
python -m pip list | Select-String "Django|djangorestframework"

# Get bundle size
$size = (Get-ChildItem $venvPath -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host "`n📊 Bundle Size: $([math]::Round($size, 2)) MB" -ForegroundColor Cyan
Write-Host "📁 Location: $venvPath" -ForegroundColor White

Write-Host "`n✅ Python bundle created successfully!" -ForegroundColor Green
Write-Host "This will be included in the installer.`n" -ForegroundColor White
