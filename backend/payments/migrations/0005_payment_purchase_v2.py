import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0004_alter_payment_payment_date'),
        ('purchases', '0005_purchase_invoice_and_raw_lines'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='purchase_v2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='purchases.purchase'),
        ),
    ]
