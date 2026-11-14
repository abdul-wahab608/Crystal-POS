from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from core.validators import validate_unit_code


class RawMaterial(models.Model):
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, validators=[validate_unit_code])
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'unit']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def needs_reorder(self):
        return self.quantity <= self.reorder_level


class RawMaterialHistory(models.Model):
    OPENING = 'OPENING'
    CHANGE_TYPE_CHOICES = [
        (OPENING, 'Opening stock'),
    ]
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='history')
    change_type = models.CharField(max_length=15, choices=CHANGE_TYPE_CHOICES)
    quantity_change = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        ordering = ['date', 'id']

    def __str__(self):
        return f"{self.raw_material.name} - {self.change_type} - {self.quantity_change}"


class RawMaterialUsage(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='usage')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_used = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_used']

    def __str__(self):
        return f"{self.raw_material.name} - {self.quantity_used} used on {self.date_used.date()}"
