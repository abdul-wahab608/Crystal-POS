from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from payments.models import Payment
from products.models import Color, Product, ProductVariant, SizeRange
from raw_materials.models import RawMaterial
from vendors.models import Vendor, VendorTransaction
from .models import Purchase, PurchaseItem


class PurchaseAPITests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='buyer', password='x', role=get_user_model().MANAGER)
        self.client.force_authenticate(self.user)
        self.vendor = Vendor.objects.create(name='Acme Fabrics')
        self.size = SizeRange.objects.create(name='Standard')
        self.other_size = SizeRange.objects.create(name='Large')
        self.color = Color.objects.create(name='Black')
        self.cloth = Product.objects.create(name='Cloth', unit='PCS', cop=Decimal('10'), quantity=Decimal('5'), product_type='PURCHASED')
        self.cloth.size_ranges.add(self.size)
        self.thread = Product.objects.create(name='Thread', unit='PCS', cop=Decimal('2'), quantity=Decimal('0'), product_type='PURCHASED')
        self.thread.size_ranges.add(self.size)
        self.leather = RawMaterial.objects.create(name='Leather', unit='KG', quantity=Decimal('0'))

    def product_line(self, product, **overrides):
        line = {'product': product.id, 'size_range': self.size.id, 'color': self.color.id, 'quantity': 1, 'unit_cost': 1}
        line.update(overrides)
        return line

    def payload(self, items):
        return {'vendor': self.vendor.id, 'items': items}

    def test_create_with_several_lines_increments_stock_and_vendor_balance(self):
        response = self.client.post('/api/purchases/', self.payload([
            self.product_line(self.cloth, quantity='10', unit_cost='12.50'),
            self.product_line(self.thread, quantity=4, unit_cost=3),
        ]), format='json')

        self.assertEqual(response.status_code, 201, response.data)
        purchase = Purchase.objects.get(pk=response.data['id'])
        self.assertEqual(purchase.total_amount, Decimal('137.00'))
        self.assertEqual(len(response.data['items']), 2)
        self.assertEqual(response.data['items'][0]['product_name'], 'Cloth')
        self.assertEqual(PurchaseItem.objects.filter(purchase=purchase).count(), 2)

        self.cloth.refresh_from_db()
        self.thread.refresh_from_db()
        self.assertEqual(self.cloth.quantity, Decimal('15'))
        self.assertEqual(self.thread.quantity, Decimal('4'))
        self.assertEqual(ProductVariant.objects.get(product=self.cloth, size_range=self.size, color=self.color).quantity, Decimal('10'))

        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('137.00'))
        self.assertEqual(
            VendorTransaction.objects.filter(vendor=self.vendor, type=VendorTransaction.PURCHASE, amount=Decimal('137.00')).count(),
            1,
        )

    def test_mixed_raw_material_and_product_lines_in_one_document(self):
        response = self.client.post('/api/purchases/', {
            'vendor': self.vendor.id,
            'invoice_number': 'INV-77',
            'items': [
                {'raw_material': self.leather.id, 'quantity': '5', 'unit_cost': '100'},
                self.product_line(self.cloth, quantity=2, unit_cost=10),
            ],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['invoice_number'], 'INV-77')
        self.assertEqual(response.data['total_amount'], '520.00')
        self.leather.refresh_from_db()
        self.assertEqual(self.leather.quantity, Decimal('5'))

    def test_client_total_amount_is_ignored(self):
        response = self.client.post('/api/purchases/', {
            'vendor': self.vendor.id,
            'total_amount': '1.00',
            'items': [self.product_line(self.cloth, quantity=2, unit_cost=5)],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(response.data['total_amount'], '10.00')

    def test_staff_cannot_create_purchases(self):
        staff = get_user_model().objects.create_user(username='clerk', password='x', role=get_user_model().STAFF)
        self.client.force_authenticate(staff)
        response = self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth)]), format='json')
        self.assertEqual(response.status_code, 403)
        self.assertFalse(Purchase.objects.exists())

    def test_duplicate_vendor_bill_number_is_rejected(self):
        first = self.payload([self.product_line(self.cloth)])
        first['invoice_number'] = 'FH-001'
        self.assertEqual(self.client.post('/api/purchases/', first, format='json').status_code, 201)
        again = self.payload([self.product_line(self.cloth)])
        again['invoice_number'] = 'fh-001'
        response = self.client.post('/api/purchases/', again, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('invoice_number', response.data)
        self.assertEqual(Purchase.objects.count(), 1)

    def test_same_bill_number_from_another_vendor_is_allowed(self):
        first = self.payload([self.product_line(self.cloth)])
        first['invoice_number'] = 'FH-001'
        self.client.post('/api/purchases/', first, format='json')
        other = Vendor.objects.create(name='Other Mills')
        second = {'vendor': other.id, 'invoice_number': 'FH-001', 'items': [self.product_line(self.cloth)]}
        self.assertEqual(self.client.post('/api/purchases/', second, format='json').status_code, 201)

    def test_create_records_creator(self):
        response = self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth)]), format='json')
        self.assertEqual(response.status_code, 201, response.data)
        self.assertEqual(Purchase.objects.get(pk=response.data['id']).created_by, self.user)

    def test_create_without_items_is_rejected(self):
        response = self.client.post('/api/purchases/', self.payload([]), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('items', response.data)
        self.assertEqual(Purchase.objects.count(), 0)

    def test_create_with_unknown_product_is_400_and_writes_nothing(self):
        response = self.client.post('/api/purchases/', self.payload([
            self.product_line(self.cloth),
            {**self.product_line(self.thread), 'product': 99999},
        ]), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Purchase.objects.count(), 0)
        self.cloth.refresh_from_db()
        self.assertEqual(self.cloth.quantity, Decimal('5'))

    def test_line_needs_exactly_one_of_product_or_raw_material(self):
        neither = self.client.post('/api/purchases/', self.payload([{'quantity': 1, 'unit_cost': 1}]), format='json')
        self.assertEqual(neither.status_code, 400)
        both = self.client.post('/api/purchases/', self.payload([
            self.product_line(self.cloth, raw_material=self.leather.id),
        ]), format='json')
        self.assertEqual(both.status_code, 400)
        self.assertEqual(Purchase.objects.count(), 0)

    def test_product_line_requires_size_range_and_color(self):
        no_size = self.client.post('/api/purchases/', self.payload([
            {'product': self.cloth.id, 'color': self.color.id, 'quantity': 1, 'unit_cost': 1},
        ]), format='json')
        self.assertEqual(no_size.status_code, 400)
        no_color = self.client.post('/api/purchases/', self.payload([
            {'product': self.cloth.id, 'size_range': self.size.id, 'quantity': 1, 'unit_cost': 1},
        ]), format='json')
        self.assertEqual(no_color.status_code, 400)
        self.assertEqual(Purchase.objects.count(), 0)

    def test_product_line_size_range_must_belong_to_product(self):
        response = self.client.post('/api/purchases/', self.payload([
            self.product_line(self.cloth, size_range=self.other_size.id),
        ]), format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Purchase.objects.count(), 0)

    def test_raw_material_line_cannot_carry_size_or_color(self):
        response = self.client.post('/api/purchases/', self.payload([
            {'raw_material': self.leather.id, 'size_range': self.size.id, 'quantity': 1, 'unit_cost': 1},
        ]), format='json')
        self.assertEqual(response.status_code, 400)

    def test_quantity_and_cost_validation(self):
        response = self.client.post('/api/purchases/', self.payload([
            self.product_line(self.cloth, quantity=0),
            self.product_line(self.cloth, unit_cost=-1),
        ]), format='json')
        self.assertEqual(response.status_code, 400)

    def test_vendor_is_required(self):
        response = self.client.post('/api/purchases/', {'items': [self.product_line(self.cloth)]}, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('vendor', response.data)

    def test_list_and_retrieve_nest_items(self):
        self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth, quantity=3, unit_cost=2)]), format='json')
        listing = self.client.get('/api/purchases/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.data[0]['vendor_name'], 'Acme Fabrics')
        self.assertEqual(listing.data[0]['items'][0]['subtotal'], '6.00')
        self.assertEqual(listing.data[0]['items'][0]['unit'], 'PCS')
        self.assertEqual(listing.data[0]['items'][0]['color_name'], 'Black')
        detail = self.client.get(f"/api/purchases/{listing.data[0]['id']}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(len(detail.data['items']), 1)

    def test_delete_reverses_stock_and_vendor_balance(self):
        created = self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth, quantity=4, unit_cost=5)]), format='json')
        response = self.client.delete(f"/api/purchases/{created.data['id']}/")
        self.assertEqual(response.status_code, 204)
        self.cloth.refresh_from_db()
        self.vendor.refresh_from_db()
        self.assertEqual(self.cloth.quantity, Decimal('5'))
        self.assertEqual(self.vendor.balance, Decimal('0'))
        self.assertFalse(PurchaseItem.objects.exists())
        self.assertFalse(VendorTransaction.objects.filter(type=VendorTransaction.PURCHASE).exists())

    def test_delete_is_refused_when_purchased_stock_was_already_sold(self):
        created = self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth, quantity=4, unit_cost=5)]), format='json')
        ProductVariant.objects.filter(product=self.cloth).update(quantity=Decimal('1'))
        response = self.client.delete(f"/api/purchases/{created.data['id']}/")
        self.assertEqual(response.status_code, 400)
        self.assertTrue(Purchase.objects.filter(pk=created.data['id']).exists())

    def test_delete_is_refused_when_raw_material_was_already_used(self):
        created = self.client.post('/api/purchases/', self.payload([
            {'raw_material': self.leather.id, 'quantity': 10, 'unit_cost': 4},
        ]), format='json')
        RawMaterial.objects.filter(pk=self.leather.pk).update(quantity=Decimal('3'))
        response = self.client.delete(f"/api/purchases/{created.data['id']}/")
        self.assertEqual(response.status_code, 400)
        self.leather.refresh_from_db()
        self.assertEqual(self.leather.quantity, Decimal('3'))

    def test_delete_is_refused_while_vendor_payments_exist(self):
        created = self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth, quantity=4, unit_cost=5)]), format='json')
        purchase = Purchase.objects.get(pk=created.data['id'])
        Payment.objects.create(payment_type=Payment.OUTGOING, amount=Decimal('5'), vendor=self.vendor, purchase=purchase)
        response = self.client.delete(f'/api/purchases/{purchase.pk}/')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['detail'], f'Delete the vendor payments for Purchase #{purchase.pk} first')
        self.assertTrue(Purchase.objects.filter(pk=purchase.pk).exists())

    def test_vendor_ledger_lists_purchase_and_payments_in_order(self):
        self.user.role = 'MANAGER'
        self.client.force_authenticate(self.user)
        self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth, quantity=2, unit_cost=10)]), format='json')
        payment = self.client.post('/api/payments/', {
            'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': '5.00', 'vendor': self.vendor.id,
        }, format='json')
        self.assertEqual(payment.status_code, 201, payment.data)
        self.client.post('/api/purchases/', self.payload([{'raw_material': self.leather.id, 'quantity': 1, 'unit_cost': 3}]), format='json')
        response = self.client.get(f'/api/vendors/vendor-transactions/?vendor={self.vendor.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual([row['type'] for row in response.data], ['PURCHASE', 'PAYMENT', 'PURCHASE'])
        self.assertEqual([row['amount'] for row in response.data], ['20.00', '5.00', '3.00'])
        self.vendor.refresh_from_db()
        self.assertEqual(self.vendor.balance, Decimal('18.00'))

    def test_purchase_is_not_editable_in_place(self):
        created = self.client.post('/api/purchases/', self.payload([self.product_line(self.cloth)]), format='json')
        response = self.client.patch(f"/api/purchases/{created.data['id']}/", {'vendor': self.vendor.id}, format='json')
        self.assertEqual(response.status_code, 405)

    def test_requires_authentication(self):
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get('/api/purchases/').status_code, 401)


