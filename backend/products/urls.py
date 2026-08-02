from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductHistoryViewSet, SizeRangeViewSet, ColorViewSet, ProductVariantViewSet

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from .views import ProductViewSet, ProductHistoryViewSet, SizeRangeViewSet, ColorViewSet, ProductVariantViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet)
router.register(r'product-history', ProductHistoryViewSet)
router.register(r'size-ranges', SizeRangeViewSet)
router.register(r'colors', ColorViewSet)
router.register(r'product-variants', ProductVariantViewSet)

# Explicit custom actions for mixins
custom_actions = [
	path('export/', ProductViewSet.as_view({'get': 'export'}), name='product-export'),
	path('download_template/', ProductViewSet.as_view({'get': 'download_template'}), name='product-download-template'),
	path('bulk_update/', ProductViewSet.as_view({'post': 'bulk_update'}), name='product-bulk-update'),
	path('bulk_delete/', ProductViewSet.as_view({'post': 'bulk_delete'}), name='product-bulk-delete'),
	path('bulk_activate/', ProductViewSet.as_view({'post': 'bulk_activate'}), name='product-bulk-activate'),
	path('bulk_deactivate/', ProductViewSet.as_view({'post': 'bulk_deactivate'}), name='product-bulk-deactivate'),
	path('get_import_fields/', ProductViewSet.as_view({'get': 'get_import_fields'}), name='product-get-import-fields'),
	path('validate_import/', ProductViewSet.as_view({'post': 'validate_import'}), name='product-validate-import'),
	path('bulk_import/', ProductViewSet.as_view({'post': 'bulk_import'}), name='product-bulk-import'),
]

urlpatterns = router.urls + custom_actions