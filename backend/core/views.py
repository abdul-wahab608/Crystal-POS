"""
Core views for health check, system monitoring, and import functionality
"""
from django.http import JsonResponse
from django.db import connection
from django.conf import settings
from django.utils import timezone
from django.apps import apps
import sys

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Unit, ImportSession
from .serializers import (
    UnitSerializer, 
    ImportSessionSerializer, 
    ImportSessionDetailSerializer
)


def health_check(request):
    """
    Health check endpoint for desktop app
    Returns system status, database connectivity, and Python info
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return JsonResponse({
        "status": "healthy",
        "database": db_status,
        "python_version": sys.version,
        "django_version": settings.DATABASES['default']['ENGINE'],
        "debug": settings.DEBUG
    })


class UnitViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing measurement units.
    GET: All authenticated users
    POST/PUT/DELETE: Superuser only
    """
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = ['code', 'name', 'created_at']
    ordering = ['name']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Prevent deletion of system units
        if instance.is_system:
            return Response(
                {'error': 'System units cannot be deleted.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if unit is in use by any product or raw material
        Product = apps.get_model('products', 'Product')
        RawMaterial = apps.get_model('raw_materials', 'RawMaterial')
        
        if Product.objects.filter(unit=instance.code).exists():
            return Response(
                {'error': 'Cannot delete unit that is in use by products.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if RawMaterial.objects.filter(unit=instance.code).exists():
            return Response(
                {'error': 'Cannot delete unit that is in use by raw materials.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return super().destroy(request, *args, **kwargs)


class ImportSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing import history and performing undo.
    Superuser only.
    """
    queryset = ImportSession.objects.all()
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['entity_type', 'status']
    ordering_fields = ['created_at', 'total_rows', 'success_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ImportSessionDetailSerializer
        return ImportSessionSerializer

    @action(detail=True, methods=['post'])
    def undo(self, request, pk=None):
        """
        Undo an import session by deleting all imported records.
        Only available within 7 days of import and if not already undone.
        """
        session = self.get_object()
        
        # Check if undo is allowed
        if not session.can_undo:
            if session.status == 'undone':
                return Response(
                    {'error': 'This import has already been undone.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if session.status == 'failed':
                return Response(
                    {'error': 'Cannot undo a failed import.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'error': 'Undo period has expired (7 days limit).'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the model class based on entity type
        model_map = {
            'customer': ('customers', 'Customer'),
            'vendor': ('vendors', 'Vendor'),
            'product': ('products', 'Product'),
            'raw_material': ('raw_materials', 'RawMaterial'),
            'asset': ('assets', 'Asset'),
        }
        
        if session.entity_type not in model_map:
            return Response(
                {'error': f'Unknown entity type: {session.entity_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        app_label, model_name = model_map[session.entity_type]
        
        try:
            Model = apps.get_model(app_label, model_name)
        except LookupError:
            return Response(
                {'error': f'Model not found: {app_label}.{model_name}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Delete all imported records
        deleted_count = 0
        not_found_count = 0
        hard_errors = []

        for record_id in session.imported_ids:
            try:
                obj = Model.objects.get(pk=record_id)
                obj.delete()
                deleted_count += 1
            except Model.DoesNotExist:
                not_found_count += 1
            except Exception as e:
                hard_errors.append(f'Error deleting record {record_id}: {str(e)}')

        if hard_errors:
            return Response(
                {'error': 'Undo failed due to errors.', 'errors': hard_errors},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        session.status = 'undone'
        session.undone_at = timezone.now()
        session.save()

        response = {
            'message': f'Successfully undone import. Deleted {deleted_count} records.',
            'deleted_count': deleted_count,
        }
        if not_found_count:
            response['not_found_count'] = not_found_count
        return Response(response)

