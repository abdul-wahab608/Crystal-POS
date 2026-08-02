from django.db import models
from customers.models import Customer
from django.contrib.auth import get_user_model


class Sale(models.Model):
    PAID = 'PAID'
    PARTIAL = 'PARTIAL'
    UNPAID = 'UNPAID'
    PAYMENT_STATUS_CHOICES = [
        (PAID, 'Paid'),
        (PARTIAL, 'Partial'),
        (UNPAID, 'Unpaid'),
    ]
    WALK_IN = 'WALK_IN'
    PHONE_ORDER = 'PHONE_ORDER'
    REGULAR = 'REGULAR'
    SALE_TYPE_CHOICES = [
        (WALK_IN, 'Walk-in'),
        (PHONE_ORDER, 'Phone Order'),
        (REGULAR, 'Regular'),
    ]

    bill_no = models.CharField(max_length=20, unique=True, blank=True)
    sale_type = models.CharField(max_length=20, choices=SALE_TYPE_CHOICES, default=REGULAR)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='sales')
    date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default=UNPAID)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.bill_no:
            super().save(*args, **kwargs)
            # Use the actual pk (guaranteed unique) to avoid race conditions
            Sale.objects.filter(pk=self.pk).update(bill_no=f'BILL-{self.pk:04d}')
            self.bill_no = f'BILL-{self.pk:04d}'
            return
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.bill_no} - {self.customer.name}"


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE)
    size_range = models.ForeignKey('products.SizeRange', on_delete=models.PROTECT)
    color = models.ForeignKey('products.Color', on_delete=models.PROTECT)
    quantity_dozens = models.PositiveIntegerField(default=0)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.size_range.name}, {self.color.name}) x {self.quantity_dozens} dz"
