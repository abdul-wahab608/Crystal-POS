from rest_framework import serializers
from django.db import transaction
from .models import RawMaterial, RawMaterialHistory, RawMaterialUsage


class RawMaterialSerializer(serializers.ModelSerializer):
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = RawMaterial
        fields = [
            'id', 'name', 'unit', 'quantity', 'reorder_level', 'needs_reorder', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'needs_reorder', 'created_at', 'updated_at']

    @transaction.atomic
    def create(self, validated_data):
        material = super().create(validated_data)
        if material.quantity:
            RawMaterialHistory.objects.create(
                raw_material=material,
                change_type=RawMaterialHistory.OPENING,
                quantity_change=material.quantity,
                reference='Opening stock',
            )
        return material

    def update(self, instance, validated_data):
        validated_data.pop('quantity', None)
        return super().update(instance, validated_data)


class RawMaterialUsageSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)

    class Meta:
        model = RawMaterialUsage
        fields = ['id', 'raw_material', 'raw_material_name', 'quantity_used', 'reference', 'notes', 'date_used']
        read_only_fields = ['id', 'date_used']
