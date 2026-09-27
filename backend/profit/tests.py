from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from customers.models import Customer
from products.models import Product, SizeRange, Color
from sales.models import Sale, SaleItem
from .models import CostComponentType, ProductCost
from .services import CostLookup, aggregate, build_trend, compute_profit_rows, summary_totals

User = get_user_model()


def _set_sale_date(sale, when):
    Sale.objects.filter(pk=sale.pk).update(date=timezone.make_aware(when) if timezone.is_naive(when) else when)
    sale.refresh_from_db()


class ProfitFixtureMixin:
    """Builds a shared scenario: two products (one with versioned cost history,
    one with only Product.cop as fallback), two customers in different cities,
    and three sales spread across Winter/Spring so season+location+trend all differ."""

    def build_fixture(self):
        self.size_range = SizeRange.objects.create(name='Standard')
        self.color = Color.objects.create(name='Blue')

        self.product_tracked = Product.objects.create(
            name='Tracked Widget', unit='PCS', cop=Decimal('99.00'),
            quantity=0, size_range=self.size_range,
        )
        self.product_fallback = Product.objects.create(
            name='Fallback Widget', unit='PCS', cop=Decimal('15.00'),
            quantity=0, size_range=self.size_range,
        )

        self.raw_material = CostComponentType.objects.get(name='Raw Material')
        self.electricity = CostComponentType.objects.get(name='Electricity')
        self.labor = CostComponentType.objects.get(name='Labor')

        # Cost history for the tracked product: 35/dozen from Jan 1, rising to 40/dozen from Apr 1
        ProductCost.objects.create(product=self.product_tracked, component_type=self.raw_material,
                                    amount_per_dozen=Decimal('20.00'), valid_from=date(2026, 1, 1))
        ProductCost.objects.create(product=self.product_tracked, component_type=self.electricity,
                                    amount_per_dozen=Decimal('5.00'), valid_from=date(2026, 1, 1))
        ProductCost.objects.create(product=self.product_tracked, component_type=self.labor,
                                    amount_per_dozen=Decimal('10.00'), valid_from=date(2026, 1, 1))
        ProductCost.objects.create(product=self.product_tracked, component_type=self.raw_material,
                                    amount_per_dozen=Decimal('25.00'), valid_from=date(2026, 4, 1))

        self.customer_lahore = Customer.objects.create(name='Lahore Customer', city='Lahore')
        self.customer_karachi = Customer.objects.create(name='Karachi Customer', city='Karachi')

        # Sale 1: Jan (Winter), Lahore, tracked product, cost=35/dz -> profit 650
        self.sale1 = Sale.objects.create(customer=self.customer_lahore, total_amount=Decimal('1000.00'))
        _set_sale_date(self.sale1, datetime(2026, 1, 15))
        self.item1 = SaleItem.objects.create(
            sale=self.sale1, product=self.product_tracked, size_range=self.size_range, color=self.color,
            quantity_dozens=10, unit_price=Decimal('100.00'), subtotal=Decimal('1000.00'),
        )

        # Sale 2: Apr (Spring), Karachi, tracked product, cost=40/dz -> profit 350
        self.sale2 = Sale.objects.create(customer=self.customer_karachi, total_amount=Decimal('550.00'))
        _set_sale_date(self.sale2, datetime(2026, 4, 20))
        self.item2 = SaleItem.objects.create(
            sale=self.sale2, product=self.product_tracked, size_range=self.size_range, color=self.color,
            quantity_dozens=5, unit_price=Decimal('110.00'), subtotal=Decimal('550.00'),
        )

        # Sale 3: Feb (Winter), Lahore, fallback product (no cost history) -> cost = cop * qty = 120, profit 120
        self.sale3 = Sale.objects.create(customer=self.customer_lahore, total_amount=Decimal('240.00'))
        _set_sale_date(self.sale3, datetime(2026, 2, 10))
        self.item3 = SaleItem.objects.create(
            sale=self.sale3, product=self.product_fallback, size_range=self.size_range, color=self.color,
            quantity_dozens=8, unit_price=Decimal('30.00'), subtotal=Decimal('240.00'),
        )


