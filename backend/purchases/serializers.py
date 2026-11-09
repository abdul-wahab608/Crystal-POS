from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from products.models import Color, Product, SizeRange
from raw_materials.models import RawMaterial
from .models import Purchase, PurchaseItem


class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True, default=None)
    size_range_name = serializers.CharField(source='size_range.name', read_only=True, default=None)
    color_name = serializers.CharField(source='color.name', read_only=True, default=None)
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True, default=None)
    unit = serializers.SerializerMethodField()

    class Meta:
        model = PurchaseItem
        fields = [
            'id', 'product', 'product_name', 'size_range', 'size_range_name', 'color', 'color_name',
            'raw_material', 'raw_material_name', 'unit', 'quantity', 'unit_cost', 'subtotal',
        ]

    def get_unit(self, obj):
        if obj.raw_material_id:
            return obj.raw_material.unit
        return obj.product.unit


class PurchaseLineSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=False, allow_null=True)
    size_range = serializers.PrimaryKeyRelatedField(queryset=SizeRange.objects.all(), required=False, allow_null=True)
    color = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), required=False, allow_null=True)
    raw_material = serializers.PrimaryKeyRelatedField(queryset=RawMaterial.objects.all(), required=False, allow_null=True)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    unit_cost = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0'))

    def validate(self, attrs):
        product = attrs.get('product')
        raw_material = attrs.get('raw_material')
        if (product is None) == (raw_material is None):
            raise serializers.ValidationError('Each line must be exactly one of a product or a raw material.')
        if raw_material is not None:
            if attrs.get('size_range') or attrs.get('color'):
                raise serializers.ValidationError('Raw material lines cannot have a size range or color.')
            return attrs
        if attrs.get('size_range') is None or attrs.get('color') is None:
            raise serializers.ValidationError('Product lines need a size range and a color.')
        if not product.size_ranges.filter(pk=attrs['size_range'].pk).exists():
            raise serializers.ValidationError(
                f'"{attrs["size_range"].name}" is not a size range of {product.name}.'
            )
        return attrs


class PurchaseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    items = PurchaseLineSerializer(many=True, write_only=True, min_length=1)
    paid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    unpaid_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    payment_status = serializers.CharField(read_only=True)

    class Meta:
        model = Purchase
        fields = [
            'id', 'vendor', 'vendor_name', 'date', 'invoice_number', 'total_amount', 'created_by', 'items',
            'paid_amount', 'unpaid_amount', 'payment_status',
        ]
        read_only_fields = ['date', 'total_amount', 'created_by']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['items'] = PurchaseItemSerializer(instance.items.all(), many=True).data
        return rep

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        subtotals = [line['quantity'] * line['unit_cost'] for line in items_data]
        purchase = Purchase.objects.create(total_amount=sum(subtotals, Decimal('0')), **validated_data)
        for line, subtotal in zip(items_data, subtotals):
            PurchaseItem.objects.create(
                purchase=purchase,
                product=line.get('product'),
                size_range=line.get('size_range'),
                color=line.get('color'),
                raw_material=line.get('raw_material'),
                quantity=line['quantity'],
                unit_cost=line['unit_cost'],
                subtotal=subtotal,
            )
        return purchase
