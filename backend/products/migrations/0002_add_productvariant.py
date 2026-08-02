from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='product_type',
            field=models.CharField(
                choices=[('MANUFACTURED', 'Manufactured Product'), ('PURCHASED', 'Purchased Item')],
                default='MANUFACTURED',
                max_length=20,
            ),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='ProductHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_type', models.CharField(choices=[('SALE', 'Sale'), ('PURCHASE', 'Purchase'), ('ADJUSTMENT', 'Adjustment')], max_length=15)),
                ('quantity_change', models.DecimalField(decimal_places=2, max_digits=12)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reference', models.CharField(blank=True, max_length=255, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='history', to='products.product')),
            ],
        ),
    ]
