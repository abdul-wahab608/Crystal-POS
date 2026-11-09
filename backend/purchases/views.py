from decimal import Decimal
from django.db import transaction
from django.db.models import F, Q, Sum
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from payments.models import Payment
from products.models import ProductVariant
from .models import Purchase
from .serializers import PurchaseSerializer

STOCK_GONE_MESSAGE = 'Stock from this purchase has already been used and cannot be reversed.'


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.select_related('vendor').prefetch_related('items__product', 'items__raw_material')
    serializer_class = PurchaseSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.query_params.get('unpaid') == 'true':
            queryset = queryset.annotate(
                paid_total=Coalesce(
                    Sum('payments__amount', filter=Q(payments__payment_type=Payment.OUTGOING)),
                    Decimal('0'),
                ),
            ).filter(paid_total__lt=F('total_amount'))
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @transaction.atomic
    def perform_destroy(self, instance):
        if instance.payments.exists():
            raise ValidationError({'detail': f'Delete the vendor payments for Purchase #{instance.pk} first'})
        for item in instance.items.select_related('raw_material'):
            if item.raw_material_id:
                if item.raw_material.quantity < item.quantity:
                    raise ValidationError({'detail': STOCK_GONE_MESSAGE})
                continue
            variant = ProductVariant.objects.filter(
                product_id=item.product_id, size_range_id=item.size_range_id, color_id=item.color_id,
            ).first()
            if variant is None or variant.quantity < item.quantity:
                raise ValidationError({'detail': STOCK_GONE_MESSAGE})
        instance.delete()
