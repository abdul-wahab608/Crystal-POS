from django.db import models
from vendors.models import Vendor
from products.models import Product
from django.contrib.auth import get_user_model

class Purchase(models.Model):
    PAID = 'PAID'
    PARTIAL = 'PARTIAL'
    UNPAID = 'UNPAID'
    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (PARTIAL, 'Partial'),
        (UNPAID, 'Unpaid'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='purchases')
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    invoice_number = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Purchase #{self.id} - {self.vendor.name}"

class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
