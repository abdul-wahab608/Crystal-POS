from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from products.models import Color, Product, ProductVariant, SizeRange
from raw_materials.models import RawMaterial, RawMaterialUsage
from .models import ProductionRun


class ProductionRunTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='maker', password='x', role='MANAGER')
        self.client.force_authenticate(self.user)
        self.size = SizeRange.objects.create(name='Men (40-46)')
        self.black = Color.objects.create(name='Black')
        self.shoe = Product.objects.create(name='Oxford', unit='PCS', cop=Decimal('100'), quantity=0)
        self.shoe.size_ranges.add(self.size)
        self.variant = ProductVariant.objects.create(product=self.shoe, size_range=self.size, color=self.black, quantity=0)
        self.leather = RawMaterial.objects.create(name='Leather', unit='KG', quantity=Decimal('20'))
        self.glue = RawMaterial.objects.create(name='Glue', unit='KG', quantity=Decimal('2'))

    def _run_payload(self, items=None, inputs=None, **extra):
        payload = {
            'reference': 'Batch 1',
            'notes': '',
            'items': items if items is not None else [{'variant': self.variant.pk, 'quantity': '6'}],
            'inputs': inputs if inputs is not None else [{'raw_material': self.leather.pk, 'quantity': '5'}],
        }
        payload.update(extra)
        return payload

    def test_create_run_increments_variant_and_product_and_consumes_raw_materials(self):
        res = self.client.post('/api/production/runs/', self._run_payload(), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(len(res.data['items']), 1)
        self.assertEqual(res.data['created_by'], self.user.pk)

        self.variant.refresh_from_db()
        self.shoe.refresh_from_db()
        self.leather.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal('6'))
        self.assertEqual(self.shoe.quantity, Decimal('6'))
        self.assertEqual(self.leather.quantity, Decimal('15'))
        usage = RawMaterialUsage.objects.get(raw_material=self.leather)
        self.assertEqual(usage.quantity_used, Decimal('5'))
        self.assertEqual(usage.reference, f'Production run #{res.data["id"]}')

    def test_insufficient_raw_material_is_rejected_and_writes_nothing(self):
        res = self.client.post('/api/production/runs/', self._run_payload(
            inputs=[{'raw_material': self.glue.pk, 'quantity': '3'}],
        ), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertEqual(ProductionRun.objects.count(), 0)
        self.variant.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal('0'))
        self.glue.refresh_from_db()
        self.assertEqual(self.glue.quantity, Decimal('2'))

    def test_run_needs_at_least_one_raw_material_input(self):
        res = self.client.post('/api/production/runs/', self._run_payload(inputs=[]), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(ProductionRun.objects.exists())

    def test_run_needs_at_least_one_output_item(self):
        res = self.client.post('/api/production/runs/', self._run_payload(items=[]), format='json')
        self.assertEqual(res.status_code, 400)

    def test_quantities_must_be_positive(self):
        res = self.client.post('/api/production/runs/', self._run_payload(
            items=[{'variant': self.variant.pk, 'quantity': '0'}],
        ), format='json')
        self.assertEqual(res.status_code, 400)

    def test_delete_reverses_outputs_and_restores_raw_materials(self):
        created = self.client.post('/api/production/runs/', self._run_payload(), format='json')
        res = self.client.delete(f"/api/production/runs/{created.data['id']}/")
        self.assertEqual(res.status_code, 204)
        self.variant.refresh_from_db()
        self.shoe.refresh_from_db()
        self.leather.refresh_from_db()
        self.assertEqual(self.variant.quantity, Decimal('0'))
        self.assertEqual(self.shoe.quantity, Decimal('0'))
        self.assertEqual(self.leather.quantity, Decimal('20'))
        self.assertFalse(RawMaterialUsage.objects.exists())

    def test_delete_is_refused_when_output_was_already_sold(self):
        created = self.client.post('/api/production/runs/', self._run_payload(), format='json')
        ProductVariant.objects.filter(pk=self.variant.pk).update(quantity=Decimal('1'))
        res = self.client.delete(f"/api/production/runs/{created.data['id']}/")
        self.assertEqual(res.status_code, 400)
        self.assertTrue(ProductionRun.objects.filter(pk=created.data['id']).exists())

    def test_runs_cannot_be_updated(self):
        created = self.client.post('/api/production/runs/', self._run_payload(), format='json')
        res = self.client.patch(f"/api/production/runs/{created.data['id']}/", {'reference': 'x'}, format='json')
        self.assertEqual(res.status_code, 405)

    def test_list_and_retrieve(self):
        created = self.client.post('/api/production/runs/', self._run_payload(), format='json')
        self.assertEqual(len(self.client.get('/api/production/runs/').data), 1)
        detail = self.client.get(f"/api/production/runs/{created.data['id']}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data['inputs'][0]['raw_material_name'], 'Leather')
