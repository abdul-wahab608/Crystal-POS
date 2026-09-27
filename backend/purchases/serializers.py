from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Purchase, PurchaseItem

class PurchaseItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = PurchaseItem
        fields = '__all__'

class PurchaseSerializer(serializers.ModelSerializer):
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)
    items = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Purchase
        fields = '__all__'

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['items'] = PurchaseItemSerializer(instance.items.all(), many=True).data
        return rep

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        purchase = Purchase.objects.create(**validated_data)
        for item_data in items_data:
            quantity = Decimal(str(item_data['quantity']))
            unit_cost = Decimal(str(item_data['unit_cost']))
            PurchaseItem.objects.create(
                purchase=purchase,
                product_id=item_data['product'],
                quantity=quantity,
                unit_cost=unit_cost,
                subtotal=quantity * unit_cost,
            )
        return purchase
