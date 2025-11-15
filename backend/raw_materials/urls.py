from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RawMaterialViewSet, RawMaterialUsageViewSet, RawMaterialPurchaseViewSet

router = DefaultRouter()
# Register the main viewset with a specific pattern
router.register(r'materials', RawMaterialViewSet, basename='rawmaterial')

urlpatterns = [
    path('', include(router.urls)),
    # Add explicit paths for sub-endpoints
    path('purchase/', RawMaterialPurchaseViewSet.as_view({'get': 'list', 'post': 'create'}), name='rawmaterial-purchase'),
    path('usage/', RawMaterialUsageViewSet.as_view({'get': 'list', 'post': 'create'}), name='rawmaterial-usage'),
] 