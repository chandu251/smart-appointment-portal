from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'tenant', 'is_staff')
    list_filter = ('role', 'tenant', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'employee_id')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Profile Fields', {
            'fields': ('role', 'tenant', 'employee_id', 'designation', 'department', 'mobile_number'),
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Profile Fields', {
            'fields': ('role', 'tenant', 'employee_id', 'designation', 'department', 'mobile_number', 'email'),
        }),
    )
