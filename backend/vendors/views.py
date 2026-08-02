from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Vendor, VendorTransaction, VendorProduct
from .serializers import VendorSerializer, VendorTransactionSerializer, VendorProductSerializer
from core.mixins import BulkImportMixin, BulkExportMixin, BatchActionsMixin

# Create your views here.

class VendorViewSet(BulkImportMixin, BulkExportMixin, BatchActionsMixin, viewsets.ModelViewSet):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    # Restrict detail lookups to numeric IDs so this blank-prefix viewset's
    # detail route doesn't shadow sibling resources (vendor-transactions/, vendor-products/) registered later in the same router.
    lookup_value_regex = r'\d+'

    # Batch update allowed fields
    batch_update_fields = ['is_active']

    # Import configuration
    import_entity_type = 'vendor'
    import_unique_fields = ['name']  # Vendor name is unique
    import_fields = {
    'name': {
        'required': True,
        'type': 'string',
        'example': 'ABC Supplies Ltd',
        'aliases': ['vendor_name', 'company', 'supplier', 'supplier_name'],
    },
    'phone': {
        'required': False,
        'type': 'string',
        'example': '+1234567890',
        'aliases': ['phone_number', 'mobile', 'contact', 'tel'],
    },
    'address': {
        'required': False,
        'type': 'string',
        'example': '456 Industrial Ave',
        'aliases': ['street_address', 'location'],
    },
    'contact_person': {
        'required': False,
        'type': 'string',
        'example': 'Jane Smith',
        'aliases': ['contact_name', 'representative', 'rep'],
    },
    'balance': {
        'required': False,
        'type': 'decimal',
        'default': 0,
        'example': '0.00',
        'aliases': ['opening_balance', 'initial_balance', 'amount'],
    },
    'is_active': {
        'required': False,
        'type': 'boolean',
        'default': True,
        'example': 'true',
        'aliases': ['active', 'status'],
    },
    }

    # Export configuration
    export_filename = 'vendors'
    export_fields = {
        'name': {'label': 'Vendor Name', 'type': 'string'},
        'phone': {'label': 'Phone', 'type': 'string'},
        'address': {'label': 'Address', 'type': 'string'},
        'city': {'label': 'City', 'type': 'string'},
        'contact_person': {'label': 'Contact Person', 'type': 'string'},
        'balance': {'label': 'Balance', 'type': 'decimal'},
        'is_active': {'label': 'Active', 'type': 'boolean'},
        'created_at': {'label': 'Created At', 'type': 'datetime'},
    }

    def create(self, request, *args, **kwargs):
        """Check for duplicate vendor name before creating"""
        name = request.data.get('name', '').strip()

        if Vendor.objects.filter(name__iexact=name).exists():
            return Response(
                {'error': f'Vendor "{name}" already exists. Please use a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """Check for duplicate vendor name when updating (except current vendor)"""
        name = request.data.get('name', '').strip()
        instance = self.get_object()

        if name and Vendor.objects.filter(name__iexact=name).exclude(id=instance.id).exists():
            return Response(
                {'error': f'Vendor "{name}" already exists. Please use a different name.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().update(request, *args, **kwargs)

    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get all products supplied by this vendor"""
        vendor = self.get_object()
        vendor_products = vendor.vendor_products.filter(is_active=True)
        serializer = VendorProductSerializer(vendor_products, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def price_comparison(self, request, pk=None):
        """Compare this vendor's prices with other vendors for same products"""
        vendor = self.get_object()
        vendor_products = vendor.vendor_products.filter(is_active=True)

        comparison_data = []
        for vp in vendor_products:
            # Find other vendors selling the same item
            if vp.product_type == 'PRODUCT':
                other_vendors = VendorProduct.objects.filter(
                    product=vp.product,
                    is_active=True
                ).exclude(vendor=vendor)
            else:
                other_vendors = VendorProduct.objects.filter(
                    raw_material=vp.raw_material,
                    is_active=True
                ).exclude(vendor=vendor)

            comparison_data.append({
                'item_name': vp.item_name,
                'this_vendor_price': vp.unit_price,
                'other_vendors': VendorProductSerializer(other_vendors, many=True).data
            })

        return Response(comparison_data)

class VendorProductViewSet(viewsets.ModelViewSet):
    queryset = VendorProduct.objects.all()
    serializer_class = VendorProductSerializer
    
    @action(detail=False, methods=['get'])
    def by_product(self, request):
        """Get all vendors for a specific product"""
        product_id = request.query_params.get('product_id')
        product_type = request.query_params.get('product_type', 'PRODUCT')
        
        if product_type == 'PRODUCT':
            vendor_products = VendorProduct.objects.filter(
                product_id=product_id,
                is_active=True
            ).order_by('unit_price')
        else:
            vendor_products = VendorProduct.objects.filter(
                raw_material_id=product_id,
                is_active=True
            ).order_by('unit_price')
        
        serializer = self.get_serializer(vendor_products, many=True)
        return Response(serializer.data)

class VendorTransactionViewSet(viewsets.ModelViewSet):
    queryset = VendorTransaction.objects.all()
    serializer_class = VendorTransactionSerializer
