from rest_framework import serializers
from .models import Vendor, VendorTransaction, VendorProduct


class VendorProductSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField()
    item_unit = serializers.ReadOnlyField()
    vendor_name = serializers.CharField(source='vendor.name', read_only=True)

    class Meta:
        model = VendorProduct
        fields = [
            'id', 'vendor', 'vendor_name', 'product_type', 'product', 'raw_material',
            'item_name', 'item_unit', 'unit_price', 'minimum_order_quantity',
            'lead_time_days', 'is_preferred', 'is_active', 'notes',
            'last_purchase_date', 'last_purchase_price', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'last_purchase_date', 'last_purchase_price', 'created_at', 'updated_at']

    def validate(self, attrs):
        instance = self.instance
        product_type = attrs.get('product_type', getattr(instance, 'product_type', None))
        product = attrs.get('product', getattr(instance, 'product', None))
        raw_material = attrs.get('raw_material', getattr(instance, 'raw_material', None))
        if product_type == 'PRODUCT' and (product is None or raw_material is not None):
            raise serializers.ValidationError('A finished-product entry needs a product and no raw material.')
        if product_type == 'RAW_MATERIAL' and (raw_material is None or product is not None):
            raise serializers.ValidationError('A raw-material entry needs a raw material and no product.')
        return attrs


class VendorSerializer(serializers.ModelSerializer):
    vendor_products = VendorProductSerializer(many=True, read_only=True)
    total_products_count = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = [
            'id', 'name', 'phone', 'address', 'city', 'contact_person',
            'balance', 'is_active', 'created_at', 'updated_at',
            'vendor_products', 'total_products_count'
        ]

    def get_total_products_count(self, obj):
        return obj.vendor_products.filter(is_active=True).count()

    def update(self, instance, validated_data):
        validated_data.pop('balance', None)
        return super().update(instance, validated_data)


class VendorTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorTransaction
        fields = '__all__'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value
