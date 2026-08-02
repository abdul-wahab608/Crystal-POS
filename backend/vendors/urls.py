from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, VendorTransactionViewSet, VendorProductViewSet

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from .views import VendorViewSet, VendorTransactionViewSet, VendorProductViewSet

router = DefaultRouter()
router.register(r'', VendorViewSet)
router.register(r'vendor-transactions', VendorTransactionViewSet)
router.register(r'vendor-products', VendorProductViewSet)

# Explicit custom actions for mixins
custom_actions = [
	path('export/', VendorViewSet.as_view({'get': 'export'}), name='vendor-export'),
	path('download_template/', VendorViewSet.as_view({'get': 'download_template'}), name='vendor-download-template'),
	path('bulk_update/', VendorViewSet.as_view({'post': 'bulk_update'}), name='vendor-bulk-update'),
	path('bulk_delete/', VendorViewSet.as_view({'post': 'bulk_delete'}), name='vendor-bulk-delete'),
	path('bulk_activate/', VendorViewSet.as_view({'post': 'bulk_activate'}), name='vendor-bulk-activate'),
	path('bulk_deactivate/', VendorViewSet.as_view({'post': 'bulk_deactivate'}), name='vendor-bulk-deactivate'),
	path('get_import_fields/', VendorViewSet.as_view({'get': 'get_import_fields'}), name='vendor-get-import-fields'),
	path('validate_import/', VendorViewSet.as_view({'post': 'validate_import'}), name='vendor-validate-import'),
	path('bulk_import/', VendorViewSet.as_view({'post': 'bulk_import'}), name='vendor-bulk-import'),
]

urlpatterns = router.urls + custom_actions