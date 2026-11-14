from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Sale, SaleItem
from .services import adjust_stock, aggregate_lines, reserve_stock
from payments.models import Payment
from products.models import Product, SizeRange, Color


class SaleItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    size_range_name = serializers.CharField(source='size_range.name', read_only=True)
    color_name = serializers.CharField(source='color.name', read_only=True)

    class Meta:
        model = SaleItem
        fields = [
            'id', 'product', 'product_name', 'size_range', 'size_range_name',
            'color', 'color_name', 'quantity', 'unit_price', 'subtotal'
        ]


class SaleItemInputSerializer(serializers.Serializer):
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    size_range_id = serializers.PrimaryKeyRelatedField(queryset=SizeRange.objects.all(), source='size_range')
    color_id = serializers.PrimaryKeyRelatedField(queryset=Color.objects.all(), source='color')
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    unit_price = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0'))


class SaleSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source='customer.name', read_only=True)
    customer_city = serializers.CharField(source='customer.city', read_only=True)
    items_count = serializers.SerializerMethodField()
    amount_paid = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    items = SaleItemInputSerializer(many=True, write_only=True, required=False)
    sale_items = SaleItemSerializer(many=True, read_only=True, source='items')
    amount_received = serializers.DecimalField(
        max_digits=12, decimal_places=2, min_value=Decimal('0'), write_only=True, required=False
    )
    payment_method = serializers.ChoiceField(
        choices=Payment.PAYMENT_METHOD_CHOICES, write_only=True, required=False
    )

    class Meta:
        model = Sale
        fields = [
            'id', 'bill_no', 'sale_type', 'customer', 'customer_name', 'customer_city',
            'date', 'total_amount', 'payment_status', 'amount_paid', 'balance', 'created_by',
            'items_count', 'items', 'sale_items', 'amount_received', 'payment_method'
        ]
        read_only_fields = ['bill_no', 'created_by', 'date', 'total_amount', 'payment_status']

    def get_items_count(self, obj):
        return obj.items.count()

    def get_amount_paid(self, obj):
        return str(obj.amount_paid().quantize(Decimal('0.01')))

    def get_balance(self, obj):
        return str((obj.total_amount - obj.amount_paid()).quantize(Decimal('0.01')))

    def validate(self, attrs):
        if self.instance is not None:
            for field in ('items', 'amount_received', 'payment_method'):
                if field in attrs:
                    raise serializers.ValidationError({field: 'Cannot be changed after the sale is created.'})
            if 'customer' in attrs and attrs['customer'] != self.instance.customer:
                raise serializers.ValidationError({'customer': 'Cannot be changed after the sale is created.'})
            return attrs

        items = attrs.get('items')
        if not items:
            raise serializers.ValidationError({'items': 'Add at least one product line.'})

        total = sum((i['unit_price'] * i['quantity'] for i in items), Decimal('0'))
        received = attrs.get('amount_received') or Decimal('0')
        if received > total:
            raise serializers.ValidationError({'amount_received': 'Cannot exceed the sale total.'})
        if received > 0 and not attrs.get('payment_method'):
            raise serializers.ValidationError({'payment_method': 'Choose how the amount was received.'})
        return attrs

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        received = validated_data.pop('amount_received', None) or Decimal('0')
        payment_method = validated_data.pop('payment_method', None)
        user = self.context['request'].user

        lines = [(i['product'], i['size_range'], i['color'], i['quantity']) for i in items_data]
        reserve_stock(lines)

        subtotals = {}
        for i in items_data:
            key = (i['product'].pk, i['size_range'].pk, i['color'].pk)
            subtotals[key] = subtotals.get(key, Decimal('0')) + i['unit_price'] * i['quantity']
        quantities = aggregate_lines(lines)
        total = sum(subtotals.values(), Decimal('0'))
        sale = Sale.objects.create(created_by=user, total_amount=total, **validated_data)

        for i in items_data:
            key = (i['product'].pk, i['size_range'].pk, i['color'].pk)
            if key not in quantities:
                continue
            quantity = quantities.pop(key)
            subtotal = subtotals[key]
            SaleItem.objects.create(
                sale=sale,
                product=i['product'],
                size_range=i['size_range'],
                color=i['color'],
                quantity=quantity,
                unit_price=(subtotal / quantity).quantize(Decimal('0.01')),
                subtotal=subtotal,
            )
            adjust_stock(i['product'], i['size_range'], i['color'], quantity)

        if received > 0:
            Payment.objects.create(
                payment_type=Payment.INCOMING,
                payment_method=payment_method,
                amount=received,
                status=Payment.COMPLETED,
                customer=sale.customer,
                sale=sale,
                reference=sale.bill_no,
                notes=f'Received with sale {sale.bill_no}',
            )

        sale.refresh_from_db()
        return sale
