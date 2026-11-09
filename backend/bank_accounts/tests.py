from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User


class BankAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ba_user', password='pw', role=User.STAFF)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.payload = {
            'name': 'Crystal Traders', 'account_number': '0012345678', 'bank_name': 'Meezan Bank',
            'branch': 'Gulberg', 'ifsc_code': 'MEZN0001', 'is_active': True,
        }

    def test_create_and_list(self):
        res = self.client.post('/api/bank-accounts/', self.payload, format='json')
        self.assertEqual(res.status_code, 201, res.data)
        listed = self.client.get('/api/bank-accounts/').data
        self.assertEqual(len(listed), 1)
        self.assertEqual(listed[0]['bank_name'], 'Meezan Bank')

    def test_duplicate_account_number_is_rejected(self):
        self.client.post('/api/bank-accounts/', self.payload, format='json')
        res = self.client.post('/api/bank-accounts/', {**self.payload, 'name': 'Other'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('account_number', res.data)

    def test_unauthenticated_access_is_rejected(self):
        self.assertEqual(APIClient().get('/api/bank-accounts/').status_code, 401)
