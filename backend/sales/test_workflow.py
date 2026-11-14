from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Product, ProductVariant, SizeRange, Color
from customers.models import Customer
from payments.models import Payment
from .models import Sale, SaleItem

User = get_user_model()


class SaleWorkflowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='clerk', password='pass', role=User.ADMIN)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(name='Ali Traders')
        self.size_s = SizeRange.objects.create(name='S')
        self.size_m = SizeRange.objects.create(name='M')
        self.red = Color.objects.create(name='Red')
        self.blue = Color.objects.create(name='Blue')
        self.product = Product.objects.create(
            name='Shirt', unit='PCS', cop=Decimal('50.00'), quantity=2400,
        )
        self.product.size_ranges.add(self.size_s, self.size_m)
        self.red_s = ProductVariant.objects.create(
            product=self.product, size_range=self.size_s, color=self.red, quantity=100)
        self.blue_m = ProductVariant.objects.create(
            product=self.product, size_range=self.size_m, color=self.blue, quantity=50)

    def line(self, size, color, dozens, price='100.00'):
        return {
            'product_id': self.product.id,
            'size_range_id': size.id,
            'color_id': color.id,
            'quantity': dozens,
            'unit_price': price,
        }

    def sale_payload(self, items, **extra):
        payload = {'customer': self.customer.id, 'sale_type': 'REGULAR', 'items': items}
        payload.update(extra)
        return payload

    def post_sale(self, items, **extra):
        return self.client.post('/api/sales/', self.sale_payload(items, **extra), format='json')

    def test_multi_line_sale_totals_stock_and_bill_no(self):
        resp = self.post_sale([self.line(self.size_s, self.red, 5), self.line(self.size_m, self.blue, 2, '50.50')])
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['total_amount'], '601.00')
        self.assertEqual(resp.data['payment_status'], 'UNPAID')
        self.assertEqual(resp.data['balance'], '601.00')
        self.assertEqual(resp.data['bill_no'], f"BILL-{resp.data['id']:04d}")
        self.assertEqual(len(resp.data['sale_items']), 2)
        self.red_s.refresh_from_db()
        self.blue_m.refresh_from_db()
        self.assertEqual(self.red_s.quantity, 95)
        self.assertEqual(self.blue_m.quantity, 48)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 2400 - 7)

    def test_sale_with_no_items_rejected(self):
        resp = self.post_sale([])
        self.assertEqual(resp.status_code, 400)
        self.assertIn('items', resp.data)

    def test_oversell_on_single_line(self):
        resp = self.post_sale([self.line(self.size_s, self.red, 101)])
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)

    def test_oversell_across_duplicate_lines(self):
        resp = self.post_sale([self.line(self.size_s, self.red, 60), self.line(self.size_s, self.red, 60)])
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)
        self.red_s.refresh_from_db()
        self.assertEqual(self.red_s.quantity, 100)

    def test_line_without_stock_record_rejected(self):
        resp = self.post_sale([self.line(self.size_m, self.red, 1)])
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)

    def test_unknown_product_returns_400_not_500(self):
        item = self.line(self.size_s, self.red, 1)
        item['product_id'] = 999999
        resp = self.post_sale([item])
        self.assertEqual(resp.status_code, 400)

    def test_missing_quantity_returns_400(self):
        item = self.line(self.size_s, self.red, 1)
        del item['quantity']
        resp = self.post_sale([item])
        self.assertEqual(resp.status_code, 400)

    def test_legacy_quantity_dozens_key_is_not_accepted(self):
        item = self.line(self.size_s, self.red, 1)
        item['quantity_dozens'] = item.pop('quantity')
        resp = self.post_sale([item])
        self.assertEqual(resp.status_code, 400)

    def test_partial_payment_at_sale_time(self):
        resp = self.post_sale(
            [self.line(self.size_s, self.red, 5)],
            amount_received='200.00', payment_method='CASH',
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['payment_status'], 'PARTIAL')
        self.assertEqual(resp.data['amount_paid'], '200.00')
        self.assertEqual(resp.data['balance'], '300.00')
        payment = Payment.objects.get(sale_id=resp.data['id'])
        self.assertEqual(payment.payment_type, Payment.INCOMING)
        self.assertEqual(payment.status, Payment.COMPLETED)
        self.assertEqual(payment.customer_id, self.customer.id)
        self.assertEqual(Payment.objects.count(), 1)

    def test_received_amount_without_method_rejected(self):
        resp = self.post_sale([self.line(self.size_s, self.red, 1)], amount_received='10.00')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('payment_method', resp.data)

    def test_received_more_than_total_rejected(self):
        resp = self.post_sale(
            [self.line(self.size_s, self.red, 1)], amount_received='100000.00', payment_method='CASH',
        )
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Sale.objects.count(), 0)

    def test_full_payment_sets_paid_and_partial_then_full(self):
        sale_id = self.post_sale([self.line(self.size_s, self.red, 5)]).data['id']
        pay = {'payment_type': 'INCOMING', 'payment_method': 'CASH', 'sale': sale_id, 'amount': '200.00', 'status': 'COMPLETED'}
        resp = self.client.post('/api/payments/', pay, format='json')
        self.assertEqual(resp.status_code, 201)
        sale = Sale.objects.get(pk=sale_id)
        self.assertEqual(sale.payment_status, 'PARTIAL')

        resp = self.client.post('/api/payments/', dict(pay, amount='300.00'), format='json')
        self.assertEqual(resp.status_code, 201)
        sale.refresh_from_db()
        self.assertEqual(sale.payment_status, 'PAID')

        sale_resp = self.client.get(f'/api/sales/{sale_id}/')
        self.assertEqual(sale_resp.data['balance'], '0.00')

    def test_overpayment_against_sale_rejected(self):
        sale_id = self.post_sale([self.line(self.size_s, self.red, 5)]).data['id']
        pay = {'payment_type': 'INCOMING', 'payment_method': 'CASH', 'sale': sale_id, 'amount': '500.01'}
        resp = self.client.post('/api/payments/', pay, format='json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('amount', resp.data)
        self.assertEqual(Payment.objects.count(), 0)

    def test_deleting_payment_reverts_sale_status(self):
        resp = self.post_sale([self.line(self.size_s, self.red, 5)], amount_received='500.00', payment_method='CASH')
        self.assertEqual(resp.data['payment_status'], 'PAID')
        payment = Payment.objects.get(sale_id=resp.data['id'])
        self.assertEqual(self.client.delete(f'/api/payments/{payment.id}/').status_code, 204)
        sale = Sale.objects.get(pk=resp.data['id'])
        self.assertEqual(sale.payment_status, 'UNPAID')

    def test_customer_balance_follows_sale_and_payment(self):
        sale_id = self.post_sale([self.line(self.size_s, self.red, 5)], amount_received='200.00', payment_method='CASH').data['id']
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('300.00'))
        self.client.delete(f'/api/payments/{Payment.objects.get(sale_id=sale_id).id}/')
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('500.00'))

    def test_delete_sale_restores_stock_and_reverses_balance(self):
        sale_id = self.post_sale([self.line(self.size_s, self.red, 5), self.line(self.size_m, self.blue, 2)]).data['id']
        self.assertEqual(self.client.delete(f'/api/sales/{sale_id}/').status_code, 204)
        self.red_s.refresh_from_db()
        self.blue_m.refresh_from_db()
        self.product.refresh_from_db()
        self.assertEqual(self.red_s.quantity, 100)
        self.assertEqual(self.blue_m.quantity, 50)
        self.assertEqual(self.product.quantity, 2400)
        self.assertFalse(SaleItem.objects.exists())
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('0'))

    def test_sale_items_cannot_be_patched_in(self):
        sale_id = self.post_sale([self.line(self.size_s, self.red, 5)]).data['id']
        resp = self.client.patch(f'/api/sales/{sale_id}/', {'items': [self.line(self.size_s, self.red, 1)]}, format='json')
        self.assertEqual(resp.status_code, 400)
        self.red_s.refresh_from_db()
        self.assertEqual(self.red_s.quantity, 95)

    def test_payment_status_cannot_be_set_by_client(self):
        resp = self.post_sale([self.line(self.size_s, self.red, 1)], payment_status='PAID')
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['payment_status'], 'UNPAID')

    def test_customer_cannot_be_changed_after_creation(self):
        sale_id = self.post_sale([self.line(self.size_s, self.red, 1)]).data['id']
        other = Customer.objects.create(name='Other')
        resp = self.client.patch(f'/api/sales/{sale_id}/', {'customer': other.id}, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_sale_item_endpoint_removed(self):
        self.assertEqual(self.client.get('/api/sales/sale-items/').status_code, 404)
