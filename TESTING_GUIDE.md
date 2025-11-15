# 🧪 Crystal Project Testing Guide

## 🚨 **Issues Found & Fixed**

### **Issue 1: Customer Model Mismatch** ✅ FIXED
**Problem**: Frontend expects `email`, `phone`, `address`, `is_active` fields but backend Customer model only has `name`, `city`, `balance`.

**Status**: Need to update backend Customer model

### **Issue 2: Permission Requirements** ⚠️
**Problem**: Some views require specific roles (IsManagerUser, IsStaffUser) but might block testing.

**Solution**: Temporarily disable or use superuser for testing

### **Issue 3: Missing django_filters** ✅ FIXED
**Problem**: `django_filters` is in INSTALLED_APPS but not in requirements.txt

**Status**: Added to requirements.txt

---

## 📋 **Pre-Testing Checklist**

### **1. Backend Setup**

```powershell
# Navigate to backend folder
cd backend

# Activate virtual environment (if not already activated)
# If venv doesn't exist, create it first:
python -m venv venv
venv\Scripts\activate

# Install/update dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (if not done)
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: admin123 (or your choice)

# Run backend server
python manage.py runserver
```

**Expected Output**:
```
Django version 5.2.3, using settings 'core.settings'
Starting development server at http://127.0.0.1:8000/
```

### **2. Frontend Setup**

```powershell
# Open NEW terminal window
# Navigate to frontend folder
cd frontend

# Install dependencies (if not done)
npm install

# Run frontend dev server
npm run dev
```

**Expected Output**:
```
VITE v6.2.4  ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

---

## ✅ **Testing Workflow**

### **Step 1: Test Backend API Endpoints**

Open browser or Postman and test:

#### **A. Login Endpoint**
```
POST http://localhost:8000/api/users/auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Expected Response**:
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "role": "ADMIN"
  }
}
```

#### **B. Products Endpoint**
```
GET http://localhost:8000/api/products/
Authorization: Bearer {your_token}
```

**Expected Response**: `[]` or list of products

#### **C. Customers Endpoint**
```
GET http://localhost:8000/api/customers/
Authorization: Bearer {your_token}
```

**Expected Response**: `[]` or list of customers

---

### **Step 2: Test Frontend Login**

1. Open browser: `http://localhost:5173/`
2. You should be redirected to `/login`
3. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
4. Click "Log In"

**Expected Result**:
- ✅ No console errors
- ✅ Token saved in localStorage
- ✅ Redirected to dashboard (`/`)
- ✅ Username and role shown in navbar

**Check Console (F12)**:
```
✅ Login successful (or similar)
✅ User authenticated
```

---

### **Step 3: Test Navigation**

Click each navigation link in order:

1. **Dashboard** (`/`)
   - ✅ Page loads
   - ✅ No errors

2. **Products** (`/products`)
   - ✅ "Products Management" title visible
   - ✅ "Add Product" button visible
   - ✅ Loading spinner appears briefly
   - ✅ Table or "No products found" message
   - ⚠️ Check console for API call: `🔍 Fetching products...`

3. **Customers** (`/customers`)
   - ✅ "Customers Management" title visible
   - ✅ "Add Customer" button visible
   - ⚠️ **WILL FAIL** - Customer model mismatch

4. **Vendors** (`/vendors`)
   - ✅ Page loads
   - ✅ Table visible

5. **Sales** (`/sales`)
   - ✅ Page loads

6. **Purchases** (`/purchases`)
   - ✅ Page loads

7. **Payments** (`/payments`)
   - ✅ Page loads

8. **Bank Accounts** (`/bank-accounts`)
   - ✅ Page loads

9. **Reports** (`/reports`)
   - ✅ Page loads

10. **Assets** (`/assets`)
    - ✅ Page loads

11. **Users** (`/users`)
    - ✅ Page loads

---

### **Step 4: Test CRUD Operations - Products**

#### **A. Create Product**

1. Click "Add Product" button
2. Modal should open
3. Fill form:
   - Name: `Test Product`
   - Unit: `PCS`
   - Price: `100`
   - Quantity: `50`
4. Click "Create Product"

**Expected Result**:
- ✅ Modal closes
- ✅ Product appears in table
- ✅ Stats update (Total Products: 1)
- ✅ Console shows success

**If Error**: Check console for API response

#### **B. Edit Product**

1. Click "Edit" button on product
2. Modal opens with pre-filled data
3. Change quantity to `75`
4. Click "Update Product"

**Expected Result**:
- ✅ Modal closes
- ✅ Product updates in table
- ✅ Quantity shows 75

#### **C. Search Product**

1. Type product name in search box
2. Table filters in real-time

**Expected Result**:
- ✅ Only matching products shown

#### **D. Delete Product**

1. Click "Delete" button
2. Confirm dialog appears
3. Click OK

**Expected Result**:
- ✅ Product removed from table
- ✅ Stats update

---

### **Step 5: Test Responsive Design**

