from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import RawMaterial, RawMaterialUsage


@receiver(post_save, sender=RawMaterialUsage)
def deduct_stock_on_usage(sender, instance, created, **kwargs):
    if created:
        RawMaterial.objects.filter(pk=instance.raw_material_id).update(quantity=F('quantity') - instance.quantity_used)


@receiver(post_delete, sender=RawMaterialUsage)
def restore_stock_on_usage_delete(sender, instance, **kwargs):
    RawMaterial.objects.filter(pk=instance.raw_material_id).update(quantity=F('quantity') + instance.quantity_used)
