from django.db import models
from django.db.models import Sum
from django.apps import apps

# Create your models here.

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
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['name', 'unit']

    def __str__(self):
        return self.name

    @property
    def available_stock(self):
        """
        Calculate real-time available stock by subtracting all sold quantities
        from the original stock quantity
        """
        # Use Django's lazy loading to avoid circular import
        SaleItem = apps.get_model('sales', 'SaleItem')
        
        # Get total quantity sold for this product
        total_sold = SaleItem.objects.filter(product=self).aggregate(
            total_sold=Sum('quantity')
        )['total_sold'] or 0
        
        # Available stock = original stock - total sold
        available = self.quantity - total_sold
        return max(0, available)  # Ensure we don't return negative values

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
