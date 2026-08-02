from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReportViewSet, sales_report, inventory_report,
    customer_report, area_report, article_report, CustomerSalesReportView
)

router = DefaultRouter()
router.register(r'', ReportViewSet)

urlpatterns = [
    path('sales-report/', sales_report, name='sales_report'),
    path('inventory-report/', inventory_report, name='inventory_report'),
    path('customer-report/', customer_report, name='customer_report'),
    path('area-report/', area_report, name='area_report'),
    path('article-report/', article_report, name='article_report'),
    path('customer-sales/', CustomerSalesReportView.as_view(), name='customer_sales_report'),
    path('', include(router.urls)),
]
