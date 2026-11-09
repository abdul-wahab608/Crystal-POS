from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Customer, CustomerTransaction


@receiver(post_save, sender=CustomerTransaction)
def update_customer_balance(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.type == CustomerTransaction.SALE:
        delta = instance.amount
    elif instance.type == CustomerTransaction.PAYMENT:
        delta = -instance.amount
    elif instance.type == CustomerTransaction.REVERSAL:
        delta = -instance.amount if instance.reverses == CustomerTransaction.SALE else instance.amount
    else:
        return
    Customer.objects.filter(pk=instance.customer_id).update(balance=F('balance') + delta)
