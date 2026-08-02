# Test Failures and Errors (as of 2025-12-22)

## Errors

### 1. NameError: name 'Response' is not defined
- **Location:** products/views.py (ProductViewSet or ProductVariantViewSet)
- **Cause:** The `Response` class from `rest_framework.response` is not imported or used outside its import scope.

## Failures

### 2. test_bulk_update_restricted_field
- **Test:** core.tests.BatchActionsMixinTests.test_bulk_update_restricted_field
- **Error:** 400 != 200
- **Details:** Test expects HTTP 200 OK, but got 400 Bad Request when bulk updating restricted fields.

### 3. test_export_csv
- **Test:** core.tests.BulkExportMixinTests.test_export_csv
- **Error:** 404 != 200
- **Details:** Test expects HTTP 200 OK, but got 404 Not Found for CSV export endpoint.

### 4. test_export_excel
- **Test:** core.tests.BulkExportMixinTests.test_export_excel
- **Error:** 404 != 200
- **Details:** Test expects HTTP 200 OK, but got 404 Not Found for Excel export endpoint.

### 5. test_download_template
- **Test:** core.tests.BulkImportMixinTests.test_download_template
- **Error:** Content-Type mismatch
- **Details:**
    - Expected: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
    - Actual: text/csv

### 6. test_product_export
- **Test:** core.tests.ProductBatchActionsTests.test_product_export
- **Error:** 404 != 200
- **Details:** Test expects HTTP 200 OK, but got 404 Not Found for product export endpoint.

### 7. test_vendor_export
- **Test:** core.tests.VendorBatchActionsTests.test_vendor_export
- **Error:** 404 != 200
- **Details:** Test expects HTTP 200 OK, but got 404 Not Found for vendor export endpoint.

---

**Summary:**
- 1 NameError (Response not defined)
- 5 endpoint 404 errors (export/template endpoints)
- 1 status code mismatch (400 vs 200)
- 1 content-type mismatch (CSV vs Excel)

**Next Steps:**
- Fix Response import in all relevant views.
- Ensure all export/template endpoints are registered and implemented.
- Align test and view logic for bulk update and content-type.
