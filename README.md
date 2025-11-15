# 💎 Crystal POS - Complete Business Management System

<div align="center">

**A comprehensive, production-ready business management and point-of-sale system**

[![Django](https://img.shields.io/badge/Django-5.2.3-green.svg)](https://www.djangoproject.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.5.13-brightgreen.svg)](https://vuejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-blue.svg)](https://www.typescriptlang.org/)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)

</div>

---

## 📋 Table of Contents

- [About The Project](#about-the-project)
- [What Crystal POS Does](#what-crystal-pos-does)
- [Problems It Solves](#problems-it-solves)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [How to Run](#how-to-run)
- [Working with the Project](#working-with-the-project)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Production Deployment](#production-deployment)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 About The Project

Crystal POS is a **full-stack, enterprise-grade business management system** designed for small to medium-sized manufacturing and retail businesses. Built with modern technologies (Django REST Framework + Vue 3 + TypeScript), it provides a complete solution for managing all aspects of business operations from a single, unified platform.

### What Makes Crystal POS Special?

- **Complete Business Solution**: Not just a POS - includes inventory, manufacturing, vendor management, customer tracking, and financial reporting
- **Real-time Analytics**: Interactive dashboards with ApexCharts providing instant business insights
- **Manufacturing-Ready**: Raw materials tracking, usage monitoring, and production management
- **Professional Reporting**: Export detailed Excel reports with custom filters and date ranges
- **Modern Architecture**: Fully separated backend/frontend with RESTful APIs
- **Type-Safe**: Complete TypeScript implementation ensuring code reliability
- **Production-Ready**: Clean codebase, proper authentication, and scalable architecture

---

## 💡 What Crystal POS Does

Crystal POS is an **all-in-one business management platform** that handles:

### 📊 Core Business Operations
- **Point of Sale (POS)**: Fast, efficient sales transactions with real-time inventory updates
- **Inventory Management**: Track products with multiple units, quantities, and cost tracking
- **Customer Management**: Maintain customer records, purchase history, and receivables
- **Vendor Management**: Track suppliers, purchase orders, and payables
- **Raw Materials**: Monitor raw material inventory, usage, and reordering

### 💰 Financial Management
- **Payment Processing**: Record and track customer and vendor payments
- **Receivables/Payables**: Automatic balance calculations and tracking
- **Financial Reports**: Comprehensive profit/loss analysis and cash flow tracking
- **Bank Account Management**: Multiple account tracking and reconciliation

### 📈 Analytics & Reporting
- **Interactive Dashboards**: 6 real-time charts showing business performance
- **Custom Filters**: Filter data by date, customer, vendor, product
- **Excel Export**: Generate professional reports in 8 different formats
- **Sales Analytics**: Track top products, customer trends, and sales patterns

### 🏭 Manufacturing Features
- **Raw Material Tracking**: Monitor inventory levels with reorder alerts
- **Usage Recording**: Track material consumption in production
- **Asset Management**: Manage machines, molds, and equipment
- **Purchase Tracking**: Link purchases to vendors with automatic inventory updates

---

## 🔧 Problems It Solves

### For Small Businesses
✅ **No More Spreadsheet Chaos**: Replace dozens of Excel files with one integrated system  
✅ **Real-time Inventory**: Know exactly what's in stock at any moment  
✅ **Customer Tracking**: Never lose track of who owes you money  
✅ **Professional Reports**: Generate business reports in seconds, not hours  

### For Manufacturing
✅ **Material Management**: Track raw materials from purchase to production  
✅ **Usage Monitoring**: Know exactly how much material each product uses  
✅ **Reorder Alerts**: Automatic low-stock notifications prevent production delays  
✅ **Asset Tracking**: Manage machines and equipment in one place  

### For Retail
✅ **Fast POS**: Quick checkout process with real-time stock deduction  
✅ **Multi-Unit Support**: Handle products in different units (kg, pieces, meters, etc.)  
✅ **Customer History**: See complete purchase history for better service  
✅ **Sales Analytics**: Identify best-selling products and trends  

### For Financial Management
✅ **Automatic Calculations**: System updates balances automatically  
✅ **Payment Tracking**: Never miss a customer or vendor payment  
✅ **Profit Analysis**: See profit margins and financial health instantly  
✅ **Audit Trail**: Complete transaction history for compliance  

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
- Product history and audit trail

### 👥 **Customer Management**
- Customer profiles with contact information
- Purchase history tracking
- Receivables/payables balance calculation
- Payment history
- Active/inactive status
- Customer analytics and insights

### 🏢 **Vendor Management**
- Vendor profiles and contact details
- Purchase order tracking
- Payables management
- Payment history
- Vendor product catalog
- Multiple vendors per product

### 🔩 **Raw Materials Module**
- Material inventory with quantities
- Multiple unit support
- Reorder level tracking
- Usage recording with reason tracking
- Purchase history with vendor links
- Available stock calculation
- Low stock alerts
- Material-specific analytics

### 💳 **Payment Processing**
- Customer payment recording
- Vendor payment tracking
- Multiple payment methods
- Bank account linking
- Payment status management
- Transaction history
- Balance auto-calculation

### 🏭 **Asset Management**
- Machine and equipment tracking
- Mold/tooling management
- Status monitoring (Active/Maintenance/Retired)
- Condition tracking
- Location management
- Value depreciation tracking

### 📊 **Advanced Analytics Dashboard**
- **Sales Trend Chart**: Area chart showing sales over time
- **Sales vs Purchases**: Comparative line chart
- **Top Customers**: Horizontal bar chart of best customers
- **Product Distribution**: Donut chart of sales by product
- **Top Vendors**: Horizontal bar chart of vendor purchases
- **Payment Methods**: Pie chart of payment distribution
- **Filter System**: Date ranges (today/week/month/year/custom)
- **Multi-Filter**: Combine customer, vendor, and product filters

### 📈 **Professional Reports Module**
Export detailed Excel reports with summary and detail sheets:
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
- Secure token storage

---

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.2.3
- **API**: Django REST Framework
- **Authentication**: Simple JWT
- **Database**: SQLite (development) / PostgreSQL (production)
- **Python**: 3.8+

### Frontend
- **Framework**: Vue 3.5.13 (Composition API)
- **Language**: TypeScript
- **Build Tool**: Vite 6.3.5
- **State Management**: Pinia
- **Routing**: Vue Router
- **Charts**: ApexCharts (vue3-apexcharts)
- **Excel Export**: XLSX.js + file-saver
- **Styling**: Tailwind CSS
- **Testing**: Vitest + Nightwatch

### Development Tools
- **Code Editor**: VS Code recommended
- **Version Control**: Git
- **Package Manager**: npm (frontend), pip (backend)
- **API Testing**: Built-in test suite

---

## 📁 Project Structure

```
Crystal/
├── backend/                      # Django REST API Backend
│   ├── core/                    # Project settings & configuration
│   │   ├── settings.py         # Django settings
│   │   ├── urls.py             # Root URL configuration
│   │   ├── wsgi.py             # WSGI configuration
│   │   └── asgi.py             # ASGI configuration
│   │
│   ├── users/                   # User authentication & management
│   │   ├── models.py           # Custom user model
│   │   ├── views.py            # Auth views (login, logout, register)
│   │   ├── serializers.py      # User serializers
│   │   ├── permissions.py      # Role-based permissions
│   │   └── urls.py             # Auth endpoints
│   │
│   ├── customers/               # Customer management module
│   │   ├── models.py           # Customer model
│   │   ├── views.py            # Customer CRUD operations
│   │   ├── serializers.py      # Customer data serialization
│   │   ├── signals.py          # Auto-calculations & triggers
│   │   └── urls.py             # Customer endpoints
│   │
│   ├── vendors/                 # Vendor management module
│   │   ├── models.py           # Vendor & VendorProduct models
│   │   ├── views.py            # Vendor operations
│   │   ├── serializers.py      # Vendor serialization
│   │   └── urls.py             # Vendor endpoints
│   │
│   ├── products/                # Product inventory module
│   │   ├── models.py           # Product & ProductHistory models
│   │   ├── views.py            # Product CRUD & stock management
│   │   ├── serializers.py      # Product data handling
│   │   └── urls.py             # Product endpoints
│   │
│   ├── raw_materials/           # Raw materials module
│   │   ├── models.py           # Material, Usage, Purchase models
│   │   ├── views.py            # Material management & tracking
│   │   ├── serializers.py      # Material data serialization
│   │   └── urls.py             # Raw material endpoints
│   │
│   ├── sales/                   # Sales & POS module
│   │   ├── models.py           # Sale & SaleItem models
│   │   ├── views.py            # Sales transactions
│   │   ├── serializers.py      # Sales data handling
│   │   ├── signals.py          # Inventory updates & balance calculations
│   │   └── urls.py             # Sales endpoints
│   │
│   ├── purchases/               # Purchase management module
│   │   ├── models.py           # Purchase model
│   │   ├── views.py            # Purchase operations
│   │   ├── serializers.py      # Purchase serialization
│   │   ├── signals.py          # Inventory updates
│   │   └── urls.py             # Purchase endpoints
│   │
│   ├── payments/                # Payment processing module
│   │   ├── models.py           # Payment model
│   │   ├── views.py            # Payment recording
│   │   ├── serializers.py      # Payment data handling
│   │   ├── signals.py          # Balance calculations
│   │   └── urls.py             # Payment endpoints
│   │
│   ├── assets/                  # Asset management module
│   │   ├── models.py           # Asset model (machines, molds)
│   │   ├── views.py            # Asset tracking
│   │   ├── serializers.py      # Asset serialization
│   │   └── urls.py             # Asset endpoints
│   │
│   ├── bank_accounts/           # Bank account module
│   │   ├── models.py           # BankAccount model
│   │   ├── views.py            # Account management
│   │   └── urls.py             # Bank endpoints
│   │
│   ├── reports/                 # Reporting module
│   │   ├── models.py           # Report models
│   │   ├── views.py            # Report generation
│   │   └── urls.py             # Report endpoints
│   │
│   ├── manage.py                # Django management script
│   ├── requirements.txt         # Python dependencies
│   └── db.sqlite3              # SQLite database (git-ignored)
│
├── frontend/                    # Vue 3 + TypeScript Frontend
│   ├── src/
│   │   ├── main.ts             # Application entry point
│   │   ├── App.vue             # Root component
│   │   │
│   │   ├── router/             # Vue Router configuration
│   │   │   └── index.ts        # Route definitions
│   │   │
│   │   ├── views/              # Main page views
│   │   │   ├── HomeView.vue    # Analytics dashboard
│   │   │   └── LoginView.vue   # Authentication page
│   │   │
│   │   ├── shared/             # Shared resources
│   │   │   ├── api/
│   │   │   │   └── axios.ts    # API client configuration
│   │   │   ├── stores/
│   │   │   │   └── auth.ts     # Authentication store
│   │   │   ├── layouts/
│   │   │   │   └── MainLayout.vue  # App layout with navbar
│   │   │   └── components/
│   │   │       └── LoginForm.vue   # Login component
│   │   │
│   │   └── modules/            # Feature modules
│   │       │
│   │       ├── customers/
│   │       │   ├── views/
│   │       │   │   └── CustomersView.vue
│   │       │   ├── stores/
│   │       │   │   └── customers.ts
│   │       │   ├── types/
│   │       │   │   └── index.ts
│   │       │   └── components/
│   │       │
│   │       ├── vendors/
│   │       │   ├── views/
│   │       │   │   └── VendorsView.vue
│   │       │   ├── stores/
│   │       │   │   └── vendors.ts
│   │       │   └── types/
│   │       │
│   │       ├── products/
│   │       │   ├── views/
│   │       │   │   └── ProductsView.vue
│   │       │   ├── stores/
│   │       │   │   └── products.ts
│   │       │   ├── types/
│   │       │   └── components/
│   │       │
│   │       ├── raw_materials/
│   │       │   ├── views/
│   │       │   │   └── RawMaterialsView.vue
│   │       │   ├── stores/
│   │       │   │   └── raw_materials.ts
│   │       │   ├── types/
│   │       │   └── components/
│   │       │       ├── RawMaterialForm.vue
│   │       │       ├── RawMaterialUsageForm.vue
│   │       │       └── RawMaterialPurchaseForm.vue
│   │       │
│   │       ├── sales/
│   │       │   ├── views/
│   │       │   │   └── SalesView.vue
│   │       │   ├── stores/
│   │       │   │   └── sales.ts
│   │       │   ├── types/
│   │       │   └── components/
│   │       │       └── SaleForm.vue
│   │       │
│   │       ├── purchases/
│   │       │   ├── views/
│   │       │   │   └── PurchasesView.vue
│   │       │   ├── stores/
│   │       │   │   └── purchases.ts
│   │       │   └── types/
│   │       │
│   │       ├── payments/
│   │       │   ├── views/
│   │       │   │   └── PaymentsView.vue
│   │       │   ├── stores/
│   │       │   │   └── payments.ts
│   │       │   └── types/
│   │       │
│   │       ├── assets/
│   │       │   ├── views/
│   │       │   │   └── AssetsView.vue
│   │       │   ├── stores/
│   │       │   │   └── assets.ts
│   │       │   └── types/
│   │       │
│   │       ├── reports/
│   │       │   ├── views/
│   │       │   │   └── ReportsView.vue  # Excel report generator
│   │       │   ├── stores/
│   │       │   │   └── reports.ts
│   │       │   └── types/
│   │       │
│   │       └── users/
│   │           ├── views/
│   │           │   └── UsersView.vue
│   │           ├── stores/
│   │           │   └── users.ts
│   │           └── types/
│   │
│   ├── public/                 # Static assets
│   ├── package.json            # Node dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tsconfig.json           # TypeScript configuration
│   └── tailwind.config.js      # Tailwind CSS configuration
│
├── .gitignore                  # Git exclusion rules
├── README.md                   # This file
└── requiremnets sheet.xlsx     # Project requirements document
```

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16 or higher** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Code Editor** - VS Code recommended

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone <your-repository-url>
cd Crystal
```

#### 2️⃣ Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
# Follow prompts to set username and password

# Collect static files (if needed)
python manage.py collectstatic --noinput
```

#### 3️⃣ Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Build for development (optional)
npm run build
```

---

## ▶️ How to Run

### Development Mode (Recommended for Development)

You'll need **two terminal windows** - one for backend, one for frontend:

#### Terminal 1: Start Backend Server

```bash
cd backend
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
python manage.py runserver
```

✅ Backend will be running at: `http://127.0.0.1:8000`

#### Terminal 2: Start Frontend Dev Server

```bash
cd frontend
npm run dev
```

✅ Frontend will be running at: `http://localhost:5173`

### Access the Application

1. **Open your browser** and go to: `http://localhost:5173`
2. **Login** with the superuser credentials you created
3. **Start using** the application!

### Admin Panel (Django)

Access Django admin at: `http://127.0.0.1:8000/admin/`
- Use superuser credentials
- Manage data directly from Django admin

### API Documentation

API endpoints available at: `http://127.0.0.1:8000/api/`

---

## 💼 Working with the Project

### Understanding the Architecture

Crystal POS follows a **clean separation of concerns**:

- **Backend (Django)**: Handles all business logic, data storage, and API endpoints
- **Frontend (Vue)**: Provides user interface and communicates with backend via REST APIs
- **State Management (Pinia)**: Centralized state management in frontend
- **Authentication**: JWT tokens for secure communication

### Making Changes

#### Adding a New Feature to Backend

1. **Create/Modify Model** in `backend/<module>/models.py`
```python
class YourModel(models.Model):
    name = models.CharField(max_length=200)
    # Add fields...
```

2. **Create Migration**
```bash
python manage.py makemigrations
python manage.py migrate
```

3. **Create Serializer** in `serializers.py`
```python
class YourModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = YourModel
        fields = '__all__'
```

4. **Create ViewSet** in `views.py`
```python
class YourModelViewSet(viewsets.ModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
```

5. **Add URL** in `urls.py`
```python
router.register(r'your-endpoint', YourModelViewSet)
```

#### Adding a New Feature to Frontend

1. **Create Store** in `frontend/src/modules/<module>/stores/`
```typescript
export const useYourStore = defineStore('your-store', {
  state: () => ({
    items: []
  }),
  actions: {
    async fetchItems() {
      const response = await api.get('/your-endpoint/')
      this.items = response.data
    }
  }
})
```

2. **Create Component** in `frontend/src/modules/<module>/components/`
```vue
<template>
  <div>
    <!-- Your component HTML -->
  </div>
</template>

<script setup lang="ts">
import { useYourStore } from '../stores/your-store'

const store = useYourStore()
</script>
```

3. **Add Route** in `frontend/src/router/index.ts`
```typescript
{
  path: '/your-route',
  name: 'your-route',
  component: () => import('../modules/<module>/views/YourView.vue')
}
```

### Common Development Tasks

#### Run Backend Tests
```bash
cd backend
python manage.py test
```

#### Run Frontend Tests
```bash
cd frontend
npm run test
```

#### Check Code Quality
```bash
# Frontend linting
npm run lint

# Backend code check
python manage.py check
```

#### Create New Migration
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
```

#### Reset Database (Development Only!)
```bash
cd backend
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Understanding the Data Flow

```
User Action (Frontend)
    ↓
Vue Component
    ↓
Pinia Store (State Management)
    ↓
Axios API Call
    ↓
Django REST API (Backend)
    ↓
ViewSet/Serializer
    ↓
Database (SQLite/PostgreSQL)
    ↓
Response back through same chain
```

### Working with Modules

Each module (customers, products, sales, etc.) follows the same structure:

**Backend Module Structure:**
- `models.py` - Database schema
- `serializers.py` - Data transformation
- `views.py` - API endpoints
- `urls.py` - Route configuration
- `signals.py` - Automatic triggers (if needed)
- `admin.py` - Django admin configuration

**Frontend Module Structure:**
- `views/` - Full page components
- `components/` - Reusable components
- `stores/` - Pinia state management
- `types/` - TypeScript type definitions

### Debugging Tips

**Backend Debugging:**
- Check Django logs in terminal
- Use Django debug toolbar
- Access `/admin/` for data inspection
- Use `python manage.py shell` for testing queries

**Frontend Debugging:**
- Use Vue DevTools browser extension
- Check browser console for errors
- Use Network tab to inspect API calls
- Enable Vite HMR for instant updates

---

## 📡 API Documentation

### Base URL
```
http://127.0.0.1:8000/api
```

### Authentication Endpoints

#### Login
```http
POST /api/users/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "your-password"
}

Response:
{
  "access": "jwt-token",
  "refresh": "refresh-token",
  "user": { ...user-data }
}
```

#### Logout
```http
POST /api/users/auth/logout/
Authorization: Bearer <token>
```

#### Get Current User
```http
GET /api/users/auth/me/
Authorization: Bearer <token>
```

### Module Endpoints

All endpoints require authentication token in header:
```
Authorization: Bearer <your-jwt-token>
```

#### Customers
```http
GET    /api/customers/          # List all customers
POST   /api/customers/          # Create customer
GET    /api/customers/{id}/     # Get customer details
PUT    /api/customers/{id}/     # Update customer
DELETE /api/customers/{id}/     # Delete customer
```

#### Vendors
```http
GET    /api/vendors/            # List all vendors
POST   /api/vendors/            # Create vendor
GET    /api/vendors/{id}/       # Get vendor details
PUT    /api/vendors/{id}/       # Update vendor
DELETE /api/vendors/{id}/       # Delete vendor
```

#### Products
```http
GET    /api/products/           # List all products
POST   /api/products/           # Create product
GET    /api/products/{id}/      # Get product details
PUT    /api/products/{id}/      # Update product
DELETE /api/products/{id}/      # Delete product
```

#### Raw Materials
```http
GET    /api/raw-materials/materials/        # List materials
POST   /api/raw-materials/materials/        # Create material
GET    /api/raw-materials/materials/{id}/   # Get material
PUT    /api/raw-materials/materials/{id}/   # Update material
DELETE /api/raw-materials/materials/{id}/   # Delete material
POST   /api/raw-materials/usage/            # Record usage
POST   /api/raw-materials/purchase/         # Record purchase
```

#### Sales
```http
GET    /api/sales/              # List all sales
POST   /api/sales/              # Create sale
GET    /api/sales/{id}/         # Get sale details
PATCH  /api/sales/{id}/         # Update sale (payment status)
DELETE /api/sales/{id}/         # Delete sale
```

#### Purchases
```http
GET    /api/purchases/          # List all purchases
POST   /api/purchases/          # Create purchase
GET    /api/purchases/{id}/     # Get purchase details
PUT    /api/purchases/{id}/     # Update purchase
DELETE /api/purchases/{id}/     # Delete purchase
```

#### Payments
```http
GET    /api/payments/           # List all payments
POST   /api/payments/           # Create payment
GET    /api/payments/{id}/      # Get payment details
PUT    /api/payments/{id}/      # Update payment
DELETE /api/payments/{id}/      # Delete payment
```

#### Assets
```http
GET    /api/assets/             # List all assets
POST   /api/assets/             # Create asset
GET    /api/assets/{id}/        # Get asset details
PUT    /api/assets/{id}/        # Update asset
DELETE /api/assets/{id}/        # Delete asset
```

#### Users
```http
GET    /api/users/              # List all users
POST   /api/users/              # Create user
GET    /api/users/{id}/         # Get user details
PUT    /api/users/{id}/         # Update user
DELETE /api/users/{id}/         # Delete user
```

---

## 🎓 Development Guide

### Code Style Guidelines

**Python (Backend):**
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions small and focused

**TypeScript (Frontend):**
- Use TypeScript types everywhere
- Follow Vue 3 Composition API patterns
- Use Pinia for state management
- Component names in PascalCase

### Best Practices

1. **Always activate virtual environment** before working on backend
2. **Run migrations** after modifying models
3. **Test API endpoints** using built-in test suite
4. **Use TypeScript types** to catch errors early
5. **Follow modular architecture** - keep code organized by feature
6. **Never commit sensitive data** - check .gitignore
7. **Write meaningful commit messages**

### Useful Commands

```bash
# Backend
python manage.py shell          # Interactive Python shell
python manage.py dbshell        # Database shell
python manage.py showmigrations # Show migration status
python manage.py check --deploy # Production readiness check

# Frontend
npm run build                   # Production build
npm run preview                 # Preview production build
npm run lint                    # Lint code
npm run type-check              # TypeScript checking
```

---

## 🚀 Production Deployment

### Backend Configuration for Production

1. **Update `settings.py`:**
```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
SECRET_KEY = 'generate-a-strong-random-key'

# Use PostgreSQL instead of SQLite
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crystal_db',
        'USER': 'db_user',
        'PASSWORD': 'secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
```

2. **Collect Static Files:**
```bash
python manage.py collectstatic
```

3. **Use Production Server:**
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn core.wsgi:application --bind 0.0.0.0:8000
```

### Frontend Build for Production

```bash
cd frontend
npm run build
```

Output will be in `frontend/dist/` - serve these files with Nginx or Apache.

### Deployment Checklist

- [ ] Set DEBUG = False
- [ ] Configure ALLOWED_HOSTS
- [ ] Generate strong SECRET_KEY
- [ ] Set up PostgreSQL database
- [ ] Configure HTTPS/SSL
- [ ] Set secure cookie flags
- [ ] Collect static files
- [ ] Build frontend for production
- [ ] Set up reverse proxy (Nginx)
- [ ] Configure firewall
- [ ] Set up backups
- [ ] Enable monitoring
- [ ] Configure domain DNS

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is proprietary software. All rights reserved.

---

## 📞 Support

For issues, questions, or contributions:
- Create an issue in the repository
- Contact the development team
- Check documentation in the `/docs` folder (if available)

---

## 🙏 Acknowledgments

Built with:
- Django & Django REST Framework
- Vue.js & TypeScript
- ApexCharts for beautiful visualizations
- XLSX.js for Excel export functionality
- Tailwind CSS for styling

---

<div align="center">

**Made with ❤️ for modern businesses**

</div> 