from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from tenants.models import Tenant
from .models import CEOProfile, AppointmentRequest
from .serializers import TenantSerializer, CEOProfileSerializer, AppointmentRequestSerializer
from .utils import send_appointment_email

class TenantListAPI(generics.ListAPIView):
    """
    API endpoint to list all active organizations/tenants.
    """
    queryset = Tenant.objects.filter(is_active=True)
    serializer_class = TenantSerializer


class CEOListAPI(generics.ListAPIView):
    """
    API endpoint to list all CEOs within a specific tenant.
    """
    serializer_class = CEOProfileSerializer

    def get_queryset(self):
        tenant_slug = self.kwargs.get('tenant_slug')
        tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
        return CEOProfile.objects.filter(tenant=tenant, is_active=True)


class AppointmentAPI(APIView):
    """
    API endpoints for appointment requests:
    - POST: Submit new appointment request
    - GET: Track request status by UUID
    """
    
    def get(self, request, tracking_uuid):
        appointment = get_object_or_404(AppointmentRequest, tracking_uuid=tracking_uuid)
        serializer = AppointmentRequestSerializer(appointment)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, tenant_slug, ceo_id):
        tenant = get_object_or_404(Tenant, slug=tenant_slug, is_active=True)
        ceo = get_object_or_404(CEOProfile, id=ceo_id, tenant=tenant, is_active=True)
        
        # Check SaaS monthly limit for Free Plan
        if tenant.subscription_plan == 'free':
            from django.utils import timezone
            current_month = timezone.now().month
            current_year = timezone.now().year
            monthly_count = AppointmentRequest.objects.filter(
                tenant=tenant,
                created_at__month=current_month,
                created_at__year=current_year
            ).count()
            if monthly_count >= 100:
                return Response(
                    {"error": "Free plan monthly request limit reached (100). Please upgrade."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        serializer = AppointmentRequestSerializer(data=request.data)
        if serializer.is_valid():
            appointment = serializer.save(tenant=tenant, ceo=ceo, status='pending')
            # Trigger Email notification
            send_appointment_email(appointment, 'submitted')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
