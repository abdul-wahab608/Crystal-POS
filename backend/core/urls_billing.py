from rest_framework.routers import DefaultRouter
from .views_billing import InvoiceViewSet, BillViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet)
router.register(r'bills', BillViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = router.urls
