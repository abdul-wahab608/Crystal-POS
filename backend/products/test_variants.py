from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from customers.models import Customer
from products.models import Color, Product, ProductVariant, SizeRange
from production.models import ProductionRun, ProductionRunItem
from sales.models import Sale, SaleItem


class ProductVariantsNestedTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='owner', password='pw', role='MANAGER', is_staff=True)
        self.client.force_authenticate(self.user)
        self.men = SizeRange.objects.create(name='Men (40-46)')
        self.women = SizeRange.objects.create(name='Women (36-41)')
        self.kids = SizeRange.objects.create(name='Kids (24-30)')
        self.black = Color.objects.create(name='Black')
        self.brown = Color.objects.create(name='Brown')

    def _payload(self, variants, size_ranges=None, **overrides):
        data = {
            'name': 'Oxford',
            'unit': 'DOZEN',
            'cop': '100.00',
            'size_ranges': size_ranges if size_ranges is not None else [self.men.pk, self.women.pk],
            'variants': variants,
        }
        data.update(overrides)
        return data

    def test_nested_create_stores_variants_and_sums_quantity(self):
        variants = [
            {'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '4'},
            {'size_range': self.women.pk, 'color': self.black.pk, 'quantity': '2.5'},
            {'size_range': self.men.pk, 'color': self.brown.pk, 'quantity': '3'},
        ]
        res = self.client.post('/api/products/', self._payload(variants), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(Decimal(res.data['quantity']), Decimal('9.5'))
        self.assertEqual(len(res.data['variants']), 3)
        self.assertEqual(ProductVariant.objects.count(), 3)

    def test_nested_create_rejects_size_range_not_on_product(self):
        variants = [{'size_range': self.kids.pk, 'color': self.black.pk, 'quantity': '1'}]
        res = self.client.post('/api/products/', self._payload(variants), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('variants', res.data)
        self.assertFalse(Product.objects.filter(name='Oxford').exists())

    def test_nested_create_rejects_duplicate_size_and_color(self):
        variants = [
            {'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '1'},
            {'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '2'},
        ]
        res = self.client.post('/api/products/', self._payload(variants), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(Product.objects.exists())

    def test_nested_update_removes_variants_not_in_list_and_recomputes_quantity(self):
        create = self.client.post('/api/products/', self._payload([
            {'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '4'},
            {'size_range': self.men.pk, 'color': self.brown.pk, 'quantity': '6'},
        ], size_ranges=[self.men.pk]), format='json')
        product_id = create.data['id']
        res = self.client.patch(f'/api/products/{product_id}/', {
            'variants': [{'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '10'}],
        }, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(Decimal(res.data['quantity']), Decimal('10'))
        self.assertEqual(ProductVariant.objects.filter(product_id=product_id).count(), 1)
        self.assertEqual(Decimal(res.data['variants'][0]['quantity']), Decimal('10'))

    def test_removing_size_range_that_still_has_variants_is_rejected(self):
        create = self.client.post('/api/products/', self._payload([
            {'size_range': self.women.pk, 'color': self.black.pk, 'quantity': '4'},
        ]), format='json')
        res = self.client.patch(f'/api/products/{create.data["id"]}/', {'size_ranges': [self.men.pk]}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('size_ranges', res.data)

    def test_removing_variant_used_in_production_is_rejected_and_rolled_back(self):
        create = self.client.post('/api/products/', self._payload([
            {'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '4'},
            {'size_range': self.men.pk, 'color': self.brown.pk, 'quantity': '6'},
        ], size_ranges=[self.men.pk]), format='json')
        product_id = create.data['id']
        used = ProductVariant.objects.get(product_id=product_id, color=self.brown)
        ProductionRunItem.objects.create(run=ProductionRun.objects.create(), variant=used, quantity=1)
        res = self.client.patch(f'/api/products/{product_id}/', {
            'variants': [{'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '4'}],
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(ProductVariant.objects.filter(product_id=product_id).count(), 2)

    def test_more_than_three_size_ranges_is_rejected_on_nested_create(self):
        extra = SizeRange.objects.create(name='Unisex')
        res = self.client.post(
            '/api/products/',
            self._payload([], size_ranges=[self.men.pk, self.women.pk, self.kids.pk, extra.pk]),
            format='json',
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn('size_ranges', res.data)

    def test_delete_product_in_use_by_sale_returns_409(self):
        res = self.client.post('/api/products/', self._payload([
            {'size_range': self.men.pk, 'color': self.black.pk, 'quantity': '4'},
        ], size_ranges=[self.men.pk]), format='json')
        product = Product.objects.get(pk=res.data['id'])
        sale = Sale.objects.create(customer=Customer.objects.create(name='Buyer'), total_amount=Decimal('100'))
        SaleItem.objects.create(
            sale=sale, product=product, size_range=self.men, color=self.black,
            quantity=Decimal('1'), unit_price=Decimal('100'), subtotal=Decimal('100'),
        )
        res = self.client.delete(f'/api/products/{product.pk}/')
        self.assertEqual(res.status_code, 409)
        self.assertTrue(Product.objects.filter(pk=product.pk).exists())

    def test_import_links_two_size_ranges_separated_by_semicolon(self):
        rows = [{'name': 'Loafer', 'unit': 'DOZEN', 'size_range': 'Men (40-46); Women (36-41)', 'cop': '200', 'quantity': '0'}]
        res = self.client.post('/api/products/bulk_import/', {'data': rows}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.data['success_count'], 1)
        product = Product.objects.get(name='Loafer')
        self.assertEqual(sorted(product.size_ranges.values_list('name', flat=True)), ['Men (40-46)', 'Women (36-41)'])

    def test_import_with_unknown_second_size_range_fails_the_row(self):
        rows = [{'name': 'Loafer', 'unit': 'DOZEN', 'size_range': 'Men (40-46), Nope', 'cop': '200'}]
        res = self.client.post('/api/products/bulk_import/', {'data': rows}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(res.data['error_count'], 1)
        self.assertFalse(Product.objects.filter(name='Loafer').exists())

    def test_editing_a_product_without_variants_keeps_its_quantity(self):
        product = Product.objects.create(name='Legacy', unit='DOZEN', cop=1, quantity=7)
        res = self.client.patch(f'/api/products/{product.pk}/', {'variants': []}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        product.refresh_from_db()
        self.assertEqual(product.quantity, Decimal('7'))
