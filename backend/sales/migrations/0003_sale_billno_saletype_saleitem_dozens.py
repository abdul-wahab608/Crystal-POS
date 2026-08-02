from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0002_initial'),
    ]

    operations = [
        # Add bill_no to Sale
        migrations.AddField(
            model_name='sale',
            name='bill_no',
            field=models.CharField(blank=True, max_length=20, default=''),
        ),
        migrations.AlterField(
            model_name='sale',
            name='bill_no',
            field=models.CharField(blank=True, max_length=20),
        ),
        # Add unique constraint after populating (done in data migration below)
        # Add sale_type to Sale
        migrations.AddField(
            model_name='sale',
            name='sale_type',
            field=models.CharField(
                choices=[('WALK_IN', 'Walk-in'), ('PHONE_ORDER', 'Phone Order'), ('REGULAR', 'Regular')],
                default='REGULAR',
                max_length=20,
            ),
        ),
        # Add payment_status if not already present
        migrations.AddField(
            model_name='sale',
            name='payment_status',
            field=models.CharField(
                choices=[('PAID', 'Paid'), ('PARTIAL', 'Partial'), ('UNPAID', 'Unpaid')],
                default='UNPAID',
                max_length=10,
            ),
            preserve_default=False,
        ),
        # Add quantity_dozens to SaleItem
        migrations.AddField(
            model_name='saleitem',
            name='quantity_dozens',
            field=models.PositiveIntegerField(default=0),
        ),
        # Remove old quantity field
        migrations.RemoveField(
            model_name='saleitem',
            name='quantity',
        ),
    ]
