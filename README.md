# 💎 Crystal POS - Complete Business Management System

<div align="center">

**A comprehensive, production-ready business management and point-of-sale system**

[![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5.13-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**[Features](#-key-features) • [Installation](#-installation) • [Usage](#-usage) • [API Docs](#-api-documentation) • [Development](#-development)**

</div>

---

## 📋 Table of Contents

- [About The Project](#-about-the-project)
- [Key Features](#-key-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
  - [Windows Installer](#windows-installer-recommended)
  - [Manual Setup](#manual-development-setup)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [API Documentation](#-api-documentation)
- [Development](#-development)
- [Building the Installer](#-building-the-installer)
- [Troubleshooting](#-troubleshooting)
- [License](#-license)

---

## 🎯 About The Project

Crystal POS is a **full-stack, enterprise-grade business management system** designed for small to medium-sized manufacturing and retail businesses. Built with modern technologies (Django REST Framework + Vue 3 + TypeScript), it provides a complete solution for managing all aspects of business operations from a single, unified platform.

### What Makes Crystal POS Special?

- **Complete Business Solution**: Not just a POS - includes inventory, manufacturing, vendor management, customer tracking, and financial reporting
- **Windows Desktop App**: Easy one-click installer for Windows - no technical knowledge required
- **Offline Capable**: Works entirely on your local machine - no internet required after installation
- **Real-time Analytics**: Interactive dashboards with ApexCharts providing instant business insights
- **Manufacturing-Ready**: Raw materials tracking, usage monitoring, and production management
- **Professional Reporting**: Export detailed Excel reports with custom filters and date ranges
- **Modern Architecture**: Fully separated backend/frontend with RESTful APIs
- **Type-Safe**: Complete TypeScript implementation ensuring code reliability

---

## ⭐ Key Features

### 🛒 **Sales & POS Module**
- Create sales transactions with multiple items
- Link sales to customers for tracking
- Multiple payment methods (Cash, Card, Bank Transfer, Cheque)
- Automatic inventory deduction
- Payment status tracking (Paid/Unpaid)
- Receipt number generation
- Real-time profit calculation

### 📦 **Inventory Management**
- Product catalog with names, descriptions, and pricing
- Multiple unit types (KG, Piece, Meter, Liter, etc.)
- Stock quantity tracking
- Cost of Production (COP) tracking
- Price vs COP profit margin analysis
- Low stock alerts

### 👥 **Customer Management**
- Customer profiles with contact information
- Purchase history tracking
- Receivables/payables balance calculation
- Payment history
- Active/inactive status

### 🏢 **Vendor Management**
- Vendor profiles and contact details
- Purchase order tracking
- Payables management
- Payment history
- Vendor product catalog

### 🔩 **Raw Materials Module**
- Material inventory with quantities
- Multiple unit support
- Reorder level tracking
- Usage recording with reason tracking
- Purchase history with vendor links
- Low stock alerts

### 💳 **Payment Processing**
- Customer payment recording
- Vendor payment tracking
- Multiple payment methods
- Bank account linking
- Transaction history
- Balance auto-calculation

### 🏭 **Asset Management**
- Machine and equipment tracking
- Mold/tooling management
- Status monitoring (Active/Maintenance/Retired)
- Condition tracking
- Location management

### 📊 **Advanced Analytics Dashboard**
- **Sales Trend Chart**: Area chart showing sales over time
- **Sales vs Purchases**: Comparative line chart
- **Top Customers**: Horizontal bar chart of best customers
- **Product Distribution**: Donut chart of sales by product
- **Top Vendors**: Horizontal bar chart of vendor purchases
- **Payment Methods**: Pie chart of payment distribution
- **Date Filters**: Today, week, month, year, or custom range

### 📈 **Professional Reports Module**
Export detailed Excel reports:
1. **Sales Report**: Complete transaction history with items
2. **Purchases Report**: Vendor purchase details
3. **Inventory Report**: Current stock levels and values
4. **Customer Report**: Customer list with transaction totals
5. **Vendor Report**: Vendor list with purchase amounts
6. **Payments Report**: Payment transaction history
7. **Financial Summary**: Profit/loss overview
8. **Complete Report**: All data in one comprehensive file

### 🔐 **Security & Authentication**
- JWT token-based authentication
- Role-based access control (Admin, Manager, Cashier, Staff)
- Protected API endpoints
- Session management
- Password encryption

---

## 🛠️ Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Django | 5.2.3 | Web framework |
| Django REST Framework | 3.x | REST API |
| Simple JWT | Latest | Authentication |
| SQLite | 3.x | Database |
| Python | 3.10+ | Runtime |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| Vue.js | 3.5.13 | UI framework |
| TypeScript | 5.x | Type-safe JavaScript |
| Vite | 6.3.5 | Build tool |
| Pinia | Latest | State management |
| Tailwind CSS | 3.x | Styling |
| ApexCharts | Latest | Charts/graphs |

### Installer
| Technology | Purpose |
|------------|---------|
| Inno Setup 6 | Windows installer builder |
| PowerShell | Setup scripts |

---

## 📥 Installation

### Windows Installer (Recommended)

1. **Prerequisites**: Install [Python 3.10+](https://www.python.org/downloads/) and ensure it's added to PATH

2. **Download**: Get the latest `CrystalPOS-Setup-1.0.0.exe` from the releases

3. **Install**: Run the installer and follow the prompts
   - Default location: `C:\Program Files (x86)\Crystal POS`
   - The installer will automatically:
     - Create a Python virtual environment
     - Install all dependencies
     - Set up the database
     - Create a default admin user

4. **Launch**: Use the desktop shortcut "Crystal POS" or Start Menu

5. **Login**: 
   - **Username**: `admin`
   - **Password**: `admin123`

### Manual Development Setup

#### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

#### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

---

## 🚀 Usage

### Accessing the Application

After installation or starting the servers:

| Component | URL |
|-----------|-----|
| **Application** | http://localhost:8000 |
| **API Endpoints** | http://localhost:8000/api/ |
| **Django Admin** | http://localhost:8000/admin/ |

### Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |

### Quick Start Guide

1. **Login** with admin credentials
2. **Add Products** in the Products section
3. **Add Customers** and Vendors as needed
4. **Create Sales** to start recording transactions
5. **View Dashboard** for analytics and insights
6. **Generate Reports** for detailed analysis

---

## 📁 Project Structure

```
Crystal/
├── backend/                    # Django REST API
│   ├── core/                  # Project settings
│   │   ├── settings.py        # Django configuration
│   │   ├── urls.py            # URL routing (serves Vue app)
│   │   └── views.py           # Health check endpoint
│   ├── users/                 # User authentication
│   ├── customers/             # Customer management
│   ├── vendors/               # Vendor management
│   ├── products/              # Product catalog
│   ├── sales/                 # Sales transactions
│   ├── purchases/             # Purchase orders
│   ├── payments/              # Payment processing
│   ├── assets/                # Asset management
│   ├── reports/               # Report generation
│   ├── raw_materials/         # Raw material tracking
│   ├── bank_accounts/         # Bank account management
│   ├── manage.py              # Django CLI
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # Vue.js Frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── views/             # Page components
│   │   ├── stores/            # Pinia stores
│   │   ├── types/             # TypeScript types
│   │   ├── router/            # Vue Router config
│   │   └── services/          # API services
│   ├── dist/                  # Built production files
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
├── installer/                  # Windows Installer
│   ├── CrystalPOS.iss         # Inno Setup script
│   ├── setup.ps1              # Post-install setup
│   ├── start-app.ps1          # Application launcher
│   ├── start-backend.ps1      # Backend server launcher
│   └── build-installer.ps1    # Installer build script
│
├── dist/
│   └── installer/             # Built installer EXE
│
└── README.md                   # This file
```

---

## 📚 API Documentation

### Authentication

```bash
# Login
POST /api/users/auth/login/
Body: {"username": "admin", "password": "admin123"}
Response: {"token": "...", "user": {...}}

# Get current user
GET /api/users/auth/me/
Header: Authorization: Bearer <token>
```

### API Endpoints

| Module | Endpoint | Methods |
|--------|----------|---------|
| Users | `/api/users/` | GET, POST, PUT, DELETE |
| Customers | `/api/customers/` | GET, POST, PUT, DELETE |
| Vendors | `/api/vendors/` | GET, POST, PUT, DELETE |
| Products | `/api/products/` | GET, POST, PUT, DELETE |
| Sales | `/api/sales/` | GET, POST, PUT, DELETE |
| Purchases | `/api/purchases/` | GET, POST, PUT, DELETE |
| Payments | `/api/payments/` | GET, POST, PUT, DELETE |
| Assets | `/api/assets/` | GET, POST, PUT, DELETE |
| Raw Materials | `/api/raw-materials/` | GET, POST, PUT, DELETE |
| Bank Accounts | `/api/bank-accounts/` | GET, POST, PUT, DELETE |
| Reports | `/api/reports/` | GET |
| Health Check | `/api/health/` | GET |

### Response Format

All API responses follow this format:

```json
{
  "id": 1,
  "field": "value",
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-01T00:00:00Z"
}
```

---

## 💻 Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm 9+
- Git

### Running in Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm run dev
```

Access at http://localhost:5173 (Vite dev server with hot reload)

### Code Style

- **Python**: Follow PEP 8
- **TypeScript**: ESLint + Prettier configured
- **Vue**: Composition API with `<script setup>`

---

## 📦 Building the Installer

### Prerequisites

1. Install [Inno Setup 6](https://jrsoftware.org/isinfo.php)
2. Build the frontend: `cd frontend && npm run build`

### Build Steps

```powershell
# Option 1: Use the build script
cd installer
.\build-installer.ps1

# Option 2: Manual Inno Setup compile
& "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe" ".\installer\CrystalPOS.iss"
```

### Output

The installer will be created at:
```
dist/installer/CrystalPOS-Setup-1.0.0.exe
```

### What the Installer Does

1. Copies backend and frontend files to Program Files
2. Creates Python virtual environment
3. Installs pip dependencies
4. Runs Django migrations
5. Creates admin user (admin/admin123)
6. Creates desktop and Start Menu shortcuts
7. Sets up environment variables

---

## 🔧 Troubleshooting

### Common Issues

#### "Python is not installed"
- Download and install Python 3.10+ from python.org
- Make sure to check "Add Python to PATH" during installation

#### Backend server won't start
- Check if port 8000 is in use: `netstat -ano | findstr :8000`
- Kill the process or use a different port

#### Login fails with 500 error
- Check backend logs at `C:\Program Files (x86)\Crystal POS\logs\`
- Ensure database migrations ran successfully

#### Assets not loading (404)
- Make sure frontend was built: `cd frontend && npm run build`
- Rebuild the installer after frontend changes

#### Database errors
- Check if `data\db.sqlite3` exists in install directory
- Try running migrations manually:
  ```powershell
  cd "C:\Program Files (x86)\Crystal POS"
  .\venv\Scripts\python.exe backend\manage.py migrate
  ```

### Logs Location

| Log | Path |
|-----|------|
| Backend Log | `C:\Program Files (x86)\Crystal POS\logs\backend.log` |
| Backend Errors | `C:\Program Files (x86)\Crystal POS\logs\backend_error.log` |
| Setup Log | `C:\Program Files (x86)\Crystal POS\logs\setup_latest.log` |

### Getting Help

If you encounter issues:
1. Check the logs above
2. Ensure Python 3.10+ is installed and in PATH
3. Try uninstalling and reinstalling

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors

- **Crystal POS Team**

---

<div align="center">

**Made with ❤️ for small businesses**

[⬆ Back to top](#-crystal-pos---complete-business-management-system)

</div>
