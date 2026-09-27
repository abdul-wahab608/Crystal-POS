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
| Desktop | None — Electron packaging was removed; the "desktop app" is Django serving the built Vue app + API from `localhost:8010` (**temporarily moved off 8000** — see "Dev port temporarily 8010" gotcha below), opened in the OS default browser via an Inno Setup installer |
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
│   ├── profit/           CostComponentType + ProductCost (profit analytics — see below)
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

Base URL: `http://127.0.0.1:8010/api` (temporarily 8010, not the usual 8000 — see gotcha below)

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
| `/profit/` | profit | cost-components/, product-costs/, summary/, trend/ |
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

### profit · `CostComponentType`
`name` (unique) · `is_system` (bool) · `created_at`. Seeded via migration `0002_seed_system_cost_components`: Raw Material, Electricity, Labor, Misc (`is_system=True`, cannot be renamed/deleted). Custom fields created via API always get `is_system=False` regardless of what the client sends — `CostComponentTypeViewSet.perform_create()` forces it.

### profit · `ProductCost`
`product` FK → products.Product · `component_type` FK → CostComponentType · `amount_per_dozen` · `valid_from` (Date) · `created_at`. **Versioned, never edited in place** — `ProductCostViewSet` only allows `get`/`post`/`delete` (no put/patch), so changing a cost means POSTing a new row with a new `valid_from`. "Current" cost for a product as-of any date = latest row per component type with `valid_from <= that date` (see `profit/services.py::CostLookup`). If no `ProductCost` row exists yet for a product/date, falls back to `Product.cop` as the total unit cost — `product-costs/current/?product=<id>` exposes this via `using_fallback_cop`.

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
| profit | `/profit`, `/profit/costs` | ProfitAnalyticsView, CostManagementView | profit.ts | CostComponentType, ProductCost, ProfitSummaryRow, ProfitTrend |

## Shared Infrastructure (frontend/src/shared/)

| Path | Purpose |
|------|---------|
| `api/axios.ts` | Axios instance — base URL 8010 (temporarily, see gotcha below), JWT header, offline queue, 30-min IndexedDB cache for GETs |
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
`router/index.ts` still branches on `navigator.userAgent.includes('electron')` (hash vs web history) and `axios.ts`/`errorLogger.ts` still check `window.electronAPI`. This is dead code left over from the removed Electron packaging — `window.electronAPI` never exists now, so these branches always take the browser/web-history path. Harmless but stale; do not treat it as evidence Electron is still in use.

