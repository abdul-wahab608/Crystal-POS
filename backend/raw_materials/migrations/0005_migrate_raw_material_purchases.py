from decimal import Decimal
from django.db import migrations
from django.db.models import Sum


def move_raw_purchases_into_purchases(apps, schema_editor):
    RawMaterial = apps.get_model('raw_materials', 'RawMaterial')
    RawMaterialPurchase = apps.get_model('raw_materials', 'RawMaterialPurchase')
    RawMaterialUsage = apps.get_model('raw_materials', 'RawMaterialUsage')
    Vendor = apps.get_model('vendors', 'Vendor')
    VendorTransaction = apps.get_model('vendors', 'VendorTransaction')
    Purchase = apps.get_model('purchases', 'Purchase')
    PurchaseItem = apps.get_model('purchases', 'PurchaseItem')
    Payment = apps.get_model('payments', 'Payment')

    for old in RawMaterialPurchase.objects.select_related('raw_material').order_by('purchase_date', 'pk'):
        supplier = (old.supplier or '').strip()
        vendor = Vendor.objects.filter(name=supplier).first() if supplier else None
        if vendor is None:
            vendor, _ = Vendor.objects.get_or_create(name='Unknown supplier')
        purchase = Purchase.objects.create(
            vendor=vendor,
            invoice_number=old.invoice_number or '',
            total_amount=old.total_amount,
        )
        Purchase.objects.filter(pk=purchase.pk).update(date=old.purchase_date)
        PurchaseItem.objects.create(
            purchase=purchase,
            raw_material=old.raw_material,
            quantity=old.quantity_purchased,
            unit_cost=old.unit_price,
            subtotal=old.total_amount,
        )
        VendorTransaction.objects.filter(
            vendor=vendor, type='PURCHASE', reference=f'Raw purchase #{old.pk}',
        ).update(reference=f'Purchase #{purchase.pk}')
        Payment.objects.filter(purchase_id=old.pk).update(purchase_v2=purchase)

    for material in RawMaterial.objects.all():
        purchased = RawMaterialPurchase.objects.filter(raw_material=material).aggregate(
            total=Sum('quantity_purchased'))['total'] or Decimal('0')
        used = RawMaterialUsage.objects.filter(raw_material=material).aggregate(
            total=Sum('quantity_used'))['total'] or Decimal('0')
        material.quantity = material.quantity + purchased - used
        material.save(update_fields=['quantity'])


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0004_remove_rawmaterialpurchase_payment'),
        ('purchases', '0005_purchase_invoice_and_raw_lines'),
        ('payments', '0005_payment_purchase_v2'),
        ('vendors', '0002_vendor_city_remove_email'),
    ]

    operations = [
        migrations.RunPython(move_raw_purchases_into_purchases, migrations.RunPython.noop),
    ]
