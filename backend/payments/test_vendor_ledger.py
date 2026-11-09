from decimal import Decimal

from django.test import TestCase

from payments.models import Payment
from products.models import Color, Product, SizeRange
from purchases.models import Purchase, PurchaseItem
from raw_materials.models import RawMaterial
from vendors.models import Vendor, VendorTransaction


class VendorLedgerTests(TestCase):
    def setUp(self):
        self.vendor = Vendor.objects.create(name='Chaman Textiles')
        self.material = RawMaterial.objects.create(name='Leather', unit='KG', quantity=0)

    def _balance(self):
        self.vendor.refresh_from_db()
        return self.vendor.balance

    def _raw_purchase(self, quantity='10', unit_cost='50'):
        purchase = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal(quantity) * Decimal(unit_cost))
        PurchaseItem.objects.create(
            purchase=purchase, raw_material=self.material, quantity=Decimal(quantity),
            unit_cost=Decimal(unit_cost), subtotal=Decimal(quantity) * Decimal(unit_cost),
        )
        return purchase

    def test_raw_material_purchase_on_credit_raises_vendor_balance_once(self):
        purchase = self._raw_purchase()
        self.assertEqual(self._balance(), Decimal('500'))
        ledger = VendorTransaction.objects.get(vendor=self.vendor)
        self.assertEqual(ledger.type, VendorTransaction.PURCHASE)
        self.assertEqual(ledger.amount, Decimal('500'))
        self.assertEqual(ledger.reference, f'Purchase #{purchase.pk}')
        self.assertFalse(Payment.objects.filter(purchase=purchase).exists())

    def test_deleting_raw_material_purchase_reverses_balance_and_ledger(self):
        purchase = self._raw_purchase()
        purchase.delete()
        self.assertEqual(self._balance(), Decimal('0'))
        self.assertFalse(VendorTransaction.objects.exists())

    def test_multi_line_purchase_has_one_ledger_row_for_the_document(self):
        size = SizeRange.objects.create(name='Standard')
        color = Color.objects.create(name='Black')
        cloth = Product.objects.create(name='Cloth', unit='PCS', cop=Decimal('1'))
        cloth.size_ranges.add(size)
        purchase = Purchase.objects.create(vendor=self.vendor, total_amount=Decimal('130'))
        PurchaseItem.objects.create(purchase=purchase, raw_material=self.material, quantity=Decimal('2'), unit_cost=Decimal('50'), subtotal=Decimal('100'))
        PurchaseItem.objects.create(purchase=purchase, product=cloth, size_range=size, color=color, quantity=Decimal('3'), unit_cost=Decimal('10'), subtotal=Decimal('30'))
        self.assertEqual(VendorTransaction.objects.filter(type=VendorTransaction.PURCHASE).count(), 1)
        self.assertEqual(self._balance(), Decimal('130'))

    def test_outgoing_vendor_payment_reduces_balance_and_delete_restores_it(self):
        self._raw_purchase()
        payment = Payment.objects.create(
            payment_type=Payment.OUTGOING, payment_method=Payment.CASH,
            amount=Decimal('200'), vendor=self.vendor,
        )
        self.assertEqual(self._balance(), Decimal('300'))
        payment.delete()
        self.assertEqual(self._balance(), Decimal('500'))

    def test_deleting_purchase_after_payment_does_not_double_reverse(self):
        purchase = self._raw_purchase()
        Payment.objects.create(
            payment_type=Payment.OUTGOING, payment_method=Payment.CASH,
            amount=Decimal('200'), vendor=self.vendor, purchase=purchase,
        )
        purchase.delete()
        self.assertEqual(self._balance(), Decimal('-200'))
        self.assertEqual(VendorTransaction.objects.filter(type=VendorTransaction.PAYMENT).count(), 1)

    def test_incoming_payment_does_not_touch_vendor_balance(self):
        Payment.objects.create(
            payment_type=Payment.INCOMING, payment_method=Payment.CASH,
            amount=Decimal('200'), vendor=self.vendor,
        )
        self.assertEqual(self._balance(), Decimal('0'))
