import re

from django.db import transaction
from django.db.models import F, ProtectedError, Q
from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.permissions import IsManagerUser
from profit.services import CostLookup
from .models import Product, ProductHistory, SizeRange, Color, ProductVariant
from .serializers import ProductSerializer, ProductHistorySerializer, SizeRangeSerializer, ColorSerializer, ProductVariantSerializer
from core.mixins import BulkImportMixin, BulkExportMixin, BatchActionsMixin


class ProtectedDeleteMixin:
    protected_delete_message = 'This is used by existing products or sales and cannot be deleted.'

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response({'error': self.protected_delete_message}, status=status.HTTP_409_CONFLICT)


class SizeRangeViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = SizeRange.objects.all()
    serializer_class = SizeRangeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ColorViewSet(ProtectedDeleteMixin, viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'size_range__name', 'color__name']
    ordering_fields = ['quantity']

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs

    @transaction.atomic
    def perform_destroy(self, instance):
        Product.objects.filter(pk=instance.product_id).update(quantity=F('quantity') - instance.quantity)
        instance.delete()


class ProductViewSet(ProtectedDeleteMixin, BulkImportMixin, BulkExportMixin, BatchActionsMixin, viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('size_ranges', 'variants').all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'cop', 'quantity']
    # Restrict detail lookups to numeric IDs so this blank-prefix viewset's
    # detail route doesn't shadow sibling resources (size-ranges/, colors/, product-variants/, product-history/) registered later in the same router.
    lookup_value_regex = r'\d+'

    batch_update_fields = ['product_type']
    protected_delete_message = 'This product already has sales or purchases, so it cannot be deleted.'

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsManagerUser()]
        return super().get_permissions()

    def get_batch_permissions(self):
        if self.action == 'bulk_delete':
            return [IsAuthenticated(), IsManagerUser()]
        return super().get_batch_permissions()

    import_entity_type = 'product'
    import_unique_fields = ['name', 'unit']

    import_fields = {
        'name': {
            'required': True,
            'type': 'string',
            'example': 'Widget A',
            'aliases': ['product_name', 'item', 'item_name', 'product'],
        },
        'unit': {
            'required': True,
            'type': 'unit',
            'example': 'PCS',
            'aliases': ['uom', 'unit_of_measure', 'measurement'],
        },
        'size_range': {
            'required': False,
            'type': 'string',
            'example': 'Men (40-46)',
            'aliases': ['size', 'size_range_name'],
        },
        'cop': {
            'required': True,
            'type': 'decimal',
            'example': '100.00',
            'aliases': ['cost', 'cost_of_production', 'price', 'unit_cost', 'cost_price'],
        },
        'quantity': {
            'required': False,
            'type': 'decimal',
            'default': 0,
            'example': '50',
            'aliases': ['qty', 'stock', 'initial_quantity', 'initial_stock', 'opening_stock'],
        },
        'product_type': {
            'required': False,
            'type': 'choice',
            'choices': ['MANUFACTURED', 'PURCHASED'],
            'default': 'MANUFACTURED',
            'example': 'MANUFACTURED',
            'aliases': ['type', 'category'],
        },
    }

    export_filename = 'products'
    export_fields = {
        'name': {'label': 'Product Name', 'type': 'string'},
        'unit': {'label': 'Unit', 'type': 'string'},
        'cop': {'label': 'Cost of Production', 'type': 'decimal'},
        'quantity': {'label': 'Quantity', 'type': 'decimal'},
        'product_type': {'label': 'Product Type', 'type': 'string'},
        'created_at': {'label': 'Created At', 'type': 'datetime'},
    }

    def _transform_row(self, row_data):
        transformed, new_units = super()._transform_row(row_data)
        names = [n.strip() for n in re.split(r'[,;]', transformed.pop('size_range', '')) if n.strip()]
        size_ranges = []
        for name in names:
            size_range = SizeRange.objects.filter(name__iexact=name).first()
            if size_range is None:
                raise ValueError(f'Size range "{name}" does not exist. Create it on the Catalog page first.')
            size_ranges.append(size_range.pk)
        transformed['size_ranges'] = size_ranges
        return transformed, new_units

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if self.action == 'list':
            context['cost_lookup'] = CostLookup(Product.objects.values_list('id', flat=True))
        return context

    def get_queryset(self):
        qs = super().get_queryset()
        size_range_id = self.request.query_params.get('size_range')
        if size_range_id:
            qs = qs.filter(Q(size_ranges__id=size_range_id) | Q(variants__size_range_id=size_range_id)).distinct()
        color_id = self.request.query_params.get('color')
        if color_id:
            qs = qs.filter(variants__color_id=color_id).distinct()
        return qs


class ProductHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProductHistory.objects.all()
    serializer_class = ProductHistorySerializer
