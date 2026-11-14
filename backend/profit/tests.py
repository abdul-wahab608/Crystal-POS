from datetime import date, datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from customers.models import Customer
from production.models import ProductionRun, ProductionRunInput, ProductionRunItem
from products.models import Product, ProductVariant, SizeRange, Color
from purchases.models import Purchase, PurchaseItem
from raw_materials.models import RawMaterial
from sales.models import Sale, SaleItem
from vendors.models import Vendor
from .models import CostComponentType, ProductCost
from production.services import latest_raw_material_unit_costs
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
            quantity=0,
        )
        self.product_fallback = Product.objects.create(
            name='Fallback Widget', unit='PCS', cop=Decimal('15.00'),
            quantity=0,
        )
        self.product_tracked.size_ranges.add(self.size_range)
        self.product_fallback.size_ranges.add(self.size_range)

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
            quantity=10, unit_price=Decimal('100.00'), subtotal=Decimal('1000.00'),
        )

        # Sale 2: Apr (Spring), Karachi, tracked product, cost=40/dz -> profit 350
        self.sale2 = Sale.objects.create(customer=self.customer_karachi, total_amount=Decimal('550.00'))
        _set_sale_date(self.sale2, datetime(2026, 4, 20))
        self.item2 = SaleItem.objects.create(
            sale=self.sale2, product=self.product_tracked, size_range=self.size_range, color=self.color,
            quantity=5, unit_price=Decimal('110.00'), subtotal=Decimal('550.00'),
        )

        # Sale 3: Feb (Winter), Lahore, fallback product (no cost history) -> cost = cop * qty = 120, profit 120
        self.sale3 = Sale.objects.create(customer=self.customer_lahore, total_amount=Decimal('240.00'))
        _set_sale_date(self.sale3, datetime(2026, 2, 10))
        self.item3 = SaleItem.objects.create(
            sale=self.sale3, product=self.product_fallback, size_range=self.size_range, color=self.color,
            quantity=8, unit_price=Decimal('30.00'), subtotal=Decimal('240.00'),
        )


