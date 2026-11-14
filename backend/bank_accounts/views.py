from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from users.permissions import IsManagerUser
from .models import BankAccount
from .serializers import BankAccountSerializer

# Create your views here.

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return super().get_permissions()
        return [IsAuthenticated(), IsManagerUser()]
