from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsManagerUser
from .models import RawMaterial, RawMaterialUsage
from .serializers import RawMaterialSerializer, RawMaterialUsageSerializer
from core.mixins import BulkImportMixin, BulkExportMixin, BatchActionsMixin


class RawMaterialViewSet(BulkImportMixin, BulkExportMixin, BatchActionsMixin, viewsets.ModelViewSet):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    batch_update_fields = ['reorder_level']

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsManagerUser()]
        return super().get_permissions()

    def get_batch_permissions(self):
        if self.action == 'bulk_delete':
            return [IsAuthenticated(), IsManagerUser()]
        return super().get_batch_permissions()

    import_entity_type = 'raw_material'
    import_unique_fields = ['name', 'unit']
    import_fields = {
        'name': {
            'required': True,
            'type': 'string',
            'example': 'Steel Rod',
            'aliases': ['material_name', 'material name', 'item', 'item_name', 'material', 'raw_material'],
        },
        'unit': {
            'required': True,
            'type': 'unit',
            'example': 'KG',
            'aliases': ['uom', 'unit_of_measure', 'measurement'],
        },
        'quantity': {
            'required': False,
            'type': 'decimal',
            'default': 0,
            'example': '100',
            'aliases': ['qty', 'stock', 'initial_quantity', 'initial_stock', 'initial stock', 'opening_stock'],
        },
        'reorder_level': {
            'required': False,
            'type': 'decimal',
            'default': 0,
            'example': '10',
            'aliases': ['reorder', 'reorder level', 'minimum_stock', 'min_stock', 'threshold'],
        },
    }

    export_filename = 'raw_materials'
    export_fields = {
        'name': {'label': 'Material Name', 'type': 'string'},
        'unit': {'label': 'Unit', 'type': 'string'},
        'quantity': {'label': 'Quantity', 'type': 'decimal'},
        'reorder_level': {'label': 'Reorder Level', 'type': 'decimal'},
        'created_at': {'label': 'Created At', 'type': 'datetime'},
    }

    def get_queryset(self):
        return RawMaterial.objects.all()

    def destroy(self, request, *args, **kwargs):
        material = self.get_object()
        try:
            material.delete()
        except ProtectedError:
            return Response(
                {'error': f'{material.name} is used in purchases or production and cannot be deleted.'},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        low_stock_materials = [
            {
                'id': material.id,
                'name': material.name,
                'quantity': material.quantity,
                'reorder_level': material.reorder_level,
            }
            for material in self.get_queryset()
            if material.needs_reorder
        ]
        return Response(low_stock_materials)

    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        material = self.get_object()
        usage_history = RawMaterialUsage.objects.filter(raw_material=material).order_by('-date_used')
        serializer = RawMaterialUsageSerializer(usage_history, many=True)
        return Response(serializer.data)


class RawMaterialUsageViewSet(viewsets.ModelViewSet):
    queryset = RawMaterialUsage.objects.all()
    serializer_class = RawMaterialUsageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            material = serializer.validated_data['raw_material']
            quantity_used = serializer.validated_data['quantity_used']
            if quantity_used > material.quantity:
                return Response(
                    {'error': f'Insufficient stock. Available: {material.quantity}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            usage = serializer.save()
            return Response(RawMaterialUsageSerializer(usage).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
