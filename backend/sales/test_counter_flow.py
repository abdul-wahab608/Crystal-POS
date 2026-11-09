from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient
from bank_accounts.models import BankAccount
from customers.models import Customer
from payments.models import Payment
from products.models import Color, Product, ProductVariant, SizeRange
from vendors.models import Vendor
from .models import Sale, SaleItem

User = get_user_model()


class CounterFlowTests(TestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='mgr', password='x', role=User.MANAGER)
        self.staff = User.objects.create_user(username='cashier', password='x', role=User.STAFF)
        self.client = APIClient()
        self.client.force_authenticate(self.manager)

        self.customer = Customer.objects.create(name='Shop A', city='Lahore')
        self.s = SizeRange.objects.create(name='S')
        self.m = SizeRange.objects.create(name='M')
        self.red = Color.objects.create(name='Red')
        self.blue = Color.objects.create(name='Blue')
        self.shirt = Product.objects.create(name='Shirt', unit='DOZEN', cop=Decimal('100'), quantity=0)
        self.shirt.size_ranges.add(self.s, self.m)
        self.variant_s_red = self.variant(self.s, self.red, 10)
        self.variant_s_blue = self.variant(self.s, self.blue, 4)
        self.variant_m_red = self.variant(self.m, self.red, 6)
        self.shirt.quantity = 20
        self.shirt.save()
        self.bank = BankAccount.objects.create(name='HBL Main', account_number='001', bank_name='HBL')

    def variant(self, size_range, color, quantity):
        return ProductVariant.objects.create(
            product=self.shirt, size_range=size_range, color=color, quantity=Decimal(quantity)
        )

    def line(self, size_range, color, quantity, unit_price='500.00'):
        return {
            'product_id': self.shirt.id, 'size_range_id': size_range.id, 'color_id': color.id,
            'quantity': str(quantity), 'unit_price': unit_price,
        }

    def post_sale(self, items, **extra):
        payload = {'customer': self.customer.id, 'sale_type': 'REGULAR', 'items': items}
        payload.update(extra)
        return self.client.post('/api/sales/', payload, format='json')

    def stock(self, variant):
        variant.refresh_from_db()
        return variant.quantity

    def test_multi_line_sale_across_sizes_and_colors(self):
        resp = self.post_sale([
            self.line(self.s, self.red, 3, '100.00'),
            self.line(self.s, self.blue, 2, '200.00'),
            self.line(self.m, self.red, 1, '300.00'),
        ])
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['total_amount'], '1000.00')
        self.assertEqual(SaleItem.objects.filter(sale_id=resp.data['id']).count(), 3)
        self.assertEqual(self.stock(self.variant_s_red), 7)
        self.assertEqual(self.stock(self.variant_s_blue), 2)
        self.assertEqual(self.stock(self.variant_m_red), 5)
        self.shirt.refresh_from_db()
        self.assertEqual(self.shirt.quantity, 14)

    def test_oversell_refused_per_variant_with_server_message(self):
        resp = self.post_sale([
            self.line(self.s, self.red, 7, '100.00'),
            self.line(self.s, self.blue, 5, '100.00'),
        ])
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Insufficient stock for Shirt (S, Blue): requested 5.00, available 4.00.', str(resp.data['items']))
        self.assertEqual(Sale.objects.count(), 0)
        self.assertEqual(self.stock(self.variant_s_red), 10)

    def test_oversell_across_duplicate_lines_of_same_variant(self):
        resp = self.post_sale([self.line(self.m, self.red, 4, '100.00'), self.line(self.m, self.red, 3, '100.00')])
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(self.stock(self.variant_m_red), 6)

    def test_deleting_sale_restores_stock_and_customer_balance(self):
        sale_id = self.post_sale([self.line(self.s, self.red, 4, '100.00')]).data['id']
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('400.00'))

        self.assertEqual(self.client.delete(f'/api/sales/{sale_id}/').status_code, 204)
        self.assertEqual(self.stock(self.variant_s_red), 10)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('0'))

    def test_partial_payment_at_counter_sets_partial_status(self):
        resp = self.post_sale(
            [self.line(self.s, self.red, 2, '500.00')],
            amount_received='300.00', payment_method='CASH',
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data['payment_status'], 'PARTIAL')
        self.assertEqual(resp.data['amount_paid'], '300.00')
        self.assertEqual(resp.data['balance'], '700.00')

    def test_later_payment_settles_sale_and_changes_customer_balance(self):
        sale_id = self.post_sale(
            [self.line(self.s, self.red, 2, '500.00')],
            amount_received='300.00', payment_method='CASH',
        ).data['id']
        resp = self.client.post('/api/payments/', {
            'payment_type': 'INCOMING', 'payment_method': 'BANK', 'amount': '700.00',
            'customer': self.customer.id, 'sale': sale_id, 'bank_account': self.bank.id,
        }, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)

        self.assertEqual(Sale.objects.get(pk=sale_id).payment_status, Sale.PAID)
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('0'))

    def test_customer_payment_changes_balance_and_ledger_in_date_order(self):
        self.post_sale([self.line(self.s, self.red, 1, '400.00')])
        self.client.post('/api/payments/', {
            'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '150.00',
            'customer': self.customer.id,
        }, format='json')
        self.post_sale([self.line(self.m, self.red, 1, '250.00')])

        resp = self.client.get(f'/api/customers/{self.customer.id}/ledger/')
        self.assertEqual(resp.status_code, 200)
        rows = resp.data['rows']
        self.assertEqual([row['type'] for row in rows], ['SALE', 'PAYMENT', 'SALE'])
        self.assertEqual([row['balance'] for row in rows], ['400.00', '250.00', '500.00'])
        self.assertEqual(rows[0]['debit'], '400.00')
        self.assertEqual(rows[1]['credit'], '150.00')
        self.assertEqual(resp.data['customer']['balance'], '500.00')

    def test_staff_can_create_sale_and_record_customer_payment(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.post_sale([self.line(self.s, self.red, 1)]).status_code, 201)
        resp = self.client.post('/api/payments/', {
            'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '50.00',
            'customer': self.customer.id,
        }, format='json')
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(Payment.objects.get(pk=resp.data['id']).status, Payment.COMPLETED)

    def test_staff_cannot_record_vendor_payment(self):
        self.client.force_authenticate(self.staff)
        vendor = Vendor.objects.create(name='Dye House')
        resp = self.client.post('/api/payments/', {
            'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': '50.00', 'vendor': vendor.id,
        }, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('payment_type', resp.data)

    def test_staff_cannot_delete_sale_or_payment_or_edit_or_delete_customer(self):
        sale_id = self.post_sale([self.line(self.s, self.red, 1)]).data['id']
        payment_id = self.client.post('/api/payments/', {
            'payment_type': 'INCOMING', 'payment_method': 'CASH', 'amount': '50.00',
            'customer': self.customer.id,
        }, format='json').data['id']
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.delete(f'/api/sales/{sale_id}/').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/payments/{payment_id}/').status_code, 403)
        self.assertEqual(self.client.delete(f'/api/customers/{self.customer.id}/').status_code, 403)
        self.assertEqual(
            self.client.patch(f'/api/customers/{self.customer.id}/', {'city': 'X'}, format='json').status_code, 403
        )

    def test_customer_with_sales_cannot_be_deleted(self):
        self.post_sale([self.line(self.s, self.red, 1)])
        resp = self.client.delete(f'/api/customers/{self.customer.id}/')
        self.assertEqual(resp.status_code, 400)
        self.assertTrue(Customer.objects.filter(pk=self.customer.id).exists())

    def test_sales_list_filters_by_customer_and_status(self):
        other = Customer.objects.create(name='Shop B')
        self.post_sale([self.line(self.s, self.red, 1)], amount_received='100.00', payment_method='CASH')
        self.client.post('/api/sales/', {
            'customer': other.id, 'items': [self.line(self.s, self.red, 1)],
        }, format='json')
        resp = self.client.get(f'/api/sales/?customer={self.customer.id}&payment_status=PARTIAL')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
