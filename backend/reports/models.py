from django.db import models

# Placeholder for future report models or report generation logic

class Report(models.Model):
    REPORT_TYPES = [
        ('SALES', 'Sales Report'),
        ('INVENTORY', 'Inventory Report'),
        ('CUSTOMER', 'Customer Report'),
        ('VENDOR', 'Vendor Report'),
        ('FINANCIAL', 'Financial Report'),
    ]
    
    name = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey('users.User', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    file_path = models.CharField(max_length=500, blank=True, null=True)
    parameters = models.JSONField(default=dict)
    
    def __str__(self):
        return f"{self.name} - {self.get_report_type_display()}"
    
    class Meta:
        ordering = ['-generated_at']
