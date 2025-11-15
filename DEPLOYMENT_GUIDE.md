# Crystal POS - Desktop App Deployment Guide

## Overview
This guide covers the complete process of deploying Crystal POS as a standalone desktop application.

## Build Options

### Option 1: Development Build (Recommended for Testing)
- **Size:** ~200MB
- **Requires:** Python installed on target machine
- **Backend:** Runs using `python manage.py runserver`
- **Pros:** Easier debugging, smaller build time
- **Cons:** Requires Python installation

### Option 2: Production Build (Recommended for Distribution)
- **Size:** ~150MB
- **Requires:** Nothing (fully standalone)
- **Backend:** Bundled executable
- **Pros:** No dependencies, fully portable
- **Cons:** Larger build time, harder to debug

---

## Quick Build (Development)

```bash
# 1. Navigate to frontend
cd frontend

# 2. Install dependencies (if not done)
npm install

# 3. Build frontend
npm run build

# 4. Build Windows installer
npm run electron:build:win
```

**Output:** `frontend/release/Crystal POS-Setup-0.0.0.exe`

---

## Production Build (With Backend Executable)

```bash
# 1. Build backend executable
cd backend
python build_backend.py

# 2. Build frontend and package
cd ../frontend
npm run build
npm run electron:build:win
```

**Output:** `frontend/release/Crystal POS-Setup-0.0.0.exe`

---

## Installation

### For Users:

1. **Download** the installer (.exe file)
2. **Run** the installer (may require Administrator)
3. **Choose** installation directory (default: `C:\Users\{User}\AppData\Local\Programs\crystal-pos`)
4. **Wait** for installation to complete
5. **Launch** from Desktop shortcut or Start Menu

### First Launch:

1. Setup wizard appears
2. Click "Start Setup"
3. Database initializes automatically
4. Backend server starts
5. Main app window opens

### Subsequent Launches:

- No setup wizard
- Backend starts automatically
- Opens directly to login/dashboard

---

## App Data Locations

### Windows:
- **App Data:** `C:\Users\{User}\AppData\Roaming\crystal-pos\`
- **Database:** `C:\Users\{User}\AppData\Roaming\crystal-pos\db.sqlite3`
- **Config:** `C:\Users\{User}\AppData\Roaming\crystal-pos\config.json`
- **Logs:** `C:\Users\{User}\AppData\Roaming\crystal-pos\logs\`

### Files Created:
- `db.sqlite3` - SQLite database
- `config.json` - App configuration
- `.setup_complete` - Setup completion flag

---

## Distribution

### Method 1: GitHub Releases (Recommended)

1. Create a new release on GitHub
2. Upload the `.exe` installer
3. Add release notes
4. Users download from Releases page

```bash
# Tag and push release
git tag v1.0.0
git push origin v1.0.0
```

### Method 2: Direct Download

1. Upload installer to web server
2. Create download link
3. Share link with users

### Method 3: Enterprise Deployment

1. Place installer on network share
2. Deploy via group policy
3. Silent install: `Crystal-POS-Setup-0.0.0.exe /S`

---

## Versioning

Update version in `frontend/package.json`:

```json
{
  "version": "1.0.0"
}
```

Installer will be named: `Crystal POS-Setup-1.0.0.exe`

---

## Updating the App

### For New Releases:

1. Build new installer with updated version
2. Users download new installer
3. Run installer (will upgrade existing installation)
4. Database and settings are preserved

### Auto-Update (Future):

To implement auto-updates:
- Install `electron-updater` package
- Configure update server
- App checks for updates on startup

---

## Troubleshooting

### Build Fails:

**"dist/ folder not found"**
```bash
npm run build
```

**"Python not found"**
```bash
# Install Python 3.14 or higher
# Add to PATH
```

**"electron-builder error"**
```bash
npm cache clean --force
npm install
```

### App Won't Start:

**Check logs:**
- Press `Ctrl+Shift+I` to open DevTools
- Check Console tab for errors

**Backend not starting:**
- Check if port 8000 is available
- Check Task Manager for stuck python.exe processes

**Database error:**
- Delete `AppData/Roaming/crystal-pos/db.sqlite3`
- Restart app (will create fresh database)

### Installer Issues:

**"Windows protected your PC"**
- Click "More info" → "Run anyway"
- Or sign the installer with a code signing certificate

**Antivirus blocks installer**
- Add exception for Crystal POS
- Temporarily disable antivirus

---

## Performance Optimization

### Reduce Bundle Size:

1. Remove unused dependencies
2. Compress assets
3. Use production builds only

### Faster Startup:

1. Optimize backend startup
2. Lazy-load heavy modules
3. Cache frequently used data

---

## Security Considerations

### Production Checklist:

- ✅ Change Django SECRET_KEY
- ✅ Disable DEBUG mode
- ✅ Enable HTTPS (if using remote backend)
- ✅ Implement proper authentication
- ✅ Regular security updates
- ✅ Code signing certificate (for trust)

### Code Signing (Optional):

Benefits:
- Removes "Unknown publisher" warning
- Builds trust with users
- Prevents tampering

Cost:
- ~$100-400/year for certificate
- Additional setup time

---

## Support & Maintenance

### User Support:

- Create user manual
- Setup FAQ page
- Provide support email
- Create video tutorials

### Regular Updates:

- Bug fixes
- Security patches
- New features
- Database backups

---

## License & Distribution

Make sure to:
- Include LICENSE file
- Add copyright notices
- Comply with open-source licenses
- Document dependencies

---

## Next Steps

After successful build:

1. ✅ Test installer on clean machine
2. ✅ Test first-run setup
3. ✅ Test offline functionality
4. ✅ Test update process
5. ✅ Create user documentation
6. ✅ Plan deployment strategy
7. ✅ Setup support channels

---

**For more details, see BUILD_INSTRUCTIONS.md**
