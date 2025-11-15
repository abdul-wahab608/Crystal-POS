from rest_framework import serializers
from .models import Sale, SaleItem
from products.models import Product
from django.db import transaction

class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = ['id', 'product', 'product_name', 'quantity', 'unit_price', 'subtotal']

class SaleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    items_count = serializers.SerializerMethodField()
    items = serializers.ListField(write_only=True, required=False)
    sale_items = SaleItemSerializer(many=True, read_only=True, source='items')
    
    class Meta:
        model = Sale
        fields = ['id', 'customer', 'customer_name', 'date', 'total_amount', 'payment_status', 
                 'receipt_number', 'created_by', 'items_count', 'items', 'sale_items']
        read_only_fields = ['receipt_number', 'created_by', 'date']
    
    def get_items_count(self, obj):
        return obj.items.count()
    
    def validate_items(self, value):
        """Validate that all items have sufficient stock"""
        if not value:
            raise serializers.ValidationError("At least one item is required.")
        
        for item in value:
            product_id = item.get('product_id')
            quantity = item.get('quantity')
            unit_price = item.get('unit_price')
            
            if not product_id or not quantity:
                raise serializers.ValidationError("Each item must have product_id and quantity.")
            
            if unit_price is None or unit_price < 0:
                raise serializers.ValidationError("Each item must have a valid unit_price.")
            
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with id {product_id} does not exist.")
            
            # Check available stock
            if quantity > product.available_stock:
                raise serializers.ValidationError(
                    f"Insufficient stock for {product.name}. "
                    f"Requested: {quantity}, Available: {product.available_stock}"
                )
        
        return value
    
    @transaction.atomic
    def create(self, validated_data):
            items_data = validated_data.pop('items', [])
            user = self.context["request"].user  # Ensure created_by is saved

            sale = Sale.objects.create(created_by=user, **validated_data)

            for item_data in items_data:
                product_id = item_data['product_id']
                quantity = item_data['quantity']
                unit_price = item_data.get('unit_price', 0)
                product = Product.objects.get(id=product_id)

                if quantity > product.available_stock:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. "
                        f"Requested: {quantity}, Available: {product.available_stock}"
                    )

                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=unit_price * quantity
                )

                # Deduct stock here if not already handled elsewhere:
                product.quantity -= quantity
                product.save()

            return sale