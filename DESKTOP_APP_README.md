# 💎 Crystal POS - Desktop Application

> **Complete Point of Sale & Business Management System**  
> Standalone desktop app with offline support for Windows, macOS, and Linux

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-green.svg)](package.json)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)](BUILD_INSTRUCTIONS.md)

---

## 🚀 Desktop App Features

### ✨ Core Capabilities
- 🖥️ **Standalone Desktop Application** - No browser required
- 🔌 **Full Offline Support** - Works without internet connection
- 💾 **Local Database** - SQLite with automatic sync
- 🔄 **Auto-sync** - Syncs changes when back online
- 📦 **One-click Installation** - Easy setup wizard
- 🎯 **Native Performance** - Built with Electron
- 🔐 **Secure Local Storage** - Data stored in user's AppData folder

### 📊 Business Features
- **Sales Management** - Complete POS system
- **Inventory Tracking** - Real-time stock management
- **Customer Management** - CRM functionality
- **Vendor Management** - Supplier tracking
- **Purchase Orders** - Procurement system
- **Reports & Analytics** - 8 Excel report types with charts
- **Payment Tracking** - Multi-payment support
- **Asset Management** - Equipment & asset tracking

---

## 📥 Installation

### For End Users:

1. **Download** the latest installer:
   - Windows: `Crystal-POS-Setup-1.0.0.exe`
   - macOS: `Crystal-POS-1.0.0.dmg`
   - Linux: `Crystal-POS-1.0.0.AppImage`

2. **Run** the installer
3. **Follow** the setup wizard
4. **Launch** from Desktop or Start Menu

### First Launch:
- Setup wizard initializes database
- Backend server starts automatically
- Ready to use in seconds!

---

## 🛠️ For Developers

### Prerequisites
```bash
# Node.js 18+ and Python 3.14+
node --version
python --version
```

### Clone & Setup
```bash
# Clone repository
git clone https://github.com/abdul-wahab608/Crystal-POS.git
cd Crystal-POS

# Checkout desktop app branch
git checkout desktop-app

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip install -r requirements.txt
```

### Development Mode
```bash
# Start in development mode (hot reload enabled)
cd frontend
npm run electron:dev
```

This starts:
- ✅ Vite dev server (frontend)
- ✅ Django backend (auto-start)
- ✅ Electron window

### Build Production App
```bash
# Build Windows installer
npm run electron:build:win

# Build for macOS
npm run electron:build:mac

# Build for Linux
npm run electron:build:linux
```

**Output:** `frontend/release/Crystal-POS-Setup-*.exe`

For detailed build instructions, see [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md)

---

## 🏗️ Architecture

### Technology Stack
- **Frontend:** Vue 3.5 + TypeScript + Vite
- **Desktop Shell:** Electron 39
- **Backend:** Django 5.2 + Django REST Framework
- **Database:** SQLite (local) + IndexedDB (cache)
- **Charts:** ApexCharts
- **Reports:** XLSX.js (Excel generation)

### Project Structure
```
Crystal-POS/
├── frontend/               # Vue 3 + Electron
│   ├── electron/          # Electron main process
│   │   ├── main.cjs       # Main process entry
│   │   ├── preload.cjs    # IPC bridge
│   │   ├── port-utils.cjs # Port management
│   │   └── setup.html     # First-run setup UI
│   ├── src/               # Vue app
│   │   ├── shared/        # Shared utilities
│   │   │   ├── utils/     # Offline & DB managers
│   │   │   └── components/# Reusable components
│   │   └── modules/       # Feature modules
│   └── scripts/           # Build scripts
├── backend/               # Django REST API
│   ├── core/              # Django settings
│   ├── [app modules]/     # Business logic
│   ├── build_backend.py   # PyInstaller script
│   └── server_manager.py  # Backend entry point
├── BUILD_INSTRUCTIONS.md  # Build guide
└── DEPLOYMENT_GUIDE.md    # Deployment docs
```

---

## 🔌 Offline Capabilities

