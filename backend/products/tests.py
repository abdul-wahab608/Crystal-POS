from products.models import ProductHistory
from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from products.models import Color, Product, ProductVariant, SizeRange
from profit.models import CostComponentType, ProductCost


class ProductApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='owner', password='pw', role='MANAGER', is_staff=True)
        self.client.force_authenticate(self.user)
        self.men = SizeRange.objects.create(name='Men (40-46)')
        self.women = SizeRange.objects.create(name='Women (36-41)')
        self.kids = SizeRange.objects.create(name='Kids (24-30)')
        self.extra = SizeRange.objects.create(name='Unisex')
        self.black = Color.objects.create(name='Black')
        self.brown = Color.objects.create(name='Brown')

    def _product_payload(self, **overrides):
        data = {'name': 'Oxford', 'unit': 'DOZEN', 'cop': '100.00', 'quantity': 0, 'size_ranges': [self.men.pk]}
        data.update(overrides)
        return data

    def test_create_product_returns_201_with_linked_size_ranges(self):
        res = self.client.post('/api/products/', self._product_payload(quantity=12, size_ranges=[self.men.pk, self.women.pk]), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(sorted(res.data['size_ranges']), sorted([self.men.pk, self.women.pk]))
        self.assertEqual(Decimal(res.data['quantity']), Decimal('12'))

    def test_product_without_size_ranges_is_allowed(self):
        res = self.client.post('/api/products/', self._product_payload(size_ranges=[]), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.data['size_ranges'], [])

    def test_more_than_three_size_ranges_is_rejected(self):
        res = self.client.post(
            '/api/products/',
            self._product_payload(size_ranges=[self.men.pk, self.women.pk, self.kids.pk, self.extra.pk]),
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('size_ranges', res.data)

    def test_create_product_with_unknown_unit_is_rejected(self):
        res = self.client.post('/api/products/', self._product_payload(unit='NOPE'), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('unit', res.data)

    def test_duplicate_name_and_unit_is_rejected(self):
        self.client.post('/api/products/', self._product_payload(), format='json')
        res = self.client.post('/api/products/', self._product_payload(), format='json')
        self.assertEqual(res.status_code, 400)

    def test_same_name_in_another_unit_is_allowed(self):
        self.client.post('/api/products/', self._product_payload(), format='json')
        res = self.client.post('/api/products/', self._product_payload(unit='PCS'), format='json')
        self.assertEqual(res.status_code, 201, res.content)

    def test_list_retrieve_patch_and_delete(self):
        product = Product.objects.create(name='Oxford', unit='DOZEN', cop=100)
        product.size_ranges.add(self.men)
        self.assertEqual(self.client.get('/api/products/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/products/{product.pk}/').status_code, 200)
        res = self.client.patch(f'/api/products/{product.pk}/', {'cop': '150.50', 'unit': 'POUND'}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(Decimal(res.data['cop']), Decimal('150.50'))
        self.assertEqual(res.data['unit'], 'POUND')
        self.assertEqual(self.client.delete(f'/api/products/{product.pk}/').status_code, 204)

    def test_size_range_filter_matches_linked_and_variant_products(self):
        linked = Product.objects.create(name='A', unit='DOZEN', cop=1)
        linked.size_ranges.add(self.men)
        with_variant = Product.objects.create(name='B', unit='DOZEN', cop=1)
        ProductVariant.objects.create(product=with_variant, size_range=self.men, color=self.black, quantity=1)
        other = Product.objects.create(name='C', unit='DOZEN', cop=1)
        other.size_ranges.add(self.women)
        res = self.client.get(f'/api/products/?size_range={self.men.pk}')
        self.assertEqual(sorted(p['name'] for p in res.data), ['A', 'B'])

    def test_color_filter_matches_products_with_a_variant_of_that_color(self):
        a = Product.objects.create(name='A', unit='DOZEN', cop=1)
        ProductVariant.objects.create(product=a, size_range=self.men, color=self.black, quantity=1)
        b = Product.objects.create(name='B', unit='DOZEN', cop=1)
        ProductVariant.objects.create(product=b, size_range=self.men, color=self.brown, quantity=1)
        res = self.client.get(f'/api/products/?color={self.black.pk}')
        self.assertEqual([p['name'] for p in res.data], ['A'])

    def test_bulk_update_and_bulk_delete(self):
        a = Product.objects.create(name='A', unit='DOZEN', cop=1)
        b = Product.objects.create(name='B', unit='DOZEN', cop=1)
        res = self.client.post('/api/products/bulk_update/', {'ids': [a.pk, b.pk], 'data': {'product_type': 'PURCHASED'}}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(Product.objects.filter(product_type='PURCHASED').count(), 2)
        res = self.client.post('/api/products/bulk_delete/', {'ids': [a.pk]}, format='json')
        self.assertEqual(res.data['deleted_count'], 1)

    def test_export_and_template_endpoints(self):
        Product.objects.create(name='A', unit='DOZEN', cop=1)
        self.assertEqual(self.client.get('/api/products/export/?export_format=csv').status_code, 200)
        self.assertEqual(self.client.get('/api/products/download_template/').status_code, 200)
        self.assertEqual(self.client.get('/api/products/get_import_fields/').status_code, 200)

    def test_json_bulk_import_links_size_range_by_name(self):
        rows = [{'name': 'Loafer', 'unit': 'DOZEN', 'size_range': 'men (40-46)', 'cop': '200', 'quantity': '3'}]
        res = self.client.post('/api/products/bulk_import/', {'data': rows}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.data['success_count'], 1)
        self.assertEqual(list(Product.objects.get(name='Loafer').size_ranges.all()), [self.men])

    def test_json_bulk_import_reports_unknown_size_range(self):
        rows = [{'name': 'Loafer', 'unit': 'DOZEN', 'size_range': 'Nope', 'cop': '200'}]
        res = self.client.post('/api/products/bulk_import/', {'data': rows}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['error_count'], 1)


class VariantApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='owner', password='pw', role='MANAGER', is_staff=True)
        self.client.force_authenticate(self.user)
        self.men = SizeRange.objects.create(name='Men (40-46)')
        self.women = SizeRange.objects.create(name='Women (36-41)')
        self.black = Color.objects.create(name='Black')
        self.brown = Color.objects.create(name='Brown')
        self.product = Product.objects.create(name='Oxford', unit='DOZEN', cop=100)
        self.product.size_ranges.add(self.men)

    def _variant(self, **overrides):
        data = {'product': self.product.pk, 'size_range': self.men.pk, 'color': self.black.pk, 'quantity': 4}
        data.update(overrides)
        return data

    def test_create_variant_returns_names_and_adds_to_product_quantity(self):
        res = self.client.post('/api/products/product-variants/', self._variant(), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(res.data['color_name'], 'Black')
        self.assertEqual(res.data['size_range_name'], 'Men (40-46)')
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal('4'))

    def test_variant_size_range_must_belong_to_product(self):
        res = self.client.post('/api/products/product-variants/', self._variant(size_range=self.women.pk), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('size_range', res.data)

    def test_duplicate_size_and_color_is_rejected(self):
        self.client.post('/api/products/product-variants/', self._variant(), format='json')
        res = self.client.post('/api/products/product-variants/', self._variant(quantity=9), format='json')
        self.assertEqual(res.status_code, 400)

    def test_same_size_different_color_is_allowed(self):
        self.client.post('/api/products/product-variants/', self._variant(), format='json')
        res = self.client.post('/api/products/product-variants/', self._variant(color=self.brown.pk), format='json')
        self.assertEqual(res.status_code, 201)

    def test_decimal_quantity_is_accepted_in_product_unit(self):
        res = self.client.post('/api/products/product-variants/', self._variant(quantity='2.5'), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(Decimal(res.data['quantity']), Decimal('2.5'))

    def test_negative_variant_quantity_is_rejected(self):
        res = self.client.post('/api/products/product-variants/', self._variant(quantity=-1), format='json')
        self.assertEqual(res.status_code, 400)

    def test_variant_update_adjusts_product_quantity_and_delete_removes_it(self):
        variant = ProductVariant.objects.create(product=self.product, size_range=self.men, color=self.black, quantity=4)
        self.product.quantity = Decimal('4')
        self.product.save()
        res = self.client.patch(f'/api/products/product-variants/{variant.pk}/', {'quantity': 10}, format='json')
        self.assertEqual(res.status_code, 200)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal('10'))
        self.assertEqual(self.client.delete(f'/api/products/product-variants/{variant.pk}/').status_code, 204)
        self.product.refresh_from_db()
        self.assertEqual(self.product.quantity, Decimal('0'))

    def test_variants_nested_on_product_and_filterable(self):
        ProductVariant.objects.create(product=self.product, size_range=self.men, color=self.black, quantity=4)
        res = self.client.get(f'/api/products/{self.product.pk}/')
        self.assertEqual(len(res.data['variants']), 1)
        res = self.client.get(f'/api/products/product-variants/?product={self.product.pk}')
        self.assertEqual(len(res.data), 1)

    def test_deleting_a_color_in_use_returns_409(self):
        ProductVariant.objects.create(product=self.product, size_range=self.men, color=self.black, quantity=4)
        res = self.client.delete(f'/api/products/colors/{self.black.pk}/')
        self.assertEqual(res.status_code, 409)
        self.assertTrue(Color.objects.filter(pk=self.black.pk).exists())

    def test_deleting_a_size_range_in_use_returns_409(self):
        ProductVariant.objects.create(product=self.product, size_range=self.men, color=self.black, quantity=4)
        res = self.client.delete(f'/api/products/size-ranges/{self.men.pk}/')
        self.assertEqual(res.status_code, 409)

    def test_unused_color_and_size_range_can_be_deleted(self):
        self.assertEqual(self.client.delete(f'/api/products/colors/{self.brown.pk}/').status_code, 204)
        self.assertEqual(self.client.delete(f'/api/products/size-ranges/{self.women.pk}/').status_code, 204)

    def test_duplicate_color_name_is_rejected(self):
        res = self.client.post('/api/products/colors/', {'name': 'Black'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(self.client.post('/api/products/colors/', {'name': 'Tan'}, format='json').status_code, 201)


class ProductDeletePermissionTests(APITestCase):
    def setUp(self):
        self.staff = get_user_model().objects.create_user(username='clerk', password='pw', role='STAFF')
        self.manager = get_user_model().objects.create_user(username='boss', password='pw', role='MANAGER')
        self.size = SizeRange.objects.create(name='Men (40-46)')
        self.color = Color.objects.create(name='Black')
        self.product = Product.objects.create(name='Oxford', unit='DOZEN', cop=100, quantity=0)
        self.product.size_ranges.add(self.size)

    def test_staff_cannot_delete_a_product(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.delete(f'/api/products/{self.product.pk}/').status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_staff_cannot_batch_delete_products(self):
        self.client.force_authenticate(self.staff)
        res = self.client.post('/api/products/bulk_delete/', {'ids': [self.product.pk]}, format='json')
        self.assertEqual(res.status_code, 403)
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())

    def test_product_with_variant_stock_history_refuses_delete_with_plain_message(self):
        from sales.models import Sale, SaleItem
        from customers.models import Customer
        self.client.force_authenticate(self.manager)
        sale = Sale.objects.create(customer=Customer.objects.create(name='C'), total_amount=100)
        SaleItem.objects.create(
            sale=sale, product=self.product, size_range=self.size, color=self.color,
            quantity=1, unit_price=100, subtotal=100,
        )
        res = self.client.delete(f'/api/products/{self.product.pk}/')
        self.assertEqual(res.status_code, 409)
        self.assertEqual(res.data['error'], 'This product already has sales or purchases, so it cannot be deleted.')
        self.assertTrue(Product.objects.filter(pk=self.product.pk).exists())


class ProductCostSourceTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='cost_owner', password='pw', role='MANAGER')
        self.client.force_authenticate(self.user)
        self.size = SizeRange.objects.create(name='Cost Size')

    def test_cop_is_optional_and_defaults_to_zero_meaning_no_manual_cost(self):
        res = self.client.post('/api/products/', {'name': 'Boot', 'unit': 'PCS', 'size_ranges': [self.size.pk]}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(Decimal(res.data['cop']), Decimal('0'))
        self.assertEqual(res.data['cost_source'], 'MISSING')

    def test_list_reports_cost_source_per_product(self):
        manual = Product.objects.create(name='Manual', unit='PCS', cop=Decimal('0'), quantity=0)
        cop = Product.objects.create(name='Cop', unit='PCS', cop=Decimal('12.00'), quantity=0)
        Product.objects.create(name='Missing', unit='PCS', cop=Decimal('0'), quantity=0)
        ProductCost.objects.create(
            product=manual, component_type=CostComponentType.objects.get(name='Labor'),
            amount_per_dozen=Decimal('5.00'), valid_from=date(2026, 1, 1),
        )
        sources = {r['name']: r['cost_source'] for r in self.client.get('/api/products/').data}
        self.assertEqual(sources, {'Manual': 'MANUAL', 'Cop': 'COP', 'Missing': 'MISSING'})


class OpeningStockLedgerTests(APITestCase):
    def setUp(self):
        self.manager = get_user_model().objects.create_user(username='opening_mgr', password='pw', role='MANAGER', is_staff=True)
        self.client.force_authenticate(self.manager)
        self.size = SizeRange.objects.create(name='Opening Size')
        self.color = Color.objects.create(name='Opening Color')

    def test_create_with_quantity_records_opening_history_row(self):
        response = self.client.post('/api/products/', {'name': 'Opening Tee', 'unit': 'PCS', 'cop': '5', 'quantity': '50'}, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        row = ProductHistory.objects.get(product_id=response.data['id'])
        self.assertEqual(row.change_type, ProductHistory.OPENING)
        self.assertEqual(row.quantity_change, Decimal('50'))
        self.assertEqual(row.reference, 'Opening stock')

    def test_create_without_quantity_records_no_history(self):
        response = self.client.post('/api/products/', {'name': 'No Stock Tee', 'unit': 'PCS', 'cop': '5'}, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertFalse(ProductHistory.objects.filter(product_id=response.data['id']).exists())

    def test_create_with_variants_records_the_variant_total_as_opening(self):
        response = self.client.post('/api/products/', {
            'name': 'Variant Tee', 'unit': 'PCS', 'cop': '5', 'size_ranges': [self.size.id],
            'variants': [{'size_range': self.size.id, 'color': self.color.id, 'quantity': '7'}],
        }, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        product = Product.objects.get(pk=response.data['id'])
        self.assertEqual(product.quantity, Decimal('7'))
        self.assertEqual(ProductHistory.objects.get(product=product).quantity_change, Decimal('7'))

    def test_bulk_import_with_quantity_writes_the_same_opening_row(self):
        response = self.client.post('/api/products/bulk_import/', {
            'data': [{'name': 'Imported Tee', 'unit': 'PCS', 'cop': '5', 'quantity': '12'}],
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        product = Product.objects.get(name='Imported Tee')
        self.assertEqual(product.quantity, Decimal('12'))
        row = ProductHistory.objects.get(product=product)
        self.assertEqual(row.change_type, ProductHistory.OPENING)
        self.assertEqual(row.quantity_change, Decimal('12'))
