from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from customers.models import CustomerTransaction
from vendors.models import VendorTransaction, adjust_vendor_balance
from .models import Payment


def _payment_reference(payment):
    return f"Payment #{payment.pk}"


@receiver(post_save, sender=Payment)
def on_payment_saved(sender, instance, created, **kwargs):
    if created and instance.payment_type == Payment.INCOMING and instance.customer_id:
        CustomerTransaction.objects.create(
            customer_id=instance.customer_id,
            type=CustomerTransaction.PAYMENT,
            amount=instance.amount,
            reference=instance.reference or _payment_reference(instance),
            notes=_payment_reference(instance),
        )
    if created and instance.payment_type == Payment.OUTGOING and instance.vendor_id:
        VendorTransaction.objects.create(
            vendor_id=instance.vendor_id,
            type=VendorTransaction.PAYMENT,
            amount=instance.amount,
            reference=_payment_reference(instance),
            notes=_payment_reference(instance),
        )
    if instance.sale_id:
        instance.sale.sync_payment_status()


@receiver(post_delete, sender=Payment)
def on_payment_deleted(sender, instance, **kwargs):
    if instance.payment_type == Payment.INCOMING and instance.customer_id:
        CustomerTransaction.objects.create(
            customer_id=instance.customer_id,
            type=CustomerTransaction.REVERSAL,
            reverses=CustomerTransaction.PAYMENT,
            amount=instance.amount,
            reference=f"Payment #{instance.pk} reversed",
            notes=f"Reversal of deleted payment #{instance.pk}",
        )
    if instance.payment_type == Payment.OUTGOING and instance.vendor_id:
        VendorTransaction.objects.filter(
            vendor_id=instance.vendor_id,
            type=VendorTransaction.PAYMENT,
            reference=_payment_reference(instance),
        ).delete()
        adjust_vendor_balance(instance.vendor_id, instance.amount)
    if instance.sale_id:
        instance.sale.sync_payment_status()
