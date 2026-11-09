from decimal import Decimal
from django.core.validators import MinValueValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sales', '0005_alter_saleitem_product'),
    ]

    operations = [
        migrations.RenameField(
            model_name='saleitem',
            old_name='quantity_dozens',
            new_name='quantity',
        ),
        migrations.AlterField(
            model_name='saleitem',
            name='quantity',
            field=models.DecimalField(decimal_places=2, max_digits=12, validators=[MinValueValidator(Decimal('0.01'))]),
        ),
    ]
