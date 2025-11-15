from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Product, ProductHistory
from .serializers import ProductSerializer, ProductHistorySerializer
from decimal import Decimal

# Create your views here.

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

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

class ProductHistoryViewSet(viewsets.ModelViewSet):
    queryset = ProductHistory.objects.all()
    serializer_class = ProductHistorySerializer
