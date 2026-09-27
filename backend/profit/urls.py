from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CostComponentTypeViewSet, ProductCostViewSet, ProfitSummaryView, ProfitTrendView

router = DefaultRouter()
router.register(r'cost-components', CostComponentTypeViewSet, basename='cost-component')
router.register(r'product-costs', ProductCostViewSet, basename='product-cost')

urlpatterns = [
    path('summary/', ProfitSummaryView.as_view(), name='profit-summary'),
    path('trend/', ProfitTrendView.as_view(), name='profit-trend'),
    path('', include(router.urls)),
]
