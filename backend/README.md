# Inventory Management & POS System - Backend

A Django REST API backend for a comprehensive inventory management and point-of-sale system.

## Features

- **Customer Management** - Track customers and receivables
- **Vendor Management** - Track vendors and payables  
- **Product Inventory** - Stock tracking with multiple units
- **Sales Management** - POS transactions with customer linking
- **Purchase Management** - Vendor purchase tracking
- **Asset Tracking** - Machines and molds management
- **Payment Processing** - Customer and vendor payments
- **Role-Based Access Control** - Admin, Manager, Cashier, Staff roles
- **Automatic Business Logic** - Balance and stock updates

## Setup

1. **Activate Virtual Environment:**
   ```bash
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

5. **Start Development Server:**
   ```bash
   python manage.py runserver
   ```

## API Endpoints

- **Admin:** `http://127.0.0.1:8000/admin/`
- **Users:** `http://127.0.0.1:8000/api/users/`
- **Customers:** `http://127.0.0.1:8000/api/customers/`
- **Vendors:** `http://127.0.0.1:8000/api/vendors/`
- **Products:** `http://127.0.0.1:8000/api/products/`
- **Sales:** `http://127.0.0.1:8000/api/sales/`
- **Purchases:** `http://127.0.0.1:8000/api/purchases/`
- **Assets:** `http://127.0.0.1:8000/api/assets/`
- **Payments:** `http://127.0.0.1:8000/api/payments/`
- **Reports:** `http://127.0.0.1:8000/api/reports/`

## Project Structure

```
backend/
├── core/                 # Django project settings
├── users/               # Custom user model & authentication
├── customers/           # Customer management
├── vendors/            # Vendor management
├── products/           # Product inventory
├── sales/              # Sales & POS
├── purchases/          # Purchase management
├── assets/             # Asset tracking
├── payments/           # Payment processing
├── reports/            # Reporting module
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── venv/              # Virtual environment
```

## User Roles

- **Admin:** Full system access
- **Manager:** Customer, vendor, product, sales, purchase management
- **Cashier:** Sales transactions and basic operations
- **Staff:** Read-only access to most modules 