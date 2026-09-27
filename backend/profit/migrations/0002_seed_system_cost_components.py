from django.db import migrations

SYSTEM_COMPONENTS = ['Raw Material', 'Electricity', 'Labor', 'Misc']


def seed_components(apps, schema_editor):
    CostComponentType = apps.get_model('profit', 'CostComponentType')
    for name in SYSTEM_COMPONENTS:
        CostComponentType.objects.get_or_create(name=name, defaults={'is_system': True})


def unseed_components(apps, schema_editor):
    CostComponentType = apps.get_model('profit', 'CostComponentType')
    CostComponentType.objects.filter(name__in=SYSTEM_COMPONENTS, is_system=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('profit', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_components, unseed_components),
    ]
