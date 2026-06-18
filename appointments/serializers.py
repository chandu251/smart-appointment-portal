from rest_framework import serializers
from tenants.models import Tenant
from .models import CEOProfile, AppointmentRequest

class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = ['id', 'name', 'slug', 'logo', 'email', 'contact_number', 'address', 'subscription_plan', 'is_active']


class CEOProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = CEOProfile
        fields = ['id', 'username', 'full_name', 'title', 'department', 'qr_code', 'is_active']


class AppointmentRequestSerializer(serializers.ModelSerializer):
    ceo_name = serializers.CharField(source='ceo.user.get_full_name', read_only=True)
    ceo_title = serializers.CharField(source='ceo.title', read_only=True)

    class Meta:
        model = AppointmentRequest
        fields = [
            'id', 'tracking_uuid', 'full_name', 'employee_id', 'designation', 
            'department', 'email', 'mobile_number', 'preferred_date', 
            'preferred_time', 'purpose', 'description', 'priority', 
            'status', 'remarks', 'token_number', 'appointment_number', 
            'scheduled_date', 'scheduled_time', 'ceo_name', 'ceo_title',
            'created_at'
        ]
        read_only_fields = ['tracking_uuid', 'status', 'remarks', 'token_number', 'appointment_number', 'scheduled_date', 'scheduled_time']
