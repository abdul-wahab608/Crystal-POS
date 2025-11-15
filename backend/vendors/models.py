from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.

class Vendor(models.Model):
    name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    contact_person = models.CharField(max_length=255, blank=True, null=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class VendorProduct(models.Model):
    """
    Tracks which products/raw materials a vendor supplies and their pricing
    Supports both finished products and raw materials
    """
    PRODUCT_TYPE_CHOICES = [
        ('PRODUCT', 'Finished Product'),
        ('RAW_MATERIAL', 'Raw Material'),
    ]
    
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='vendor_products')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES)
    
    # For finished products
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_supplies')
    
    # For raw materials
    raw_material = models.ForeignKey('raw_materials.RawMaterial', on_delete=models.CASCADE, null=True, blank=True, related_name='vendor_supplies')
    
    # Pricing information
    unit_price = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    minimum_order_quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    lead_time_days = models.IntegerField(default=0, help_text="Lead time in days")
    
    # Status
    is_preferred = models.BooleanField(default=False, help_text="Mark as preferred supplier for this item")
    is_active = models.BooleanField(default=True)
    
    # Metadata
    notes = models.TextField(blank=True, null=True)
    last_purchase_date = models.DateTimeField(null=True, blank=True)
    last_purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['vendor__name', 'product_type']
        # Ensure a vendor can't be added twice for the same product
        constraints = [
            models.CheckConstraint(
                check=models.Q(product__isnull=False) | models.Q(raw_material__isnull=False),
                name='vendor_product_item_required'
            ),
            models.CheckConstraint(
                check=~(models.Q(product__isnull=False) & models.Q(raw_material__isnull=False)),
                name='vendor_product_only_one_item'
            )
        ]

    def __str__(self):
        item_name = self.product.name if self.product else (self.raw_material.name if self.raw_material else "Unknown")
        return f"{self.vendor.name} - {item_name} @ ${self.unit_price}"
    
    @property
    def item_name(self):
        """Get the name of the product or raw material"""
        if self.product:
            return f"{self.product.name} ({self.product.unit})"
        elif self.raw_material:
            return f"{self.raw_material.name} ({self.raw_material.unit})"
        return "Unknown"
    
    @property
    def item_unit(self):
        """Get the unit of the product or raw material"""
        if self.product:
            return self.product.unit
        elif self.raw_material:
            return self.raw_material.unit
        return ""

class VendorTransaction(models.Model):
    PURCHASE = 'PURCHASE'
    PAYMENT = 'PAYMENT'
    TRANSACTION_TYPE_CHOICES = [
        (PURCHASE, 'Purchase'),
        (PAYMENT, 'Payment'),
    ]
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    reference = models.CharField(max_length=255, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.type} - {self.amount}"
