from django.test import TestCase
from rest_framework.test import APIClient

from decimal import Decimal

from bank_accounts.models import BankAccount
from customers.models import Customer
from payments.models import Payment
from users.models import User
from vendors.models import Vendor


class BankAccountTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='ba_user', password='pw', role=User.MANAGER)
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


class BankAccountBalanceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='bal_user', password='pw', role=User.MANAGER)
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.account = BankAccount.objects.create(name='Savings', account_number='777', bank_name='MCB')
        self.customer = Customer.objects.create(name='Balance Buyer')

    def balance(self):
        res = self.client.get(f'/api/bank-accounts/{self.account.id}/')
        self.assertEqual(res.status_code, 200)
        return Decimal(res.data['balance'])

    def test_account_with_no_payments_shows_zero(self):
        self.assertEqual(self.balance(), Decimal('0'))

    def test_incoming_bank_transfer_adds_and_outgoing_subtracts(self):
        Payment.objects.create(payment_type=Payment.INCOMING, payment_method=Payment.BANK, amount=Decimal('2400'),
                               customer=self.customer, bank_account=self.account)
        Payment.objects.create(payment_type=Payment.OUTGOING, payment_method=Payment.BANK, amount=Decimal('500'),
                               vendor=Vendor.objects.create(name='Bank Vendor'), bank_account=self.account)
        self.assertEqual(self.balance(), Decimal('1900'))

    def test_cash_cheque_and_parchi_do_not_count(self):
        for method in (Payment.CASH, Payment.CHEQUE, Payment.PARCHI):
            Payment.objects.create(payment_type=Payment.INCOMING, payment_method=method, amount=Decimal('300'),
                                   customer=self.customer, bank_account=self.account)
        self.assertEqual(self.balance(), Decimal('0'))

    def test_balance_is_read_only(self):
        res = self.client.patch(f'/api/bank-accounts/{self.account.id}/', {'balance': '999'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(self.balance(), Decimal('0'))

