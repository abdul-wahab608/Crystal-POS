from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from .models import Customer, CustomerTransaction


class CustomerAPITests(APITestCase):
    def setUp(self):
        self.manager = get_user_model().objects.create_user(username='manager', password='x', role='MANAGER')
        self.client.force_authenticate(self.manager)

    def test_create_customer_with_city_and_type(self):
        response = self.client.post('/api/customers/', {
            'name': 'Ali Traders', 'phone': '0300', 'city': 'Karachi', 'customer_type': 'WALK_IN', 'is_active': True,
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['city'], 'Karachi')
        self.assertEqual(response.data['balance'], '0.00')

    def test_name_is_required(self):
        response = self.client.post('/api/customers/', {'name': '', 'is_active': True}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_invalid_customer_type_is_rejected(self):
        response = self.client.post('/api/customers/', {'name': 'X', 'customer_type': 'WHOLESALE'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_put_without_optional_fields_is_accepted(self):
        customer = Customer.objects.create(name='Old Name')
        response = self.client.put(f'/api/customers/{customer.id}/', {'name': 'New Name'}, format='json')
        self.assertEqual(response.status_code, 200, response.data)
        customer.refresh_from_db()
        self.assertEqual(customer.name, 'New Name')

    def test_delete_customer(self):
        customer = Customer.objects.create(name='Gone')
        self.assertEqual(self.client.delete(f'/api/customers/{customer.id}/').status_code, 204)
        self.assertFalse(Customer.objects.filter(pk=customer.id).exists())

    def test_payment_transaction_reduces_balance(self):
        customer = Customer.objects.create(name='Ali', balance=Decimal('250'))
        response = self.client.post('/api/customers/customer-transactions/', {
            'customer': customer.id, 'type': CustomerTransaction.PAYMENT, 'amount': '100.00', 'reference': 'CASH',
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        customer.refresh_from_db()
        self.assertEqual(customer.balance, Decimal('150.00'))

    def test_sale_transaction_increases_balance(self):
        customer = Customer.objects.create(name='Ali')
        self.client.post('/api/customers/customer-transactions/', {
            'customer': customer.id, 'type': CustomerTransaction.SALE, 'amount': '75.50',
        }, format='json')
        customer.refresh_from_db()
        self.assertEqual(customer.balance, Decimal('75.50'))

    def test_non_positive_transaction_amount_is_rejected(self):
        customer = Customer.objects.create(name='Ali')
        response = self.client.post('/api/customers/customer-transactions/', {
            'customer': customer.id, 'type': CustomerTransaction.PAYMENT, 'amount': '0',
        }, format='json')
        self.assertEqual(response.status_code, 400)

    def test_staff_cannot_post_transactions(self):
        staff = get_user_model().objects.create_user(username='staff', password='x', role='STAFF')
        self.client.force_authenticate(staff)
        customer = Customer.objects.create(name='Ali')
        response = self.client.post('/api/customers/customer-transactions/', {
            'customer': customer.id, 'type': CustomerTransaction.PAYMENT, 'amount': '10',
        }, format='json')
        self.assertEqual(response.status_code, 403)
