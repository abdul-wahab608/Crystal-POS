from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsManagerUser
from .models import ProductionRun
from .serializers import ProductionRunSerializer
from .services import delete_run


class ProductionRunViewSet(viewsets.ModelViewSet):
    queryset = ProductionRun.objects.select_related('created_by').prefetch_related(
        'items__variant__product', 'items__variant__size_range', 'items__variant__color',
        'inputs__raw_material',
    )
    serializer_class = ProductionRunSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAuthenticated(), IsManagerUser()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        delete_run(instance)
