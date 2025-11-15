from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerTransactionViewSet

router = DefaultRouter()
router.register(r'', CustomerViewSet)
router.register(r'customer-transactions', CustomerTransactionViewSet)

urlpatterns = router.urls 