class CostLookupServiceTests(TestCase, ProfitFixtureMixin):
    def setUp(self):
        self.build_fixture()

    def test_unit_cost_before_any_history_uses_cop_fallback(self):
        lookup = CostLookup([self.product_tracked.id])
        cost = lookup.unit_cost_per_dozen(self.product_tracked.id, date(2025, 12, 31))
        self.assertEqual(cost, Decimal('99.00'))

    def test_unit_cost_uses_versioned_history_as_of_date(self):
        lookup = CostLookup([self.product_tracked.id])
        self.assertEqual(lookup.unit_cost_per_dozen(self.product_tracked.id, date(2026, 1, 15)), Decimal('35.00'))
        self.assertEqual(lookup.unit_cost_per_dozen(self.product_tracked.id, date(2026, 3, 31)), Decimal('35.00'))
        self.assertEqual(lookup.unit_cost_per_dozen(self.product_tracked.id, date(2026, 4, 20)), Decimal('40.00'))

    def test_unit_cost_with_no_history_ever_uses_cop(self):
        lookup = CostLookup([self.product_fallback.id])
        self.assertEqual(lookup.unit_cost_per_dozen(self.product_fallback.id, date(2026, 6, 1)), Decimal('15.00'))


class ProfitAggregationServiceTests(TestCase, ProfitFixtureMixin):
    def setUp(self):
        self.build_fixture()

    def test_compute_profit_rows_totals(self):
        rows = compute_profit_rows()
        self.assertEqual(len(rows), 3)
        totals = summary_totals(rows)
        self.assertEqual(totals['revenue'], Decimal('1790.00'))
        self.assertEqual(totals['cost'], Decimal('350.00') + Decimal('200.00') + Decimal('120.00'))
        self.assertEqual(totals['profit_amount'], Decimal('1120.00'))

    def test_group_by_month(self):
        rows = compute_profit_rows()
        grouped = {r['label']: r for r in aggregate(rows, 'month')}
        self.assertEqual(grouped['2026-01']['profit_amount'], Decimal('650.00'))
        self.assertEqual(grouped['2026-02']['profit_amount'], Decimal('120.00'))
        self.assertEqual(grouped['2026-04']['profit_amount'], Decimal('350.00'))
        self.assertEqual(list(grouped.keys()), ['2026-01', '2026-02', '2026-04'])

    def test_group_by_season(self):
        rows = compute_profit_rows()
        grouped = {r['label']: r for r in aggregate(rows, 'season')}
        self.assertEqual(grouped['Winter']['profit_amount'], Decimal('770.00'))
        self.assertEqual(grouped['Spring']['profit_amount'], Decimal('350.00'))
        self.assertEqual(list(grouped.keys())[0], 'Spring')

    def test_group_by_location(self):
        rows = compute_profit_rows()
        grouped = {r['label']: r for r in aggregate(rows, 'location')}
        self.assertEqual(grouped['Lahore']['profit_amount'], Decimal('770.00'))
        self.assertEqual(grouped['Karachi']['profit_amount'], Decimal('350.00'))

    def test_group_by_product(self):
        rows = compute_profit_rows()
        grouped = {r['label']: r for r in aggregate(rows, 'product')}
        self.assertEqual(grouped['Tracked Widget']['profit_amount'], Decimal('1000.00'))
        self.assertEqual(grouped['Fallback Widget']['profit_amount'], Decimal('120.00'))

    def test_piece_vs_dozen_unit_conversion(self):
        rows = compute_profit_rows(product_id=self.product_tracked.id)
        dozen_totals = summary_totals(rows, unit='dozen')
        piece_totals = summary_totals(rows, unit='piece')
        self.assertEqual(piece_totals['quantity'], dozen_totals['quantity'] * 12)
        self.assertEqual(piece_totals['profit_per_unit'] * 12, dozen_totals['profit_per_unit'])

    def test_filters_by_city_and_season(self):
        rows = compute_profit_rows(city='Lahore', season='Winter')
        self.assertEqual(len(rows), 2)
        self.assertEqual(sum((r['profit_amount'] for r in rows), Decimal('0')), Decimal('770.00'))

    def test_trend_with_series_by_product(self):
        rows = compute_profit_rows()
        trend = build_trend(rows, x='month', series='product', metric='profit_amount')
        self.assertEqual(trend['categories'], ['2026-01', '2026-02', '2026-04'])
        series_by_name = {s['name']: s['data'] for s in trend['series']}
        self.assertEqual(series_by_name['Tracked Widget'], [650.0, 0.0, 350.0])
        self.assertEqual(series_by_name['Fallback Widget'], [0.0, 120.0, 0.0])


