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
| Desktop | No Electron. Django serves the built Vue app and the API from `localhost:8010` on the same machine (same origin, so no CORS needed). Shipped as an Inno Setup installer that bundles its own Python runtime (see "Installer is fully offline" gotcha) |
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
│   ├── sales/            Sale + SaleItem  (bill_no, quantity in product unit)
│   ├── purchases/        Purchase + PurchaseItem (raw-material and product lines)
│   ├── raw_materials/    RawMaterial + RawMaterialUsage
│   ├── production/       ProductionRun + ProductionRunItem + ProductionRunInput
│   ├── assets/           Asset + AssetLog
│   ├── payments/         Payment (links to Sale, Purchase, Customer, Vendor)
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

Base URL: `http://localhost:8010/api` (fixed port — see "Port 8010 is final" gotcha)

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
| `/raw-materials/` | raw_materials | materials/, usage/ |
| `/production/` | production | runs/ (list, create, retrieve, delete) |
| `/bank-accounts/` | bank_accounts | bank_accounts.urls |
| `/billing/` | core (urls_billing) | Invoice + Bill + BillingPayment |
| `/profit/` | profit | cost-components/, product-costs/, summary/, trend/ |
| `/health/` | core | health_check (GET) |

## Django Models — Field Reference

### users · `User` (extends AbstractUser)
`username, password, email, first_name, last_name, is_active`  
`role` (ADMIN/MANAGER/STAFF) · `phone`

### customers · `Customer`
`name` · `phone` · `address` · `city` · `customer_type` (REGULAR/WALK_IN) · `balance` · `is_active` · `created_at` · `updated_at`  
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
`name` · `unit` · `cop` (cost per unit) · `quantity` (Decimal, in `unit`; equals sum of variant quantities when it has variants) · `product_type` (MANUFACTURED/PURCHASED) · `size_ranges` M2M → SizeRange (max 3) · `last_updated` · `created_at`. Unique (`name`, `unit`).  
**No `available_stock` property** — ProductSerializer must NOT declare it as ReadOnlyField.

### products · `ProductVariant`
`product` FK · `size_range` FK (must be in `product.size_ranges`) · `color` FK · `quantity` (Decimal, in product unit) · `created_at`. Unique (`product`, `size_range`, `color`).

### products · `ProductHistory`
`product` FK · `change_type` · `quantity_change` · `date` · `reference` · `notes`

### sales · `Sale`
`bill_no` (unique, auto-generated in save()) · `sale_type` (WALK_IN/PHONE_ORDER/REGULAR, default REGULAR) · `customer` FK · `date` · `total_amount` · `payment_status` (PAID/UNPAID/PARTIAL) · `created_by` FK  
**No `receipt_number` field** — use `bill_no`.

### sales · `SaleItem`
`sale` FK · `product` FK · `size_range` FK · `color` FK · `quantity` (Decimal, in product unit) · `unit_price` · `subtotal`  
**No `quantity_dozens` field.** Duplicate variant lines in one sale are aggregated into one row.