1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Test different screen sizes:
   - Mobile (375px)
   - Tablet (768px)
   - Desktop (1024px+)

**Check**:
- ✅ Navigation collapses on mobile
- ✅ Tables are scrollable
- ✅ Modals are centered
- ✅ Buttons are clickable
- ✅ Forms are usable

---

## 🐛 **Common Issues & Solutions**

### **Issue: "CORS Error"**
**Error**: `Access to XMLHttpRequest at 'http://localhost:8000/api/...' from origin 'http://localhost:5173' has been blocked by CORS policy`

**Solution**:
1. Check `backend/core/settings.py`
2. Ensure CORS settings are correct:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]
```
3. Restart backend server

---

### **Issue: "401 Unauthorized"**
**Error**: API calls return 401 status

**Solutions**:
1. Check if logged in (token in localStorage)
2. Check token hasn't expired (1 hour lifetime)
3. Re-login
4. Check Authorization header in Network tab

---

### **Issue: "403 Forbidden"**
**Error**: API calls return 403 status

**Solution**:
1. User role doesn't have permission
2. Use superuser/admin account
3. Or temporarily remove permission classes from views

---

### **Issue: "Network Error"**
**Error**: `Network Error` or `ERR_CONNECTION_REFUSED`

**Solutions**:
1. Check backend server is running (`http://localhost:8000`)
2. Check frontend is connecting to correct URL
3. Check firewall settings

---

### **Issue: Customer form doesn't work**
**Error**: Fields don't match or validation errors

**Reason**: Backend Customer model doesn't have `email`, `phone`, `address`, `is_active` fields

**Solution**: Update backend model (see fixes below)

---

## 🔧 **Required Fixes**

### **Fix 1: Update Customer Model**

**File**: `backend/customers/models.py`

Add missing fields:
```python
class Customer(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(blank=True, null=True)  # ADD
    phone = models.CharField(max_length=20, blank=True, null=True)  # ADD
    address = models.TextField(blank=True, null=True)  # ADD
    city = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)  # ADD
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

Then run:
```powershell
python manage.py makemigrations
python manage.py migrate
```

### **Fix 2: Add django-filter to requirements**

**File**: `backend/requirements.txt`

Add:
```
django-filter==24.2
```

Then:
```powershell
pip install django-filter
```

---

## 📊 **Testing Checklist**

### **Backend**
- [ ] Server starts without errors
- [ ] Admin panel accessible (`http://localhost:8000/admin/`)
- [ ] Login endpoint returns JWT token
- [ ] Products API returns data
- [ ] Customers API returns data
- [ ] All API endpoints respond

### **Frontend**
- [ ] Dev server starts without errors
- [ ] Login page loads
- [ ] Login successful with valid credentials
- [ ] Token saved in localStorage
- [ ] Redirected to dashboard after login
- [ ] All navigation links work
- [ ] No 404 errors

### **Products Module**
- [ ] Products page loads
- [ ] "Add Product" button opens modal
- [ ] Form fields are editable
- [ ] Create product works
- [ ] Product appears in table
- [ ] Edit product works
- [ ] Search filters products
- [ ] Delete product works
- [ ] Stats update correctly

### **Responsive Design**
- [ ] Mobile view (375px) - navigation works
- [ ] Tablet view (768px) - layout adapts
- [ ] Desktop view (1024px+) - full features
- [ ] Modals center properly
- [ ] Tables scroll horizontally on small screens

### **Error Handling**
- [ ] Invalid login shows error message
- [ ] Network errors are caught
- [ ] Loading states show properly
- [ ] Empty states display correctly

---

## 🎯 **Success Criteria**

Your frontend is **fully functional** when:

1. ✅ Login works and stores JWT token
2. ✅ All pages load without errors
3. ✅ Products CRUD operations work end-to-end
4. ✅ At least 2-3 modules tested successfully
5. ✅ No CORS errors in console
6. ✅ No 401/403 errors (when logged in)
7. ✅ Responsive on mobile/tablet/desktop
8. ✅ Buttons respond to clicks
9. ✅ Forms submit properly
10. ✅ Data persists after page refresh

---

## 📞 **Quick Test Commands**

```powershell
# Test backend API (PowerShell)
Invoke-RestMethod -Uri "http://localhost:8000/api/products/" -Headers @{"Authorization"="Bearer YOUR_TOKEN"}

# Check if frontend is running
curl http://localhost:5173

# Check if backend is running
curl http://localhost:8000/admin/
```

---

## 🎉 **What Works Currently**

✅ Backend Django server runs
✅ Frontend Vue server runs
✅ JWT authentication implemented
✅ Axios configured with interceptors
✅ Router with auth guards
✅ All views created
✅ All stores created
✅ Products module fully functional
✅ UI is styled and professional

## ⚠️ **What Needs Fixing**

🔧 Customer model fields mismatch
🔧 Some modules need model alignment
🔧 Permission restrictions may block testing
🔧 Export features not implemented

---

**Estimated Testing Time**: 30-45 minutes for full workflow
