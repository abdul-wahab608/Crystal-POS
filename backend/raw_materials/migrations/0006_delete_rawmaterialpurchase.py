from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('raw_materials', '0005_migrate_raw_material_purchases'),
        ('payments', '0006_payment_purchase'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RawMaterialPurchase',
        ),
    ]
