from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from customers.models import Customer, CustomerTransaction
from vendors.models import Vendor
from sales.models import Sale
from .models import Payment

User = get_user_model()


class PaymentWorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='clerk', password='pass', role=User.ADMIN)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(name='Ali Traders')
        self.vendor = Vendor.objects.create(name='Fabric Co')
        self.sale = Sale.objects.create(customer=self.customer, total_amount=Decimal('400.00'), created_by=self.user)

    def pay(self, **extra):
        payload = {'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '100.00', 'customer': self.customer.id}
        payload.update(extra)
        return self.client.post('/api/payments/', payload, format='json')

    def make_payment(self, amount):
        return Payment.objects.latest('id') if self.pay(amount=amount).status_code == 201 else None

    def test_incoming_requires_customer(self):
        resp = self.client.post('/api/payments/', {'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '10'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('customer', resp.data)

    def test_outgoing_requires_vendor(self):
        resp = self.client.post('/api/payments/', {'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': '10'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('vendor', resp.data)

    def test_non_positive_amount_rejected(self):
        self.assertEqual(self.pay(amount='0').status_code, 400)
        self.assertEqual(self.pay(amount='-5').status_code, 400)

    def test_bank_transfer_requires_bank_account(self):
        resp = self.pay(payment_method='BANK')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('bank_account', resp.data)

    def test_sale_link_fills_customer_and_rejects_outgoing(self):
        resp = self.client.post('/api/payments/', {
            'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '50', 'sale': self.sale.id,
        }, format='json')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['customer'], self.customer.id)
        resp = self.client.post('/api/payments/', {
            'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': '50', 'vendor': self.vendor.id, 'sale': self.sale.id,
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_payment_customer_must_match_sale_customer(self):
        other = Customer.objects.create(name='Other')
        resp = self.pay(sale=self.sale.id, customer=other.id)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('customer', resp.data)

    def test_customer_payment_reduces_balance(self):
        self.assertEqual(self.pay(amount='75.00').status_code, 201)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('325.00'))
        self.assertTrue(CustomerTransaction.objects.filter(type=CustomerTransaction.PAYMENT).exists())

    def test_locked_money_fields_cannot_change_on_update(self):
        payment = self.make_payment("100.00")
        resp = self.client.patch(f'/api/payments/{payment.id}/', {'amount': '999.00'}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('amount', resp.data)
        resp = self.client.patch(f'/api/payments/{payment.id}/', {'reference': 'CHQ-1', 'payment_method': 'CHEQUE'}, format='json')
        self.assertEqual(resp.status_code, 200)
        payment.refresh_from_db()
        self.assertEqual(payment.reference, 'CHQ-1')
        self.assertEqual(payment.amount, Decimal('100.00'))

    def test_edit_with_unchanged_locked_fields_allowed(self):
        payment = self.make_payment("100.00")
        resp = self.client.patch(f'/api/payments/{payment.id}/', {
            'payment_type': 'INCOMING', 'amount': '100.00', 'customer': self.customer.id, 'notes': 'paid',
        }, format='json')
        self.assertEqual(resp.status_code, 200)

    def test_delete_customer_payment_reverses_balance(self):
        payment = self.make_payment('75.00')
        self.assertEqual(self.client.delete(f'/api/payments/{payment.id}/').status_code, 204)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('400.00'))

    def test_summary_and_filter_by_sale(self):
        self.client.post('/api/payments/', {
            'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '50', 'sale': self.sale.id,
        }, format='json')
        resp = self.client.get(f'/api/payments/?sale={self.sale.id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(self.client.get('/api/payments/summary/').status_code, 200)
