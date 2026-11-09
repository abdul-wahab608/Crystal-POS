from rest_framework import serializers
from .models import RawMaterial, RawMaterialUsage


class RawMaterialSerializer(serializers.ModelSerializer):
    needs_reorder = serializers.BooleanField(read_only=True)

    class Meta:
        model = RawMaterial
        fields = [
            'id', 'name', 'unit', 'quantity', 'reorder_level', 'needs_reorder', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'needs_reorder', 'created_at', 'updated_at']

    def update(self, instance, validated_data):
        validated_data.pop('quantity', None)
        return super().update(instance, validated_data)


class RawMaterialUsageSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)

    class Meta:
        model = RawMaterialUsage
        fields = ['id', 'raw_material', 'raw_material_name', 'quantity_used', 'reference', 'notes', 'date_used']
        read_only_fields = ['id', 'date_used']
