from django.core.exceptions import ValidationError
from django.test import TestCase

from products.models import Product


class ProductUnitValidationTests(TestCase):
    def _product(self, unit):
        return Product(name='Oxford', unit=unit, cop=100)

    def test_seeded_dozen_and_pound_units_are_accepted(self):
        self._product('DOZEN').full_clean()
        self._product('POUND').full_clean()

    def test_unknown_unit_is_rejected(self):
        with self.assertRaises(ValidationError):
            self._product('NOPE').full_clean()
