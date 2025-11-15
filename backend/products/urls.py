from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, ProductHistoryViewSet

router = DefaultRouter()
router.register(r'', ProductViewSet)
router.register(r'product-history', ProductHistoryViewSet)

urlpatterns = router.urls 