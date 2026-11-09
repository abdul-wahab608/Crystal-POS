from decimal import Decimal
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from .models import Customer, CustomerTransaction
from .serializers import CustomerSerializer, CustomerTransactionSerializer
from users.permissions import IsManagerUser, IsStaffUser
from core.mixins import BulkImportMixin, BulkExportMixin, BatchActionsMixin

class CustomerViewSet(BulkImportMixin, BulkExportMixin, BatchActionsMixin, viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    # Restrict detail lookups to numeric IDs so this blank-prefix viewset's
    # detail route doesn't shadow sibling resources (customer-transactions/) registered later in the same router.
    lookup_value_regex = r'\d+'

    def get_permissions(self):
        if self.request.method in SAFE_METHODS or self.action == 'create':
            return [IsAuthenticated(), IsStaffUser()]
        return [IsAuthenticated(), IsManagerUser()]

    def perform_destroy(self, instance):
        if instance.sales.exists() or instance.payments.exists() or instance.transactions.exists():
            raise ValidationError({'detail': f'{instance.name} has sales or payments and cannot be deleted. Mark them inactive instead.'})
        instance.delete()

    @action(detail=True, methods=['get'])
    def ledger(self, request, pk=None):
        customer = self.get_object()
        running = Decimal('0')
        rows = []
        for transaction in customer.transactions.order_by('date', 'id'):
            amount = transaction.amount
            if transaction.type == CustomerTransaction.SALE or (
                transaction.type == CustomerTransaction.REVERSAL and transaction.reverses == CustomerTransaction.PAYMENT
            ):
                running += amount
                debit, credit = amount, None
            else:
                running -= amount
                debit, credit = None, amount
            rows.append({
                'id': transaction.id,
                'date': transaction.date,
                'type': transaction.type,
                'reference': transaction.reference,
                'notes': transaction.notes,
                'debit': None if debit is None else str(debit),
                'credit': None if credit is None else str(credit),
                'balance': str(running),
            })
        return Response({'customer': CustomerSerializer(customer).data, 'rows': rows})

    # Batch update allowed fields
    batch_update_fields = ['is_active', 'city', 'customer_type']

    # Import configuration
    import_entity_type = 'customer'
    import_unique_fields = ['name']  # Check for duplicate by name
    import_fields = {
        'name': {
            'required': True,
            'type': 'string',
            'example': 'John Doe',
            'aliases': ['customer_name', 'full_name', 'customer'],
        },
        'phone': {
            'required': False,
            'type': 'string',
            'example': '+1234567890',
            'aliases': ['phone_number', 'mobile', 'contact', 'tel'],
        },
        'address': {
            'required': False,
            'type': 'string',
            'example': '123 Main St',
            'aliases': ['street_address', 'location'],
        },
        'city': {
            'required': False,
            'type': 'string',
            'example': 'New York',
            'aliases': ['town'],
        },
        'customer_type': {
            'required': False,
            'type': 'string',
            'example': 'WALK_IN',
            'aliases': ['type', 'customer kind'],
        },
        'balance': {
            'required': False,
            'type': 'decimal',
            'default': 0,
            'example': '0.00',
            'aliases': ['opening_balance', 'initial_balance', 'amount'],
        },
        'is_active': {
            'required': False,
            'type': 'boolean',
            'default': True,
            'example': 'true',
            'aliases': ['active', 'status'],
        },
    }

    # Export configuration
    export_filename = 'customers'
    export_fields = {
        'name': {'label': 'Customer Name', 'type': 'string'},
        'phone': {'label': 'Phone', 'type': 'string'},
        'address': {'label': 'Address', 'type': 'string'},
        'city': {'label': 'City', 'type': 'string'},
        'balance': {'label': 'Balance', 'type': 'decimal'},
        'is_active': {'label': 'Active', 'type': 'boolean'},
        'created_at': {'label': 'Created At', 'type': 'datetime'},
    }

class CustomerTransactionViewSet(viewsets.ModelViewSet):
    queryset = CustomerTransaction.objects.all()
    serializer_class = CustomerTransactionSerializer
    permission_classes = [IsAuthenticated, IsManagerUser]
