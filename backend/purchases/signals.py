from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchase, PurchaseItem
from vendors.models import VendorTransaction
from products.models import ProductHistory

@receiver(post_save, sender=Purchase)
def create_vendor_transaction_on_purchase(sender, instance, created, **kwargs):
    """Create vendor transaction when a purchase is created"""
    if created:
        VendorTransaction.objects.create(
            vendor=instance.vendor,
            type=VendorTransaction.PURCHASE,
            amount=instance.total_amount,
            reference=f"Purchase #{instance.id}",
            notes=f"Purchase invoice: {instance.invoice_number}"
        )

@receiver(post_save, sender=PurchaseItem)
def update_product_stock_on_purchase(sender, instance, created, **kwargs):
    """Update product stock when a purchase item is created"""
    if created:
        product = instance.product
        # Increase stock
        product.quantity += instance.quantity
        product.save()
        
        # Create product history record
        ProductHistory.objects.create(
            product=product,
            change_type=ProductHistory.PURCHASE,
            quantity_change=instance.quantity,  # Positive for increase
            reference=f"Purchase #{instance.purchase.id}",
            notes=f"Purchase from {instance.purchase.vendor.name}"
        ) 