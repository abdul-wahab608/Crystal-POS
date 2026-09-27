from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from products.models import Product, ProductVariant, SizeRange, Color
from customers.models import Customer
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
            size_range=self.size_range,
        )
        ProductVariant.objects.create(
            product=self.product,
            size_range=self.size_range,
            color=self.color,
            quantity_dozens=100,
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
                'quantity_dozens': 5,
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
                'quantity_dozens': 9999,
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
                'quantity_dozens': 5,
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
        self.assertEqual(variant.quantity_dozens, 95)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, 1200 - (5 * 12))
