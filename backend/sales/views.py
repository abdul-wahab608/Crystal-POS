from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from customers.models import CustomerTransaction
from users.permissions import IsManagerUser, IsStaffUser
from .models import Sale
from .serializers import SaleSerializer
from .services import adjust_stock


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('customer', 'created_by').prefetch_related(
        'items__product', 'items__size_range', 'items__color', 'payments'
    ).all()
    serializer_class = SaleSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'payment_status', 'sale_type']
    search_fields = ['bill_no', 'customer__name']
    ordering_fields = ['date', 'total_amount', 'bill_no']
    ordering = ['-date', '-id']

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return [IsAuthenticated(), IsStaffUser()]
        return [IsAuthenticated(), IsManagerUser()]

    def get_queryset(self):
        queryset = super().get_queryset()
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(date__date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__date__lte=date_to)
        return queryset

    def perform_destroy(self, instance):
        with transaction.atomic():
            for payment in instance.payments.all():
                payment.delete()
            for item in instance.items.select_related('product', 'size_range', 'color'):
                adjust_stock(item.product, item.size_range, item.color, -item.quantity)
            CustomerTransaction.objects.create(
                customer=instance.customer,
                type=CustomerTransaction.REVERSAL,
                reverses=CustomerTransaction.SALE,
                amount=instance.total_amount,
                reference=instance.bill_no,
                notes=f'Reversal of deleted sale {instance.bill_no}',
            )
            instance.delete()
