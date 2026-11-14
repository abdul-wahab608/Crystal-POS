from raw_materials.models import RawMaterialHistory
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase

from raw_materials.models import RawMaterial, RawMaterialUsage
from vendors.models import Vendor


class RawMaterialApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='owner', password='pw', is_staff=True, role=get_user_model().MANAGER)
        self.client.force_authenticate(self.user)
        self.vendor = Vendor.objects.create(name='Chaman Textiles')

    def _material(self, **overrides):
        data = {'name': 'Leather', 'unit': 'POUND', 'quantity': '10', 'reorder_level': '2'}
        data.update(overrides)
        return data

    def test_create_list_retrieve_update_delete(self):
        res = self.client.post('/api/raw-materials/materials/', self._material(), format='json')
        self.assertEqual(res.status_code, 201, res.content)
        pk = res.data['id']
        self.assertEqual(Decimal(res.data['quantity']), Decimal('10'))
        self.assertNotIn('available_stock', res.data)
        self.assertEqual(self.client.get('/api/raw-materials/materials/').status_code, 200)
        self.assertEqual(self.client.get(f'/api/raw-materials/materials/{pk}/').status_code, 200)
        res = self.client.put(f'/api/raw-materials/materials/{pk}/', self._material(quantity='20'), format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(Decimal(res.data['quantity']), Decimal('10'))
        self.assertEqual(self.client.delete(f'/api/raw-materials/materials/{pk}/').status_code, 204)

    def test_unknown_unit_is_rejected(self):
        res = self.client.post('/api/raw-materials/materials/', self._material(unit='NOPE'), format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('unit', res.data)

    def test_negative_quantity_is_rejected(self):
        res = self.client.post('/api/raw-materials/materials/', self._material(quantity='-1'), format='json')
        self.assertEqual(res.status_code, 400)

    def test_duplicate_name_and_unit_is_rejected(self):
        self.client.post('/api/raw-materials/materials/', self._material(), format='json')
        res = self.client.post('/api/raw-materials/materials/', self._material(), format='json')
        self.assertEqual(res.status_code, 400)

    def test_raw_purchase_line_adds_stock_once(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=10, reorder_level=2)
        res = self.client.post('/api/purchases/', {
            'vendor': self.vendor.id,
            'items': [{'raw_material': material.pk, 'quantity': '5', 'unit_cost': '100'}],
        }, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        self.assertEqual(Decimal(res.data['total_amount']), Decimal('500'))
        material.refresh_from_db()
        self.assertEqual(material.quantity, Decimal('15'))

    def test_deleting_raw_purchase_removes_its_stock(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=0, reorder_level=0)
        purchase = self.client.post('/api/purchases/', {
            'vendor': self.vendor.id,
            'items': [{'raw_material': material.pk, 'quantity': '5', 'unit_cost': '1'}],
        }, format='json').data
        self.assertEqual(self.client.delete(f"/api/purchases/{purchase['id']}/").status_code, 204)
        material.refresh_from_db()
        self.assertEqual(material.quantity, Decimal('0'))

    def test_usage_within_stock_is_recorded_and_deducted(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=10, reorder_level=0)
        res = self.client.post('/api/raw-materials/usage/', {'raw_material': material.pk, 'quantity_used': '4', 'reference': 'Batch 1'}, format='json')
        self.assertEqual(res.status_code, 201, res.content)
        material.refresh_from_db()
        self.assertEqual(material.quantity, Decimal('6'))
        self.assertEqual(len(self.client.get(f'/api/raw-materials/materials/{material.pk}/usage/').data), 1)

    def test_deleting_usage_restores_stock(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=10, reorder_level=0)
        usage = self.client.post('/api/raw-materials/usage/', {'raw_material': material.pk, 'quantity_used': '4'}, format='json').data
        self.assertEqual(self.client.delete(f"/api/raw-materials/usage/{usage['id']}/").status_code, 204)
        material.refresh_from_db()
        self.assertEqual(material.quantity, Decimal('10'))

    def test_usage_beyond_stock_is_rejected(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=3, reorder_level=0)
        res = self.client.post('/api/raw-materials/usage/', {'raw_material': material.pk, 'quantity_used': '4'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('error', res.data)
        self.assertEqual(RawMaterialUsage.objects.count(), 0)

    def test_usage_is_not_editable(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=10, reorder_level=0)
        usage = self.client.post('/api/raw-materials/usage/', {'raw_material': material.pk, 'quantity_used': '1'}, format='json').data
        res = self.client.patch(f"/api/raw-materials/usage/{usage['id']}/", {'quantity_used': '9'}, format='json')
        self.assertEqual(res.status_code, 405)

    def test_low_stock_lists_materials_at_or_below_reorder_level(self):
        RawMaterial.objects.create(name='Low', unit='POUND', quantity=1, reorder_level=5)
        RawMaterial.objects.create(name='Fine', unit='POUND', quantity=50, reorder_level=5)
        res = self.client.get('/api/raw-materials/materials/low_stock/')
        self.assertEqual([m['name'] for m in res.data], ['Low'])

    def test_purchase_history_endpoint_is_gone(self):
        material = RawMaterial.objects.create(name='Leather', unit='POUND', quantity=0, reorder_level=0)
        self.assertEqual(self.client.get(f'/api/raw-materials/materials/{material.pk}/purchase_history/').status_code, 404)
        self.assertEqual(self.client.get('/api/raw-materials/purchase/').status_code, 404)

    def test_material_used_in_a_purchase_cannot_be_deleted(self):
        material = RawMaterial.objects.create(name='Sole', unit='PCS')
        self.client.post('/api/purchases/', {
            'vendor': self.vendor.id,
            'items': [{'raw_material': material.id, 'quantity': 5, 'unit_cost': 2}],
        }, format='json')
        response = self.client.delete(f'/api/raw-materials/materials/{material.id}/')
        self.assertEqual(response.status_code, 409)
        self.assertIn('cannot be deleted', response.data['error'])
        self.assertTrue(RawMaterial.objects.filter(pk=material.pk).exists())

    def test_bulk_import_json(self):
        rows = [{'name': 'Thread', 'unit': 'POUND', 'quantity': '4', 'reorder_level': '1'}]
        res = self.client.post('/api/raw-materials/materials/bulk_import/', {'data': rows}, format='json')
        self.assertEqual(res.status_code, 200, res.content)
        self.assertEqual(res.data['success_count'], 1)


class RawMaterialOpeningStockTests(APITestCase):
    def setUp(self):
        self.admin = get_user_model().objects.create_user(username='raw_opening_admin', password='pw', role='ADMIN', is_staff=True)
        self.client.force_authenticate(self.admin)

    def test_create_with_quantity_records_opening_row(self):
        response = self.client.post('/api/raw-materials/materials/', {'name': 'Opening Steel', 'unit': 'KG', 'quantity': '100'}, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        material = RawMaterial.objects.get(pk=response.data['id'])
        self.assertEqual(material.quantity, Decimal('100'))
        row = RawMaterialHistory.objects.get(raw_material=material)
        self.assertEqual(row.change_type, RawMaterialHistory.OPENING)
        self.assertEqual(row.quantity_change, Decimal('100'))
        self.assertEqual(row.reference, 'Opening stock')

    def test_create_without_quantity_records_no_row(self):
        response = self.client.post('/api/raw-materials/materials/', {'name': 'Empty Steel', 'unit': 'KG'}, format='json')
        self.assertEqual(response.status_code, 201, response.content)
        self.assertFalse(RawMaterialHistory.objects.filter(raw_material_id=response.data['id']).exists())

    def test_bulk_import_with_quantity_writes_the_same_opening_row(self):
        response = self.client.post('/api/raw-materials/materials/bulk_import/', {
            'data': [{'name': 'Imported Steel', 'unit': 'KG', 'quantity': '25'}],
        }, format='json')
        self.assertEqual(response.status_code, 200, response.content)
        material = RawMaterial.objects.get(name='Imported Steel')
        self.assertEqual(material.quantity, Decimal('25'))
        row = RawMaterialHistory.objects.get(raw_material=material)
        self.assertEqual(row.change_type, RawMaterialHistory.OPENING)
        self.assertEqual(row.quantity_change, Decimal('25'))


class RawMaterialImportHeaderTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='import_admin', password='pw', role='ADMIN', is_staff=True)
        self.client.force_authenticate(self.user)

    def test_spreadsheet_headers_with_spaces_are_auto_mapped(self):
        csv = b'Material Name,Unit,Initial Stock,Reorder Level\nSteel Rod,KG,100,10\n'
        upload = SimpleUploadedFile('materials.csv', csv, content_type='text/csv')
        response = self.client.post('/api/raw-materials/materials/preview_import/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, 200, response.content)
        self.assertEqual(response.data['suggested_mappings'], {
            'Material Name': 'name',
            'Unit': 'unit',
            'Initial Stock': 'quantity',
            'Reorder Level': 'reorder_level',
        })

