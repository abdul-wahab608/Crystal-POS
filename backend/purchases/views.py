from django.shortcuts import render
from rest_framework import viewsets
from .models import Purchase, PurchaseItem
from .serializers import PurchaseSerializer, PurchaseItemSerializer

# Create your views here.

class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    serializer_class = PurchaseSerializer

class PurchaseItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseItem.objects.all()
    serializer_class = PurchaseItemSerializer
