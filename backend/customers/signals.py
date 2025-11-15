from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomerTransaction
from decimal import Decimal

@receiver(post_save, sender=CustomerTransaction)
def update_customer_balance(sender, instance, created, **kwargs):
    """Update customer balance when a transaction is created or updated"""
    if created:
        customer = instance.customer
        if instance.type == CustomerTransaction.SALE:
            # Sale increases customer balance (they owe us money)
            customer.balance += instance.amount
        elif instance.type == CustomerTransaction.PAYMENT:
            # Payment decreases customer balance (they paid us)
            customer.balance -= instance.amount
        customer.save() 