from datetime import date
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from .models import Asset, AssetLog


class AssetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='as_user', password='pw', role=User.MANAGER)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_accountant_records_asset_with_purchase_value_and_location(self):
        res = self.client.post('/api/assets/', {
            'name': 'Embroidery Machine', 'type': 'MACHINE', 'status': 'ACTIVE',
            'purchase_value': '75000.50', 'current_value': '60000.00',
            'purchase_date': '2026-03-01', 'location': 'Factory Floor A', 'description': '',
        }, format='json')
        self.assertEqual(res.status_code, 201, res.data)
        self.assertEqual(res.data['purchase_value'], '75000.50')
        self.assertEqual(res.data['location'], 'Factory Floor A')
        asset = Asset.objects.get(pk=res.data['id'])
        self.assertEqual(asset.purchase_value, Decimal('75000.50'))

    def test_update_round_trips_decimal_strings(self):
        asset = Asset.objects.create(name='Mold A', type='MOLD', purchase_value=Decimal('1200.00'),
                                     current_value=Decimal('900.00'), purchase_date=date(2026, 1, 1))
        res = self.client.patch(f'/api/assets/{asset.id}/', {'current_value': '850.00'}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        self.assertEqual(res.data['current_value'], '850.00')

    def test_asset_log_endpoint_is_reachable(self):
        asset = Asset.objects.create(name='Van', type='VEHICLE')
        AssetLog.objects.create(asset=asset, log_type=AssetLog.MAINTENANCE, date=date(2026, 2, 2))
        res = self.client.get('/api/assets/asset-logs/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data), 1)

    def test_import_value_column_populates_current_value(self):
        from .views import AssetViewSet
        transformed, _ = AssetViewSet()._transform_row({
            'name': 'Lathe', 'type': 'MACHINE', 'value': '500.00', 'purchase_value': '800.00',
            'location': 'Shed', 'status': 'ACTIVE',
        })
        self.assertEqual(transformed['current_value'], 500.0)
        self.assertNotIn('value', transformed)

    def test_unauthenticated_access_is_rejected(self):
        self.assertEqual(APIClient().get('/api/assets/').status_code, 401)
