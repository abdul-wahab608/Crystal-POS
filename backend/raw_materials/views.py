from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .models import RawMaterial, RawMaterialUsage, RawMaterialPurchase
from .serializers import (
    RawMaterialSerializer, 
    RawMaterialUsageSerializer, 
    RawMaterialPurchaseSerializer,
    RawMaterialUsageCreateSerializer,
    RawMaterialPurchaseCreateSerializer
)

# Create your views here.

class RawMaterialViewSet(viewsets.ModelViewSet):
    queryset = RawMaterial.objects.all()
    serializer_class = RawMaterialSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        unit = request.data.get('unit')
        quantity = request.data.get('quantity', 0)
        
        # Check if material already exists
        material = RawMaterial.objects.filter(name=name, unit=unit).first()
        if material:
            # Add quantity to existing material
            material.quantity += quantity
            material.save()
            serializer = self.get_serializer(material)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        # Create new material
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        return RawMaterial.objects.all()

    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get materials that need reordering"""
        low_stock_materials = []
        for material in self.get_queryset():
            # Calculate available stock for this material
            total_used = RawMaterialUsage.objects.filter(raw_material=material).aggregate(
                total=Sum('quantity_used')
            )['total'] or 0
            
            total_purchased = RawMaterialPurchase.objects.filter(raw_material=material).aggregate(
                total=Sum('quantity_purchased')
            )['total'] or 0
            
            available_stock = material.quantity - total_used + total_purchased
            
            if available_stock <= material.reorder_level:
                low_stock_materials.append({
                    'id': material.id,
                    'name': material.name,
                    'available_stock': available_stock,
                    'reorder_level': material.reorder_level
                })
        return Response(low_stock_materials)

    @action(detail=True, methods=['get'])
    def usage(self, request, pk=None):
        """Get usage history for a material"""
        material = self.get_object()
        usage_history = RawMaterialUsage.objects.filter(raw_material=material).order_by('-date_used')
        serializer = RawMaterialUsageSerializer(usage_history, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def purchase_history(self, request, pk=None):
        """Get purchase history for a material"""
        material = self.get_object()
        purchase_history = RawMaterialPurchase.objects.filter(raw_material=material).order_by('-purchase_date')
        serializer = RawMaterialPurchaseSerializer(purchase_history, many=True)
        return Response(serializer.data)

class RawMaterialUsageViewSet(viewsets.ModelViewSet):
    queryset = RawMaterialUsage.objects.all()
    serializer_class = RawMaterialUsageSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return RawMaterialUsageCreateSerializer
        return RawMaterialUsageSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Validate stock availability
            material = serializer.validated_data['raw_material']
            quantity_used = serializer.validated_data['quantity_used']
            
            # Calculate available stock
            total_used = RawMaterialUsage.objects.filter(raw_material=material).aggregate(
                total=Sum('quantity_used')
            )['total'] or 0
            
            total_purchased = RawMaterialPurchase.objects.filter(raw_material=material).aggregate(
                total=Sum('quantity_purchased')
            )['total'] or 0
            
            available_stock = material.quantity - total_used + total_purchased
            
            if quantity_used > available_stock:
                return Response(
                    {'error': f'Insufficient stock. Available: {available_stock}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RawMaterialPurchaseViewSet(viewsets.ModelViewSet):
    queryset = RawMaterialPurchase.objects.all()
    serializer_class = RawMaterialPurchaseSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'put', 'patch', 'delete']

    def get_serializer_class(self):
        if self.action == 'create':
            return RawMaterialPurchaseCreateSerializer
        return RawMaterialPurchaseSerializer

    def list(self, request, *args, **kwargs):
        """Get all purchase history with material details"""
        queryset = self.get_queryset().select_related('raw_material').order_by('-purchase_date')
        serializer = self.get_serializer(queryset, many=True)
        
        # Add material details to each purchase
        data = serializer.data
        for purchase in data:
            material = purchase['raw_material']
            purchase['raw_material_name'] = material['name']
            purchase['unit'] = material['unit']
        
        return Response(data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Calculate total amount
            quantity = serializer.validated_data['quantity_purchased']
            unit_price = serializer.validated_data['unit_price']
            total_amount = quantity * unit_price
            
            # Save with calculated total
            purchase = serializer.save(total_amount=total_amount)
            
            # Update material quantity
            material = purchase.raw_material
            material.quantity += quantity
            material.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
