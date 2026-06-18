from django.contrib import admin
from .models import CEOProfile, AppointmentRequest

@admin.register(CEOProfile)
class CEOProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant', 'title', 'department', 'is_active', 'created_at')
    list_filter = ('tenant', 'is_active')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'title', 'department')


@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'ceo', 'tenant', 'preferred_date', 'status', 'token_number', 'created_at')
    list_filter = ('status', 'priority', 'tenant', 'preferred_date')
    search_fields = ('full_name', 'employee_id', 'purpose', 'token_number', 'appointment_number')
    readonly_fields = ('tracking_uuid',)
