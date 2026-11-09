from rest_framework import serializers
from .models import Customer, CustomerTransaction


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerTransaction
        fields = '__all__'

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Amount must be greater than zero.')
        return value
