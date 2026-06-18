from django.db import models

class Tenant(models.Model):
    PLAN_CHOICES = [
        ('free', 'Free Plan (1 CEO, 100 requests/mo)'),
        ('professional', 'Professional Plan (Multiple CEOs, Unlimited requests)'),
        ('enterprise', 'Enterprise Plan (Custom, Dedicated support)'),
    ]

    name = models.CharField(max_length=255, help_text="Organization/Department Name")
    slug = models.SlugField(max_length=100, unique=True, help_text="Unique slug for tenant URL routing (e.g. 'anits')")
    logo = models.ImageField(upload_to='tenant_logos/', blank=True, null=True)
    email = models.EmailField(max_length=255)
    contact_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    subscription_plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default='free')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_subscription_plan_display()})"
