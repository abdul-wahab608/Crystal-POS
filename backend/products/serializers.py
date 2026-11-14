from decimal import Decimal

from django.db import transaction
from django.db.models import F, ProtectedError
from django.utils import timezone
from rest_framework import serializers
from profit.services import CostLookup
from .models import Product, ProductHistory, SizeRange, Color, ProductVariant


class SizeRangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SizeRange
        fields = ['id', 'name', 'created_at']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'created_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    size_range_name = serializers.CharField(source='size_range.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'product', 'size_range', 'size_range_name', 'color', 'color_name', 'quantity', 'created_at']

    def validate(self, attrs):
        product = attrs.get('product') or self.instance.product
        size_range = attrs.get('size_range') or self.instance.size_range
        if not product.size_ranges.filter(pk=size_range.pk).exists():
            raise serializers.ValidationError({'size_range': f'"{size_range.name}" is not a size range of {product.name}.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        variant = super().create(validated_data)
        Product.objects.filter(pk=variant.product_id).update(quantity=F('quantity') + variant.quantity)
        return variant

    @transaction.atomic
    def update(self, instance, validated_data):
        old_quantity = instance.quantity
        variant = super().update(instance, validated_data)
        Product.objects.filter(pk=variant.product_id).update(quantity=F('quantity') + variant.quantity - old_quantity)
        return variant


class VariantLineSerializer(serializers.ModelSerializer):
    size_range_name = serializers.CharField(source='size_range.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = ProductVariant
        fields = ['id', 'size_range', 'size_range_name', 'color', 'color_name', 'quantity']


class ProductSerializer(serializers.ModelSerializer):
    size_ranges = serializers.PrimaryKeyRelatedField(many=True, queryset=SizeRange.objects.all(), required=False)
    variants = VariantLineSerializer(many=True, required=False)
    cost_source = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'unit', 'cop', 'cost_source', 'quantity', 'product_type', 'size_ranges', 'variants', 'last_updated', 'created_at']
        extra_kwargs = {'cop': {'required': False, 'default': 0, 'min_value': 0}}

    def get_cost_source(self, obj):
        lookup = self.context.get('cost_lookup') or CostLookup([obj.pk])
        return lookup.resolve(obj.pk, timezone.localdate())[1]

    def validate_size_ranges(self, value):
        if len(value) > 3:
            raise serializers.ValidationError('A product can have at most 3 size ranges.')
        return value

    def validate(self, attrs):
        if 'size_ranges' in attrs:
            allowed = {size_range.pk for size_range in attrs['size_ranges']}
        elif self.instance is not None:
            allowed = set(self.instance.size_ranges.values_list('pk', flat=True))
        else:
            allowed = set()

        variants = attrs.get('variants')
        if variants is not None:
            seen = set()
            for line in variants:
                size_range = line['size_range']
                if size_range.pk not in allowed:
                    raise serializers.ValidationError({'variants': f'"{size_range.name}" is not one of this product\'s size ranges.'})
                key = (size_range.pk, line['color'].pk)
                if key in seen:
                    raise serializers.ValidationError({'variants': 'Each size range and color can appear only once.'})
                seen.add(key)
        elif self.instance is not None and 'size_ranges' in attrs:
            if self.instance.variants.exclude(size_range_id__in=allowed).exists():
                raise serializers.ValidationError({'size_ranges': 'Remove the variants of a size range before removing the size range.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        size_ranges = validated_data.pop('size_ranges', [])
        variants = validated_data.pop('variants', None)
        product = Product.objects.create(**validated_data)
        product.size_ranges.set(size_ranges)
        if variants is not None:
            self._write_variants(product, variants)
        if product.quantity:
            ProductHistory.objects.create(
                product=product,
                change_type=ProductHistory.OPENING,
                quantity_change=product.quantity,
                reference='Opening stock',
            )
        return product

    @transaction.atomic
    def update(self, instance, validated_data):
        size_ranges = validated_data.pop('size_ranges', None)
        variants = validated_data.pop('variants', None)
        validated_data.pop('quantity', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if size_ranges is not None:
            instance.size_ranges.set(size_ranges)
        if variants is not None:
            self._write_variants(instance, variants)
        return instance

    def _write_variants(self, product, lines):
        wanted = {(line['size_range'].pk, line['color'].pk): line for line in lines}
        existing = {(v.size_range_id, v.color_id): v for v in ProductVariant.objects.filter(product=product)}
        try:
            for key, variant in existing.items():
                if key not in wanted:
                    variant.delete()
        except ProtectedError:
            raise serializers.ValidationError({'variants': 'A size and color already used in production cannot be removed.'})
        for key, line in wanted.items():
            if key in existing:
                existing[key].quantity = line['quantity']
                existing[key].save(update_fields=['quantity'])
            else:
                ProductVariant.objects.create(
                    product=product,
                    size_range=line['size_range'],
                    color=line['color'],
                    quantity=line['quantity'],
                )
        if lines or existing:
            product.quantity = sum((line['quantity'] for line in lines), Decimal('0'))
            product.save(update_fields=['quantity', 'last_updated'])


class ProductHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHistory
        fields = '__all__'
