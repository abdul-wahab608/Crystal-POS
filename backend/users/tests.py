from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User


class UserManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='um_admin', password='adminpw', role=User.ADMIN)
        self.staff = User.objects.create_user(username='um_staff', password='staffpw', role=User.STAFF)
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_admin_creates_user_with_role_and_password_that_can_log_in(self):
        res = self.client.post('/api/users/', {
            'username': 'cashier1', 'first_name': 'Ali', 'last_name': 'Khan', 'email': 'ali@example.com',
            'role': 'CASHIER', 'password': 'secret123', 'is_active': True,
        }, format='json')
        self.assertEqual(res.status_code, 201, res.data)
        self.assertNotIn('password', res.data)
        created = User.objects.get(username='cashier1')
        self.assertEqual(created.role, User.CASHIER)
        self.assertTrue(created.check_password('secret123'))

        login = APIClient().post('/api/users/auth/login/', {'username': 'cashier1', 'password': 'secret123'}, format='json')
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.data['user']['role'], 'CASHIER')

    def test_create_without_password_is_rejected(self):
        res = self.client.post('/api/users/', {'username': 'nopw', 'role': 'STAFF'}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('password', res.data)

    def test_update_with_blank_password_keeps_existing_password(self):
        res = self.client.patch(f'/api/users/{self.staff.id}/', {'role': 'MANAGER', 'password': ''}, format='json')
        self.assertEqual(res.status_code, 200, res.data)
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.role, User.MANAGER)
        self.assertTrue(self.staff.check_password('staffpw'))

    def test_update_with_password_changes_it(self):
        self.client.patch(f'/api/users/{self.staff.id}/', {'password': 'newpass1'}, format='json')
        self.staff.refresh_from_db()
        self.assertTrue(self.staff.check_password('newpass1'))

    def test_non_admin_cannot_list_users(self):
        self.client.force_authenticate(user=self.staff)
        self.assertEqual(self.client.get('/api/users/').status_code, 403)

    def test_admin_cannot_delete_own_account(self):
        res = self.client.delete(f'/api/users/{self.admin.id}/')
        self.assertEqual(res.status_code, 400)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_last_login_is_returned_after_login(self):
        APIClient().post('/api/users/auth/login/', {'username': 'um_staff', 'password': 'staffpw'}, format='json')
        res = self.client.get(f'/api/users/{self.staff.id}/')
        self.assertIsNotNone(res.data['last_login'])
