from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Payment
from sales.models import Sale
from raw_materials.models import RawMaterialPurchase

@receiver(post_save, sender=Sale)
def create_sale_payment(sender, instance, created, **kwargs):
    """Automatically create payment record when a sale is created"""
    if created:
        Payment.objects.create(
            payment_type=Payment.INCOMING,
            payment_method=Payment.CASH,  # Default, can be updated later
            amount=instance.total_amount,
            status=Payment.PENDING,
            customer=instance.customer,
            sale=instance,
            original_amount=instance.total_amount,
            remaining_amount=instance.total_amount,
            reference=f"Sale #{instance.receipt_number}",
            notes=f"Auto-generated payment for sale {instance.receipt_number}"
        )

@receiver(post_save, sender=RawMaterialPurchase)
def create_purchase_payment(sender, instance, created, **kwargs):
    """Automatically create payment record when a purchase is created"""
    if created:
        Payment.objects.create(
            payment_type=Payment.OUTGOING,
            payment_method=Payment.CASH,  # Default, can be updated later
            amount=instance.total_amount,
            status=Payment.PENDING,
            vendor_id=instance.supplier,  # Note: This assumes supplier is a vendor ID
            purchase=instance,
            original_amount=instance.total_amount,
            remaining_amount=instance.total_amount,
            reference=f"Purchase #{instance.id}",
            notes=f"Auto-generated payment for purchase of {instance.raw_material.name}"
        ) 