### How It Works:

**Online Mode:**
- ✅ All operations go to Django backend
- ✅ Responses cached in IndexedDB
- ✅ Real-time data updates

**Going Offline:**
- 🔴 Red banner appears
- 📦 Reads from cache
- 📥 Writes queued for sync

**Back Online:**
- 🔄 Blue banner shows "Syncing..."
- ✅ Queue processed automatically
- 🟢 Banner disappears when synced

### Features:
- **Smart Caching** - 30-minute TTL for GET requests
- **Sync Queue** - POST/PUT/DELETE operations queued
- **Auto-retry** - Failed syncs retry 3 times
- **Conflict Resolution** - Last-write-wins strategy
- **Offline Settings** - Manual sync & cache management

---

## 📱 App Data Storage

### Windows:
```
C:\Users\{User}\AppData\Roaming\crystal-pos\
├── db.sqlite3           # Database
├── config.json          # Configuration
├── .setup_complete      # Setup flag
└── logs/                # Application logs
```

### macOS:
```
~/Library/Application Support/crystal-pos/
```

### Linux:
```
~/.config/crystal-pos/
```

---

## 🔐 Security Features

- ✅ JWT Authentication
- ✅ Local data encryption (user's AppData)
- ✅ Dynamic secret keys
- ✅ CORS protection
- ✅ SQL injection prevention
- ✅ XSS protection

---

## 📊 Reports & Analytics

### Available Reports:
1. **Sales Report** - Daily/monthly sales analysis
2. **Purchases Report** - Procurement tracking
3. **Inventory Report** - Stock levels & valuation
4. **Customer Report** - Customer analytics
5. **Vendor Report** - Supplier performance
6. **Payment Report** - Financial transactions
7. **Financial Summary** - P&L statement
8. **Complete Business Report** - All-in-one report

All reports export to Excel with:
- ✅ Summary sheets
- ✅ Detailed data
- ✅ Charts & graphs
- ✅ Timestamp tracking

---

## 🐛 Troubleshooting

### App Won't Start
```bash
# Check if port 8000 is available
netstat -ano | findstr :8000

# Kill conflicting process
taskkill /PID [PID] /F

# Clear app data and restart
# Delete: %APPDATA%\crystal-pos\
```

### Build Issues
```bash
# Clear caches
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# Rebuild
npm run build
npm run electron:build:win
```

### Database Errors
```bash
# Reset database
# Delete: %APPDATA%\crystal-pos\db.sqlite3
# Restart app (creates fresh database)
```

For more troubleshooting, see [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

---

## 🚀 Deployment

### Distribution Options:

1. **GitHub Releases** (Recommended)
   - Upload installer to Releases
   - Users download directly
   - Version tracking

2. **Direct Download**
   - Host on web server
   - Share download link

3. **Enterprise Deployment**
   - Network share
   - Group Policy
   - Silent install: `/S` flag

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for complete deployment guide.

---

## 🔄 Updates

### Manual Update:
1. Download new installer
2. Run installer
3. Existing installation upgraded
4. Database/settings preserved

### Auto-Update (Future):
- Install `electron-updater`
- Configure update server
- App checks on startup

---

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/abdul-wahab608/Crystal-POS/issues)
- **Discussions:** [GitHub Discussions](https://github.com/abdul-wahab608/Crystal-POS/discussions)
- **Email:** support@crystalpos.com

---

## 🎯 Roadmap

### Version 1.1
- [ ] Auto-update functionality
- [ ] Multi-language support
- [ ] Cloud backup
- [ ] Receipt printer support

### Version 2.0
- [ ] Multi-store support
- [ ] Real-time collaboration
- [ ] Mobile companion app
- [ ] Advanced analytics

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=abdul-wahab608/Crystal-POS&type=Date)](https://star-history.com/#abdul-wahab608/Crystal-POS&Date)

---

**Made with ❤️ by Crystal POS Team**

[⬆ Back to top](#-crystal-pos---desktop-application)
