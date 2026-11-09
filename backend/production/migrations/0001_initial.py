import decimal
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('products', '0006_quantity_and_size_ranges'),
        ('raw_materials', '0006_delete_rawmaterialpurchase'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionRun',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('reference', models.CharField(blank=True, max_length=100)),
                ('notes', models.TextField(blank=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionRunItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'))])),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='production.productionrun')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='production_items', to='products.productvariant')),
            ],
        ),
        migrations.CreateModel(
            name='ProductionRunInput',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(decimal.Decimal('0.01'))])),
                ('raw_material', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='production_inputs', to='raw_materials.rawmaterial')),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inputs', to='production.productionrun')),
            ],
        ),
    ]
