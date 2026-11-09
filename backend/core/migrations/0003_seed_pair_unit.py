from django.db import migrations


def seed_pair(apps, schema_editor):
    Unit = apps.get_model('core', 'Unit')
    Unit.objects.get_or_create(code='PAIR', defaults={'name': 'Pairs', 'is_system': True})


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_seed_system_units'),
    ]

    operations = [
        migrations.RunPython(seed_pair, migrations.RunPython.noop),
    ]
