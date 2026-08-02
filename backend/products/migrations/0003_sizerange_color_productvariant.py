from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """
    Creates SizeRange, Color, and ProductVariant tables and adds size_range FK to Product.
    """

    dependencies = [
        ('products', '0002_add_productvariant'),
    ]

    operations = [
        migrations.CreateModel(
            name='SizeRange',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='product',
            name='size_range',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='products',
                to='products.sizerange',
                null=True,
                blank=True,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='product',
            unique_together={('name', 'unit', 'size_range')},
        ),
        migrations.CreateModel(
            name='ProductVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_dozens', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('color', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.color')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.product')),
                ('size_range', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='products.sizerange')),
            ],
            options={
                'unique_together': {('product', 'size_range', 'color')},
            },
        ),
    ]
