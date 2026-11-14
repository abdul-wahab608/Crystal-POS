from django.db import migrations, models


def snapshot_existing_input_costs(apps, schema_editor):
    ProductionRunInput = apps.get_model('production', 'ProductionRunInput')
    PurchaseItem = apps.get_model('purchases', 'PurchaseItem')
    for line in ProductionRunInput.objects.select_related('run'):
        latest = (
            PurchaseItem.objects
            .filter(raw_material_id=line.raw_material_id, purchase__date__lte=line.run.date)
            .order_by('-purchase__date', '-id')
            .first()
        )
        if latest is not None:
            line.unit_cost = latest.unit_cost
            line.save(update_fields=['unit_cost'])


class Migration(migrations.Migration):

    dependencies = [
        ('production', '0001_initial'),
        ('purchases', '0005_purchase_invoice_and_raw_lines'),
    ]

    operations = [
        migrations.AddField(
            model_name='productionruninput',
            name='unit_cost',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.RunPython(snapshot_existing_input_costs, migrations.RunPython.noop),
    ]
