import datetime
from django.utils import timezone
from rest_framework import serializers
from .models import Payment
from customers.serializers import CustomerSerializer
from vendors.serializers import VendorSerializer
from bank_accounts.serializers import BankAccountSerializer
from sales.serializers import SaleSerializer
from purchases.serializers import PurchaseSerializer


class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)
    bank_account = BankAccountSerializer(read_only=True)
    sale = SaleSerializer(read_only=True)
    purchase = PurchaseSerializer(read_only=True)
    direct_payment_to_vendor = VendorSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = '__all__'


PAYMENT_WRITE_FIELDS = [
    'id', 'payment_type', 'payment_method', 'amount', 'status',
    'customer', 'vendor', 'bank_account', 'sale', 'purchase',
    'direct_payment_to_vendor', 'due_date', 'payment_date', 'reference', 'notes',
    'original_amount', 'remaining_amount', 'bank_name', 'account_number'
]


class PaymentCreateSerializer(serializers.ModelSerializer):
    payment_date = serializers.DateField(write_only=True, required=False)

    class Meta:
        model = Payment
        fields = PAYMENT_WRITE_FIELDS
        read_only_fields = ['status']

    def validate(self, data):
        user = self.context['request'].user
        payment_type = data.get('payment_type', Payment.INCOMING)

        if payment_type != Payment.INCOMING and not user.is_manager():
            raise serializers.ValidationError({'payment_type': 'Only managers can record vendor payments.'})

        if data['amount'] <= 0:
            raise serializers.ValidationError({'amount': 'Amount must be greater than zero.'})

        purchase = data.get('purchase')
        if purchase:
            if payment_type != Payment.OUTGOING:
                raise serializers.ValidationError({'purchase': 'Only outgoing vendor payments can be linked to a purchase bill.'})
            if data.get('vendor') is None:
                data['vendor'] = purchase.vendor
            elif data['vendor'] != purchase.vendor:
                raise serializers.ValidationError({'vendor': "Vendor must match the purchase bill's vendor."})
            unpaid = purchase.unpaid_amount()
            if data['amount'] > unpaid:
                raise serializers.ValidationError({'amount': f'Amount exceeds the unpaid balance of {unpaid} on Purchase #{purchase.pk}.'})

        sale = data.get('sale')
        if sale:
            if payment_type != Payment.INCOMING:
                raise serializers.ValidationError({'sale': 'Only incoming payments can be linked to a sale.'})
            if data.get('customer') is None:
                data['customer'] = sale.customer
            elif data['customer'] != sale.customer:
                raise serializers.ValidationError({'customer': "Customer must match the sale's customer."})
            balance = sale.total_amount - sale.amount_paid()
            if data['amount'] > balance:
                raise serializers.ValidationError({'amount': f'Amount exceeds the sale balance of {balance}.'})

        if payment_type == Payment.INCOMING:
            if not data.get('customer'):
                raise serializers.ValidationError({'customer': 'Customer is required for incoming payments.'})
            if data.get('vendor'):
                raise serializers.ValidationError({'vendor': 'Vendor should not be set for incoming payments.'})

        elif payment_type == Payment.OUTGOING:
            if not data.get('vendor'):
                raise serializers.ValidationError({'vendor': 'Vendor is required for outgoing payments.'})
            if data.get('customer'):
                raise serializers.ValidationError({'customer': 'Customer should not be set for outgoing payments.'})

        elif payment_type == Payment.DIRECT:
            if not data.get('customer'):
                raise serializers.ValidationError({'customer': 'Customer is required for direct payments.'})
            if not data.get('direct_payment_to_vendor'):
                raise serializers.ValidationError({'direct_payment_to_vendor': 'Receiving vendor is required for direct payments.'})

        if data.get('payment_method') == Payment.BANK and not data.get('bank_account'):
            raise serializers.ValidationError({'bank_account': 'Choose the bank account for bank transfers.'})

        payment_date = data.pop('payment_date', None)
        if payment_date is not None:
            data['payment_date'] = timezone.make_aware(datetime.datetime.combine(payment_date, datetime.time.min))

        data.setdefault('status', Payment.COMPLETED)
        return data


class PaymentUpdateSerializer(serializers.ModelSerializer):
    LOCKED_FIELDS = ('payment_type', 'amount', 'customer', 'sale', 'purchase')

    class Meta:
        model = Payment
        fields = PAYMENT_WRITE_FIELDS
        read_only_fields = ['status']

    def validate(self, data):
        for field in self.LOCKED_FIELDS:
            if field in data and data[field] != getattr(self.instance, field):
                raise serializers.ValidationError({
                    field: 'Cannot be changed after recording. Delete the payment and record it again.'
                })
        return data
