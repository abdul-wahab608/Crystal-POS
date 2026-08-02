"""
Tests for core mixins: BulkImportMixin, BulkExportMixin, BatchActionsMixin
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from io import BytesIO
import json

from customers.models import Customer
from vendors.models import Vendor
from products.models import Product


User = get_user_model()


class BulkExportMixinTests(APITestCase):
    """Tests for the BulkExportMixin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        self.user.set_password('admin123')
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test customers
        self.customer1 = Customer.objects.create(
            name='Test Customer 1',
            phone='1234567890',
            address='123 Test St',
            is_active=True
        )
        self.customer2 = Customer.objects.create(
            name='Test Customer 2',
            phone='0987654321',
            address='456 Test Ave',
            is_active=False
        )

    def test_export_csv(self):
        """Test CSV export functionality"""
        response = self.client.get('/api/customers/export/', {'export_format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response['Content-Type'], ['text/csv', 'text/csv; charset=utf-8'])
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.csv', response['Content-Disposition'])
        # Check content contains customer data
        content = response.content.decode('utf-8')
        self.assertIn('Test Customer 1', content)
        self.assertIn('Test Customer 2', content)

    def test_export_excel(self):
        """Test Excel export functionality"""
        response = self.client.get('/api/customers/export/', {'export_format': 'excel'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response['Content-Type'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        self.assertIn('attachment', response['Content-Disposition'])
        self.assertIn('.xlsx', response['Content-Disposition'])
    
    def test_export_default_format(self):
        """Test export defaults to CSV when no format specified"""
        response = self.client.get('/api/customers/export/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(response['Content-Type'], ['text/csv', 'text/csv; charset=utf-8'])
    
    def test_export_unauthenticated(self):
        """Test export requires authentication"""
        self.client.logout()
        response = self.client.get('/api/customers/export/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class BatchActionsMixinTests(APITestCase):
    """Tests for the BatchActionsMixin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        self.user.set_password('admin123')
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test customers
        self.customer1 = Customer.objects.create(
            name='Batch Customer 1',
            phone='1111111111',
            is_active=True
        )
        self.customer2 = Customer.objects.create(
            name='Batch Customer 2',
            phone='2222222222',
            is_active=True
        )
        self.customer3 = Customer.objects.create(
            name='Batch Customer 3',
            phone='3333333333',
            is_active=False
        )
    
    def test_bulk_delete(self):
        """Test bulk delete functionality"""
        ids = [self.customer1.id, self.customer2.id]
        response = self.client.post(
            '/api/customers/bulk_delete/',
            {'ids': ids},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
        
        # Verify customers are deleted
        self.assertFalse(Customer.objects.filter(id=self.customer1.id).exists())
        self.assertFalse(Customer.objects.filter(id=self.customer2.id).exists())
        self.assertTrue(Customer.objects.filter(id=self.customer3.id).exists())
    
    def test_bulk_delete_empty_ids(self):
        """Test bulk delete with empty IDs list"""
        response = self.client.post(
            '/api/customers/bulk_delete/',
            {'ids': []},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_bulk_activate(self):
        """Test bulk activate functionality"""
        # First deactivate customer1
        self.customer1.is_active = False
        self.customer1.save()
        
        ids = [self.customer1.id, self.customer3.id]
        response = self.client.post(
            '/api/customers/bulk_activate/',
            {'ids': ids},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        # Verify customers are activated
        self.customer1.refresh_from_db()
        self.customer3.refresh_from_db()
        self.assertTrue(self.customer1.is_active)
        self.assertTrue(self.customer3.is_active)
    
    def test_bulk_deactivate(self):
        """Test bulk deactivate functionality"""
        ids = [self.customer1.id, self.customer2.id]
        response = self.client.post(
            '/api/customers/bulk_deactivate/',
            {'ids': ids},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        # Verify customers are deactivated
        self.customer1.refresh_from_db()
        self.customer2.refresh_from_db()
        self.assertFalse(self.customer1.is_active)
        self.assertFalse(self.customer2.is_active)
    
    def test_bulk_update(self):
        """Test bulk update functionality"""
        ids = [self.customer1.id, self.customer2.id]
        response = self.client.post(
            '/api/customers/bulk_update/',
            {
                'ids': ids,
                'data': {'is_active': False}
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)
        
        # Verify customers are updated
        self.customer1.refresh_from_db()
        self.customer2.refresh_from_db()
        self.assertFalse(self.customer1.is_active)
        self.assertFalse(self.customer2.is_active)
    
    def test_bulk_update_restricted_field(self):
        """Test bulk update doesn't allow updating restricted fields"""
        ids = [self.customer1.id]
        response = self.client.post(
            '/api/customers/bulk_update/',
            {
                'ids': ids,
                'data': {'name': 'Hacked Name'}  # name not in batch_update_fields
            },
            format='json'
        )
        # Should reject since 'name' isn't an allowed batch_update_fields entry
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.customer1.refresh_from_db()
        self.assertEqual(self.customer1.name, 'Batch Customer 1')  # Unchanged


class BulkImportMixinTests(APITestCase):
    """Tests for the BulkImportMixin functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        self.user.set_password('admin123')
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
    
    def test_download_template(self):
        """Test template download functionality"""
        response = self.client.get('/api/customers/download_template/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_validate_import_no_file(self):
        """Test validation fails without file"""
        response = self.client.post('/api/customers/validate_import/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_import_fields(self):
        """Test get import fields endpoint"""
        response = self.client.get('/api/customers/get_import_fields/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('fields', response.data)
        
        # Check required fields are present
        field_names = [f['name'] for f in response.data['fields']]
        self.assertIn('name', field_names)
        self.assertIn('phone', field_names)


class VendorBatchActionsTests(APITestCase):
    """Tests for vendor batch actions"""
    
    def setUp(self):
        """Set up test data"""
        self.user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        self.user.set_password('admin123')
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        
        # Create test vendors
        self.vendor1 = Vendor.objects.create(
            name='Test Vendor 1',
            contact_person='Contact 1',
            phone='1234567890',
            is_active=True
        )
        self.vendor2 = Vendor.objects.create(
            name='Test Vendor 2',
            contact_person='Contact 2',
            phone='0987654321',
            is_active=True
        )

    def test_vendor_export(self):
        """Test vendor export"""
        response = self.client.get('/api/vendors/export/', {'export_format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode('utf-8')
        self.assertIn('Test Vendor 1', content)
    
    def test_vendor_bulk_delete(self):
        """Test vendor bulk delete"""
        ids = [self.vendor1.id]
        response = self.client.post(
            '/api/vendors/bulk_delete/',
            {'ids': ids},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Vendor.objects.filter(id=self.vendor1.id).exists())


class ProductBatchActionsTests(APITestCase):
    """Tests for product batch actions"""
    
    def setUp(self):
        """Set up test data"""
        self.user, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_superuser': True,
                'is_staff': True
            }
        )
        self.user.set_password('admin123')
        self.user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # Create a SizeRange for products
        from products.models import SizeRange
        self.size_range = SizeRange.objects.create(name='Default Size')

        # Create test products
        self.product1 = Product.objects.create(
            name='Test Product 1',
            unit='PCS',
            quantity=100,
            cop=10.00,
            size_range=self.size_range
        )
        self.product2 = Product.objects.create(
            name='Test Product 2',
            unit='KG',
            quantity=50,
            cop=25.00,
            size_range=self.size_range
        )
    
    def test_product_export(self):
        """Test product export"""
        response = self.client.get('/api/products/export/', {'export_format': 'csv'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        content = response.content.decode('utf-8')
        self.assertIn('Test Product 1', content)
    
    def test_product_bulk_delete(self):
        """Test product bulk delete"""
        ids = [self.product1.id, self.product2.id]
        response = self.client.post(
            '/api/products/bulk_delete/',
            {'ids': ids},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['deleted_count'], 2)
