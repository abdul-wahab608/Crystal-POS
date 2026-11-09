from decimal import Decimal
from django.db import models
from django.db.models import Q, Sum
from vendors.models import Vendor
from payments.models import Payment
from django.contrib.auth import get_user_model


class Purchase(models.Model):
    PAID = 'PAID'
    PARTIAL = 'PARTIAL'
    UNPAID = 'UNPAID'

    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateTimeField(auto_now_add=True)
    invoice_number = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Purchase #{self.id} - {self.vendor.name}"

    def paid_amount(self):
        return self.payments.filter(payment_type=Payment.OUTGOING).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0')

    def unpaid_amount(self):
        return self.total_amount - self.paid_amount()

    @property
    def payment_status(self):
        paid = self.paid_amount()
        if paid >= self.total_amount:
            return self.PAID
        if paid > 0:
            return self.PARTIAL
        return self.UNPAID


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT, null=True, blank=True)
    size_range = models.ForeignKey('products.SizeRange', on_delete=models.PROTECT, null=True, blank=True)
    color = models.ForeignKey('products.Color', on_delete=models.PROTECT, null=True, blank=True)
    raw_material = models.ForeignKey('raw_materials.RawMaterial', on_delete=models.PROTECT, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    Q(product__isnull=False, raw_material__isnull=True)
                    | Q(product__isnull=True, raw_material__isnull=False)
                ),
                name='purchaseitem_exactly_one_target',
            ),
        ]

    def __str__(self):
        target = self.product or self.raw_material
        return f"{target.name} x {self.quantity}"
