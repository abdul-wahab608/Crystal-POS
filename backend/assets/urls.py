from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, AssetLogViewSet

router = DefaultRouter()
router.register(r'', AssetViewSet)
router.register(r'asset-logs', AssetLogViewSet)

urlpatterns = router.urls 