### purchases · `Purchase`
`vendor` FK · `date` · `invoice_number` (vendor's bill number, blank) · `total_amount` (server-computed) · `created_by` FK  
**No `payment_status`** — handled by `core.models_billing.Bill`.

### purchases · `PurchaseItem`
`purchase` FK · `product` FK (null) · `size_range` FK (null) · `color` FK (null) · `raw_material` FK → raw_materials.RawMaterial (null) · `quantity` (Decimal > 0, in the line's unit) · `unit_cost` · `subtotal`. Exactly one of `product` / `raw_material` is set (DB check constraint). Product lines require `size_range` (must be in `product.size_ranges`) and `color`; raw lines must not have them.

### raw_materials · `RawMaterial`
`name` · `unit` · `quantity` (stock on hand, maintained by signals) · `reorder_level` · `created_at` · `updated_at`. Unique (`name`, `unit`).

### raw_materials · `RawMaterialUsage`
`raw_material` FK · `quantity_used` · `reference` · `notes` · `date_used`. Creating it decrements `RawMaterial.quantity`; deleting it restores it.

### production · `ProductionRun`
`date` (auto) · `reference` · `notes` · `created_by` FK. Children: `ProductionRunItem` (`run`, `variant` FK → ProductVariant, `quantity`) and `ProductionRunInput` (`run`, `raw_material` FK, `quantity`). Create increments variant/product stock and consumes raw materials (via `RawMaterialUsage` rows with reference `Production run #<id>`); delete reverses it.

### assets · `Asset`
`name` · `description` · `category` · `type` · `value` · `current_value` · `purchase_value` · `purchase_date` · `location` · `status` (ACTIVE/INACTIVE/DISPOSED) · `created_at`

### payments · `Payment`
`payment_type` (INCOMING/OUTGOING) · `payment_method` (CASH/CHEQUE/BANK) · `amount` · `status` · `customer` FK · `vendor` FK · `bank_account` FK · `bank_name` · `account_number` · `sale` FK → sales.Sale · `purchase` FK → purchases.Purchase · `direct_payment_to_vendor` FK · `due_date` · `payment_date` · `reference` · `notes` · `original_amount` · `remaining_amount`

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
`product` FK → products.Product · `component_type` FK → CostComponentType · `amount_per_dozen` (name kept from the old dozen model; the value is the cost per unit of the product's unit) · `valid_from` (Date) · `created_at`. **Versioned, never edited in place** — `ProductCostViewSet` only allows `get`/`post`/`delete` (no put/patch), so changing a cost means POSTing a new row with a new `valid_from`. "Current" cost for a product as-of any date = latest row per component type with `valid_from <= that date` (see `profit/services.py::CostLookup`). If no `ProductCost` row exists yet for a product/date, falls back to `Product.cop` as the total unit cost — `product-costs/current/?product=<id>` exposes this via `using_fallback_cop`.

## Frontend Module Map

Each module lives at `frontend/src/modules/<name>/` with this shape:
`views/<Name>View.vue` · `components/` · `stores/<name>.ts` · `types/index.ts`

| Module | Route path | View | Store | Key types |
|--------|-----------|------|-------|-----------|
| customers | `/customers` | CustomersView | customers.ts | Customer, CreateCustomerRequest |
| vendors | `/vendors` | VendorsView | vendors.ts | Vendor (no email field) |
| products | `/products` | ProductsView | products.ts + color.ts + sizeRange.ts + productVariant.ts | Product, ProductVariant, SizeRange, Color |
| sales | `/sales` | SalesView | sales.ts + billing.ts | Sale, SaleItem (quantity in product unit) |
| purchases | `/purchases` | PurchasesView | purchases.ts + billing.ts | Purchase, PurchaseItem |
| raw_materials | `/raw-materials` | RawMaterialsView | raw_materials.ts | RawMaterial |
| assets | `/assets` | AssetsView | assets.ts | Asset |
| payments | `/payments` | PaymentsView | payments.ts | Payment |
| reports | `/reports` | ReportsView | reports.ts | — |
| users | `/users` | UsersView | users.ts | User |
| bank_accounts | `/bank-accounts` | BankAccountsView | bank_accounts.ts | BankAccount |
| profit | `/profit`, `/profit/costs` | ProfitAnalyticsView, CostManagementView | profit.ts | CostComponentType, ProductCost, ProfitSummaryRow, ProfitTrend |

## Shared Infrastructure (frontend/src/shared/)

| Path | Purpose |
|------|---------|
| `shared/api/baseUrl.ts` | `API_BASE_URL` = `http://localhost:8010/api` (separate file to avoid an axios ↔ offlineManager import cycle) |
| `api/axios.ts` | Axios instance. GET responses cached in IndexedDB; served from cache when the backend is unreachable. Write calls with no response are queued via offlineManager and reject with `QueuedWriteError` |
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
| `utils/offlineManager.ts` | Reachability via `GET /api/health/` (every 10 s and after any no-response error); FIFO write queue persisted in IndexedDB (`syncQueue` store), replayed on reconnect; failed items (4xx / exhausted 5xx) shown in OfflineSettings for retry/discard |
| `utils/indexedDBManager.ts` | IndexedDB cache for offline GET responses |
| `constants/importFields.ts` | IMPORT_CONFIGS — field metadata for import wizard (mirrors backend import_fields) |
| `utils/queuedWrite.ts` | `acceptQueued(write)` runs a write and swallows only `QueuedWriteError`; `isQueuedWrite(e)` guard. Store actions rethrow queued errors so views close the form without showing a failure |

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

### Quantities are in the product's unit
Every quantity (`Product`, `ProductVariant`, `RawMaterial`, `SaleItem`, `PurchaseItem`, `ProductionRunItem`, `ProductionRunInput`) is in the unit of the product or raw material it belongs to (DOZEN, PCS, KG, POUND...). Nothing converts units and nothing sums quantities across units: reports and profit return per-unit quantities, and single-unit totals also carry `unit`, `quantity` and `profit_per_unit`, while mixed-unit totals return `null` for those and list `quantities` per unit.

### Sale identifier
Field is `bill_no`. There is **no** `receipt_number` on Sale. Reports and displays must use `bill_no`.

### Purchase payment tracking
`Purchase` has no stored `payment_status`. It is computed from the outgoing `Payment` rows linked to the bill (`Payment.purchase`): `paid_amount`, `unpaid_amount` and `payment_status` (PAID / PARTIAL / UNPAID) are serialized on every purchase, and `GET /api/purchases/?unpaid=true` returns bills with a balance. `Purchase.invoice_number` stores the vendor's bill number. `core.Bill` (`/api/billing/`) is a separate, unused billing concept.

### Purchase ledger and stock signals
`purchases/signals.py`: each `Purchase` creates one PURCHASE `VendorTransaction` (amount = `total_amount`); deleting the purchase reverses that row and the vendor balance. Each `PurchaseItem` adds stock on create and removes it on delete (variant + product for product lines, `RawMaterial.quantity` for raw lines). `PurchaseViewSet.perform_destroy` refuses the delete if that stock has already been used. Vendor payments stay `VendorTransaction` PAYMENT rows from `payments/signals.py`.

### RawMaterial stock
`RawMaterial.quantity` is the single source of truth, maintained by the signals in `raw_materials/signals.py` (usage) and `purchases/signals.py` (purchase lines). There is no `available_stock` and no `RawMaterialPurchase`.

### Vendor/Customer email
Neither `Vendor` nor `Customer` has an `email` field. Frontend search filters must not call `.toLowerCase()` on `vendor.email` or `customer.email`.

### Stock oversell
`SaleSerializer.create()` validates the aggregated quantity per variant against `variant.quantity` and raises `ValidationError` before writing anything. A line with no matching `ProductVariant` is refused.

### Color fallback
`color_id` is now **required** per sale item — `SaleSerializer.create()` raises `ValidationError` if absent. No more silent `Color.objects.first()` fallback.

### Import undo (core/views.py)
`session.status = 'undone'` is only set after a `hard_errors` check — if any delete raises an unexpected exception, the view returns 500 before touching `session.status`, so `can_undo` still allows a retry. (Not-found records are tolerated and don't block marking the session undone.)

### BulkImportMixin
All ViewSets using bulk import inherit `download_template`, `bulk_import`, `get_import_fields` from `core.mixins.BulkImportMixin`. Do **not** re-implement these `@action`s on individual ViewSets.

### Router mode
`router/index.ts` always uses web history. Electron was removed; `window.electronAPI` no longer exists anywhere.

### Installer is fully offline / self-contained (fixed 2026-08-06)
The installer bundles a python.org "embeddable" Python distribution with every `backend/requirements.txt` dependency pre-installed into its own `Lib\site-packages`, staged at *build time* by `installer/build-python-runtime.ps1` (developer machine, online) and shipped via `[Files]` into `{app}\python\` (see `CrystalPOS.iss`). `setup.ps1` has no Python-detection/venv/pip-install steps anymore — do not reintroduce any of those; the whole point is zero network access and no system Python requirement at install time. Two non-obvious things that make this actually work:
- **User site-packages pollution**: an embeddable interpreter's "user site" path on Windows is keyed only by Python version (`%APPDATA%\Python\PythonXY\site-packages`), so it silently collides with any regular same-version Python already on the machine and pip/import will prefer it over the bundled runtime's own packages unless `$env:PYTHONNOUSERSITE = "1"` is set before every invocation. It's set in `build-python-runtime.ps1` (build time) and in `setup.ps1`/`start-app.ps1`/`start-backend.ps1` (every runtime invocation) — if you add a new script that shells out to the bundled `python.exe`, set it there too.
- **`._pth` isolation**: a `._pth` file next to `python.exe` makes `sys.path` *entirely* fixed to its listed entries — `PYTHONPATH` is ignored outright and the executed script's own directory is never auto-added (both are documented CPython behavior for embeddable distributions, not a bug). The backend package (`core`, etc.) is only importable because `build-python-runtime.ps1` appends a relative `..\backend` line to the `_pth` file, which resolves against `{app}\python\`'s own location — this works precisely because `{app}\python\` and `{app}\backend\` are always sibling folders by construction of `CrystalPOS.iss`. Don't try to fix missing-module errors from the bundled interpreter by setting `PYTHONPATH` — it won't do anything; fix the `_pth` file instead.

### Auth guard
`router/index.ts` beforeEach: checks `localStorage['auth_token']`. Redirect to `/login` if absent.

### Offline behaviour
- Reachability is probed against `/api/health/`, not `navigator.onLine` (which only reflects network adapters).
- GET fallback: the last cached response for the exact method + URL (including query params) is served when the backend is unreachable. No TTL.
- Writes when unreachable: queued in IndexedDB and the call rejects with `QueuedWriteError`. Every write call site must go through `acceptQueued()` or rethrow queued errors; never show a red error for a queued save and never re-submit it (duplicate sales/payments).
- Replay: 2xx removes the item; 4xx moves it to failed (visible in OfflineSettings, discard button); 5xx retries 3 times then fails; network error or 401 stops replay and keeps the item.
- Auth URLs and FormData uploads are never queued.
- Known gap: creating a NEW product with size/color variants is refused while offline (variants need the product id).

### export_fields on ViewSets
Do not define `export_fields` twice in the same ViewSet class body — Python silently uses the last definition.

### Port 8010 is final
The backend, the frontend API base URL (`shared/api/baseUrl.ts`) and the installer scripts all use `8010`. Change them together if the port ever changes. Never bulk-kill processes by scanning `netstat` output for a port number: a wildcard-bound system service (for example Docker Desktop) matches the same grep and gets killed too.

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

Retired in the 2026 restructure. Do not rebuild these from memory: the purchase form is `modules/purchases/views/PurchasesView.vue`, the bank accounts page is routed at `/bank-accounts`, and the catalog (units, size ranges, colors) is at `/catalog`.
```

### Profit Analytics (implemented 2026-08-09)
`backend/profit/` computes profit from existing `SaleItem` rows (`quantity` in the product's unit, and `subtotal` as revenue).
- **Cost model** (per sale line, as of the sale date, `profit/services.py::CostLookup.resolve`): 1) MANUAL: `ProductCost` rows with `valid_from <= date`, latest per component; 2) PRODUCTION: the most recent usable production run for the product on or before the date, unit cost = sum(input qty × latest raw purchase unit cost) allocated to the product by its share of that run's output in the same unit; 3) COP: `Product.cop` if > 0; 4) MISSING: cost, profit and margin are null and `cost_missing` is true. A profit margin is never shown when cost is missing. Group rows carry the weakest `cost_source`.
- **Aggregation**: `profit/services.py::compute_profit_rows()` builds one row per `SaleItem` (revenue/cost/profit), filterable by `product`, `size_range`, `color`, `city` (via `sale.customer.city` — Sale has no location field of its own), `year`, `month`, `season`, `date_from`/`date_to`. `aggregate()` groups rows by `product`/`month`/`season`/`year`/`location`; `build_trend()` shapes grouped rows for ApexCharts, with an optional `series` dimension for multi-line charts (e.g. one line per article). Quantities are per unit (see "Quantities are in the product's unit"); there is no piece/dozen toggle.
- **Season buckets** (hardcoded, 4-season): Spring Mar–May, Summer Jun–Aug, Autumn Sep–Nov, Winter Dec–Feb — see `SEASON_BY_MONTH` in services.py.
- **profit_ratio** = profit_amount / revenue (margin, not markup) throughout.
- **API**: `GET /api/profit/summary/` (totals, or grouped rows if `?group_by=` given), `GET /api/profit/trend/` (chart-shaped, `?x=` dimension (defaults to `month`, invalid values 400) + optional `?series=`). `cost-components/` and `product-costs/` are read-open (any authenticated user) but write-gated to Admin/Manager via `IsAuthenticatedForReadManagerForWrite` in `profit/views.py`.
- **Frontend**: `CostManagementView.vue` (`/profit/costs`) is where costs get entered per product — pick a product, see the current effective breakdown (or the `Product.cop` fallback banner), add dated cost entries, add custom cost fields. `ProfitAnalyticsView.vue` (`/profit`) has the filter bar, KPI cards, ApexCharts trend chart, and breakdown table. Both follow the DecimalField-as-string convention (wrap in `Number(...)`) and never prefix calls with `/api/`.
- Full test coverage: `backend/profit/tests.py` (21 tests — cost versioning/fallback, aggregation math, permissions) and `frontend/src/modules/profit/stores/__tests__/profit.spec.ts` (9 tests). Verified end-to-end in a real browser (Selenium) against the offline-installed app: cost entry → sale → profit dashboard, including the piece/dozen unit toggle, with zero console errors.

## Dev Commands

```bash
# Backend (port 8010 is final — see "Port 8010 is final" gotcha)
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
- `desktop-app` — current feature branch (Inno Setup installer; Electron was removed, see Router mode gotcha)
