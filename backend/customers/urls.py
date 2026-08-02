from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerTransactionViewSet

from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns
from django.urls import path
from .views import CustomerViewSet, CustomerTransactionViewSet

router = DefaultRouter()
router.register(r'', CustomerViewSet)
router.register(r'customer-transactions', CustomerTransactionViewSet)

customer_list = CustomerViewSet.as_view({'get': 'list', 'post': 'create'})
customer_detail = CustomerViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'})

# Explicit custom actions for mixins
custom_actions = [
	path('export/', CustomerViewSet.as_view({'get': 'export'}), name='customer-export'),
	path('download_template/', CustomerViewSet.as_view({'get': 'download_template'}), name='customer-download-template'),
	path('bulk_update/', CustomerViewSet.as_view({'post': 'bulk_update'}), name='customer-bulk-update'),
	path('bulk_delete/', CustomerViewSet.as_view({'post': 'bulk_delete'}), name='customer-bulk-delete'),
	path('bulk_activate/', CustomerViewSet.as_view({'post': 'bulk_activate'}), name='customer-bulk-activate'),
	path('bulk_deactivate/', CustomerViewSet.as_view({'post': 'bulk_deactivate'}), name='customer-bulk-deactivate'),
	path('get_import_fields/', CustomerViewSet.as_view({'get': 'get_import_fields'}), name='customer-get-import-fields'),
	path('validate_import/', CustomerViewSet.as_view({'post': 'validate_import'}), name='customer-validate-import'),
	path('bulk_import/', CustomerViewSet.as_view({'post': 'bulk_import'}), name='customer-bulk-import'),
]

urlpatterns = router.urls + custom_actions