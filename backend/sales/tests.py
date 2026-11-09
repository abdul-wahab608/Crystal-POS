from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Product, ProductVariant, SizeRange, Color
from customers.models import Customer, CustomerTransaction
from payments.models import Payment
from .models import Sale, SaleItem

User = get_user_model()


class SaleSerializerDecimalTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='pass', role=User.ADMIN
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        self.customer = Customer.objects.create(name='Test Customer')
        self.size_range = SizeRange.objects.create(name='S')
        self.color = Color.objects.create(name='Red')
        self.product = Product.objects.create(
            name='Test Product', unit='PCS', cop=Decimal('50.00'), quantity=1200,
        )
        self.product.size_ranges.add(self.size_range)
        ProductVariant.objects.create(
            product=self.product,
            size_range=self.size_range,
            color=self.color,
            quantity=100,
        )

    def _post_sale(self, unit_price):
        return self.client.post('/api/sales/', {
            'customer': self.customer.id,
            'sale_type': 'REGULAR',
            'total_amount': '500.00',
            'payment_status': 'PAID',
            'items': [{
                'product_id': self.product.id,
                'size_range_id': self.size_range.id,
                'color_id': self.color.id,
                'quantity': 5,
                'unit_price': unit_price,
            }],
        }, format='json')

    def test_unit_price_as_number(self):
        resp = self._post_sale(100)
        self.assertEqual(resp.status_code, 201)
        item = SaleItem.objects.get(sale_id=resp.data['id'])
        self.assertEqual(item.subtotal, Decimal('500'))

    def test_unit_price_as_string(self):
        resp = self._post_sale('100.00')
        self.assertEqual(resp.status_code, 201)
        item = SaleItem.objects.get(sale_id=resp.data['id'])
        self.assertEqual(item.subtotal, Decimal('500.00'))

    def test_unit_price_as_float_string(self):
        resp = self._post_sale('99.99')
        self.assertEqual(resp.status_code, 201)
        item = SaleItem.objects.get(sale_id=resp.data['id'])
        self.assertEqual(item.subtotal, Decimal('99.99') * 5)

    def test_oversell_guard(self):
        resp = self._post_sale('100.00')
        self.assertEqual(resp.status_code, 201)

        resp2 = self.client.post('/api/sales/', {
            'customer': self.customer.id,
            'sale_type': 'REGULAR',
            'total_amount': '100000.00',
            'payment_status': 'PAID',
            'items': [{
                'product_id': self.product.id,
                'size_range_id': self.size_range.id,
                'color_id': self.color.id,
                'quantity': 9999,
                'unit_price': '100.00',
            }],
        }, format='json')
        self.assertEqual(resp2.status_code, 400)

    def test_color_required(self):
        resp = self.client.post('/api/sales/', {
            'customer': self.customer.id,
            'sale_type': 'REGULAR',
            'total_amount': '500.00',
            'payment_status': 'PAID',
            'items': [{
                'product_id': self.product.id,
                'size_range_id': self.size_range.id,
                'quantity': 5,
                'unit_price': 100,
            }],
        }, format='json')
        self.assertEqual(resp.status_code, 400)

    def test_stock_deducted(self):
        resp = self._post_sale(100)
        self.assertEqual(resp.status_code, 201)
        variant = ProductVariant.objects.get(
            product=self.product, size_range=self.size_range, color=self.color
        )
        self.assertEqual(variant.quantity, 95)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 1200 - 5)


class SaleDeleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='owner', password='pass', role=User.ADMIN)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(name='Credit Customer')
        self.size_range = SizeRange.objects.create(name='M')
        self.color = Color.objects.create(name='Blue')
        self.product = Product.objects.create(name='Shirt', unit='PCS', cop=Decimal('50'), quantity=100)
        self.product.size_ranges.add(self.size_range)
        self.variant = ProductVariant.objects.create(
            product=self.product, size_range=self.size_range, color=self.color, quantity=100,
        )

    def _create_sale_with_part_payment(self):
        response = self.client.post('/api/sales/', {
            'customer': self.customer.id,
            'sale_type': 'REGULAR',
            'total_amount': '500.00',
            'payment_status': 'UNPAID',
            'items': [{
                'product_id': self.product.id,
                'size_range_id': self.size_range.id,
                'color_id': self.color.id,
                'quantity': 5,
                'unit_price': '100.00',
            }],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.data)
        sale = Sale.objects.get(pk=response.data['id'])
        Payment.objects.create(
            payment_type=Payment.INCOMING, payment_method=Payment.CASH,
            amount=Decimal('200.00'), customer=self.customer, sale=sale,
        )
        return sale

    def test_delete_removes_payments_restores_stock_and_clears_balance(self):
        sale = self._create_sale_with_part_payment()
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('300.00'))

        response = self.client.delete(f'/api/sales/{sale.pk}/')
        self.assertEqual(response.status_code, 204)

        self.customer.refresh_from_db()
        self.assertEqual(self.customer.balance, Decimal('0'))
        self.assertFalse(Payment.objects.filter(customer=self.customer).exists())
        self.assertFalse(Sale.objects.filter(pk=sale.pk).exists())
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, 100)
        summary = self.client.get('/api/payments/summary/')
        self.assertEqual(Decimal(str(summary.data['total_incoming'])), Decimal('0'))

    def test_sale_reversal_is_written_once_as_reversal_row(self):
        sale = self._create_sale_with_part_payment()
        self.client.delete(f'/api/sales/{sale.pk}/')
        reversals = CustomerTransaction.objects.filter(type=CustomerTransaction.REVERSAL, reference=sale.bill_no)
        self.assertEqual(reversals.count(), 1)
        self.assertEqual(reversals.get().reverses, CustomerTransaction.SALE)
        self.assertEqual(CustomerTransaction.objects.filter(type=CustomerTransaction.SALE, reference=sale.bill_no).count(), 1)

    def test_staff_cannot_delete_a_sale(self):
        sale = self._create_sale_with_part_payment()
        staff = User.objects.create_user(username='clerk', password='pass', role=User.STAFF)
        self.client.force_authenticate(user=staff)
        response = self.client.delete(f'/api/sales/{sale.pk}/')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Sale.objects.filter(pk=sale.pk).exists())
