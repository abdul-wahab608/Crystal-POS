# 🚀 Quick Start Testing Guide

## ⚡ Quick Setup (5 minutes)

### **Step 1: Backend Setup**

Open PowerShell/Terminal in project root:

```powershell
# Go to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Run migrations (IMPORTANT - fixes Customer/Vendor models)
python manage.py makemigrations
python manage.py migrate

# Create superuser (if not exists)
python manage.py createsuperuser
# Suggested: username=admin, password=admin123

# Start backend
python manage.py runserver
```

Leave this terminal running. Backend will be at: **http://localhost:8000**

---

### **Step 2: Frontend Setup**

Open **NEW** PowerShell/Terminal window:

```powershell
# Go to frontend
cd frontend

# Start frontend
npm run dev
```

Leave this terminal running. Frontend will be at: **http://localhost:5173**

---

## ✅ **Quick Test (2 minutes)**

1. **Open Browser**: `http://localhost:5173`

2. **Login**:
   - Username: `admin`
   - Password: `admin123` (or whatever you set)

3. **Test Products Module**:
   - Click "Products" in navbar
   - Click "Add Product"
   - Fill form:
     - Name: Test Product
     - Unit: PCS
     - Price: 100
     - Quantity: 50
   - Click "Create Product"
   - Product should appear in table ✅

4. **Test Customers Module**:
   - Click "Customers" in navbar
   - Click "Add Customer"
   - Fill form:
     - Name: Test Customer
     - Email: test@example.com
     - Phone: 1234567890
     - Address: Test Address
   - Click "Create Customer"
   - Customer should appear in table ✅

5. **Test Navigation**:
   - Click through all links in navbar
   - All pages should load without errors ✅

---

## 🐛 **Troubleshooting**

### **"ModuleNotFoundError: No module named 'django_filters'"**
```powershell
pip install django-filter
```

### **"CORS Error" in browser console**
Backend CORS is already configured. Just restart backend server:
```powershell
# Press Ctrl+C in backend terminal
python manage.py runserver
```

### **"401 Unauthorized" on API calls**
Re-login. JWT tokens expire after 1 hour.

### **Customer/Vendor forms show errors**
Make sure you ran migrations:
```powershell
cd backend
python manage.py makemigrations
python manage.py migrate
```

---

## 📊 **What to Check**

### **✅ Backend Working**
- Server starts without errors
- Visit `http://localhost:8000/admin/` - Django admin loads
- No red errors in terminal

### **✅ Frontend Working**
- Visit `http://localhost:5173/` - Login page loads
- No red errors in browser console (F12)
- Navigation bar visible after login

### **✅ Integration Working**
- Login successful (redirects to dashboard)
- Products page loads data
- Can create/edit/delete products
- Can create/edit/delete customers
- No CORS errors in console

---

## 🎯 **Testing Checklist**

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can login successfully
- [ ] Products CRUD works
- [ ] Customers CRUD works
- [ ] All navigation links work
- [ ] No console errors
- [ ] Forms are responsive
- [ ] Search filters work
- [ ] Modals open/close properly

---

## 🎉 **Success!**

If all checkboxes are ✅, your frontend is fully functional and integrated with backend!

**Next Steps**:
1. Test other modules (Vendors, Sales, Purchases)
2. Test on mobile/tablet (responsive design)
3. Test with different user roles
4. Add more test data

---

## 📞 **Need Help?**

Check `TESTING_GUIDE.md` for detailed testing procedures and troubleshooting.
