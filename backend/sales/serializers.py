from rest_framework import serializers
from .models import Sale, SaleItem
from products.models import Product, ProductVariant, SizeRange, Color
from django.db import transaction


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    size_range_name = serializers.CharField(source='size_range.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'size_range', 'size_range_name',
            'color', 'color_name', 'quantity_dozens', 'unit_price', 'subtotal'
        ]


class SaleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_city = serializers.CharField(source='customer.city', read_only=True)
    items_count = serializers.SerializerMethodField()
    items = serializers.ListField(write_only=True, required=False)
    sale_items = SaleItemSerializer(many=True, read_only=True, source='items')

    class Meta:
        model = Sale
        fields = [
            'id', 'bill_no', 'sale_type', 'customer', 'customer_name', 'customer_city',
            'date', 'total_amount', 'payment_status', 'created_by',
            'items_count', 'items', 'sale_items'
        ]
        read_only_fields = ['bill_no', 'created_by', 'date']

    def get_items_count(self, obj):
        return obj.items.count()

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        user = self.context['request'].user

        # Resolve and validate all items before any DB writes
        resolved = []
        for item_data in items_data:
            product_id = item_data['product_id']
            size_range_id = item_data.get('size_range_id')
            color_id = item_data.get('color_id')
            quantity_dozens = int(item_data.get('quantity_dozens', item_data.get('quantity', 0)))
            unit_price = item_data.get('unit_price', 0)

            if not color_id:
                raise serializers.ValidationError(
                    {'items': f'color_id is required for product {product_id}.'}
                )

            product = Product.objects.get(id=product_id)
            size_range = SizeRange.objects.get(id=size_range_id) if size_range_id else SizeRange.objects.filter(products=product).first()
            color = Color.objects.get(id=color_id)

            variant = ProductVariant.objects.filter(
                product=product, size_range=size_range, color=color
            ).first()
            if variant and quantity_dozens > variant.quantity_dozens:
                raise serializers.ValidationError({
                    'items': (
                        f'Insufficient stock for {product.name} ({color.name}): '
                        f'requested {quantity_dozens} dozens, available {variant.quantity_dozens}.'
                    )
                })

            resolved.append((product, size_range, color, quantity_dozens, unit_price, variant))

        sale = Sale.objects.create(created_by=user, **validated_data)

        for product, size_range, color, quantity_dozens, unit_price, variant in resolved:
            SaleItem.objects.create(
                sale=sale,
                product=product,
                size_range=size_range,
                color=color,
                quantity_dozens=quantity_dozens,
                unit_price=unit_price,
                subtotal=unit_price * quantity_dozens,
            )

            if variant:
                variant.quantity_dozens -= quantity_dozens
                variant.save()

            product.quantity = max(0, product.quantity - (quantity_dozens * 12))
            product.save()

        return sale