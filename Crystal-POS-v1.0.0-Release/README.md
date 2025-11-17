# Crystal POS - Desktop Application Installer

## 📦 Installation

### System Requirements
- **Operating System**: Windows 10/11 (64-bit)
- **Python**: 3.10 or higher (required for backend)
- **RAM**: Minimum 4GB
- **Disk Space**: 500MB free space
- **Internet**: Optional (for initial setup only)

### Installation Steps

1. **Download the Installer**
   - Locate `Crystal POS-Setup-1.0.0.exe` (91.73 MB)

2. **Run the Installer**
   - Right-click the installer
   - Select "Run as Administrator"
   - Follow the installation wizard

3. **Choose Installation Location**
   - Default: `C:\Program Files\Crystal POS`
   - Or choose custom location

4. **First Launch**
   - Desktop shortcut will be created
   - Start Menu entry: "Crystal POS"
   - Click to launch

5. **Initial Setup**
   - On first run, a setup wizard will appear
   - Database will be initialized automatically
   - Click "Start Setup" to proceed

6. **Login**
   - **Default Username**: `admin`
   - **Default Password**: `admin123`
   - ⚠️ **Important**: Change password after first login!

---

## 🚀 Features

- ✅ **Offline First**: Works without internet connection
- ✅ **Complete POS System**: Sales, purchases, inventory
- ✅ **Customer Management**: Track customers and transactions
- ✅ **Vendor Management**: Manage suppliers
- ✅ **Payment Tracking**: Multiple payment methods
- ✅ **Reports & Analytics**: Sales reports, inventory reports
- ✅ **Asset Management**: Track business assets
- ✅ **Raw Materials**: Manufacturing support
- ✅ **Multi-User**: User management system

---

## 🔧 Troubleshooting

### App Won't Start
1. Make sure Python is installed
2. Check if port 8000 is available
3. Run as Administrator
4. Check logs in: `%APPDATA%\crystal-fronend\`

### Database Issues
1. Navigate to: `C:\Users\<YourName>\AppData\Roaming\crystal-fronend\`
2. Delete `db.sqlite3` to reset
3. Restart the app for fresh setup

### Python Not Found
1. Download Python from: https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Restart computer after Python installation

### Port Already in Use
- Close any apps using port 8000
- Or restart your computer

---

## 📝 Creating Superuser (If Needed)

If you need to create a new admin user:

1. Open PowerShell/Command Prompt
2. Navigate to installation folder
3. Run:
```powershell
cd "C:\Users\<YourName>\AppData\Roaming\crystal-fronend"
python manage.py createsuperuser
```

---

## 🗑️ Uninstallation

1. Go to Windows Settings → Apps
2. Find "Crystal POS"
3. Click "Uninstall"
4. Optional: Delete app data from `%APPDATA%\crystal-fronend\`

---

## 📞 Support

For issues or questions:
- GitHub: https://github.com/abdul-wahab608/Crystal-POS
- Email: support@crystalpos.com (if applicable)

---

## 📄 License & Credits

Crystal POS - Point of Sale Desktop Application
Version 1.0.0

Built with:
- Electron (Desktop shell)
- Vue.js 3 (Frontend)
- Django (Backend)
- SQLite (Database)

---

## 🔐 Security Notes

- Change default password immediately
- Keep your installation updated
- Regular backups recommended (backup `db.sqlite3`)
- Don't share your credentials

---

## 💾 Backup Your Data

**Important**: Your data is stored in:
```
C:\Users\<YourName>\AppData\Roaming\crystal-fronend\db.sqlite3
```

**Backup regularly** by copying this file to a safe location!

---

## 🎯 Quick Start Guide

1. **Install** → Run installer as admin
2. **Launch** → Click desktop icon
3. **Setup** → Click "Start Setup" button
4. **Login** → Use `admin` / `admin123`
5. **Change Password** → Go to Settings
6. **Start Using** → Add products, customers, make sales!

---

## ⚡ Performance Tips

- Keep database size manageable (< 100MB for best performance)
- Close unused apps while running POS
- Regular database maintenance
- Clear old transaction logs periodically

---

**Enjoy using Crystal POS! 🎉**
