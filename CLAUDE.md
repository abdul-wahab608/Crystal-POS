# CLAUDE.md — Crystal Project

## First step for every task

Read [context.md](context.md) before grepping or opening files. It contains:
- Full model field lists (so you don't grep models.py to find field names)
- API endpoint map (so you don't grep urls.py to find routes)
- Frontend module map (so you don't glob to find the right store or view)
- Key gotchas that have already caused bugs (oversell guard, bill_no race, email field removal, etc.)

Only grep/read source files when context.md doesn't have enough detail for the task.

## Code rules

- No comments unless the WHY is non-obvious (hidden constraint, workaround, invariant).
- No docstrings. No multi-line comment blocks.
- No backwards-compat shims for removed code — delete cleanly.
- No error handling for impossible paths. Trust Django/DRF/Vue internal guarantees.
- No features beyond what the task requires.

## Backend

- Django 5.2.3 + DRF 3.15 + SimpleJWT. DB is SQLite.
- `AUTH_USER_MODEL = 'users.User'` — always import User via `get_user_model()`.
- Bulk import actions (`download_template`, `bulk_import`, `get_import_fields`) live in `core.mixins.BulkImportMixin`. Do not reimplement them on individual ViewSets.
- `Sale.bill_no` is auto-generated in `save()` — not concurrency-safe. Don't add a second generation path.
- `SaleItem` uses `quantity_dozens` (PositiveIntegerField). Never use `quantity` on SaleItem.
- `Purchase` has no `invoice_number` or `payment_status` — those are on `core.Bill` via `/api/billing/`.
- `Vendor` and `Customer` have no `email` field.
- `Product` has no `available_stock` property — do not add it to serializers as ReadOnlyField.

## Frontend

- Vue 3 Composition API (`<script setup>`). All imports must appear before any executable code.
- Pinia for state. Stores are in `modules/<name>/stores/` or `shared/stores/`.
- Axios instance is at `shared/api/axios.ts` — use it, don't create new instances.
- Auth token: `localStorage['auth_token']`. Auth store: `shared/stores/auth.ts`.
- Offline: GET responses cached in IndexedDB 30 min. Mutations queued when offline.
- Router: hash history in Electron, web history in browser. Routes defined in `router/index.ts`.
- `SaleItem` quantities are `quantity_dozens` — never render or POST as `quantity`.
- `Sale` identifier is `bill_no` — never reference `receipt_number`.
- `vendor.email` and `customer.email` do not exist — never call `.toLowerCase()` on them.
- `SelectAllCheckbox` `:allIds` prop — don't pass a fresh `.map()` array inline in the template (causes child re-render on every tick).

## Testing

- Unit tests: `cd frontend && npm run test:unit` (Vitest).
- No mocking the database in backend tests — use real SQLite.
