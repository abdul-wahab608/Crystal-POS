from django.db import models

# New models for size ranges and colors
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

# Product model updated to require size_range
class Product(models.Model):
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
    PRODUCT_TYPE_CHOICES = [
        ('MANUFACTURED', 'Manufactured Product'),
        ('PURCHASED', 'Purchased Item'),
    ]
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES)
    cop = models.DecimalField(max_digits=12, decimal_places=2)
    quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, default='MANUFACTURED')
    size_range = models.ForeignKey(SizeRange, on_delete=models.PROTECT, related_name='products')
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['name', 'unit', 'size_range']
    def __str__(self):
        return self.name

# Stock per product-size-color
class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size_range = models.ForeignKey(SizeRange, on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT)
    quantity_dozens = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ['product', 'size_range', 'color']
    def __str__(self):
        return f"{self.product.name} - {self.size_range.name} - {self.color.name}"

class ProductHistory(models.Model):
    SALE = 'SALE'
    PURCHASE = 'PURCHASE'
    ADJUSTMENT = 'ADJUSTMENT'
    CHANGE_TYPE_CHOICES = [
        (SALE, 'Sale'),
        (PURCHASE, 'Purchase'),
        (ADJUSTMENT, 'Adjustment'),
    ]
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='history')
    change_type = models.CharField(max_length=15, choices=CHANGE_TYPE_CHOICES)
    quantity_change = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.change_type} - {self.quantity_change}"
