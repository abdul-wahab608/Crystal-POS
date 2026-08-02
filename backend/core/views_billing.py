from rest_framework import viewsets, status
from rest_framework.response import Response
from .models_billing import Invoice, Bill, Payment
from .serializers_billing import InvoiceSerializer, BillSerializer, PaymentSerializer
from sales.models import Sale
from purchases.models import Purchase
from rest_framework.exceptions import ValidationError

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def perform_create(self, serializer):
        sale = serializer.validated_data.get('sale')
        if sale and hasattr(sale, 'invoice'):
            raise ValidationError('This sale already has an invoice.')
        serializer.save()

class BillViewSet(viewsets.ModelViewSet):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer

    def perform_create(self, serializer):
        purchase = serializer.validated_data.get('purchase')
        if purchase and hasattr(purchase, 'bill'):
            raise ValidationError('This purchase already has a bill.')
        serializer.save()

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        invoice = serializer.validated_data.get('invoice')
        bill = serializer.validated_data.get('bill')
        if not invoice and not bill:
            raise ValidationError('Payment must be linked to either an invoice or a bill.')
        payment = serializer.save()
        # Update payment status for invoice
        if invoice:
            total_paid = sum(p.amount for p in invoice.payments.all())
            if total_paid >= invoice.amount:
                invoice.payment_status = 'PAID'
            elif total_paid > 0:
                invoice.payment_status = 'PARTIAL'
            else:
                invoice.payment_status = 'UNPAID'
            invoice.save(update_fields=['payment_status'])
        # Update payment status for bill
        if bill:
            total_paid = sum(p.amount for p in bill.payments.all())
            if total_paid >= bill.amount:
                bill.payment_status = 'PAID'
            elif total_paid > 0:
                bill.payment_status = 'PARTIAL'
            else:
                bill.payment_status = 'UNPAID'
            bill.save(update_fields=['payment_status'])