class ProfitApiPermissionTests(APITestCase, ProfitFixtureMixin):
    def setUp(self):
        self.build_fixture()
        self.admin = User.objects.create_user(username='admin_u', password='pw', role=User.ADMIN)
        self.manager = User.objects.create_user(username='manager_u', password='pw', role=User.MANAGER)
        self.staff = User.objects.create_user(username='staff_u', password='pw', role=User.STAFF)
        self.client = APIClient()

    def test_summary_requires_authentication(self):
        response = self.client.get('/api/profit/summary/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_staff_can_read_summary(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/profit/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Decimal(response.data['profit_amount']), Decimal('1120.00'))

    def test_staff_cannot_create_cost_component(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post('/api/profit/cost-components/', {'name': 'Packaging'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_create_custom_cost_component(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post('/api/profit/cost-components/', {'name': 'Packaging', 'is_system': True})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(response.data['is_system'])

    def test_system_component_cannot_be_renamed_or_deleted(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(f'/api/profit/cost-components/{self.raw_material.id}/', {'name': 'Renamed'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.delete(f'/api/profit/cost-components/{self.raw_material.id}/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_staff_cannot_create_product_cost(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.post('/api/profit/product-costs/', {
            'product': self.product_tracked.id, 'component_type': self.raw_material.id,
            'amount_per_dozen': '30.00', 'valid_from': '2026-07-01',
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_add_new_cost_version_not_edit_in_place(self):
        self.client.force_authenticate(user=self.manager)
        response = self.client.post('/api/profit/product-costs/', {
            'product': self.product_tracked.id, 'component_type': self.raw_material.id,
            'amount_per_dozen': '30.00', 'valid_from': '2026-07-01',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Old rows are untouched -- versioning via new rows, not PUT/PATCH
        self.assertEqual(ProductCost.objects.filter(product=self.product_tracked, component_type=self.raw_material).count(), 3)
        put_response = self.client.put(f"/api/profit/product-costs/{response.data['id']}/", {
            'product': self.product_tracked.id, 'component_type': self.raw_material.id,
            'amount_per_dozen': '999.00', 'valid_from': '2026-07-01',
        })
        self.assertEqual(put_response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_current_cost_endpoint_reports_fallback_flag(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/profit/product-costs/current/', {'product': self.product_fallback.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['using_fallback_cop'])
        self.assertEqual(Decimal(response.data['total_per_dozen']), Decimal('15.00'))

        response = self.client.get('/api/profit/product-costs/current/', {
            'product': self.product_tracked.id, 'as_of': '2026-04-20',
        })
        self.assertFalse(response.data['using_fallback_cop'])
        self.assertEqual(Decimal(response.data['total_per_dozen']), Decimal('40.00'))


class ProfitApiAggregationTests(APITestCase, ProfitFixtureMixin):
    def setUp(self):
        self.build_fixture()
        self.staff = User.objects.create_user(username='staff_u2', password='pw', role=User.STAFF)
        self.client = APIClient()
        self.client.force_authenticate(user=self.staff)

    def test_summary_group_by_location(self):
        response = self.client.get('/api/profit/summary/', {'group_by': 'location'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rows = {r['label']: r for r in response.data['rows']}
        self.assertEqual(Decimal(rows['Lahore']['profit_amount']), Decimal('770.00'))
        self.assertEqual(Decimal(rows['Karachi']['profit_amount']), Decimal('350.00'))

    def test_trend_endpoint_shape(self):
        response = self.client.get('/api/profit/trend/', {'x': 'season', 'metric': 'profit_amount'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('categories', response.data)
        self.assertIn('series', response.data)
        self.assertEqual(response.data['categories'], ['Spring', 'Winter'])
