from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VendorTransaction

@receiver(post_save, sender=VendorTransaction)
def update_vendor_balance(sender, instance, created, **kwargs):
    """Update vendor balance when a transaction is created or updated"""
    if created:
        vendor = instance.vendor
        if instance.type == VendorTransaction.PURCHASE:
            # Purchase increases vendor balance (we owe them money)
            vendor.balance += instance.amount
        elif instance.type == VendorTransaction.PAYMENT:
            # Payment decreases vendor balance (we paid them)
            vendor.balance -= instance.amount
        vendor.save() 