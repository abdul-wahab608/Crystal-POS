from decimal import Decimal
from django.db.models import Sum
from rest_framework import serializers
from payments.models import Payment
from .models import BankAccount


class BankAccountSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = BankAccount
        fields = '__all__'

    def get_balance(self, obj):
        transfers = Payment.objects.filter(bank_account=obj, payment_method=Payment.BANK)
        received = transfers.filter(payment_type=Payment.INCOMING).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        paid = transfers.filter(payment_type=Payment.OUTGOING).aggregate(total=Sum('amount'))['total'] or Decimal('0')
        return str((received - paid).quantize(Decimal('0.01'))) 