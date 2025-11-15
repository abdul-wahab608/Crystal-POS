from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReportViewSet, sales_report, inventory_report, customer_report

router = DefaultRouter()
router.register(r'', ReportViewSet)

urlpatterns = [
    # Report endpoints
    path('sales-report/', sales_report, name='sales_report'),
    path('inventory-report/', inventory_report, name='inventory_report'),
    path('customer-report/', customer_report, name='customer_report'),
    # Report management endpoints
    path('', include(router.urls)),
] 