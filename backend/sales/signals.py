from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale
from customers.models import CustomerTransaction

@receiver(post_save, sender=Sale)
def create_customer_transaction_on_sale(sender, instance, created, **kwargs):
    """Create customer transaction when a sale is created"""
    if created:
        CustomerTransaction.objects.create(
            customer=instance.customer,
            type=CustomerTransaction.SALE,
            amount=instance.total_amount,
            reference=f"Sale #{instance.id}",
            # instance.bill_no isn't assigned yet at post_save time (Sale.save() sets it via a
            # follow-up .update() after the initial insert) — derive it the same way the model does.
            notes=f"Sale receipt: BILL-{instance.pk:04d}"
        )

# Stock deduction for sale items is handled directly in SaleSerializer.create(),
# which is variant-aware (adjusts ProductVariant.quantity_dozens and Product.quantity).
# A duplicate post_save(SaleItem) signal here would double-deduct stock. 