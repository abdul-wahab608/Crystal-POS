from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import migrations, models


QUANTITY_VALIDATORS = [MinValueValidator(Decimal('0'))]


def copy_size_range_to_m2m(apps, schema_editor):
    Product = apps.get_model('products', 'Product')
    for product in Product.objects.all():
        product.size_ranges.add(product.size_range_id)


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_product_unit'),
    ]

    operations = [
        migrations.RenameField(
            model_name='productvariant',
            old_name='quantity_dozens',
            new_name='quantity',
        ),
        migrations.AlterField(
            model_name='productvariant',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=QUANTITY_VALIDATORS),
        ),
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=12, validators=QUANTITY_VALIDATORS),
        ),
        migrations.AlterField(
            model_name='producthistory',
            name='change_type',
            field=models.CharField(choices=[('SALE', 'Sale'), ('PURCHASE', 'Purchase'), ('ADJUSTMENT', 'Adjustment'), ('PRODUCTION', 'Production')], max_length=15),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('name', 'unit')},
        ),
        migrations.AddField(
            model_name='product',
            name='size_ranges',
            field=models.ManyToManyField(blank=True, related_name='+', to='products.sizerange'),
        ),
        migrations.RunPython(copy_size_range_to_m2m, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='product',
            name='size_range',
        ),
        migrations.AlterField(
            model_name='product',
            name='size_ranges',
            field=models.ManyToManyField(blank=True, related_name='products', to='products.sizerange'),
        ),
    ]
