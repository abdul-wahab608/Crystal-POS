from rest_framework.routers import DefaultRouter
from .views import PurchaseViewSet

router = DefaultRouter()
router.register(r'', PurchaseViewSet)

urlpatterns = router.urls
