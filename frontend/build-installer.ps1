# Crystal POS Installer Build Script
Write-Host "🚀 Building Crystal POS Installer..." -ForegroundColor Cyan
Write-Host ""

# Set environment variables
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"
$env:NODE_OPTIONS = "--no-deprecation"

# Navigate to frontend directory
Set-Location "c:\Globacode stuff\Crystal project\Crystal\Crystal\frontend"

# Clean previous build
Write-Host "🧹 Cleaning previous build..." -ForegroundColor Yellow
Remove-Item -Path "release" -Recurse -Force -ErrorAction SilentlyContinue

# Build frontend
Write-Host "📦 Building frontend..." -ForegroundColor Yellow
npm run build-only
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Frontend build failed!" -ForegroundColor Red
    exit 1
}

# Build installer
Write-Host "🔨 Building Windows installer..." -ForegroundColor Yellow
npx electron-builder --win --x64

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host ""
    
    $installer = Get-Item "release\Crystal POS-Setup-*.exe" -ErrorAction SilentlyContinue
    if ($installer) {
        Write-Host "📦 Installer Details:" -ForegroundColor Cyan
        Write-Host "   File: $($installer.Name)"
        Write-Host "   Size: $([math]::Round($installer.Length/1MB,2)) MB"
        Write-Host "   Path: $($installer.FullName)"
        Write-Host ""
        Write-Host "🎉 You can now distribute this installer!" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "❌ Build failed! Check errors above." -ForegroundColor Red
    exit 1
}
