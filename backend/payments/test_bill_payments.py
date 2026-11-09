from decimal import Decimal

from rest_framework.test import APITestCase

from payments.models import Payment
from purchases.models import Purchase
from users.models import User
from vendors.models import Vendor


class BillPaymentTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='bill_mgr', password='pw', role=User.MANAGER)
        self.client.force_authenticate(self.manager)
        self.vendor = Vendor.objects.create(name='Bill Vendor')
        self.other_vendor = Vendor.objects.create(name='Other Vendor')
        self.bill = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('500.00'))

    def pay_bill(self, amount, purchase=None, vendor=None):
        payload = {
            'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': str(amount),
            'vendor': (vendor or self.vendor).id,
            'purchase': (purchase or self.bill).id,
        }
        return self.client.post('/api/payments/', payload, format='json')

    def vendor_balance(self):
        self.vendor.refresh_from_db()
        return self.vendor.balance

    def test_payment_against_bill_reduces_vendor_balance_and_unpaid_amount(self):
        response = self.pay_bill('200.00')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], Payment.COMPLETED)
        self.assertEqual(self.vendor_balance(), Decimal('300.00'))
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.unpaid_amount(), Decimal('300.00'))
        self.assertEqual(self.bill.payment_status, Purchase.PARTIAL)

    def test_full_payment_marks_bill_paid(self):
        self.assertEqual(self.pay_bill('500.00').status_code, 201)

        self.assertEqual(self.bill.payment_status, Purchase.PAID)
        self.assertEqual(self.bill.unpaid_amount(), Decimal('0'))

    def test_overpaying_a_bill_is_refused(self):
        self.pay_bill('200.00')

        response = self.pay_bill('400.00')

        self.assertEqual(response.status_code, 400)
        self.assertIn('amount', response.data)
        self.assertEqual(Payment.objects.filter(purchase=self.bill).count(), 1)
        self.assertEqual(self.vendor_balance(), Decimal('300.00'))

    def test_payment_against_another_vendors_bill_is_refused(self):
        response = self.pay_bill('100.00', vendor=self.other_vendor)

        self.assertEqual(response.status_code, 400)
        self.assertIn('vendor', response.data)
        self.assertFalse(Payment.objects.exists())

    def test_bill_can_be_named_without_vendor(self):
        payload = {'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': '100.00', 'purchase': self.bill.id}
        response = self.client.post('/api/payments/', payload, format='json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['vendor'], self.vendor.id)

    def test_only_outgoing_payments_can_name_a_bill(self):
        payload = {
            'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '100.00',
            'customer': None, 'purchase': self.bill.id,
        }
        response = self.client.post('/api/payments/', payload, format='json')

        self.assertEqual(response.status_code, 400)
        self.assertIn('purchase', response.data)

    def test_deleting_bill_payment_restores_vendor_balance_and_unpaid_amount(self):
        response = self.pay_bill('200.00')

        self.assertEqual(self.client.delete(f"/api/payments/{response.data['id']}/").status_code, 204)

        self.assertEqual(self.vendor_balance(), Decimal('500.00'))
        self.bill.refresh_from_db()
        self.assertEqual(self.bill.unpaid_amount(), Decimal('500.00'))
        self.assertEqual(self.bill.payment_status, Purchase.UNPAID)

    def test_bill_link_cannot_change_after_recording(self):
        response = self.pay_bill('200.00')
        other_bill = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('100.00'))

        update = self.client.patch(f"/api/payments/{response.data['id']}/", {'purchase': other_bill.id}, format='json')

        self.assertEqual(update.status_code, 400)
        self.assertIn('purchase', update.data)
