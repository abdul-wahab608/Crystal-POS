from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Report
from .serializers import ReportSerializer

# Create your views here.

class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sales_report(request):
    """Generate sales report"""
    # Placeholder for sales report logic
    return Response({'message': 'Sales report endpoint'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def inventory_report(request):
    """Generate inventory report"""
    # Placeholder for inventory report logic
    return Response({'message': 'Inventory report endpoint'})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def customer_report(request):
    """Generate customer report"""
    # Placeholder for customer report logic
    return Response({'message': 'Customer report endpoint'})
