from django.shortcuts import render
from rest_framework import viewsets
from .models import Asset, AssetLog
from .serializers import AssetSerializer, AssetLogSerializer

# Create your views here.

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

class AssetLogViewSet(viewsets.ModelViewSet):
    queryset = AssetLog.objects.all()
    serializer_class = AssetLogSerializer
