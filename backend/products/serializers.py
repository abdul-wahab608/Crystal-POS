from rest_framework import serializers
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
        fields = ['id', 'product', 'size_range', 'size_range_name', 'color', 'color_name', 'quantity_dozens', 'created_at']

class ProductSerializer(serializers.ModelSerializer):
    size_range_name = serializers.CharField(source='size_range.name', read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit', 'cop', 'quantity', 'product_type', 'size_range', 'size_range_name', 'variants', 'last_updated', 'created_at']

class ProductHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHistory
        fields = '__all__'