### Installer is fully offline / self-contained (fixed 2026-08-06)
The installer bundles a python.org "embeddable" Python distribution with every `backend/requirements.txt` dependency pre-installed into its own `Lib\site-packages`, staged at *build time* by `installer/build-python-runtime.ps1` (developer machine, online) and shipped via `[Files]` into `{app}\python\` (see `CrystalPOS.iss`). `setup.ps1` has no Python-detection/venv/pip-install steps anymore — do not reintroduce any of those; the whole point is zero network access and no system Python requirement at install time. Two non-obvious things that make this actually work:
- **User site-packages pollution**: an embeddable interpreter's "user site" path on Windows is keyed only by Python version (`%APPDATA%\Python\PythonXY\site-packages`), so it silently collides with any regular same-version Python already on the machine and pip/import will prefer it over the bundled runtime's own packages unless `$env:PYTHONNOUSERSITE = "1"` is set before every invocation. It's set in `build-python-runtime.ps1` (build time) and in `setup.ps1`/`start-app.ps1`/`start-backend.ps1` (every runtime invocation) — if you add a new script that shells out to the bundled `python.exe`, set it there too.
- **`._pth` isolation**: a `._pth` file next to `python.exe` makes `sys.path` *entirely* fixed to its listed entries — `PYTHONPATH` is ignored outright and the executed script's own directory is never auto-added (both are documented CPython behavior for embeddable distributions, not a bug). The backend package (`core`, etc.) is only importable because `build-python-runtime.ps1` appends a relative `..\backend` line to the `_pth` file, which resolves against `{app}\python\`'s own location — this works precisely because `{app}\python\` and `{app}\backend\` are always sibling folders by construction of `CrystalPOS.iss`. Don't try to fix missing-module errors from the bundled interpreter by setting `PYTHONPATH` — it won't do anything; fix the `_pth` file instead.

### Auth guard
`router/index.ts` beforeEach: checks `localStorage['auth_token']`. Redirect to `/login` if absent.

### Axios offline behaviour
GET responses cached in IndexedDB for 30 min. POST/PUT/DELETE added to sync queue when offline. On 401, token removed and redirect to `/login`.

### export_fields on ViewSets
Do not define `export_fields` twice in the same ViewSet class body — Python silently uses the last definition.

### Sales unit_price string-multiplication bug (found 2026-08-09, NOT fixed — out of scope when found)
`sales/serializers.py::SaleSerializer.create()` does `subtotal=unit_price * quantity_dozens` where `unit_price` comes straight from the request's `items` list (`serializers.ListField`, not a nested serializer with type coercion). If `unit_price` ever arrives as a JSON string (e.g. `"100.00"` — the same DecimalField-as-string shape DRF itself produces everywhere else, and plausible from a future import/API caller), Python does **string repetition** instead of multiplication (`'100.00' * 10` → garbage), then crashes with `django.core.exceptions.ValidationError: value must be a decimal number` writing `SaleItem.subtotal`. The existing `SalesForm.vue` happens to send `unit_price` as a JS number so this doesn't fire in normal UI use today — found while seeding test data via a raw API call with a quoted decimal. Fix would be `Decimal(str(item_data['unit_price']))` before multiplying, matching the pattern already used in `purchases/serializers.py`.

### Dev port temporarily 8010, not 8000 (since 2026-08-17)
This dev machine has an unrelated Docker Compose project (`be-api-1`, plus `fe-web-1`/`be-worker-1`/`be-postgres-1`/`be-redis-1`) that also publishes port 8000, and fighting it caused real collateral damage (see incident below). Rather than keep contesting port 8000, the whole app was moved to **8010** everywhere it's hardcoded: `frontend/src/shared/api/axios.ts` (both the Electron and browser branches), `installer/start-app.ps1`, `installer/start-backend.ps1` (`$Port` default), `installer/start-frontend.ps1` (`$BackendUrl` default), and both READMEs. `manage.py runserver` must be started with `8010` explicitly (see Dev Commands below) — there is no code default anymore, the port is only baked into the scripts above. **This is provisional and may be reverted back to 8000** — if so, revert all the files just listed together, don't change axios.ts alone (the installed app's Django server and the frontend's hardcoded API base URL must always agree on the same port).

**Incident that prompted this (2026-08-09)**: `docker stop be-api-1` isn't durable — its `restart: unless-stopped` policy brings it back if Docker Desktop's backend restarts for any reason. Worse, **`localhost` resolves differently by process**: Vite's dev server binds only `[::1]:5173` (IPv6) by default, and the container's IPv6-loopback forwarding (`wslrelay.exe` on `[::1]:8000`) won over a plain `manage.py runserver 8000` (IPv4-only bind) whenever a browser resolved `localhost` to `::1` first — so `curl http://localhost:8000/...` and a Chrome-driven request to the same URL could silently hit two different backends. While attempting to clean up test processes, a `netstat`-scanning `taskkill` loop also killed `com.docker.backend.exe` (it was wildcard-bound to `0.0.0.0:8000`, so it matched a naive grep for `:8000` too) — this took down **every** container on the machine, not just `be-api-1`, and Docker Desktop got stuck mid-restart for an extended period afterward. **Lesson: never bulk-`taskkill` by scanning `netstat` output for a port number** — match by PID you already know, not by re-deriving PIDs from a port grep.

### Full-app browser verification pass (2026-08-06) — bug map
Every nav route + CRUD flow was driven end-to-end against the offline-installed app (not dev servers). Nodes below are `file → symptom → root cause`; all fixed same session.

