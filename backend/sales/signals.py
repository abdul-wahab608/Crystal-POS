from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale, SaleItem
from customers.models import CustomerTransaction
from products.models import ProductHistory

@receiver(post_save, sender=Sale)
def create_customer_transaction_on_sale(sender, instance, created, **kwargs):
    """Create customer transaction when a sale is created"""
    if created:
        CustomerTransaction.objects.create(
            customer=instance.customer,
            type=CustomerTransaction.SALE,
            amount=instance.total_amount,
            reference=f"Sale #{instance.id}",
            notes=f"Sale receipt: {instance.receipt_number}"
        )

@receiver(post_save, sender=SaleItem)
def update_product_stock_on_sale(sender, instance, created, **kwargs):
    """Update product stock when a sale item is created"""
    if created:
        product = instance.product
        # Reduce stock
        product.quantity -= instance.quantity
        product.save()
        
        # Create product history record
        ProductHistory.objects.create(
            product=product,
            change_type=ProductHistory.SALE,
            quantity_change=-instance.quantity,  # Negative for reduction
            reference=f"Sale #{instance.sale.id}",
            notes=f"Sale to {instance.sale.customer.name}"
        ) 