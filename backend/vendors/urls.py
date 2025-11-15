from rest_framework.routers import DefaultRouter
from .views import VendorViewSet, VendorTransactionViewSet, VendorProductViewSet

router = DefaultRouter()
router.register(r'', VendorViewSet)
router.register(r'vendor-transactions', VendorTransactionViewSet)
router.register(r'vendor-products', VendorProductViewSet)

urlpatterns = router.urls 