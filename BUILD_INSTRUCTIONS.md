# Build Instructions for Crystal POS Desktop App

## Prerequisites
- Node.js installed
- Python installed
- All dependencies installed (`npm install` in frontend, `pip install -r requirements.txt` in backend)

## Build Steps

### Step 1: Build Frontend
```bash
cd frontend
npm run build
```

This creates the production `dist/` folder with optimized Vue app.

### Step 2: Build Backend (Optional - for standalone executable)
```bash
cd backend
python build_backend.py
```

This creates `backend/dist/crystal-backend.exe` using PyInstaller.

**Note:** For development builds, you can skip this step. The app will use `python manage.py runserver` instead.

### Step 3: Build Electron App
```bash
cd frontend
npm run electron:build:win
```

This creates the Windows installer in `frontend/release/`.

## Output Files

### Development Build (without backend executable)
- `Crystal POS Setup X.X.X.exe` - NSIS installer (~200MB)
- Includes entire backend folder with Python files
- Requires Python to be installed on target machine

### Production Build (with backend executable)
- `Crystal POS Setup X.X.X.exe` - NSIS installer (~150MB)
- Includes standalone backend executable
- No Python installation required

## Testing the Build

1. Run the installer
2. Install to desired location (e.g., `C:\Program Files\Crystal POS`)
3. Launch from Start Menu or Desktop shortcut
4. First run: Setup wizard will initialize database
5. Subsequent runs: Direct to main app

## Build Configuration

Edit `package.json` to customize:
- `appId`: Application identifier
- `productName`: Display name
- `icon`: App icon path
- `nsis`: Installer settings

## Troubleshooting

**Build fails:**
- Ensure `npm run build` completes successfully first
- Check that all dependencies are installed
- Try `npm cache clean --force` and reinstall

**App doesn't start:**
- Check console for errors (press Ctrl+Shift+I in development)
- Verify backend is starting (check Task Manager for python.exe)
- Check database path in AppData folder

**Installer issues:**
- Run as Administrator
- Disable antivirus temporarily
- Check available disk space (needs ~500MB)

## Distribution

The generated `.exe` file in `frontend/release/` can be distributed directly.
Users just need to download and run the installer.

### Recommended Distribution Methods:
1. GitHub Releases - Upload to repository releases page
2. Direct download - Host on website/server
3. USB/Physical media - Copy installer to removable media
4. Network share - Place in shared folder for enterprise deployment

## Auto-Updates (Future Enhancement)

To add auto-update functionality:
1. Install `electron-updater`
2. Set up a releases server
3. Configure `publish` in electron-builder config
4. App will check for updates on startup
