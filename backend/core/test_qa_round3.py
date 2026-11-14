from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from bank_accounts.models import BankAccount
from customers.models import Customer
from payments.models import Payment
from production.models import ProductionRun
from products.models import Product
from profit.models import CostComponentType, ProductCost
from sales.models import Sale
from vendors.models import Vendor, adjust_vendor_balance

User = get_user_model()


class QaRoundThreeTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='r3_admin', password='x', role=User.ADMIN)
        self.manager = User.objects.create_user(username='r3_manager', password='x', role=User.MANAGER)
        self.staff = User.objects.create_user(username='r3_staff', password='x', role=User.STAFF)
        self.client.force_authenticate(self.manager)

    def test_admin_cannot_remove_own_admin_role_or_deactivate_self(self):
        self.client.force_authenticate(self.admin)
        url = f'/api/users/{self.admin.id}/'
        self.assertEqual(self.client.patch(url, {'role': 'STAFF'}, format='json').status_code, 400)
        self.assertEqual(self.client.patch(url, {'is_active': False}, format='json').status_code, 400)
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.role, User.ADMIN)
        self.assertTrue(self.admin.is_active)

    def test_admin_can_change_another_admins_role(self):
        other = User.objects.create_user(username='r3_other_admin', password='x', role=User.ADMIN)
        self.client.force_authenticate(self.admin)
        self.assertEqual(self.client.patch(f'/api/users/{other.id}/', {'role': 'MANAGER'}, format='json').status_code, 200)

    def test_product_patch_by_staff_is_refused(self):
        product = Product.objects.create(name='R3 Tee', unit='PCS', cop=Decimal('10'), quantity=Decimal('5'))
        self.client.force_authenticate(self.staff)
        response = self.client.patch(f'/api/products/{product.id}/', {'cop': '1'}, format='json')
        self.assertEqual(response.status_code, 403)
        product.refresh_from_db()
        self.assertEqual(product.cop, Decimal('10'))

    def test_product_quantity_cannot_be_patched(self):
        product = Product.objects.create(name='R3 Shirt', unit='PCS', cop=Decimal('10'), quantity=Decimal('5'))
        response = self.client.patch(f'/api/products/{product.id}/', {'quantity': '999'}, format='json')
        self.assertEqual(response.status_code, 200)
        product.refresh_from_db()
        self.assertEqual(product.quantity, Decimal('5'))

    def test_negative_cost_of_production_is_refused(self):
        response = self.client.post('/api/products/', {'name': 'R3 Neg', 'unit': 'PCS', 'cop': '-5'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_customer_balance_cannot_be_patched(self):
        customer = Customer.objects.create(name='R3 Buyer')
        response = self.client.patch(f'/api/customers/{customer.id}/', {'balance': '1234'}, format='json')
        self.assertEqual(response.status_code, 200)
        customer.refresh_from_db()
        self.assertEqual(customer.balance, Decimal('0'))

    def test_sale_customer_cannot_be_changed(self):
        first = Customer.objects.create(name='R3 First')
        second = Customer.objects.create(name='R3 Second')
        sale = Sale.objects.create(customer=first, total_amount=Decimal('100'))
        response = self.client.patch(f'/api/sales/{sale.id}/', {'customer': second.id}, format='json')
        self.assertEqual(response.status_code, 400)
        sale.refresh_from_db()
        self.assertEqual(sale.customer_id, first.id)

    def test_profit_summary_rejects_unknown_group_by(self):
        response = self.client.get('/api/profit/summary/', {'group_by': 'foo'})
        self.assertEqual(response.status_code, 400)

    def test_profit_trend_rejects_unknown_x(self):
        response = self.client.get('/api/profit/trend/', {'x': 'foo'})
        self.assertEqual(response.status_code, 400)

    def test_cost_component_in_use_returns_409(self):
        component = CostComponentType.objects.create(name='R3 Component', is_system=False)
        product = Product.objects.create(name='R3 Costed', unit='PCS', cop=Decimal('0'))
        ProductCost.objects.create(product=product, component_type=component,
                                   amount_per_dozen=Decimal('12.5'), valid_from=date(2026, 11, 1))
        response = self.client.delete(f'/api/profit/cost-components/{component.id}/')
        self.assertEqual(response.status_code, 409)
        self.assertTrue(CostComponentType.objects.filter(pk=component.pk).exists())

    def test_staff_cannot_write_assets_or_bank_accounts(self):
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.post('/api/assets/', {'name': 'R3 Asset', 'type': 'MACHINE'}, format='json').status_code, 403)
        account = BankAccount.objects.create(name='R3 Bank', account_number='R3-1', bank_name='MCB')
        self.assertEqual(self.client.delete(f'/api/bank-accounts/{account.id}/').status_code, 403)
        self.assertTrue(BankAccount.objects.filter(pk=account.pk).exists())

    def test_asset_purchase_value_cannot_be_negative(self):
        response = self.client.post('/api/assets/', {'name': 'R3 Neg Asset', 'type': 'MACHINE', 'purchase_value': '-1'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_staff_cannot_delete_production_run(self):
        run = ProductionRun.objects.create()
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.delete(f'/api/production/runs/{run.id}/').status_code, 403)
        self.assertTrue(ProductionRun.objects.filter(pk=run.pk).exists())

    def test_payment_patch_cannot_change_status(self):
        customer = Customer.objects.create(name='R3 Payer')
        payment = Payment.objects.create(payment_type=Payment.INCOMING, payment_method=Payment.CASH,
                                         amount=Decimal('10'), customer=customer, status=Payment.COMPLETED)
        self.client.patch(f'/api/payments/{payment.id}/', {'status': Payment.PENDING}, format='json')
        payment.refresh_from_db()
        self.assertEqual(payment.status, Payment.COMPLETED)

    def test_zero_vendor_balance_is_never_stored_negative(self):
        vendor = Vendor.objects.create(name='R3 Zero Mills')
        adjust_vendor_balance(vendor.id, Decimal('-0.001'))
        vendor.refresh_from_db()
        self.assertEqual(str(vendor.balance), '0.00')

class DuplicateCostAndDeleteMessageTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='r5_manager', password='x', role=User.MANAGER)
        self.client.force_authenticate(self.manager)
        self.component = CostComponentType.objects.create(name='R5 Component', is_system=False)
        self.product = Product.objects.create(name='R5 Costed', unit='PCS', cop=Decimal('0'))

    def cost(self, valid_from, amount='25'):
        return self.client.post('/api/profit/product-costs/', {
            'product': self.product.id, 'component_type': self.component.id,
            'amount_per_dozen': amount, 'valid_from': valid_from,
        }, format='json')

    def test_same_product_component_and_date_is_rejected(self):
        self.assertEqual(self.cost('2026-11-01').status_code, 201)
        response = self.cost('2026-11-01', amount='30')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(ProductCost.objects.filter(product=self.product).count(), 1)

    def test_same_component_on_another_date_is_allowed(self):
        self.assertEqual(self.cost('2026-11-01').status_code, 201)
        self.assertEqual(self.cost('2026-12-01').status_code, 201)


class VendorCreditSplitTests(APITestCase):
    def setUp(self):
        self.manager = User.objects.create_user(username='r6_manager', password='x', role=User.MANAGER)
        self.client.force_authenticate(self.manager)

    def test_dashboard_splits_payables_from_vendor_credits(self):
        Vendor.objects.create(name='R6 Owed', balance=Decimal('100.00'))
        Vendor.objects.create(name='R6 Credit', balance=Decimal('-50.00'))
        response = self.client.get('/api/reports/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Decimal(str(response.data['vendor_payables'])), Decimal('100.00'))
        self.assertEqual(Decimal(str(response.data['vendor_credits'])), Decimal('50.00'))

