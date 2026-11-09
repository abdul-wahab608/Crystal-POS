from django.db.models import F
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from .models import Purchase, PurchaseItem
from products.models import Product, ProductHistory, ProductVariant
from raw_materials.models import RawMaterial
from vendors.models import Vendor, VendorTransaction


def _purchase_reference(purchase_id):
    return f"Purchase #{purchase_id}"


@receiver(post_save, sender=Purchase)
def create_vendor_transaction_on_purchase(sender, instance, created, **kwargs):
    if created:
        VendorTransaction.objects.create(
            vendor=instance.vendor,
            type=VendorTransaction.PURCHASE,
            amount=instance.total_amount,
            reference=_purchase_reference(instance.id),
            notes=f"Purchase #{instance.id} from {instance.vendor.name}"
        )


@receiver(post_delete, sender=Purchase)
def reverse_vendor_transaction_on_purchase(sender, instance, **kwargs):
    ledger_rows = VendorTransaction.objects.filter(
        vendor_id=instance.vendor_id, type=VendorTransaction.PURCHASE, reference=_purchase_reference(instance.id),
    )
    for row in ledger_rows:
        Vendor.objects.filter(pk=instance.vendor_id).update(balance=F('balance') - row.amount)
    ledger_rows.delete()


@receiver(post_save, sender=PurchaseItem)
def add_stock_on_purchase_line(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.raw_material_id:
        RawMaterial.objects.filter(pk=instance.raw_material_id).update(quantity=F('quantity') + instance.quantity)
        return
    variant, _ = ProductVariant.objects.get_or_create(
        product_id=instance.product_id, size_range_id=instance.size_range_id, color_id=instance.color_id,
    )
    ProductVariant.objects.filter(pk=variant.pk).update(quantity=F('quantity') + instance.quantity)
    Product.objects.filter(pk=instance.product_id).update(quantity=F('quantity') + instance.quantity)
    ProductHistory.objects.create(
        product_id=instance.product_id,
        change_type=ProductHistory.PURCHASE,
        quantity_change=instance.quantity,
        reference=_purchase_reference(instance.purchase_id),
        notes=f"Purchase from {instance.purchase.vendor.name}"
    )


@receiver(post_delete, sender=PurchaseItem)
def remove_stock_on_purchase_line_delete(sender, instance, **kwargs):
    if instance.raw_material_id:
        RawMaterial.objects.filter(pk=instance.raw_material_id).update(quantity=F('quantity') - instance.quantity)
        return
    ProductVariant.objects.filter(
        product_id=instance.product_id, size_range_id=instance.size_range_id, color_id=instance.color_id,
    ).update(quantity=F('quantity') - instance.quantity)
    Product.objects.filter(pk=instance.product_id).update(quantity=F('quantity') - instance.quantity)
    ProductHistory.objects.create(
        product_id=instance.product_id,
        change_type=ProductHistory.ADJUSTMENT,
        quantity_change=-instance.quantity,
        reference=_purchase_reference(instance.purchase_id),
        notes="Reversed: purchase deleted",
    )
