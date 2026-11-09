from django.db import migrations

SYSTEM_UNITS = [
    ('BAG', 'Bags'),
    ('BOX', 'Boxes'),
    ('CM', 'Centimeters'),
    ('CUP', 'Cups'),
    ('DOZEN', 'Dozens'),
    ('FOOT', 'Feet'),
    ('GALLON', 'Gallons'),
    ('GRAM', 'Grams'),
    ('INCH', 'Inches'),
    ('KG', 'Kilograms'),
    ('KILO', 'Kilos'),
    ('L', 'Liters'),
    ('M', 'Meters'),
    ('MM', 'Millimeters'),
    ('OUNCE', 'Ounces'),
    ('PACK', 'Packs'),
    ('PCS', 'Pieces'),
    ('POUND', 'Pounds'),
    ('TABLESPOON', 'Tablespoons'),
    ('TEASPOON', 'Teaspoons'),
    ('TON', 'Tons'),
    ('UNIT', 'Units'),
    ('YARD', 'Yards'),
]


def seed_units(apps, schema_editor):
    Unit = apps.get_model('core', 'Unit')
    for code, name in SYSTEM_UNITS:
        Unit.objects.get_or_create(code=code, defaults={'name': name, 'is_system': True})


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_units, migrations.RunPython.noop),
    ]
