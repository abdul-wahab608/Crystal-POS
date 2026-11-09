from decimal import Decimal
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models


class ProductionRun(models.Model):
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Production run #{self.pk}"


class ProductionRunItem(models.Model):
    run = models.ForeignKey(ProductionRun, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey('products.ProductVariant', on_delete=models.PROTECT, related_name='production_items')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.variant} x {self.quantity}"


class ProductionRunInput(models.Model):
    run = models.ForeignKey(ProductionRun, on_delete=models.CASCADE, related_name='inputs')
    raw_material = models.ForeignKey('raw_materials.RawMaterial', on_delete=models.PROTECT, related_name='production_inputs')
    quantity = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.raw_material.name} x {self.quantity}"
