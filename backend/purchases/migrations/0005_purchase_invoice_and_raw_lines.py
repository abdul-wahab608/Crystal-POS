import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0004_purchaseitem_color_purchaseitem_size_range'),
        ('products', '0006_quantity_and_size_ranges'),
        ('raw_materials', '0004_remove_rawmaterialpurchase_payment'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='invoice_number',
            field=models.CharField(blank=True, default='', max_length=50),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='product',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='products.product'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='size_range',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='products.sizerange'),
        ),
        migrations.AlterField(
            model_name='purchaseitem',
            name='color',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='products.color'),
        ),
        migrations.AddField(
            model_name='purchaseitem',
            name='raw_material',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='raw_materials.rawmaterial'),
        ),
        migrations.AddConstraint(
            model_name='purchaseitem',
            constraint=models.CheckConstraint(
                condition=(
                    Q(product__isnull=False, raw_material__isnull=True)
                    | Q(product__isnull=True, raw_material__isnull=False)
                ),
                name='purchaseitem_exactly_one_target',
            ),
        ),
    ]
