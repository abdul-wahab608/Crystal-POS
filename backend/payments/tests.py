from sales.models import Sale
from purchases.models import Purchase
from customers.models import Customer
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from payments.models import Payment
from vendors.models import Vendor, VendorTransaction


class OnAccountVendorPaymentTests(APITestCase):
    def setUp(self):
        self.manager = get_user_model().objects.create_user(username='manager', password='x', role=get_user_model().MANAGER)
        self.client.force_authenticate(self.manager)
        self.vendor = Vendor.objects.create(name='Denim Mills')
        VendorTransaction.objects.create(vendor=self.vendor, type=VendorTransaction.PURCHASE, amount=Decimal('100'))

    def pay(self, amount):
        return self.client.post('/api/payments/', {
            'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': amount,
            'payment_date': '2026-11-14', 'vendor': self.vendor.id,
        }, format='json')

    def test_payment_above_amount_owed_is_accepted_and_leaves_vendor_owing_us(self):
        response = self.pay('150.00')
        self.assertEqual(response.status_code, 201, response.content)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('-50.00'))

    def test_payment_up_to_amount_owed_is_accepted(self):
        self.assertEqual(self.pay('100.00').status_code, 201)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('0'))

    def test_payment_to_vendor_with_nothing_owed_leaves_negative_balance(self):
        self.pay('100.00')
        response = self.pay('1.00')
        self.assertEqual(response.status_code, 201, response.content)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('-1.00'))


class ParchiPaymentTests(APITestCase):
    def setUp(self):
        self.manager = get_user_model().objects.create_user(username='parchi_mgr', password='pw', role='MANAGER')
        self.client.force_authenticate(self.manager)
        self.vendor = Vendor.objects.create(name='Parchi Mills')
        self.customer = Customer.objects.create(name='Parchi Buyer')

    def pay(self, **overrides):
        payload = {'payment_method': 'PARCHI', 'amount': '40.00', 'payment_date': '2026-11-14'}
        payload.update(overrides)
        return self.client.post('/api/payments/', payload, format='json')

    def test_outgoing_parchi_on_purchase_updates_status_and_vendor_balance(self):
        purchase = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('100'))
        response = self.pay(payment_type='OUTGOING', vendor=self.vendor.id, purchase=purchase.id)
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data['payment_method'], Payment.PARCHI)
        purchase.refresh_from_db()
        self.assertEqual(purchase.payment_status, Purchase.PARTIAL)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('60.00'))

        response = self.pay(payment_type='OUTGOING', vendor=self.vendor.id, purchase=purchase.id, amount='60.00')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(purchase.payment_status, Purchase.PAID)
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('0'))

    def test_outgoing_parchi_is_refused_above_the_bill(self):
        purchase = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('100'))
        response = self.pay(payment_type='OUTGOING', vendor=self.vendor.id, purchase=purchase.id, amount='150.00')
        self.assertEqual(response.status_code, 400)

    def test_incoming_parchi_on_sale_updates_sale_status_and_customer_balance(self):
        sale = Sale.objects.create(customer=self.customer, total_amount=Decimal('200'))
        response = self.pay(payment_type='INCOMING', customer=self.customer.id, sale=sale.id, amount='50.00')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertEqual(response.data['payment_method'], Payment.PARCHI)
        sale.refresh_from_db()
        self.assertEqual(sale.payment_status, Sale.PARTIAL)
        self.assertEqual(sale.amount_paid(), Decimal('50.00'))
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('150.00'))
