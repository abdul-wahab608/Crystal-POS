"""
Core models for system-wide functionality
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Unit(models.Model):
    """
    Dynamic unit model for products and raw materials.
    Replaces hardcoded UNIT_CHOICES with database-driven units.
    """
    code = models.CharField(max_length=20, unique=True, help_text="Uppercase code, e.g., 'KG', 'DOZEN'")
    name = models.CharField(max_length=50, help_text="Display name, e.g., 'Kilograms', 'Dozens'")
    is_system = models.BooleanField(default=False, help_text="System units cannot be deleted")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"

    def save(self, *args, **kwargs):
        # Always uppercase the code
        self.code = self.code.upper().strip()
        self.name = self.name.strip()
        super().save(*args, **kwargs)


class ImportSession(models.Model):
    """
    Tracks import operations for history and undo functionality.
    """
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('partial', 'Partial Success'),
        ('failed', 'Failed'),
        ('undone', 'Undone'),
    ]

    ENTITY_CHOICES = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('product', 'Product'),
        ('raw_material', 'Raw Material'),
        ('asset', 'Asset'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_type = models.CharField(max_length=20, choices=ENTITY_CHOICES)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='import_sessions'
    )
    file_name = models.CharField(max_length=255, help_text="Original uploaded filename")
    total_rows = models.IntegerField(default=0)
    success_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    duplicate_count = models.IntegerField(default=0)
    imported_ids = models.JSONField(default=list, help_text="List of created record IDs")
    errors = models.JSONField(default=list, help_text="List of error details per row")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    created_at = models.DateTimeField(auto_now_add=True)
    undone_at = models.DateTimeField(null=True, blank=True)
    undo_expires_at = models.DateTimeField(help_text="Undo available until this time")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Import Session'
        verbose_name_plural = 'Import Sessions'

    def __str__(self):
        return f"{self.entity_type} import - {self.file_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"

    def save(self, *args, **kwargs):
        # Auto-set undo expiry to 7 days from creation
        if not self.undo_expires_at:
            self.undo_expires_at = timezone.now() + timedelta(days=7)
        super().save(*args, **kwargs)

    @property
    def can_undo(self):
        """Check if this import can still be undone"""
        if self.status == 'undone':
            return False
        if self.status == 'failed':
            return False
        return timezone.now() < self.undo_expires_at

    @property
    def undo_time_remaining(self):
        """Return time remaining for undo in human-readable format"""
        if not self.can_undo:
            return None
        remaining = self.undo_expires_at - timezone.now()
        days = remaining.days
        hours = remaining.seconds // 3600
        if days > 0:
            return f"{days} day{'s' if days != 1 else ''}"
        return f"{hours} hour{'s' if hours != 1 else ''}"
