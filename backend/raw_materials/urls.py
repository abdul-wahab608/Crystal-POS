from rest_framework.routers import DefaultRouter
from .views import RawMaterialViewSet, RawMaterialUsageViewSet

router = DefaultRouter()
router.register(r'materials', RawMaterialViewSet, basename='rawmaterial')
router.register(r'usage', RawMaterialUsageViewSet, basename='rawmaterialusage')

urlpatterns = router.urls
