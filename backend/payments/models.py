from django.db import models
from customers.models import Customer
from vendors.models import Vendor
from bank_accounts.models import BankAccount

class Payment(models.Model):
    # Payment Type
    INCOMING = 'INCOMING'  # Client paying you
    OUTGOING = 'OUTGOING'  # You paying vendor
    DIRECT = 'DIRECT'      # Client paying vendor directly
    PAYMENT_TYPE_CHOICES = [
        (INCOMING, 'Incoming'),
        (OUTGOING, 'Outgoing'),
        (DIRECT, 'Direct Client-Vendor'),
    ]
    
    # Payment Method
    CASH = 'CASH'
    BANK = 'BANK'
    CHEQUE = 'CHEQUE'
    PARCHI = 'PARCHI'
    PAYMENT_METHOD_CHOICES = [
        (CASH, 'Cash'),
        (BANK, 'Bank Transfer'),
        (CHEQUE, 'Cheque'),
        (PARCHI, 'Parchi (Promissory)'),
    ]
    
    # Payment Status
    PENDING = 'PENDING'
    PARTIAL = 'PARTIAL'
    COMPLETED = 'COMPLETED'
    OVERDUE = 'OVERDUE'
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PARTIAL, 'Partially Paid'),
        (COMPLETED, 'Completed'),
        (OVERDUE, 'Overdue'),
    ]
    
    # Core fields
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE_CHOICES, default=INCOMING)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default=CASH)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDING)
    
    # Relationships
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, null=True, blank=True, related_name='payments')
    bank_account = models.ForeignKey(BankAccount, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Bank details (for bank transfers)
    bank_name = models.CharField(max_length=200, blank=True, null=True)
    account_number = models.CharField(max_length=100, blank=True, null=True)
    
    # Transaction links (for automatic payments)
    sale = models.ForeignKey('sales.Sale', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    purchase = models.ForeignKey('raw_materials.RawMaterialPurchase', on_delete=models.SET_NULL, null=True, blank=True, related_name='payments')
    
    # Direct payment tracking (client paying vendor directly)
    direct_payment_to_vendor = models.ForeignKey(Vendor, on_delete=models.SET_NULL, null=True, blank=True, related_name='direct_payments')
    
    # Timing and tracking
    due_date = models.DateField(null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    
    # For partial payments and compounding
    original_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    remaining_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        if self.payment_type == self.INCOMING and self.customer:
            return f"Incoming: {self.customer.name} - ${self.amount}"
        elif self.payment_type == self.OUTGOING and self.vendor:
            return f"Outgoing: {self.vendor.name} - ${self.amount}"
        elif self.payment_type == self.DIRECT and self.customer and self.direct_payment_to_vendor:
            return f"Direct: {self.customer.name} → {self.direct_payment_to_vendor.name} - ${self.amount}"
        return f"Payment: ${self.amount} ({self.payment_type})"
    
    def save(self, *args, **kwargs):
        # Auto-calculate remaining amount if original amount is set
        if self.original_amount and not self.remaining_amount:
            self.remaining_amount = self.original_amount - self.amount
        
        # Update status based on amounts
        if self.original_amount:
            if self.amount >= self.original_amount:
                self.status = self.COMPLETED
            elif self.amount > 0:
                self.status = self.PARTIAL
            else:
                self.status = self.PENDING
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-payment_date']
