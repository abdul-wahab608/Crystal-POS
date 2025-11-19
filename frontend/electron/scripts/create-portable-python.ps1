# Crystal POS - Portable Python Bundle Creator
# Production-grade bundled Python with all dependencies

$ErrorActionPreference = "Stop"

Write-Host "`n==== Crystal POS - Creating Portable Python Bundle ====`n" -ForegroundColor Cyan

# Paths
$scriptDir = $PSScriptRoot
$resourcesDir = Join-Path $scriptDir "..\resources"
$bundleDir = Join-Path $resourcesDir "python-runtime"
$backendDir = Join-Path $scriptDir "..\..\..\backend"
$requirementsFile = Join-Path $backendDir "requirements.txt"
$pythonUrl = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
$pythonZip = Join-Path $bundleDir "python.zip"
$pythonExtracted = Join-Path $bundleDir "python"

Write-Host "Setup Directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null

# Download Python if needed
if (!(Test-Path $pythonExtracted)) {
    Write-Host "`nDownloading Python 3.11.9 Embedded (25 MB)..." -ForegroundColor Yellow
    
    $webClient = New-Object System.Net.WebClient
    $webClient.DownloadFile($pythonUrl, $pythonZip)
    
    Write-Host "Download complete" -ForegroundColor Green
    
    Write-Host "`nExtracting Python..." -ForegroundColor Yellow
    Expand-Archive -Path $pythonZip -DestinationPath $pythonExtracted -Force
    Remove-Item $pythonZip
    Write-Host "Python extracted" -ForegroundColor Green
} else {
    Write-Host "`nPython already exists" -ForegroundColor Green
}

$pythonExe = Join-Path $pythonExtracted "python.exe"

# Configure Python
Write-Host "`nConfiguring Python for pip..." -ForegroundColor Yellow

$pthFile = Join-Path $pythonExtracted "python311._pth"
$pthContent = Get-Content $pthFile -Raw
$pthContent = $pthContent -replace '#import site', 'import site'
if ($pthContent -notmatch 'import site') {
    $pthContent += "`nimport site`n"
}
Set-Content $pthFile $pthContent

$scriptsDir = Join-Path $pythonExtracted "Scripts"
New-Item -ItemType Directory -Path $scriptsDir -Force | Out-Null

Write-Host "Python configured" -ForegroundColor Green

# Install pip
Write-Host "`nInstalling pip..." -ForegroundColor Yellow

$getPipUrl = "https://bootstrap.pypa.io/get-pip.py"
$getPipPath = Join-Path $pythonExtracted "get-pip.py"

$webClient = New-Object System.Net.WebClient
$webClient.DownloadFile($getPipUrl, $getPipPath)

& $pythonExe $getPipPath --no-warn-script-location | Out-Host

Write-Host "Pip installed" -ForegroundColor Green

# Install Django dependencies
Write-Host "`nInstalling Django and dependencies (2-3 minutes)...`n" -ForegroundColor Yellow

& $pythonExe -m pip install -r $requirementsFile --no-cache-dir --disable-pip-version-check | Out-Host

Write-Host "`nAll dependencies installed" -ForegroundColor Green

# Verify
Write-Host "`nVerification:" -ForegroundColor Yellow
& $pythonExe --version
& $pythonExe -m pip list | Select-String "Django|djangorestframework|cors|jwt|filter"

$size = (Get-ChildItem $pythonExtracted -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB

Write-Host "`n==== BUNDLE CREATED SUCCESSFULLY ====" -ForegroundColor Green
Write-Host "Location: $pythonExtracted" -ForegroundColor White
Write-Host "Size: $([math]::Round($size, 2)) MB" -ForegroundColor White
Write-Host "`nNext: Build installer to include this bundle`n" -ForegroundColor Yellow
