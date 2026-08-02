from django.db import models
from sales.models import Sale
from purchases.models import Purchase


class Invoice(models.Model):
    number = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=[('PAID', 'Paid'), ('PARTIAL', 'Partial'), ('UNPAID', 'Unpaid')], default='UNPAID')
    payment_method = models.CharField(max_length=20, choices=[('CASH', 'Cash'), ('CHEQUE', 'Cheque'), ('BANK_TRANSFER', 'Bank Transfer')])
    sale = models.OneToOneField('sales.Sale', on_delete=models.CASCADE, related_name='invoice', null=True, blank=True)

    def __str__(self):
        return f"Invoice #{self.number}"


class Bill(models.Model):
    number = models.CharField(max_length=100, unique=True)
    date = models.DateField(auto_now_add=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_status = models.CharField(max_length=10, choices=[('PAID', 'Paid'), ('PARTIAL', 'Partial'), ('UNPAID', 'Unpaid')], default='UNPAID')
    payment_method = models.CharField(max_length=20, choices=[('CASH', 'Cash'), ('CHEQUE', 'Cheque'), ('BANK_TRANSFER', 'Bank Transfer')])
    purchase = models.OneToOneField('purchases.Purchase', on_delete=models.CASCADE, related_name='bill', null=True, blank=True)

    def __str__(self):
        return f"Bill #{self.number}"

class Payment(models.Model):
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=20, choices=[('CASH', 'Cash'), ('CHEQUE', 'Cheque'), ('BANK_TRANSFER', 'Bank Transfer')])
    reference = models.CharField(max_length=255, blank=True, null=True)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)

    def __str__(self):
        if self.invoice:
            return f"Payment for Invoice {self.invoice.number} - {self.amount}"
        elif self.bill:
            return f"Payment for Bill {self.bill.number} - {self.amount}"
        return f"Payment {self.amount}"
