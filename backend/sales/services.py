from collections import defaultdict
from decimal import Decimal
from django.db.models import F
from rest_framework import serializers
from products.models import Product, ProductVariant


def aggregate_lines(lines):
    totals = defaultdict(Decimal)
    for product, size_range, color, quantity in lines:
        totals[(product.pk, size_range.pk, color.pk)] += quantity
    return totals


def reserve_stock(lines):
    labels = {}
    for product, size_range, color, _ in lines:
        labels[(product.pk, size_range.pk, color.pk)] = f'{product.name} ({size_range.name}, {color.name})'

    for key, quantity in aggregate_lines(lines).items():
        product_id, size_range_id, color_id = key
        variant = ProductVariant.objects.select_for_update().filter(
            product_id=product_id, size_range_id=size_range_id, color_id=color_id
        ).first()
        if variant is None:
            raise serializers.ValidationError({'items': f'No stock recorded for {labels[key]}.'})
        if quantity > variant.quantity:
            raise serializers.ValidationError({
                'items': (
                    f'Insufficient stock for {labels[key]}: '
                    f'requested {quantity}, available {variant.quantity}.'
                )
            })


def adjust_stock(product, size_range, color, quantity):
    ProductVariant.objects.filter(
        product=product, size_range=size_range, color=color
    ).update(quantity=F('quantity') - quantity)
    Product.objects.filter(pk=product.pk).update(quantity=F('quantity') - quantity)