class CostLookupServiceTests(TestCase, ProfitFixtureMixin):
    def setUp(self):
        self.build_fixture()

    def test_unit_cost_before_any_history_uses_cop_fallback(self):
        lookup = CostLookup([self.product_tracked.id])
        cost = lookup.resolve(self.product_tracked.id, date(2025, 12, 31))[0]
        self.assertEqual(cost, Decimal('99.00'))

    def test_unit_cost_uses_versioned_history_as_of_date(self):
        lookup = CostLookup([self.product_tracked.id])
        self.assertEqual(lookup.resolve(self.product_tracked.id, date(2026, 1, 15))[0], Decimal('35.00'))
        self.assertEqual(lookup.resolve(self.product_tracked.id, date(2026, 3, 31))[0], Decimal('35.00'))
        self.assertEqual(lookup.resolve(self.product_tracked.id, date(2026, 4, 20))[0], Decimal('40.00'))

    def test_unit_cost_with_no_history_ever_uses_cop(self):
        lookup = CostLookup([self.product_fallback.id])
        self.assertEqual(lookup.resolve(self.product_fallback.id, date(2026, 6, 1))[0], Decimal('15.00'))


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

    def test_single_unit_totals_report_quantity_and_profit_per_unit(self):
        rows = compute_profit_rows(product_id=self.product_tracked.id)
        totals = summary_totals(rows)
        self.assertEqual(totals['unit'], 'PCS')
        self.assertEqual(totals['quantity'], Decimal('15'))
        self.assertEqual(totals['profit_per_unit'], Decimal('1000.00') / Decimal('15'))

    def test_mixed_units_are_not_summed(self):
        dozen_product = Product.objects.create(name='Shoe Box', unit='DOZEN', cop=Decimal('50.00'), quantity=0)
        sale = Sale.objects.create(customer=self.customer_lahore, total_amount=Decimal('300.00'))
        SaleItem.objects.create(
            sale=sale, product=dozen_product, size_range=self.size_range, color=self.color,
            quantity=Decimal('2'), unit_price=Decimal('150.00'), subtotal=Decimal('300.00'),
        )
        totals = summary_totals(compute_profit_rows())
        self.assertIsNone(totals['quantity'])
        self.assertIsNone(totals['unit'])
        self.assertEqual(
            {q['unit']: q['quantity'] for q in totals['quantities']},
            {'PCS': Decimal('23'), 'DOZEN': Decimal('2')},
        )

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

    def test_staff_cannot_read_summary(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get('/api/profit/summary/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

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
        self.assertEqual(response.data['cost_source'], 'COP')
        self.assertEqual(Decimal(response.data['unit_cost']), Decimal('15.00'))

        response = self.client.get('/api/profit/product-costs/current/', {
            'product': self.product_tracked.id, 'as_of': '2026-04-20',
        })
        self.assertEqual(response.data['cost_source'], 'MANUAL')
        self.assertEqual(Decimal(response.data['unit_cost']), Decimal('40.00'))


class ProfitApiAggregationTests(APITestCase, ProfitFixtureMixin):
    def setUp(self):
        self.build_fixture()
        self.staff = User.objects.create_user(username='manager_u2', password='pw', role=User.MANAGER)
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


class DozenAndPcsScenarioTests(APITestCase):
    def setUp(self):
        size = SizeRange.objects.create(name='Scenario Size')
        color = Color.objects.create(name='Scenario Color')
        self.customer = Customer.objects.create(name='Scenario Buyer', city='Lahore')
        self.dozen_product = Product.objects.create(name='Shoe Pair Box', unit='DOZEN', cop=Decimal('100.00'), quantity=0)
        self.pcs_product = Product.objects.create(name='Loose Sock', unit='PCS', cop=Decimal('20.00'), quantity=0)
        self.dozen_product.size_ranges.add(size)
        self.pcs_product.size_ranges.add(size)

        sale_dozen = Sale.objects.create(customer=self.customer, total_amount=Decimal('600.00'))
        _set_sale_date(sale_dozen, datetime(2026, 5, 10, 10, 0))
        SaleItem.objects.create(sale=sale_dozen, product=self.dozen_product, size_range=size, color=color,
                                quantity=Decimal('3'), unit_price=Decimal('200.00'), subtotal=Decimal('600.00'))

        sale_pcs = Sale.objects.create(customer=self.customer, total_amount=Decimal('250.00'))
        _set_sale_date(sale_pcs, datetime(2026, 5, 11, 10, 0))
        SaleItem.objects.create(sale=sale_pcs, product=self.pcs_product, size_range=size, color=color,
                                quantity=Decimal('10'), unit_price=Decimal('25.00'), subtotal=Decimal('250.00'))

        self.user = User.objects.create_user(username='scenario_staff', password='pw', role=User.MANAGER)
        self.client.force_authenticate(user=self.user)

    def test_totals_reconcile_across_units(self):
        totals = summary_totals(compute_profit_rows())
        self.assertEqual(totals['revenue'], Decimal('850.00'))
        self.assertEqual(totals['cost'], Decimal('500.00'))
        self.assertEqual(totals['profit_amount'], Decimal('350.00'))
        self.assertEqual(
            {q['unit']: q['quantity'] for q in totals['quantities']},
            {'DOZEN': Decimal('3'), 'PCS': Decimal('10')},
        )
        self.assertIsNone(totals['quantity'])
        self.assertIsNone(totals['profit_per_unit'])

    def test_group_by_unit_gives_per_unit_profit(self):
        rows = {r['key']: r for r in aggregate(compute_profit_rows(), 'unit')}
        self.assertEqual(rows['DOZEN']['revenue'], Decimal('600.00'))
        self.assertEqual(rows['DOZEN']['cost'], Decimal('300.00'))
        self.assertEqual(rows['DOZEN']['quantity'], Decimal('3'))
        self.assertEqual(rows['DOZEN']['profit_per_unit'], Decimal('100'))
        self.assertEqual(rows['PCS']['revenue'], Decimal('250.00'))
        self.assertEqual(rows['PCS']['cost'], Decimal('200.00'))
        self.assertEqual(rows['PCS']['quantity'], Decimal('10'))
        self.assertEqual(rows['PCS']['profit_per_unit'], Decimal('5'))

    def test_quantity_trend_is_split_per_unit(self):
        trend = build_trend(compute_profit_rows(), 'month', metric='quantity')
        series = {s['name']: s['data'] for s in trend['series']}
        self.assertEqual(trend['categories'], ['2026-05'])
        self.assertEqual(series, {'DOZEN': [3.0], 'PCS': [10.0]})

    def test_summary_endpoint_returns_per_unit_quantities(self):
        response = self.client.get('/api/profit/summary/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            {q['unit']: Decimal(str(q['quantity'])) for q in response.data['quantities']},
            {'DOZEN': Decimal('3'), 'PCS': Decimal('10')},
        )
        self.assertEqual(Decimal(str(response.data['profit_amount'])), Decimal('350.00'))

    def test_date_range_end_day_includes_whole_day(self):
        response = self.client.get('/api/profit/summary/', {'date_from': '2026-05-10', 'date_to': '2026-05-10'})
        self.assertEqual(Decimal(str(response.data['revenue'])), Decimal('600.00'))


class ProfitStaffAccessTests(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(username='clerk', password='pw', role='STAFF')
        self.client.force_authenticate(self.staff)

    def test_staff_cannot_read_profit_summary_or_trend(self):
        self.assertEqual(self.client.get('/api/profit/summary/').status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(self.client.get('/api/profit/trend/').status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_can_read_profit_summary(self):
        self.staff.role = 'MANAGER'
        self.staff.save()
        self.assertEqual(self.client.get('/api/profit/summary/').status_code, status.HTTP_200_OK)


def _set_datetime(model, pk, when):
    model.objects.filter(pk=pk).update(date=timezone.make_aware(when))


class ProductionDerivedCostTests(APITestCase):
    def setUp(self):
        self.size = SizeRange.objects.create(name='Adult')
        self.color = Color.objects.create(name='Brown')
        self.customer = Customer.objects.create(name='Buyer', city='Lahore')
        self.pair = Product.objects.create(name='Leather Pair', unit='PCS', cop=Decimal('0'), quantity=0)
        self.pair.size_ranges.add(self.size)
        self.variant = ProductVariant.objects.create(product=self.pair, size_range=self.size, color=self.color, quantity=0)
        self.leather = RawMaterial.objects.create(name='Leather', unit='KG', quantity=Decimal('0'))
        self.vendor = Vendor.objects.create(name='Tannery')
        self._purchase(self.leather, '500.00', datetime(2026, 1, 10, 10, 0))
        self.run_feb = self._run(datetime(2026, 2, 1, 10, 0), '20', [(self.leather, '20')])

        self.manager = User.objects.create_user(username='cost_manager', password='pw', role=User.MANAGER)
        self.client.force_authenticate(user=self.manager)

    def _purchase(self, raw_material, unit_cost, when):
        purchase = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal(unit_cost))
        _set_datetime(Purchase, purchase.pk, when)
        PurchaseItem.objects.create(
            purchase=purchase, raw_material=raw_material, quantity=Decimal('1'),
            unit_cost=Decimal(unit_cost), subtotal=Decimal(unit_cost),
        )

    def _run(self, when, output, inputs):
        run = ProductionRun.objects.create()
        _set_datetime(ProductionRun, run.pk, when)
        ProductionRunItem.objects.create(run=run, variant=self.variant, quantity=Decimal(output))
        prices = latest_raw_material_unit_costs({raw_material.pk for raw_material, _ in inputs})
        for raw_material, quantity in inputs:
            ProductionRunInput.objects.create(
                run=run, raw_material=raw_material, quantity=Decimal(quantity), unit_cost=prices.get(raw_material.pk),
            )
        return run

    def _sale(self, when, product, quantity, subtotal):
        sale = Sale.objects.create(customer=self.customer, total_amount=Decimal(subtotal))
        _set_sale_date(sale, when)
        return SaleItem.objects.create(
            sale=sale, product=product, size_range=self.size, color=self.color,
            quantity=Decimal(quantity), unit_price=Decimal(subtotal) / Decimal(quantity), subtotal=Decimal(subtotal),
        )

    def test_production_cost_is_inputs_divided_by_output(self):
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost_source'], 'PRODUCTION')
        self.assertEqual(row['cost'], Decimal('1000.00'))
        self.assertEqual(row['profit_amount'], Decimal('200.00'))

    def test_later_purchase_does_not_reprice_an_existing_run(self):
        self._purchase(self.leather, '600.00', datetime(2026, 2, 15, 10, 0))
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '1', '600.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost'], Decimal('500.00'))

    def test_most_recent_run_on_or_before_sale_date_is_used(self):
        self._purchase(self.leather, '600.00', datetime(2026, 2, 15, 10, 0))
        self._run(datetime(2026, 4, 1, 10, 0), '10', [(self.leather, '10')])
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '1', '600.00')
        self._sale(datetime(2026, 4, 15, 12, 0), self.pair, '1', '600.00')
        costs = {r['month']: r['cost'] for r in compute_profit_rows(product_id=self.pair.id)}
        self.assertEqual(costs, {3: Decimal('500.00'), 4: Decimal('600.00')})

    def test_manual_cost_overrides_production(self):
        ProductCost.objects.create(product=self.pair, component_type=CostComponentType.objects.get(name='Labor'),
                                   amount_per_dozen=Decimal('300.00'), valid_from=date(2026, 1, 1))
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost_source'], 'MANUAL')
        self.assertEqual(row['cost'], Decimal('600.00'))

    def test_run_with_unpriced_input_is_skipped_for_cop(self):
        glue = RawMaterial.objects.create(name='Glue', unit='KG', quantity=Decimal('0'))
        ProductionRun.objects.all().delete()
        self._run(datetime(2026, 2, 1, 10, 0), '20', [(glue, '2')])
        Product.objects.filter(pk=self.pair.pk).update(cop=Decimal('15.00'))
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '100.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost_source'], 'COP')
        self.assertEqual(row['cost'], Decimal('30.00'))

    def test_cop_fallback_only_when_positive(self):
        ProductionRun.objects.all().delete()
        Product.objects.filter(pk=self.pair.pk).update(cop=Decimal('15.00'))
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '100.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost_source'], 'COP')
        self.assertEqual(row['cost'], Decimal('30.00'))

    def test_no_cost_at_all_is_missing_with_null_profit(self):
        ProductionRun.objects.all().delete()
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost_source'], 'MISSING')
        self.assertIsNone(row['cost'])
        self.assertIsNone(row['profit_amount'])

        totals = summary_totals(compute_profit_rows(product_id=self.pair.id))
        self.assertTrue(totals['cost_missing'])
        self.assertEqual(totals['cost_source'], 'MISSING')
        self.assertEqual(totals['revenue'], Decimal('1200.00'))
        self.assertIsNone(totals['cost'])
        self.assertIsNone(totals['profit_amount'])
        self.assertIsNone(totals['profit_ratio'])
        self.assertIsNone(totals['profit_per_unit'])

    def test_group_with_one_missing_row_reports_no_profit(self):
        other = Product.objects.create(name='Costed Item', unit='PCS', cop=Decimal('10.00'), quantity=0)
        ProductionRun.objects.all().delete()
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        self._sale(datetime(2026, 3, 2, 12, 0), other, '1', '50.00')
        march = {r['label']: r for r in aggregate(compute_profit_rows(), 'month')}['2026-03']
        self.assertTrue(march['cost_missing'])
        self.assertEqual(march['cost_source'], 'MISSING')
        self.assertEqual(march['cost_sources'], ['COP', 'MISSING'])
        self.assertIsNone(march['profit_amount'])
        self.assertEqual(march['revenue'], Decimal('1250.00'))

    def test_costed_group_reports_its_source_and_profit(self):
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        totals = summary_totals(compute_profit_rows())
        self.assertFalse(totals['cost_missing'])
        self.assertEqual(totals['cost_source'], 'PRODUCTION')
        self.assertEqual(totals['profit_amount'], Decimal('200.00'))

    def test_trend_points_for_missing_cost_are_null(self):
        other = Product.objects.create(name='Costed Item', unit='PCS', cop=Decimal('10.00'), quantity=0)
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        ProductionRun.objects.filter(pk=self.run_feb.pk).delete()
        self._sale(datetime(2026, 4, 2, 12, 0), other, '1', '50.00')
        trend = build_trend(compute_profit_rows(), 'month', metric='profit_amount')
        profit_series = trend['series'][0]
        self.assertEqual(trend['categories'], ['2026-03', '2026-04'])
        self.assertEqual(profit_series['data'], [None, 40.0])
        self.assertEqual(profit_series['cost_missing'], [True, False])
        self.assertEqual(profit_series['cost_source'], ['MISSING', 'COP'])

    def test_summary_endpoint_has_no_margin_without_cost(self):
        ProductionRun.objects.all().delete()
        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '1200.00')
        response = self.client.get('/api/profit/summary/', {'group_by': 'product'})
        row = response.data['rows'][0]
        self.assertTrue(row['cost_missing'])
        self.assertIsNone(row['profit_amount'])
        self.assertIsNone(row['profit_ratio'])
        self.assertEqual(Decimal(str(row['revenue'])), Decimal('1200.00'))

    def test_current_endpoint_lists_production_runs_and_used_run(self):
        self._run(datetime(2026, 4, 1, 10, 0), '10', [(self.leather, '10')])
        response = self.client.get('/api/profit/product-costs/current/', {
            'product': self.pair.id, 'as_of': '2026-03-01',
        })
        self.assertEqual(response.data['cost_source'], 'PRODUCTION')
        self.assertEqual(Decimal(str(response.data['unit_cost'])), Decimal('500.00'))
        self.assertEqual(response.data['production_run_id'], self.run_feb.pk)
        self.assertEqual(len(response.data['production_runs']), 2)

    def test_current_endpoint_missing_when_nothing_is_known(self):
        ProductionRun.objects.all().delete()
        response = self.client.get('/api/profit/product-costs/current/', {
            'product': self.pair.id, 'as_of': '2026-03-01',
        })
        self.assertEqual(response.data['cost_source'], 'MISSING')
        self.assertIsNone(response.data['unit_cost'])
        self.assertIsNone(response.data['production_run_id'])

    def test_multi_product_run_splits_input_cost_by_output_quantity(self):
        sandal = Product.objects.create(name='Sandal', unit='PCS', cop=Decimal('0'), quantity=0)
        sandal.size_ranges.add(self.size)
        sandal_variant = ProductVariant.objects.create(product=sandal, size_range=self.size, color=self.color, quantity=0)
        hide = RawMaterial.objects.create(name='Hide', unit='KG', quantity=Decimal('0'))
        self._purchase(hide, '10.00', datetime(2026, 1, 5, 10, 0))
        ProductionRun.objects.all().delete()
        run = self._run(datetime(2026, 2, 1, 10, 0), '20', [(hide, '300')])
        ProductionRunItem.objects.create(run=run, variant=sandal_variant, quantity=Decimal('10'))

        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '400.00')
        self._sale(datetime(2026, 3, 1, 13, 0), sandal, '1', '150.00')
        rows = {r['product_id']: r for r in compute_profit_rows()}
        self.assertEqual(rows[self.pair.id]['cost'], Decimal('200.00'))
        self.assertEqual(rows[sandal.id]['cost'], Decimal('100.00'))
        self.assertEqual(rows[self.pair.id]['cost_source'], 'PRODUCTION')

    def test_run_with_outputs_in_different_units_is_unusable(self):
        box = Product.objects.create(name='Box', unit='DOZEN', cop=Decimal('0'), quantity=0)
        box.size_ranges.add(self.size)
        box_variant = ProductVariant.objects.create(product=box, size_range=self.size, color=self.color, quantity=0)
        hide = RawMaterial.objects.create(name='Hide', unit='KG', quantity=Decimal('0'))
        self._purchase(hide, '10.00', datetime(2026, 1, 5, 10, 0))
        ProductionRun.objects.all().delete()
        run = self._run(datetime(2026, 2, 1, 10, 0), '20', [(hide, '300')])
        ProductionRunItem.objects.create(run=run, variant=box_variant, quantity=Decimal('5'))
        Product.objects.filter(pk=self.pair.pk).update(cop=Decimal('15.00'))

        self._sale(datetime(2026, 3, 1, 12, 0), self.pair, '2', '100.00')
        row = compute_profit_rows(product_id=self.pair.id)[0]
        self.assertEqual(row['cost_source'], 'COP')
        self.assertEqual(row['cost'], Decimal('30.00'))


