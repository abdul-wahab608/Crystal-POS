from django.db import models
from django.core.validators import MinValueValidator
from django.db.models import Sum

class RawMaterial(models.Model):
    UNIT_CHOICES = [
        ('BAG', 'Bag'),
        ('KILO', 'Kilo'),
        ('PCS', 'Pieces'),
        ('KG', 'Kilograms'),
        ('L', 'Liters'),
        ('M', 'Meters'),
        ('BOX', 'Box'),
        ('PACK', 'Pack'),
        ('UNIT', 'Unit'),
        ('GRAM', 'Grams'),
        ('TON', 'Tons'),
        ('GALLON', 'Gallons'),
        ('FOOT', 'Feet'),
        ('YARD', 'Yards'),
        ('CM', 'Centimeters'),
        ('MM', 'Millimeters'),
        ('INCH', 'Inches'),
        ('POUND', 'Pounds'),
        ('OUNCE', 'Ounces'),
        ('CUP', 'Cups'),
        ('TABLESPOON', 'Tablespoons'),
        ('TEASPOON', 'Teaspoons'),
    ]
    
    name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    reorder_level = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'unit']

    def __str__(self):
        return f"{self.name} ({self.unit})"

    @property
    def available_stock(self):
        """Calculate available stock: original + purchases - usage"""
        total_used = self.usage.aggregate(total=models.Sum('quantity_used'))['total'] or 0
        total_purchased = self.purchases.aggregate(total=models.Sum('quantity_purchased'))['total'] or 0
        return self.quantity - total_used + total_purchased
    
    @property
    def average_unit_price(self):
        """Calculate average unit price from recent purchases"""
        recent_purchases = self.purchases.order_by('-purchase_date')[:5]
        if recent_purchases:
            total = sum(p.unit_price for p in recent_purchases)
            return total / len(recent_purchases)
        return 0

    @property
    def needs_reorder(self):
        """Check if material needs reordering"""
        return self.available_stock <= self.reorder_level

class RawMaterialUsage(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='usage')
    quantity_used = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    reference = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    date_used = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.raw_material.name} - {self.quantity_used} used on {self.date_used.date()}"

    class Meta:
        ordering = ['-date_used']

class RawMaterialPurchase(models.Model):
    raw_material = models.ForeignKey(RawMaterial, on_delete=models.CASCADE, related_name='purchases')
    quantity_purchased = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    supplier = models.CharField(max_length=100, blank=True, null=True)
    invoice_number = models.CharField(max_length=50, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    purchase_date = models.DateTimeField(auto_now_add=True)
    # Payment tracking
    payment = models.ForeignKey('payments.Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='raw_material_purchases')

    def __str__(self):
        return f"{self.raw_material.name} - {self.quantity_purchased} purchased on {self.purchase_date.date()}"

    def save(self, *args, **kwargs):
        # Auto-calculate total amount
        if not self.total_amount:
            self.total_amount = self.quantity_purchased * self.unit_price
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-purchase_date']
