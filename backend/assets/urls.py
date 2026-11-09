from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, AssetLogViewSet

router = DefaultRouter()
router.register(r'asset-logs', AssetLogViewSet)
router.register(r'', AssetViewSet)

urlpatterns = router.urls
