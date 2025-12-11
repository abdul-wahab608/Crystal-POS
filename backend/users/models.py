from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    CASHIER = 'CASHIER'
    STAFF = 'STAFF'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (MANAGER, 'Manager'),
        (CASHIER, 'Cashier'),
        (STAFF, 'Staff'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=STAFF)
    phone = models.CharField(max_length=20, blank=True, null=True)
    
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == self.ADMIN
    
    def is_manager(self):
        return self.role in [self.ADMIN, self.MANAGER]
    
    def is_cashier(self):
        return self.role in [self.ADMIN, self.MANAGER, self.CASHIER] 