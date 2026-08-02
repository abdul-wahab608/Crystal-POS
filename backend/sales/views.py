from rest_framework.response import Response
from rest_framework import status, viewsets
from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleItemSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffUser


class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.select_related('customer', 'created_by').prefetch_related('items__product', 'items__size_range', 'items__color').all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer
