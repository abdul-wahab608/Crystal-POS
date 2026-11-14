from rest_framework import serializers
from products.models import ProductVariant
from raw_materials.models import RawMaterial
from .models import ProductionRun, ProductionRunItem, ProductionRunInput
from .services import create_run


class ProductionRunItemSerializer(serializers.ModelSerializer):
    variant = serializers.PrimaryKeyRelatedField(queryset=ProductVariant.objects.select_related('product', 'size_range', 'color'))
    variant_label = serializers.SerializerMethodField()
    unit = serializers.CharField(source='variant.product.unit', read_only=True)

    class Meta:
        model = ProductionRunItem
        fields = ['id', 'variant', 'variant_label', 'unit', 'quantity']

    def get_variant_label(self, obj):
        return str(obj.variant)


class ProductionRunInputSerializer(serializers.ModelSerializer):
    raw_material = serializers.PrimaryKeyRelatedField(queryset=RawMaterial.objects.all())
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)
    unit = serializers.CharField(source='raw_material.unit', read_only=True)

    class Meta:
        model = ProductionRunInput
        fields = ['id', 'raw_material', 'raw_material_name', 'unit', 'quantity']


class ProductionRunSerializer(serializers.ModelSerializer):
    items = ProductionRunItemSerializer(many=True, min_length=1)
    inputs = ProductionRunInputSerializer(many=True, min_length=1)

    class Meta:
        model = ProductionRun
        fields = ['id', 'date', 'reference', 'notes', 'created_by', 'items', 'inputs']
        read_only_fields = ['date', 'created_by']

    def create(self, validated_data):
        items = validated_data.pop('items')
        inputs = validated_data.pop('inputs')
        return create_run(
            user=self.context['request'].user,
            reference=validated_data.get('reference', ''),
            notes=validated_data.get('notes', ''),
            items=[{'variant': i['variant'], 'quantity': i['quantity']} for i in items],
            inputs=[{'raw_material': i['raw_material'], 'quantity': i['quantity']} for i in inputs],
        )
