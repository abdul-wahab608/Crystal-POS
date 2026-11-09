from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale
from customers.models import CustomerTransaction

@receiver(post_save, sender=Sale)
def create_customer_transaction_on_sale(sender, instance, created, **kwargs):
    if created:
        CustomerTransaction.objects.create(
            customer=instance.customer,
            type=CustomerTransaction.SALE,
            amount=instance.total_amount,
            reference=f"BILL-{instance.pk:04d}",
            notes=f"Sale receipt: BILL-{instance.pk:04d}"
        )
