from rest_framework import serializers
from .models_billing import Invoice, Bill, Payment

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'amount', 'date', 'method', 'reference', 'invoice', 'bill']

class InvoiceSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    class Meta:
        model = Invoice
        fields = ['id', 'number', 'date', 'amount', 'payment_status', 'payment_method', 'sale', 'payments']

class BillSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    class Meta:
        model = Bill
        fields = ['id', 'number', 'date', 'amount', 'payment_status', 'payment_method', 'purchase', 'payments']
