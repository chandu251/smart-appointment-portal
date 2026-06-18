from django.db import models
from django.contrib.auth.models import AbstractUser
from tenants.models import Tenant

class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('ceo', 'CEO / Executive'),
        ('staff', 'Staff / Faculty / Employee'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='users', blank=True, null=True, help_text="The tenant organization this user belongs to.")
    employee_id = models.CharField(max_length=50, blank=True, null=True, help_text="Employee or Faculty ID")
    designation = models.CharField(max_length=100, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)

    def is_super_admin(self):
        return self.role == 'super_admin' or self.is_superuser

    def is_ceo(self):
        return self.role == 'ceo'

    def is_staff_user(self):
        return self.role == 'staff'

    def __str__(self):
        tenant_name = self.tenant.name if self.tenant else "System"
        return f"{self.get_full_name() or self.username} ({self.get_role_display()} - {tenant_name})"
