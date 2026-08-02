from django.shortcuts import render
from rest_framework import viewsets
from .models import Asset, AssetLog
from .serializers import AssetSerializer, AssetLogSerializer
from core.mixins import BulkImportMixin, BulkExportMixin, BatchActionsMixin

# Create your views here.

class AssetViewSet(BulkImportMixin, BulkExportMixin, BatchActionsMixin, viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    
    # Batch update allowed fields
    batch_update_fields = ['status', 'location', 'category']
    
    # Import configuration
    import_entity_type = 'asset'
    import_unique_fields = ['name']  # Check by name
    import_fields = {
        'name': {
            'required': True,
            'type': 'string',
            'example': 'CNC Machine #1',
            'aliases': ['asset_name', 'item', 'item_name', 'asset'],
        },
        'description': {
            'required': False,
            'type': 'string',
            'example': 'Main production CNC machine',
            'aliases': ['desc', 'details', 'notes'],
        },
        'category': {
            'required': False,
            'type': 'string',
            'example': 'Production Equipment',
            'aliases': ['asset_category', 'group'],
        },
        'type': {
            'required': True,
            'type': 'choice',
            'choices': ['MACHINE', 'MOLD', 'EQUIPMENT', 'FURNITURE', 'VEHICLE', 'BUILDING', 'TECHNOLOGY', 'OTHER'],
            'default': 'EQUIPMENT',
            'example': 'MACHINE',
            'aliases': ['asset_type'],
        },
        'value': {
            'required': False,
            'type': 'decimal',
            'example': '50000.00',
            'aliases': ['current_value', 'worth'],
        },
        'purchase_value': {
            'required': False,
            'type': 'decimal',
            'example': '75000.00',
            'aliases': ['cost', 'purchase_price', 'original_value', 'purchase_cost'],
        },
        'location': {
            'required': False,
            'type': 'string',
            'example': 'Factory Floor A',
            'aliases': ['place', 'position'],
        },
        'status': {
            'required': False,
            'type': 'choice',
            'choices': ['ACTIVE', 'INACTIVE', 'MAINTENANCE', 'DISPOSED'],
            'default': 'ACTIVE',
            'example': 'ACTIVE',
            'aliases': ['asset_status', 'condition'],
        },
    }
    
    # Export configuration
    export_filename = 'assets'
    export_fields = {
        'name': {'label': 'Asset Name', 'type': 'string'},
        'description': {'label': 'Description', 'type': 'string'},
        'category': {'label': 'Category', 'type': 'string'},
        'type': {'label': 'Type', 'type': 'string'},
        'value': {'label': 'Current Value', 'type': 'decimal'},
        'purchase_value': {'label': 'Purchase Value', 'type': 'decimal'},
        'location': {'label': 'Location', 'type': 'string'},
        'status': {'label': 'Status', 'type': 'string'},
        'purchase_date': {'label': 'Purchase Date', 'type': 'date'},
        'created_at': {'label': 'Created At', 'type': 'datetime'},
    }

class AssetLogViewSet(viewsets.ModelViewSet):
    queryset = AssetLog.objects.all()
    serializer_class = AssetLogSerializer