```
users/signals.py (post_migrate signal, fires before setup.ps1's own admin step)
  → /api/users/ returned 403 for "admin"
  → get_or_create() defaults never set role=ADMIN → stayed 'STAFF' despite is_superuser=True
  → IsAdminUser/IsManagerUser check role, not is_staff

shared/stores/export.ts, batchActions.ts, views/ImportHistoryView.vue,
modules/reports/views/ReportsView.vue
  → 404 at /api/api/...
  → literal "/api/" re-prefixed on top of axios.ts's baseURL (which already has /api)
  → recurring bug class: never prefix a call with /api/ again

backend/raw_materials/urls.py (RawMaterialViewSet registers at "materials/", not router root
  — the only app that does this)
  → low_stock / export / bulk_* 404'd at /api/raw-materials/...
  → real paths need the extra segment: /api/raw-materials/materials/...
  → missed in export.ts, batchActions.ts, modules/raw_materials/stores/raw_materials.ts

modules/assets/views/AssetsView.vue
  → asset creation always failed
  → Category <select> bound to form.category (optional, backend ignores it) instead of
    required form.type; status options were TitleCase vs backend's uppercase choices
  → separately: purchase_value/current_value crash with TypeError on .toFixed()
    because DRF serializes DecimalFields as strings — wrap with Number(...) first
    (same pattern already used for Product.cop elsewhere)

backend/purchases/serializers.py + purchases/signals.py
  → every purchase submit crashed 500, and even when it didn't, zero PurchaseItem
    rows were ever created (stock never incremented)
  → signals.py referenced instance.invoice_number, which doesn't exist on Purchase
    (see "Purchase payment tracking" above) → 500
  → PurchaseSerializer.items was read_only with no create() override → items silently
    dropped on every request that got past the 500
  → fix: signal now uses instance.id/instance.vendor.name; serializer has an atomic
    create() that builds real PurchaseItem rows + a to_representation() override so
    GET/list still nests items the way PurchasesView.vue's table expects
  → invoice_number/payment_status typed into the form are still discarded (not real
    Purchase fields, tracked via core.Bill instead) — known limitation, not fixed

Dead code, never imported anywhere (confirmed via grep, don't trust these as current):
  modules/users/components/UserForm.vue
  modules/assets/components/AssetTable.vue
  modules/purchases/components/PurchaseForm.vue
  views/BankAccountsView.vue  (backend /api/bank-accounts/ works fine — just no
                                frontend route or nav entry exists)
```

### Profit Analytics (implemented 2026-08-09)
`backend/profit/` computes profit per piece/per dozen from existing `SaleItem` rows — no `Sale`/`SaleItem` schema changes were needed (`quantity_dozens` and `subtotal` already cover quantity/revenue).
- **Cost model**: see `CostComponentType`/`ProductCost` above. `profit/services.py::CostLookup` resolves the unit cost per dozen for a product as of a given date by summing the latest `ProductCost` row per component type with `valid_from <= that date`; falls back to `Product.cop` when no history exists yet.
- **Aggregation**: `profit/services.py::compute_profit_rows()` builds one row per `SaleItem` (revenue/cost/profit), filterable by `product`, `size_range`, `color`, `city` (via `sale.customer.city` — Sale has no location field of its own), `year`, `month`, `season`, `date_from`/`date_to`. `aggregate()` groups rows by `product`/`month`/`season`/`year`/`location`; `build_trend()` shapes grouped rows for ApexCharts, with an optional `series` dimension for multi-line charts (e.g. one line per article).
- **Season buckets** (hardcoded, 4-season): Spring Mar–May, Summer Jun–Aug, Autumn Sep–Nov, Winter Dec–Feb — see `SEASON_BY_MONTH` in services.py.
- **profit_ratio** = profit_amount / revenue (margin, not markup) throughout.
- **API**: `GET /api/profit/summary/` (totals, or grouped rows if `?group_by=` given), `GET /api/profit/trend/` (chart-shaped, `?x=` required dimension + optional `?series=`), both accept `?unit=dozen|piece`. `cost-components/` and `product-costs/` are read-open (any authenticated user) but write-gated to Admin/Manager via `IsAuthenticatedForReadManagerForWrite` in `profit/views.py`.
- **Frontend**: `CostManagementView.vue` (`/profit/costs`) is where costs get entered per product — pick a product, see the current effective breakdown (or the `Product.cop` fallback banner), add dated cost entries, add custom cost fields. `ProfitAnalyticsView.vue` (`/profit`) has the filter bar, KPI cards, ApexCharts trend chart, and breakdown table. Both follow the DecimalField-as-string convention (wrap in `Number(...)`) and never prefix calls with `/api/`.
- Full test coverage: `backend/profit/tests.py` (21 tests — cost versioning/fallback, aggregation math, permissions) and `frontend/src/modules/profit/stores/__tests__/profit.spec.ts` (9 tests). Verified end-to-end in a real browser (Selenium) against the offline-installed app: cost entry → sale → profit dashboard, including the piece/dozen unit toggle, with zero console errors.

## Dev Commands

```bash
# Backend (port is temporarily 8010, not the default 8000 — see "Dev port temporarily 8010" gotcha)
cd backend && python manage.py runserver 8010

# Frontend (bind IPv4 explicitly — Vite defaults to IPv6-only loopback, see gotcha above)
cd frontend && npm run dev -- --host 127.0.0.1

# Build frontend
cd frontend && npm run build

# Run tests
cd frontend && npm run test:unit
```

## Branch Convention
- `master` — main branch
- `desktop-app` — current feature branch (Inno Setup installer; Electron packaging was removed, see Router mode gotcha)
