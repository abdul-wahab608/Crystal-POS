from rest_framework.response import Response
from rest_framework import status
from products.models import Product
from rest_framework import viewsets
from .models import Sale, SaleItem
from .serializers import SaleSerializer, SaleItemSerializer
from rest_framework.permissions import IsAuthenticated
from users.permissions import IsStaffUser

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
    permission_classes = [IsAuthenticated, IsStaffUser]

    def create(self, request, *args, **kwargs):
        data = request.data
        items = data.get("items", [])

        # 1. Check stock for each item
        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({"detail": f"Product ID {product_id} not found."},
                                status=status.HTTP_400_BAD_REQUEST)

            if product.available_stock < quantity:
                return Response({"detail": f"Insufficient stock for {product.name}."},
                                status=status.HTTP_400_BAD_REQUEST)

        # 2. Stock deduction is handled in the serializer
        pass

        # 3. Save Sale
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class SaleItemViewSet(viewsets.ModelViewSet):
    queryset = SaleItem.objects.all()
    serializer_class = SaleItemSerializer
