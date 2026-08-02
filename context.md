# Crystal Project — Context Reference

> Read this before grepping. It maps the entire repo so you can go straight to the right file.

## Stack

| Layer | Tech |
|-------|------|
| Backend | Django 5.2.3 + DRF 3.15 + SimpleJWT 5.3 |
| Frontend | Vue 3.5 + TypeScript + Pinia + Vite |
| Styling | Tailwind CSS 4 |
| Charts | ApexCharts / vue3-apexcharts |
| Excel | openpyxl (backend) / xlsx + file-saver (frontend) |
| DB | SQLite (default) |
| Desktop | Electron (optional, hash-router mode) |
| Auth | JWT — token in `localStorage['auth_token']`, header `Authorization: Bearer <token>` |

## Repo Layout

```
Crystal/
├── backend/              Django project root
│   ├── core/             Settings, root URL conf, mixins, billing models/views
│   ├── users/            Custom User model (AbstractUser + role + phone)
│   ├── customers/        Customer + CustomerTransaction
│   ├── vendors/          Vendor + VendorProduct + VendorTransaction
│   ├── products/         Product + ProductVariant + SizeRange + Color + ProductHistory
│   ├── sales/            Sale + SaleItem  (bill_no, quantity_dozens)
│   ├── purchases/        Purchase + PurchaseItem
│   ├── raw_materials/    RawMaterial + RawMaterialUsage + RawMaterialPurchase
│   ├── assets/           Asset + AssetLog
│   ├── payments/         Payment (links to Sale, RawMaterialPurchase, Customer, Vendor)
│   ├── bank_accounts/    BankAccount
│   ├── reports/          Report (generated file metadata)
│   └── manage.py
├── frontend/
│   └── src/
│       ├── modules/      Feature modules (one per domain — see below)
│       ├── shared/       Cross-cutting: api, components, composables, stores, utils
│       ├── router/index.ts
│       ├── views/        HomeView, LoginView, ImportHistoryView
│       └── main.ts
├── installer/            Inno Setup scripts
└── dist/                 Build output
```

## API Endpoint Map

Base URL: `http://127.0.0.1:8000/api`

| Prefix | Django app | ViewSet/Router |
|--------|-----------|----------------|
| `/units/` | core | UnitViewSet |
| `/import-sessions/` | core | ImportSessionViewSet |
| `/users/` | users | users.urls |
| `/customers/` | customers | customers.urls |
| `/vendors/` | vendors | vendors.urls |
| `/products/` | products | products.urls |
| `/sales/` | sales | sales.urls |
| `/purchases/` | purchases | purchases.urls |
| `/assets/` | assets | assets.urls |
| `/payments/` | payments | payments.urls |
| `/reports/` | reports | reports.urls |
| `/raw-materials/` | raw_materials | raw_materials.urls |
| `/bank-accounts/` | bank_accounts | bank_accounts.urls |
| `/billing/` | core (urls_billing) | Invoice + Bill + BillingPayment |
| `/health/` | core | health_check (GET) |

## Django Models — Field Reference

### users · `User` (extends AbstractUser)
`username, password, email, first_name, last_name, is_active`  
`role` (ADMIN/MANAGER/STAFF) · `phone`

### customers · `Customer`
`name` · `phone` · `address` · `city` · `customer_type` (REGULAR/WHOLESALE/RETAIL) · `balance` · `is_active` · `created_at` · `updated_at`  
**No email field.**

### customers · `CustomerTransaction`
`customer` FK · `type` (DEBIT/CREDIT) · `amount` · `date` · `reference` · `notes`

### vendors · `Vendor`
`name` (unique) · `phone` · `address` · `city` · `contact_person` · `balance` · `is_active` · `created_at` · `updated_at`  
**No email field.**

### vendors · `VendorProduct`
`vendor` FK · `product_type` · `product` FK (nullable) · `raw_material` FK (nullable) · `unit_price` · `minimum_order_quantity` · `lead_time_days` · `is_preferred` · `is_active` · `notes` · `last_purchase_date` · `last_purchase_price` · `created_at` · `updated_at`

### products · `SizeRange`
`name` (unique) · `created_at`

### products · `Color`
`name` (unique) · `created_at`

### products · `Product`
`name` · `unit` · `cop` (cost of production) · `quantity` · `product_type` (MANUFACTURED/PURCHASED) · `size_range` FK → SizeRange · `last_updated` · `created_at`  
**No `available_stock` property** — ProductSerializer must NOT declare it as ReadOnlyField.

