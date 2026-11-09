from decimal import Decimal

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APIClient

from customers.models import Customer
from products.models import Color, Product, ProductVariant, SizeRange
from users.models import User
from vendors.models import Vendor


class BusinessCycleTests(TestCase):
    def setUp(self):
        call_command('seed_catalog', verbosity=0)
        self.user = User.objects.create_user(username='owner', password='x', role=User.ADMIN)
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.size = SizeRange.objects.get(name='Men (40-46)')
        self.black = Color.objects.get(name='Black')

    def _post(self, url, data, expected=201):
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, expected, response.data)
        return response.data

    def test_purchase_sell_pay_and_report_cycle(self):
        product = self._post('/api/products/', {
            'name': 'Oxford', 'unit': 'DOZEN', 'cop': '800', 'quantity': 0, 'size_ranges': [self.size.id],
        })
        vendor = self._post('/api/vendors/', {'name': 'Chaman Leather'})
        customer = self._post('/api/customers/', {'name': 'Hafiz Shoes', 'city': 'Lahore'})

        self._post('/api/purchases/', {
            'vendor': vendor['id'],
            'items': [{'product': product['id'], 'size_range': self.size.id, 'color': self.black.id,
                       'quantity': 10, 'unit_cost': '600'}],
        })
        variant = ProductVariant.objects.get(product_id=product['id'], color=self.black)
        self.assertEqual(variant.quantity, 10)
        self.assertEqual(Product.objects.get(pk=product['id']).quantity, 10)
        self.assertEqual(Vendor.objects.get(pk=vendor['id']).balance, Decimal('6000'))

        sale = self._post('/api/sales/', {
            'customer': customer['id'],
            'sale_type': 'REGULAR',
            'items': [
                {'product_id': product['id'], 'size_range_id': self.size.id, 'color_id': self.black.id,
                 'quantity': 4, 'unit_price': '1200'},
                {'product_id': product['id'], 'size_range_id': self.size.id, 'color_id': self.black.id,
                 'quantity': 2, 'unit_price': '1000'},
            ],
            'amount_received': '3000',
            'payment_method': 'CASH',
        })
        self.assertEqual(Decimal(str(sale['total_amount'])), Decimal('6800'))
        self.assertEqual(sale['payment_status'], 'PARTIAL')
        variant.refresh_from_db()
        self.assertEqual(variant.quantity, 4)
        self.assertEqual(Product.objects.get(pk=product['id']).quantity, 4)

        self._post('/api/payments/', {
            'payment_type': 'OUTGOING', 'payment_method': 'CASH', 'amount': '2000', 'vendor': vendor['id'],
        })
        self.assertEqual(Vendor.objects.get(pk=vendor['id']).balance, Decimal('4000'))

        self.assertEqual(Customer.objects.get(pk=customer['id']).balance, Decimal('3800'))

        profit = self.client.get('/api/profit/summary/').data
        self.assertEqual(Decimal(str(profit['revenue'])), Decimal('6800'))
        self.assertEqual(Decimal(str(profit['cost'])), Decimal('4800'))
        self.assertEqual(Decimal(str(profit['profit_amount'])), Decimal('2000'))
        self.assertEqual(profit['quantity'], 6)

        sales_report = self.client.get('/api/reports/sales-report/').data
        self.assertEqual(Decimal(str(sales_report[0]['total_sales'])), Decimal('6800'))
        self.assertEqual(sales_report[0]['total_quantity'], 6)

        inventory = self.client.get('/api/reports/inventory-report/').data
        self.assertEqual(inventory[0]['quantity'], 4)

    def test_oversell_is_refused_and_leaves_stock_intact(self):
        product = self._post('/api/products/', {
            'name': 'Derby', 'unit': 'DOZEN', 'cop': '700', 'quantity': 0, 'size_ranges': [self.size.id],
        })
        vendor = self._post('/api/vendors/', {'name': 'Stock Vendor'})
        self._post('/api/purchases/', {
            'vendor': vendor['id'],
            'items': [{'product': product['id'], 'size_range': self.size.id, 'color': self.black.id,
                       'quantity': 2, 'unit_cost': '500'}],
        })
        customer = self._post('/api/customers/', {'name': 'Walk-in'})
        self._post('/api/sales/', {
            'customer': customer['id'], 'sale_type': 'REGULAR',
            'items': [{'product_id': product['id'], 'size_range_id': self.size.id, 'color_id': self.black.id,
                       'quantity': 3, 'unit_price': '900'}],
        }, expected=400)
        self.assertEqual(ProductVariant.objects.get(product_id=product['id']).quantity, 2)
