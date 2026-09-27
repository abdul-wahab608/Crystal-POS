# Stages a fully self-contained, relocatable Python runtime with every
# backend dependency pre-installed, so the Inno Setup installer can ship
# Python + packages inside the .exe instead of requiring the target
# machine to have Python and internet access at install time.
#
# This script needs internet - it runs on the DEVELOPER's build machine.
# The output (installer/runtime/python/) is what setup.ps1 unpacks on the
# CLIENT machine, entirely offline.

param(
    [string]$PythonVersion = "3.14.0",
    [switch]$Force
)

$ErrorActionPreference = "Stop"
$InstallerDir = $PSScriptRoot
$ProjectRoot = Split-Path -Parent $InstallerDir
$RuntimeDir = Join-Path $InstallerDir "runtime\python"
$RequirementsPath = Join-Path $ProjectRoot "backend\requirements.txt"

if ((Test-Path $RuntimeDir) -and -not $Force) {
    $PythonExe = Join-Path $RuntimeDir "python.exe"
    if ((Test-Path $PythonExe) -and (Test-Path (Join-Path $RuntimeDir "Lib\site-packages\django"))) {
        Write-Host "Runtime already staged at: $RuntimeDir (use -Force to rebuild)"
        exit 0
    }
}

Write-Host "=========================================="
Write-Host "Staging offline Python runtime ($PythonVersion)"
Write-Host "=========================================="

if (Test-Path $RuntimeDir) {
    Write-Host "Removing existing staged runtime..."
    Remove-Item $RuntimeDir -Recurse -Force
}
New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null

# Step 1: Download the embeddable distribution
$EmbedUrl = "https://www.python.org/ftp/python/$PythonVersion/python-$PythonVersion-embed-amd64.zip"
$EmbedZip = Join-Path $env:TEMP "python-$PythonVersion-embed-amd64.zip"

Write-Host ""
Write-Host "Step 1: Downloading embeddable Python from $EmbedUrl"
Invoke-WebRequest -Uri $EmbedUrl -OutFile $EmbedZip -UseBasicParsing

Write-Host "Extracting to $RuntimeDir"
Expand-Archive -Path $EmbedZip -DestinationPath $RuntimeDir -Force
Remove-Item $EmbedZip -Force

# Step 2: Enable site-packages (embeddable distros disable `import site` by default,
# which breaks normal site-packages discovery for pip-installed packages)
Write-Host ""
Write-Host "Step 2: Enabling site-packages in embeddable distribution"
$PthFile = Get-ChildItem -Path $RuntimeDir -Filter "python*._pth" | Select-Object -First 1
if (-not $PthFile) {
    throw "Could not find python*._pth in $RuntimeDir"
}
$PthContent = Get-Content $PthFile.FullName
$PthContent = $PthContent -replace '^#import site$', 'import site'

# A ._pth file makes this interpreter fully "isolated": sys.path becomes ONLY
# the paths listed here, so PYTHONPATH and the normal auto-insertion of the
# executed script's own directory are BOTH ignored (documented CPython
# behavior for embeddable distributions). The backend package (`core`, etc.)
# would otherwise be unimportable no matter how it's invoked. Add it as a
# relative path - it resolves against python.exe's own directory, and
# {app}\python and {app}\backend are always sibling folders by construction
# of CrystalPOS.iss's [Files] section, so this holds regardless of install location.
$PthContent += "..\backend"
Set-Content -Path $PthFile.FullName -Value $PthContent

# IMPORTANT: an embeddable interpreter's "user site-packages" path on Windows is keyed
# only by Python version (%APPDATA%\Python\PythonXY\site-packages), so it collides with
# any regular Python install of the same version already on the build machine. Without
# PYTHONNOUSERSITE, pip silently installs/upgrades packages into that shared global
# location instead of the runtime folder - not self-contained, and it mutates the build
# machine's own Python environment as a side effect. Force everything into the runtime's
# own Lib\site-packages via --target and disable user-site resolution entirely.
$PythonExe = Join-Path $RuntimeDir "python.exe"
$SitePackages = Join-Path $RuntimeDir "Lib\site-packages"
$env:PYTHONNOUSERSITE = "1"

# Step 3: Bootstrap pip
Write-Host ""
Write-Host "Step 3: Bootstrapping pip"
$GetPipScript = Join-Path $env:TEMP "get-pip.py"
Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile $GetPipScript -UseBasicParsing
& $PythonExe $GetPipScript --no-warn-script-location --target $SitePackages
if ($LASTEXITCODE -ne 0) {
    throw "Failed to bootstrap pip into embeddable runtime"
}
Remove-Item $GetPipScript -Force

# Step 4: Install backend dependencies directly into the runtime's site-packages
Write-Host ""
Write-Host "Step 4: Installing backend requirements into runtime"
if (!(Test-Path $RequirementsPath)) {
    throw "requirements.txt not found at: $RequirementsPath"
}
& $PythonExe -m pip install --no-cache-dir --target $SitePackages -r $RequirementsPath
if ($LASTEXITCODE -ne 0) {
    throw "pip install failed with exit code $LASTEXITCODE"
}

# Step 5: Verify
Write-Host ""
Write-Host "Step 5: Verifying runtime"
$DjangoCheck = & $PythonExe -c "import django; print(django.VERSION)"
Write-Host "  Django: $DjangoCheck"
$PandasCheck = & $PythonExe -c "import pandas; print(pandas.__version__)"
Write-Host "  pandas: $PandasCheck"

$RuntimeSize = (Get-ChildItem $RuntimeDir -Recurse | Measure-Object -Property Length -Sum).Sum / 1MB
Write-Host ""
Write-Host "=========================================="
Write-Host "Runtime staged successfully at: $RuntimeDir"
Write-Host "Size: $([math]::Round($RuntimeSize, 1)) MB"
Write-Host "=========================================="
