from django.db import models

# Create your models here.

class BankAccount(models.Model):
    name = models.CharField(max_length=100, help_text="Account holder or nickname")
    account_number = models.CharField(max_length=50, unique=True)
    bank_name = models.CharField(max_length=100)
    branch = models.CharField(max_length=100, blank=True, null=True)
    ifsc_code = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.bank_name} ({self.account_number})"
