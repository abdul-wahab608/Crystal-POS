from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_payment_purchase_v2'),
        ('raw_materials', '0005_migrate_raw_material_purchases'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='payment',
            name='purchase',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='purchase_v2',
            new_name='purchase',
        ),
    ]
