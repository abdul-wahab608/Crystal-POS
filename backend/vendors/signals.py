from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VendorTransaction, adjust_vendor_balance


@receiver(post_save, sender=VendorTransaction)
def update_vendor_balance(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.type == VendorTransaction.PURCHASE:
        adjust_vendor_balance(instance.vendor_id, instance.amount)
    elif instance.type == VendorTransaction.PAYMENT:
        adjust_vendor_balance(instance.vendor_id, -instance.amount)
