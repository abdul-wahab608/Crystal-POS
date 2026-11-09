from django.db import transaction
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Sum, Q
from datetime import date
from users.permissions import IsManagerUser, IsStaffUser
from .models import Payment
from .serializers import PaymentSerializer, PaymentCreateSerializer, PaymentUpdateSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('customer', 'vendor', 'sale', 'bank_account').all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['payment_type', 'payment_method', 'status', 'customer', 'vendor', 'bank_account', 'sale']
    search_fields = ['reference', 'notes', 'customer__name', 'vendor__name', 'sale__bill_no']
    ordering_fields = ['payment_date', 'due_date', 'amount']
    ordering = ['-payment_date']

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [IsStaffUser()]
        return [IsManagerUser()]

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        return PaymentSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(payment_date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(payment_date__date__lte=date_to)
        return queryset

    def perform_destroy(self, instance):
        with transaction.atomic():
            instance.delete()

    @action(detail=False, methods=['get'])
    def summary(self, request):
        total_incoming = Payment.objects.filter(payment_type=Payment.INCOMING).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_outgoing = Payment.objects.filter(payment_type=Payment.OUTGOING).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_direct = Payment.objects.filter(payment_type=Payment.DIRECT).aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_payments = Payment.objects.filter(status=Payment.PENDING).count()
        overdue_payments = Payment.objects.filter(
            status__in=[Payment.PENDING, Payment.PARTIAL],
            due_date__lt=date.today()
        ).count()
        
        return Response({
            'total_incoming': total_incoming,
            'total_outgoing': total_outgoing,
            'total_direct': total_direct,
            'net_cash_flow': total_incoming - total_outgoing,
            'pending_payments': pending_payments,
            'overdue_payments': overdue_payments,
        })

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_payments = Payment.objects.filter(
            status__in=[Payment.PENDING, Payment.PARTIAL],
            due_date__lt=date.today()
        ).order_by('due_date')
        
        serializer = self.get_serializer(overdue_payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_customer(self, request):
        customer_id = request.query_params.get('customer_id')
        if customer_id:
            payments = Payment.objects.filter(customer_id=customer_id)
        else:
            payments = Payment.objects.filter(customer__isnull=False)
        
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_vendor(self, request):
        vendor_id = request.query_params.get('vendor_id')
        if vendor_id:
            payments = Payment.objects.filter(
                Q(vendor_id=vendor_id) | Q(direct_payment_to_vendor_id=vendor_id)
            )
        else:
            payments = Payment.objects.filter(
                Q(vendor__isnull=False) | Q(direct_payment_to_vendor__isnull=False)
            )
        
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_bank(self, request):
        bank_id = request.query_params.get('bank_id')
        if bank_id:
            payments = Payment.objects.filter(bank_account_id=bank_id)
        else:
            payments = Payment.objects.filter(bank_account__isnull=False)
        
        serializer = self.get_serializer(payments, many=True)
        return Response(serializer.data)
