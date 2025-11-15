from django.db import models

# Create your models here.

class Asset(models.Model):
    MACHINE = 'MACHINE'
    MOLD = 'MOLD'
    EQUIPMENT = 'EQUIPMENT'
    FURNITURE = 'FURNITURE'
    VEHICLE = 'VEHICLE'
    BUILDING = 'BUILDING'
    TECHNOLOGY = 'TECHNOLOGY'
    OTHER = 'OTHER'
    ASSET_TYPE_CHOICES = [
        (MACHINE, 'Machine'),
        (MOLD, 'Mold'),
        (EQUIPMENT, 'Equipment'),
        (FURNITURE, 'Furniture'),
        (VEHICLE, 'Vehicle'),
        (BUILDING, 'Building'),
        (TECHNOLOGY, 'Technology'),
        (OTHER, 'Other'),
    ]
    
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    MAINTENANCE = 'MAINTENANCE'
    DISPOSED = 'DISPOSED'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
        (MAINTENANCE, 'Under Maintenance'),
        (DISPOSED, 'Disposed'),
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    type = models.CharField(max_length=20, choices=ASSET_TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    current_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    purchase_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class AssetLog(models.Model):
    USAGE = 'USAGE'
    MAINTENANCE = 'MAINTENANCE'
    LOG_TYPE_CHOICES = [
        (USAGE, 'Usage'),
        (MAINTENANCE, 'Maintenance'),
    ]
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=20, choices=LOG_TYPE_CHOICES)
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.asset.name} - {self.log_type} - {self.date}"
