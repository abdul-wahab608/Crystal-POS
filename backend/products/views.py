from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from .models import Product, ProductHistory, SizeRange, Color, ProductVariant
from .serializers import ProductSerializer, ProductHistorySerializer, SizeRangeSerializer, ColorSerializer, ProductVariantSerializer
from decimal import Decimal
from core.mixins import BulkImportMixin, BulkExportMixin, BatchActionsMixin

# Create your views here.

class SizeRangeViewSet(viewsets.ModelViewSet):
    queryset = SizeRange.objects.all()
    serializer_class = SizeRangeSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class ColorViewSet(viewsets.ModelViewSet):
    queryset = Color.objects.all()
    serializer_class = ColorSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']


class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['product__name', 'size_range__name', 'color__name']
    ordering_fields = ['quantity_dozens']

    def get_queryset(self):
        qs = super().get_queryset()
        product_id = self.request.query_params.get('product')
        if product_id:
            qs = qs.filter(product_id=product_id)
        return qs


class ProductViewSet(BulkImportMixin, BulkExportMixin, BatchActionsMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'cop', 'quantity']
    # Restrict detail lookups to numeric IDs so this blank-prefix viewset's
    # detail route doesn't shadow sibling resources (size-ranges/, colors/, product-variants/, product-history/) registered later in the same router.
    lookup_value_regex = r'\d+'

    # Batch update allowed fields
    batch_update_fields = ['product_type']

    # Import configuration
    import_entity_type = 'product'
    import_unique_fields = ['name', 'unit']  # Unique together

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

    # Export configuration
    export_filename = 'products'
    export_fields = {
        'name': {'label': 'Product Name', 'type': 'string'},
        'unit': {'label': 'Unit', 'type': 'string'},
        'cop': {'label': 'Cost of Production', 'type': 'decimal'},
        'quantity': {'label': 'Quantity', 'type': 'decimal'},
        'product_type': {'label': 'Product Type', 'type': 'string'},
        'created_at': {'label': 'Created At', 'type': 'datetime'},
    }

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        unit = request.data.get('unit')
        quantity = request.data.get('quantity')
        
        # Check for existing product with same name AND unit
        product = Product.objects.filter(name=name, unit=unit).first()
        if product:
            # Add quantity to existing product
            product.quantity += Decimal(str(quantity))
            product.save()
            serializer = self.get_serializer(product)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new product if not found
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        size_range_id = self.request.query_params.get('size_range')
        if size_range_id:
            qs = qs.filter(size_range_id=size_range_id)
        return qs

class ProductHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProductHistory.objects.all()
    serializer_class = ProductHistorySerializer
