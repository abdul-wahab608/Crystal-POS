from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from payments.models import Payment
from products.models import Product, SizeRange
from .models import Vendor, VendorProduct, VendorTransaction


class VendorAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='buyer', password='x')
        self.client.force_authenticate(self.user)

    def test_create_vendor_without_phone_or_contact(self):
        response = self.client.post('/api/vendors/', {'name': 'Bare Vendor', 'is_active': True}, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['balance'], '0.00')

    def test_name_is_required(self):
        response = self.client.post('/api/vendors/', {'name': '  ', 'is_active': True}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_duplicate_name_is_rejected_case_insensitively(self):
        Vendor.objects.create(name='Acme')
        response = self.client.post('/api/vendors/', {'name': 'acme', 'is_active': True}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_keeps_own_name_and_rejects_others(self):
        acme = Vendor.objects.create(name='Acme')
        Vendor.objects.create(name='Beta')
        self.assertEqual(self.client.patch(f'/api/vendors/{acme.id}/', {'name': 'Acme', 'city': 'Lahore'}, format='json').status_code, 200)
        self.assertEqual(self.client.patch(f'/api/vendors/{acme.id}/', {'name': 'Beta'}, format='json').status_code, 400)

    def test_null_contact_person_does_not_break_list(self):
        Vendor.objects.create(name='No Contact', contact_person=None)
        response = self.client.get('/api/vendors/')
        self.assertEqual(response.status_code, 200)

    def test_ledger_is_read_only(self):
        vendor = Vendor.objects.create(name='Acme', balance=Decimal('100'))
        response = self.client.post('/api/vendors/vendor-transactions/', {
            'vendor': vendor.id, 'type': VendorTransaction.PAYMENT, 'amount': '40.00',
        }, format='json')
        self.assertEqual(response.status_code, 405)
        vendor.refresh_from_db()
        self.assertEqual(vendor.balance, Decimal('100'))

    def test_ledger_filters_by_vendor(self):
        acme = Vendor.objects.create(name='Acme')
        beta = Vendor.objects.create(name='Beta')
        VendorTransaction.objects.create(vendor=acme, type=VendorTransaction.PURCHASE, amount=Decimal('10'))
        VendorTransaction.objects.create(vendor=beta, type=VendorTransaction.PURCHASE, amount=Decimal('20'))
        response = self.client.get(f'/api/vendors/vendor-transactions/?vendor={acme.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row['vendor'] for row in response.data], [acme.id])

    def test_balance_cannot_be_set_by_update(self):
        vendor = Vendor.objects.create(name='Acme', balance=Decimal('100'))
        response = self.client.patch(f'/api/vendors/{vendor.id}/', {'balance': '0'}, format='json')
        self.assertEqual(response.status_code, 200)
        vendor.refresh_from_db()
        self.assertEqual(vendor.balance, Decimal('100'))

    def test_vendor_with_payments_cannot_be_deleted(self):
        vendor = Vendor.objects.create(name='Acme')
        Payment.objects.create(payment_type=Payment.OUTGOING, payment_method=Payment.CASH, amount=Decimal('10'), vendor=vendor)
        response = self.client.delete(f'/api/vendors/{vendor.id}/')
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Vendor.objects.filter(pk=vendor.pk).exists())

    def test_vendor_product_requires_matching_item(self):
        vendor = Vendor.objects.create(name='Acme')
        size = SizeRange.objects.create(name='Standard')
        product = Product.objects.create(name='Cloth', unit='PCS', cop=Decimal('1'))
        product.size_ranges.add(size)
        url = '/api/vendors/vendor-products/'

        neither = self.client.post(url, {'vendor': vendor.id, 'product_type': 'PRODUCT', 'unit_price': '5'}, format='json')
        self.assertEqual(neither.status_code, 400)

        mismatch = self.client.post(url, {'vendor': vendor.id, 'product_type': 'RAW_MATERIAL', 'product': product.id, 'unit_price': '5'}, format='json')
        self.assertEqual(mismatch.status_code, 400)

        ok = self.client.post(url, {'vendor': vendor.id, 'product_type': 'PRODUCT', 'product': product.id, 'unit_price': '5'}, format='json')
        self.assertEqual(ok.status_code, 201, ok.data)
        self.assertEqual(VendorProduct.objects.count(), 1)