### products · `ProductVariant`
`product` FK · `size_range` FK · `color` FK · `quantity_dozens` (PositiveIntegerField) · `created_at`

### products · `ProductHistory`
`product` FK · `change_type` · `quantity_change` · `date` · `reference` · `notes`

### sales · `Sale`
`bill_no` (unique, auto-generated in save()) · `sale_type` (REGULAR/WHOLESALE) · `customer` FK · `date` · `total_amount` · `payment_status` (PAID/UNPAID/PARTIAL) · `created_by` FK  
**No `receipt_number` field** — use `bill_no`.

### sales · `SaleItem`
`sale` FK · `product` FK · `size_range` FK · `color` FK · `quantity_dozens` (PositiveIntegerField) · `unit_price` · `subtotal`  
**No `quantity` field** — use `quantity_dozens`.

### purchases · `Purchase`
`vendor` FK · `date` · `total_amount` · `created_by` FK  
**No `invoice_number`, no `payment_status`** — handled by `core.models_billing.Bill`.

### purchases · `PurchaseItem`
`purchase` FK · `product` FK · `quantity` · `unit_cost` · `subtotal`

### raw_materials · `RawMaterial`
`name` · `unit` · `quantity` · `reorder_level` · `created_at` · `updated_at`

### raw_materials · `RawMaterialUsage`
`raw_material` FK · `quantity_used` · `reference` · `notes` · `date_used`

### raw_materials · `RawMaterialPurchase`
`raw_material` FK · `quantity_purchased` · `unit_price` · `total_amount` · `supplier` · `invoice_number` · `notes` · `purchase_date` · `payment` FK → payments.Payment

### assets · `Asset`
`name` · `description` · `category` · `type` · `value` · `current_value` · `purchase_value` · `purchase_date` · `location` · `status` (ACTIVE/INACTIVE/DISPOSED) · `created_at`

### payments · `Payment`
`payment_type` (INCOMING/OUTGOING) · `payment_method` (CASH/CHEQUE/BANK_TRANSFER) · `amount` · `status` · `customer` FK · `vendor` FK · `bank_account` FK · `bank_name` · `account_number` · `sale` FK → sales.Sale · `purchase` FK → raw_materials.RawMaterialPurchase · `direct_payment_to_vendor` FK · `due_date` · `payment_date` · `reference` · `notes` · `original_amount` · `remaining_amount`

### bank_accounts · `BankAccount`
`name` · `account_number` (unique) · `bank_name` · `branch` · `ifsc_code` · `is_active` · `created_at` · `updated_at`

### core · `Invoice` (billing)
`number` (unique) · `date` · `amount` · `payment_status` (PAID/PARTIAL/UNPAID) · `payment_method` · `sale` OneToOne → sales.Sale

### core · `Bill` (billing)
`number` (unique) · `date` · `amount` · `payment_status` · `payment_method` · `purchase` OneToOne → purchases.Purchase

### core · `BillingPayment`
`amount` · `date` · `method` · `reference` · `invoice` FK → Invoice · `bill` FK → Bill

## Frontend Module Map

Each module lives at `frontend/src/modules/<name>/` with this shape:
`views/<Name>View.vue` · `components/` · `stores/<name>.ts` · `types/index.ts`

| Module | Route path | View | Store | Key types |
|--------|-----------|------|-------|-----------|
| customers | `/customers` | CustomersView | customers.ts | Customer, CreateCustomerRequest |
| vendors | `/vendors` | VendorsView | vendors.ts | Vendor (no email field) |
| products | `/products` | ProductsView | products.ts + color.ts + sizeRange.ts + productVariant.ts | Product, ProductVariant, SizeRange, Color |
| sales | `/sales` | SalesView | sales.ts + billing.ts | Sale, SaleItem (quantity_dozens not quantity) |
| purchases | `/purchases` | PurchasesView | purchases.ts + billing.ts | Purchase, PurchaseItem |
| raw_materials | `/raw-materials` | RawMaterialsView | raw_materials.ts | RawMaterial |
| assets | `/assets` | AssetsView | assets.ts | Asset |
| payments | `/payments` | PaymentsView | payments.ts | Payment |
| reports | `/reports` | ReportsView | reports.ts | — |
| users | `/users` | UsersView | users.ts | User |
| bank_accounts | — | BankAccountsView | bank_accounts.ts | BankAccount |

## Shared Infrastructure (frontend/src/shared/)

