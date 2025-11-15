from rest_framework import serializers
from django.db.models import Sum
from .models import RawMaterial, RawMaterialUsage, RawMaterialPurchase

class RawMaterialSerializer(serializers.ModelSerializer):
    available_stock = serializers.SerializerMethodField()
    needs_reorder = serializers.SerializerMethodField()
    average_unit_price = serializers.SerializerMethodField()
    
    class Meta:
        model = RawMaterial
        fields = [
            'id', 'name', 'unit', 'quantity', 'available_stock',
            'reorder_level', 'needs_reorder', 'average_unit_price',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'available_stock', 'needs_reorder', 'average_unit_price', 'created_at', 'updated_at']

    def get_available_stock(self, obj):
        """Calculate available stock: original + purchases - usage"""
        return obj.available_stock

    def get_needs_reorder(self, obj):
        """Check if material needs reordering"""
        return obj.needs_reorder
    
    def get_average_unit_price(self, obj):
        """Get average unit price from recent purchases"""
        return obj.average_unit_price


class RawMaterialUsageSerializer(serializers.ModelSerializer):
    raw_material_name = serializers.CharField(source='raw_material.name', read_only=True)
    
    class Meta:
        model = RawMaterialUsage
        fields = ['id', 'raw_material', 'quantity_used', 'reference', 'notes', 'date_used']
        read_only_fields = ['id', 'date_used']

class RawMaterialUsageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterialUsage
        fields = ['raw_material', 'quantity_used', 'reference', 'notes']

class RawMaterialPurchaseSerializer(serializers.ModelSerializer):
    raw_material = RawMaterialSerializer(read_only=True)
    
    class Meta:
        model = RawMaterialPurchase
        fields = [
            'id', 'raw_material', 'quantity_purchased', 'unit_price', 
            'total_amount', 'supplier', 'invoice_number', 'notes', 'purchase_date'
        ]
        read_only_fields = ['id', 'total_amount', 'purchase_date']

class RawMaterialPurchaseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterialPurchase
        fields = [
            'raw_material', 'quantity_purchased', 'unit_price', 
            'supplier', 'invoice_number', 'notes'
        ] 