from rest_framework.routers import DefaultRouter
from .views import PurchaseViewSet, PurchaseItemViewSet

router = DefaultRouter()
router.register(r'', PurchaseViewSet)
router.register(r'purchase-items', PurchaseItemViewSet)

urlpatterns = router.urls 