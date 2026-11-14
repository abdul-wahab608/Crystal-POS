from django.core.validators import MinValueValidator
from django.db import models
from decimal import Decimal
from core.validators import validate_unit_code


class SizeRange(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    PRODUCT_TYPE_CHOICES = [
        ('MANUFACTURED', 'Manufactured Product'),
        ('PURCHASED', 'Purchased Item'),
    ]
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20, validators=[validate_unit_code])
    cop = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='MANUFACTURED')
    size_ranges = models.ManyToManyField(SizeRange, blank=True, related_name='products')
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'unit']

    def __str__(self):
        return self.name


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size_range = models.ForeignKey(SizeRange, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0, validators=[MinValueValidator(Decimal('0'))])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['product', 'size_range', 'color']

    def __str__(self):
        return f"{self.product.name} - {self.size_range.name} - {self.color.name}"


class ProductHistory(models.Model):
    SALE = 'SALE'
    PURCHASE = 'PURCHASE'
    ADJUSTMENT = 'ADJUSTMENT'
    PRODUCTION = 'PRODUCTION'
    OPENING = 'OPENING'
    CHANGE_TYPE_CHOICES = [
        (SALE, 'Sale'),
        (PURCHASE, 'Purchase'),
        (ADJUSTMENT, 'Adjustment'),
        (PRODUCTION, 'Production'),
        (OPENING, 'Opening stock'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    change_type = models.CharField(max_length=15, choices=CHANGE_TYPE_CHOICES)
    quantity_change = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.change_type} - {self.quantity_change}"
