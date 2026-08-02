# Size Ranges & Colors Implementation Plan

## Overview
Add shoe size ranges and colors to products for a shoe manufacturing company. Track stock per product-size-color combination in dozens.

---

## Data Structure

```
SizeRange: { id, name, created_at }
Color: { id, name, created_at }
ProductVariant: { id, product_id, size_range_id, color_id, quantity_dozens }
Product: { ..., size_range_id (required, default size) }
SaleItem: { ..., size_range_id, color_id }
```

---

## Initial Data

### Size Ranges
- 8-9-10
- 11-12-13
- 1-2-3
- 4-5-6
- 7-8-9-10
- 11-12
- 10-11-12
- 13-1-2
- 3-4-5
- 6-7-8-9
- 10-11
- 20-24
- 24-29
- 30-35
- 36-41

### Colors
- Black
- Brown
- Leather Blue
- Cream
- Skin
- Gray
- Steel Gray
- Maroon
- Red
- Sky Blue
- Purple
- Khaki
- Biscuit
- Yellow
- Green
- Pink
- Orange
- Metallic

---

## Phase 1: Backend Models & Migrations
- [x] Create `SizeRange` model in `products/models.py`
- [x] Create `Color` model in `products/models.py`
- [x] Create `ProductVariant` model (product + size + color + qty_dozens)
- [x] Add `size_range` FK to `Product` model (required)
- [x] Add `size_range` and `color` FK to `SaleItem` model
- [x] Create serializers for new models
- [ ] Create migrations
- [ ] Delete old DB and run fresh migrations

---

## Phase 2: Backend API Endpoints
- [x] `SizeRangeViewSet` - Full CRUD at `/api/size-ranges/`
- [x] `ColorViewSet` - Full CRUD at `/api/colors/`
- [x] `ProductVariantViewSet` - CRUD at `/api/product-variants/`
- [x] Add filtering on products by size_range
- [x] Add filtering on product-variants by product/size/color
- [x] Update `ProductViewSet` to include variants
- [x] Seed initial size ranges and colors

---

## Phase 3: Frontend Types & Stores
- [x] Add `SizeRange` interface
- [x] Add `Color` interface
- [x] Add `ProductVariant` interface
- [x] Update `Product` interface with size_range
- [x] Create `useSizeRangeStore()`
- [x] Create `useColorStore()`
- [x] Create `useProductVariantStore()`

---

## Phase 4: Frontend UI - Size Ranges & Colors Management
- [ ] Add "Manage Size Ranges" section in Products page
  - [ ] List all size ranges
  - [ ] Add new size range form
  - [ ] Delete size range button
- [ ] Add "Manage Colors" section in Products page
  - [ ] List all colors
  - [ ] Add new color form
  - [ ] Delete color button

---

## Phase 5: Frontend UI - Product Form Updates
- [ ] Add required size range dropdown in product form
- [ ] Add product variants section (size + color + qty)
- [ ] Allow adding multiple variants per product
- [ ] Show stock per variant in product details

---

## Phase 6: Frontend UI - Filtering & Display
- [ ] Add size range filter dropdown on products list
- [ ] Add color filter dropdown on products list
- [ ] Show stock breakdown by size/color in table
- [ ] Stock summary view

---

## Phase 7: Sales Integration
- [ ] Update sale item form to select size range
- [ ] Update sale item form to select color
- [ ] Deduct from correct variant stock on sale
- [ ] Show size/color in sale history

---

## Phase 8: Testing & Cleanup
- [ ] Test all CRUD operations
- [ ] Test filtering
- [ ] Test sales flow with size/color
- [ ] Remove this tracking file

---

## Progress Log

| Date       | Phase | Status | Notes |
|------------|-------|--------|-------|
| 2025-12-21 | 1     | Backend models & serializers done | |
| 2025-12-21 | 2     | Backend API endpoints done | |
| 2025-12-21 | 3     | Frontend Pinia stores done | |