class PurchasePaymentStatusTests(APITestCase):
    def setUp(self):
        self.manager = get_user_model().objects.create_user(username='bill_clerk', password='x', role='MANAGER')
        self.client.force_authenticate(self.manager)
        self.vendor = Vendor.objects.create(name='Status Vendor')
        self.unpaid = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('300.00'))
        self.partial = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('400.00'))
        self.paid = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('100.00'))
        Payment.objects.create(payment_type=Payment.OUTGOING, payment_method=Payment.CASH,
                               amount=Decimal('150.00'), vendor=self.vendor, purchase=self.partial)
        Payment.objects.create(payment_type=Payment.OUTGOING, payment_method=Payment.CASH,
                               amount=Decimal('100.00'), vendor=self.vendor, purchase=self.paid)

    def test_each_bill_reports_paid_unpaid_and_status(self):
        rows = {row['id']: row for row in self.client.get('/api/purchases/').data}

        self.assertEqual(Decimal(rows[self.unpaid.id]['unpaid_amount']), Decimal('300.00'))
        self.assertEqual(rows[self.unpaid.id]['payment_status'], Purchase.UNPAID)
        self.assertEqual(Decimal(rows[self.partial.id]['paid_amount']), Decimal('150.00'))
        self.assertEqual(Decimal(rows[self.partial.id]['unpaid_amount']), Decimal('250.00'))
        self.assertEqual(rows[self.partial.id]['payment_status'], Purchase.PARTIAL)
        self.assertEqual(rows[self.paid.id]['payment_status'], Purchase.PAID)

    def test_unpaid_filter_excludes_fully_paid_bills(self):
        rows = self.client.get('/api/purchases/?unpaid=true').data

        self.assertEqual({row['id'] for row in rows}, {self.unpaid.id, self.partial.id})