| Path | Purpose |
|------|---------|
| `api/axios.ts` | Axios instance — base URL 8000, JWT header, offline queue, 30-min IndexedDB cache for GETs |
| `stores/auth.ts` | Pinia auth store — login/logout, token in localStorage |
| `stores/batchActions.ts` | Batch select + delete across list views |
| `stores/export.ts` | Excel/CSV export logic |
| `stores/import.ts` | Import session management |
| `stores/toast.ts` | Toast notifications |
| `stores/units.ts` | Unit choices (shared across products, raw materials) |
| `components/ImportWizard/` | 5-step import flow: Upload→Mapping→Preview→Results |
| `components/SelectAllCheckbox.vue` | Selects all visible rows; `allIds` prop — avoid passing fresh array on every render |
| `components/BatchActionsToolbar.vue` | Toolbar shown when rows are selected |
| `components/ExportButton.vue` | Triggers export store |
| `utils/offlineManager.ts` | Online/offline detection + sync queue |
| `utils/indexedDBManager.ts` | IndexedDB cache for offline GET responses |
| `constants/importFields.ts` | IMPORT_CONFIGS — field metadata for import wizard (mirrors backend import_fields) |
| `composables/useOfflineData.ts` | Composable for offline-aware data fetching |

## Backend Shared Infrastructure (backend/core/)

| File | Purpose |
|------|---------|
| `settings.py` | Django settings; `AUTH_USER_MODEL = 'users.User'`; DEBUG via env var |
| `urls.py` | Root URL conf + SPA serving for Vue dist |
| `mixins.py` | `BulkImportMixin` — provides `download_template` + `bulk_import` + `get_import_fields` `@action`s |
| `views.py` | `UnitViewSet`, `ImportSessionViewSet`, `health_check`; import undo endpoint |
| `models_billing.py` | `Invoice`, `Bill`, `BillingPayment` |
| `views_billing.py` | Billing CRUD |
| `urls_billing.py` | Billing URL routes |

## Key Patterns & Gotchas

### bill_no generation (sales/models.py)
Auto-generated in `Sale.save()` from the row's own auto-incremented `pk` (`BILL-{pk:04d}`) after the initial insert — concurrency-safe since `pk` uniqueness is enforced by the DB.

### SaleItem quantities
Backend field is `quantity_dozens` (PositiveIntegerField). Frontend must POST and read `quantity_dozens`, not `quantity`.

### Sale identifier
Field is `bill_no`. There is **no** `receipt_number` on Sale. Reports and displays must use `bill_no`.

### Purchase payment tracking
`Purchase` model has **no** `invoice_number` or `payment_status`. Use `core.Invoice`/`core.Bill` models via `/api/billing/`.

### Vendor/Customer email
Neither `Vendor` nor `Customer` has an `email` field. Frontend search filters must not call `.toLowerCase()` on `vendor.email` or `customer.email`.

### Stock oversell
`SaleSerializer.create()` validates `quantity_dozens <= variant.quantity_dozens` and raises `ValidationError` before writing anything — guarded. Note the guard only fires when a matching `ProductVariant` row exists; if none does, the deduction goes through unchecked.

### Color fallback
`color_id` is now **required** per sale item — `SaleSerializer.create()` raises `ValidationError` if absent. No more silent `Color.objects.first()` fallback.

### Import undo (core/views.py)
`session.status = 'undone'` is only set after a `hard_errors` check — if any delete raises an unexpected exception, the view returns 500 before touching `session.status`, so `can_undo` still allows a retry. (Not-found records are tolerated and don't block marking the session undone.)

### BulkImportMixin
All ViewSets using bulk import inherit `download_template`, `bulk_import`, `get_import_fields` from `core.mixins.BulkImportMixin`. Do **not** re-implement these `@action`s on individual ViewSets.

### Router mode
Electron uses `createWebHashHistory` (hash URLs `#/...`). Browser uses `createWebHistory`. Detected via `navigator.userAgent.includes('electron')`.

### Auth guard
`router/index.ts` beforeEach: checks `localStorage['auth_token']`. Redirect to `/login` if absent.

### Axios offline behaviour
GET responses cached in IndexedDB for 30 min. POST/PUT/DELETE added to sync queue when offline. On 401, token removed and redirect to `/login`.

### export_fields on ViewSets
Do not define `export_fields` twice in the same ViewSet class body — Python silently uses the last definition.

## Dev Commands

```bash
# Backend
cd backend && python manage.py runserver 8000

# Frontend
cd frontend && npm run dev

# Build frontend
cd frontend && npm run build

# Run tests
cd frontend && npm run test:unit
```

## Branch Convention
- `master` — main branch
- `desktop-app` — current feature branch (Electron + Inno Setup installer)
