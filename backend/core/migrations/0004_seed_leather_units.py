from django.db import migrations

LEATHER_UNITS = [('SQFT', 'Square Feet'), ('METER', 'Meters (length)')]


def seed_units(apps, schema_editor):
    Unit = apps.get_model('core', 'Unit')
    for code, name in LEATHER_UNITS:
        Unit.objects.get_or_create(code=code, defaults={'name': name, 'is_system': True})


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_seed_pair_unit'),
    ]

    operations = [
        migrations.RunPython(seed_units, migrations.RunPython.noop),
    ]
