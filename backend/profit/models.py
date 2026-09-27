from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator


class CostComponentType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_system = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ProductCost(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='costs')
    component_type = models.ForeignKey(CostComponentType, on_delete=models.PROTECT, related_name='product_costs')
    amount_per_dozen = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(Decimal('0'))])
    valid_from = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-valid_from']

    def __str__(self):
        return f"{self.product.name} - {self.component_type.name} - {self.amount_per_dozen}/dz from {self.valid_from}"
