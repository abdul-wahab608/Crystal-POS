from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient

from customers.models import Customer
from products.models import Color, Product, ProductVariant, SizeRange
from sales.models import Sale, SaleItem
from users.models import User


class ReportsArithmeticTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='rep_user', password='pw', role=User.STAFF)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        size = SizeRange.objects.create(name='Rep Size')
        color = Color.objects.create(name='Rep Color')
        self.product = Product.objects.create(name='Rep Widget', unit='PCS', cop=Decimal('10.00'), quantity=0)
        self.product.size_ranges.add(size)
        self.variant = ProductVariant.objects.create(product=self.product, size_range=size, color=color,
                                                     quantity=7)
        lahore = Customer.objects.create(name='Lahore Buyer', city='Lahore')
        karachi = Customer.objects.create(name='Karachi Buyer', city='Karachi')

        self._sale(lahore, datetime(2026, 1, 15, 9, 0), size, color, 10, Decimal('100.00'))
        self._sale(lahore, datetime(2026, 4, 20, 15, 30), size, color, 5, Decimal('110.00'))
        self._sale(karachi, datetime(2026, 4, 20, 18, 0), size, color, 8, Decimal('30.00'))

    def _sale(self, customer, when, size, color, dozens, unit_price):
        sale = Sale.objects.create(customer=customer, total_amount=unit_price * dozens)
        Sale.objects.filter(pk=sale.pk).update(date=timezone.make_aware(when))
        SaleItem.objects.create(sale=sale, product=self.product, size_range=size, color=color,
                                quantity=dozens, unit_price=unit_price, subtotal=unit_price * dozens)

    def test_sales_summary_groups_by_date(self):
        rows = self.client.get('/api/reports/sales-report/').data
        by_date = {str(r['date']): r for r in rows}
        self.assertEqual(Decimal(by_date['2026-01-15']['total_sales']), Decimal('1000.00'))
        self.assertEqual(by_date['2026-01-15']['total_quantity'], 10)
        self.assertEqual(Decimal(by_date['2026-04-20']['total_sales']), Decimal('790.00'))
        self.assertEqual(by_date['2026-04-20']['total_quantity'], 13)
        self.assertEqual(by_date['2026-04-20']['transaction_count'], 2)

    def test_end_date_includes_sales_later_that_day(self):
        rows = self.client.get('/api/reports/sales-report/', {'end_date': '2026-04-20'}).data
        self.assertEqual(sum(r['total_quantity'] for r in rows), 23)

    def test_customer_report_totals(self):
        rows = {r['customer_name']: r for r in self.client.get('/api/reports/customer-report/').data}
        self.assertEqual(rows['Lahore Buyer']['total_sales'], 1550.0)
        self.assertEqual(rows['Lahore Buyer']['total_quantity'], 15)
        self.assertEqual(rows['Lahore Buyer']['sale_count'], 2)
        self.assertEqual(rows['Karachi Buyer']['total_sales'], 240.0)

    def test_area_report_totals(self):
        rows = {r['area']: r for r in self.client.get('/api/reports/area-report/').data}
        self.assertEqual(rows['Lahore']['total_sales'], 1550.0)
        self.assertEqual(rows['Lahore']['customer_count'], 1)
        self.assertEqual(rows['Karachi']['total_quantity'], 8)

    def test_article_report_totals(self):
        rows = self.client.get('/api/reports/article-report/').data
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['total_sales'], 1790.0)
        self.assertEqual(rows[0]['total_quantity'], 23)
        self.assertEqual(rows[0]['sale_count'], 3)

    def test_customer_sales_detail_totals(self):
        rows = self.client.get('/api/reports/customer-sales/').data
        lahore = [r for r in rows if r['customer_name'] == 'Lahore Buyer']
        self.assertEqual(sum(r['total_sales'] for r in lahore), 1550.0)

    def test_inventory_report_shows_stock_in_product_unit(self):
        rows = self.client.get('/api/reports/inventory-report/').data
        self.assertEqual(rows, [{'product__name': 'Rep Widget', 'size_range__name': 'Rep Size',
                                 'color__name': 'Rep Color', 'product__unit': 'PCS', 'quantity': 7}])


class DashboardSummaryTests(TestCase):
    def setUp(self):
        from payments.models import Payment
        from raw_materials.models import RawMaterial
        from vendors.models import Vendor

        self.user = User.objects.create_user(username='dash_user', password='pw', role=User.STAFF)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        size = SizeRange.objects.create(name='Dash Size')
        color = Color.objects.create(name='Dash Color')
        self.product = Product.objects.create(name='Dash Widget', unit='DOZEN', cop=Decimal('10.00'), quantity=4)
        self.product.size_ranges.add(size)
        self.out_of_stock_product = Product.objects.create(name='Dash Empty', unit='PCS', cop=Decimal('1.00'), quantity=0)
        ProductVariant.objects.create(product=self.product, size_range=size, color=color, quantity=4)

        self.customer = Customer.objects.create(name='Dash Buyer', city='Lahore')
        Customer.objects.create(name='Dash Clear', city='Lahore', balance=Decimal('-50.00'))
        Vendor.objects.create(name='Dash Vendor', balance=Decimal('300.00'))

        sale = Sale.objects.create(customer=self.customer, total_amount=Decimal('800.00'))
        SaleItem.objects.create(sale=sale, product=self.product, size_range=size, color=color,
                                quantity=Decimal('2'), unit_price=Decimal('400.00'), subtotal=Decimal('800.00'))
        Payment.objects.create(payment_type=Payment.INCOMING, payment_method=Payment.CASH,
                               amount=Decimal('200.00'), customer=self.customer, sale=sale)
        RawMaterial.objects.create(name='Dash Thread', unit='KG', quantity=Decimal('1'), reorder_level=Decimal('5'))
        RawMaterial.objects.create(name='Dash Dye', unit='KG', quantity=Decimal('50'), reorder_level=Decimal('5'))

    def test_dashboard_kpis(self):
        data = self.client.get('/api/reports/dashboard/').data
        self.assertEqual(Decimal(str(data['today']['sales_total'])), Decimal('800.00'))
        self.assertEqual(data['today']['sales_count'], 1)
        self.assertEqual(Decimal(str(data['today']['received_total'])), Decimal('200.00'))
        self.assertEqual(Decimal(str(data['month']['sales_total'])), Decimal('800.00'))
        self.assertEqual(Decimal(str(data['month']['received_total'])), Decimal('200.00'))
        self.assertEqual(Decimal(str(data['outstanding_customer_balance'])), Decimal('600.00'))
        self.assertEqual(Decimal(str(data['vendor_payables'])), Decimal('300.00'))
        self.assertEqual(data['low_stock_raw_materials'], 1)
        self.assertEqual(data['out_of_stock_products'], 1)

    def test_dashboard_vendor_bills_unpaid_total(self):
        from payments.models import Payment
        from purchases.models import Purchase
        from vendors.models import Vendor
        vendor = Vendor.objects.get(name='Dash Vendor')
        bill = Purchase.objects.create(vendor=vendor, total_amount=Decimal('1000.00'))
        Purchase.objects.create(vendor=vendor, total_amount=Decimal('250.00'))
        Payment.objects.create(payment_type=Payment.OUTGOING, payment_method=Payment.CASH,
                               amount=Decimal('250.00'), vendor=vendor, purchase=bill)
        data = self.client.get('/api/reports/dashboard/').data
        self.assertEqual(Decimal(str(data['vendor_bills_unpaid'])), Decimal('1000.00'))

    def test_dashboard_requires_authentication(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/reports/dashboard/').status_code, 401)
