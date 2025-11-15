from rest_framework import serializers
from .models import Payment
from customers.serializers import CustomerSerializer
from vendors.serializers import VendorSerializer
from bank_accounts.serializers import BankAccountSerializer
from sales.serializers import SaleSerializer
from raw_materials.serializers import RawMaterialPurchaseSerializer

class PaymentSerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)
    vendor = VendorSerializer(read_only=True)
    bank_account = BankAccountSerializer(read_only=True)
    sale = SaleSerializer(read_only=True)
    purchase = RawMaterialPurchaseSerializer(read_only=True)
    direct_payment_to_vendor = VendorSerializer(read_only=True)
    
    class Meta:
        model = Payment
        fields = '__all__'
        read_only_fields = ['payment_date']

class PaymentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'payment_method', 'amount', 'status',
            'customer', 'vendor', 'bank_account', 'sale', 'purchase',
            'direct_payment_to_vendor', 'due_date', 'reference', 'notes',
            'original_amount', 'remaining_amount', 'bank_name', 'account_number'
        ]
    
    def validate(self, data):
        # Validate payment type and related fields
        payment_type = data.get('payment_type')
        
        if payment_type == Payment.INCOMING:
            if not data.get('customer'):
                raise serializers.ValidationError("Customer is required for incoming payments")
            if data.get('vendor'):
                raise serializers.ValidationError("Vendor should not be set for incoming payments")
        
        elif payment_type == Payment.OUTGOING:
            if not data.get('vendor'):
                raise serializers.ValidationError("Vendor is required for outgoing payments")
            if data.get('customer'):
                raise serializers.ValidationError("Customer should not be set for outgoing payments")
        
        elif payment_type == Payment.DIRECT:
            if not data.get('customer'):
                raise serializers.ValidationError("Customer is required for direct payments")
            if not data.get('direct_payment_to_vendor'):
                raise serializers.ValidationError("Direct payment vendor is required for direct payments")
        
        # Validate payment method and bank details
        payment_method = data.get('payment_method')
        if payment_method == Payment.BANK and not data.get('bank_name'):
            raise serializers.ValidationError("Bank name is required for bank transfers")
        
        return data

class PaymentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'payment_type', 'payment_method', 'amount', 'status',
            'customer', 'vendor', 'bank_account', 'sale', 'purchase',
            'direct_payment_to_vendor', 'due_date', 'reference', 'notes',
            'original_amount', 'remaining_amount', 'bank_name', 'account_number'
        ] 