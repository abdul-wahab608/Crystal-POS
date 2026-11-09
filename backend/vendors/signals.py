from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Vendor, VendorTransaction


@receiver(post_save, sender=VendorTransaction)
def update_vendor_balance(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.type == VendorTransaction.PURCHASE:
        Vendor.objects.filter(pk=instance.vendor_id).update(balance=F('balance') + instance.amount)
    elif instance.type == VendorTransaction.PAYMENT:
        Vendor.objects.filter(pk=instance.vendor_id).update(balance=F('balance') - instance.amount)
