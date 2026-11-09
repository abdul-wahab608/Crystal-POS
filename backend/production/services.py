from collections import defaultdict
from decimal import Decimal
from django.db import transaction
from django.db.models import F
from django.utils import timezone
from rest_framework import serializers
from products.models import Product, ProductHistory, ProductVariant
from purchases.models import PurchaseItem
from raw_materials.models import RawMaterial, RawMaterialUsage
from .models import ProductionRun, ProductionRunItem, ProductionRunInput

ZERO = Decimal('0')


def _reference(run):
    return f"Production run #{run.pk}"


def latest_raw_material_unit_costs(raw_material_ids, as_of):
    latest = {}
    rows = (
        PurchaseItem.objects
        .filter(raw_material_id__in=raw_material_ids, purchase__date__date__lte=as_of)
        .order_by('purchase__date', 'id')
        .values_list('raw_material_id', 'unit_cost')
    )
    for raw_material_id, unit_cost in rows:
        latest[raw_material_id] = unit_cost
    return latest


def production_runs_by_product(product_ids):
    wanted = set(product_ids)
    runs = (
        ProductionRun.objects
        .filter(items__variant__product_id__in=wanted)
        .distinct()
        .prefetch_related('items__variant__product', 'inputs')
        .order_by('-date', '-id')
    )
    result = defaultdict(list)
    for run in runs:
        run_date = timezone.localdate(run.date)
        inputs = list(run.inputs.all())
        prices = latest_raw_material_unit_costs({i.raw_material_id for i in inputs}, run_date) if inputs else {}
        input_cost = None
        if inputs and all(i.raw_material_id in prices for i in inputs):
            input_cost = sum((i.quantity * prices[i.raw_material_id] for i in inputs), ZERO)

        outputs = defaultdict(lambda: ZERO)
        units = set()
        for item in run.items.all():
            outputs[item.variant.product_id] += item.quantity
            units.add(item.variant.product.unit)
        total_output = sum(outputs.values(), ZERO)
        # Outputs in different units cannot be compared, so the run cost cannot be split between them.
        # A zero-cost run would be reported as a 100% margin, so it counts as unusable too.
        usable = len(units) == 1 and input_cost is not None and input_cost > ZERO
        for product_id, output_quantity in outputs.items():
            if product_id not in wanted:
                continue
            result[product_id].append({
                'run_id': run.pk,
                'date': run_date,
                'output_quantity': output_quantity,
                'input_cost': input_cost,
                'unit_cost': input_cost / total_output if usable else None,
            })
    return result


@transaction.atomic
def create_run(*, user, reference, notes, items, inputs):
    needed = defaultdict(Decimal)
    for line in inputs:
        needed[line['raw_material'].pk] += line['quantity']
    for raw_material_id, quantity in needed.items():
        material = RawMaterial.objects.select_for_update().get(pk=raw_material_id)
        if material.quantity < quantity:
            raise serializers.ValidationError({
                'inputs': f'Insufficient {material.name}: need {quantity}, have {material.quantity}.'
            })

    run = ProductionRun.objects.create(created_by=user, reference=reference, notes=notes)
    for line in items:
        variant = line['variant']
        ProductionRunItem.objects.create(run=run, variant=variant, quantity=line['quantity'])
        ProductVariant.objects.filter(pk=variant.pk).update(quantity=F('quantity') + line['quantity'])
        Product.objects.filter(pk=variant.product_id).update(quantity=F('quantity') + line['quantity'])
        ProductHistory.objects.create(
            product_id=variant.product_id,
            change_type=ProductHistory.PRODUCTION,
            quantity_change=line['quantity'],
            reference=_reference(run),
            notes=f"{variant}",
        )
    for line in inputs:
        ProductionRunInput.objects.create(run=run, raw_material=line['raw_material'], quantity=line['quantity'])
        RawMaterialUsage.objects.create(
            raw_material=line['raw_material'],
            quantity_used=line['quantity'],
            reference=_reference(run),
            notes=f"Consumed by production run #{run.pk}",
        )
    return run


@transaction.atomic
def delete_run(run):
    for item in run.items.select_related('variant'):
        variant = item.variant
        if variant.quantity < item.quantity:
            raise serializers.ValidationError({
                'detail': 'Stock from this production run has already been sold and cannot be reversed.'
            })
    for item in run.items.select_related('variant'):
        ProductVariant.objects.filter(pk=item.variant_id).update(quantity=F('quantity') - item.quantity)
        Product.objects.filter(pk=item.variant.product_id).update(quantity=F('quantity') - item.quantity)
        ProductHistory.objects.create(
            product_id=item.variant.product_id,
            change_type=ProductHistory.ADJUSTMENT,
            quantity_change=-item.quantity,
            reference=_reference(run),
            notes="Reversed: production run deleted",
        )
    for line in run.inputs.all():
        RawMaterialUsage.objects.filter(raw_material_id=line.raw_material_id, reference=_reference(run)).delete()
    run.delete()
