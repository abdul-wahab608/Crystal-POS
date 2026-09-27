from rest_framework import serializers
from .models import CostComponentType, ProductCost


class CostComponentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CostComponentType
        fields = ['id', 'name', 'is_system', 'created_at']
        read_only_fields = ['id', 'is_system', 'created_at']


class ProductCostSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    component_type_name = serializers.CharField(source='component_type.name', read_only=True)

    class Meta:
        model = ProductCost
        fields = [
            'id', 'product', 'product_name', 'component_type', 'component_type_name',
            'amount_per_dozen', 'valid_from', 'created_at',
        ]
        read_only_fields = ['id', 'created_at']
