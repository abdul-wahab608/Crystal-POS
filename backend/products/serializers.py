from rest_framework import serializers
from .models import Product, ProductHistory

class ProductSerializer(serializers.ModelSerializer):
    available_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'unit', 'cop', 'quantity', 'product_type', 'available_stock', 'last_updated', 'created_at']

class ProductHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductHistory
        fields = '__all__' 