class PurchasedProductCostTests(TestCase):
    def setUp(self):
        self.size = SizeRange.objects.create(name='M')
        self.color = Color.objects.create(name='Blue')
        self.customer = Customer.objects.create(name='Buyer', city='Lahore')
        self.jeans = Product.objects.create(
            name='Denim Jeans', unit='PCS', cop=Decimal('900'), quantity=0, product_type='PURCHASED',
        )
        self.jeans.size_ranges.add(self.size)
        vendor = Vendor.objects.create(name='Denim Mills')
        purchase = Purchase.objects.create(vendor=vendor, total_amount=Decimal('14000'))
        _set_datetime(Purchase, purchase.pk, datetime(2026, 1, 10, 10, 0))
        PurchaseItem.objects.create(
            purchase=purchase, product=self.jeans, size_range=self.size, color=self.color,
            quantity=Decimal('20'), unit_cost=Decimal('700'), subtotal=Decimal('14000'),
        )

    def _sale(self, when, quantity, subtotal):
        sale = Sale.objects.create(customer=self.customer, total_amount=Decimal(subtotal))
        _set_sale_date(sale, when)
        return SaleItem.objects.create(
            sale=sale, product=self.jeans, size_range=self.size, color=self.color,
            quantity=Decimal(quantity), unit_price=Decimal(subtotal) / Decimal(quantity), subtotal=Decimal(subtotal),
        )

    def test_purchase_unit_cost_is_used_instead_of_cop(self):
        self._sale(datetime(2026, 3, 1, 12, 0), '2', '3000.00')
        row = compute_profit_rows(product_id=self.jeans.id)[0]
        self.assertEqual(row['cost_source'], 'PURCHASE')
        self.assertEqual(row['cost'], Decimal('1400.00'))
        self.assertEqual(row['profit_amount'], Decimal('1600.00'))

    def test_manual_cost_overrides_purchase_unit_cost(self):
        ProductCost.objects.create(product=self.jeans, component_type=CostComponentType.objects.get(name='Labor'),
                                   amount_per_dozen=Decimal('300.00'), valid_from=date(2026, 1, 1))
        self._sale(datetime(2026, 3, 1, 12, 0), '2', '3000.00')
        row = compute_profit_rows(product_id=self.jeans.id)[0]
        self.assertEqual(row['cost_source'], 'MANUAL')
        self.assertEqual(row['cost'], Decimal('600.00'))

    def test_sale_before_the_purchase_falls_back_to_cop(self):
        self._sale(datetime(2026, 1, 5, 12, 0), '2', '3000.00')
        row = compute_profit_rows(product_id=self.jeans.id)[0]
        self.assertEqual(row['cost_source'], 'COP')
        self.assertEqual(row['cost'], Decimal('1800.00'))
