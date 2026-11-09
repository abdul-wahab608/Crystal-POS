from rest_framework.routers import DefaultRouter
from .views import ProductionRunViewSet

router = DefaultRouter()
router.register(r'runs', ProductionRunViewSet)

urlpatterns = router.urls
