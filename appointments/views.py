from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.core.exceptions import PermissionDenied
from django.contrib import messages
from django.utils import timezone
from tenants.models import Tenant
from accounts.models import User
from .models import CEOProfile, AppointmentRequest
from .forms import AppointmentRequestForm
from .utils import send_appointment_email

def get_default_ceo():
    """
    Helper to get or create a default tenant and CEO so the app works out-of-the-box.
    """
    tenant, _ = Tenant.objects.get_or_create(
        slug="default",
        defaults={
            "name": "Default Organization",
            "email": "admin@organization.com",
            "contact_number": "1234567890",
            "subscription_plan": "free"
        }
    )
    
    # Get or create a default CEO user
    user, user_created = User.objects.get_or_create(
        username="ceo",
        defaults={
            "email": "ceo@organization.com",
            "first_name": "Executive",
            "last_name": "CEO",
            "role": "ceo",
            "tenant": tenant
        }
    )
    if user_created:
        user.set_password("password123")
        user.save()
        
    ceo_profile, _ = CEOProfile.objects.get_or_create(
        user=user,
        defaults={
            "tenant": tenant,
            "title": "Chief Executive Officer",
            "department": "Executive Office"
        }
    )
    return ceo_profile


@ensure_csrf_cookie
def public_request_submit(request):
    """
    Public landing page containing a simple form to submit an appointment request.
    """
    ceo = get_default_ceo()
    
    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST, request.FILES)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.tenant = ceo.tenant
            appointment.ceo = ceo
            # department is already resolved (Others -> custom text) by form.clean()
            appointment.department = form.cleaned_data['department']
            appointment.designation = form.cleaned_data.get('designation', 'Visitor')
            appointment.status = 'pending'
            appointment.save()
            
            # Send email notification
            send_appointment_email(appointment, 'submitted')
            
            messages.success(request, "Your request has been submitted to the CEO successfully!")
            return redirect('request_status', tracking_uuid=appointment.tracking_uuid)
    else:
        form = AppointmentRequestForm()
        
    return render(request, 'appointments/simple_request_form.html', {
        'form': form,
        'ceo': ceo
    })


def simple_request_status(request, tracking_uuid):
    """
    Tracks the status of a submitted request.
    """
    appointment = get_object_or_404(AppointmentRequest, tracking_uuid=tracking_uuid)
    return render(request, 'appointments/simple_request_status.html', {
        'appointment': appointment
    })


def simple_request_cancel(request, tracking_uuid):
    """
    Allows a visitor to cancel their request.
    """
    appointment = get_object_or_404(AppointmentRequest, tracking_uuid=tracking_uuid)
    if appointment.status == 'pending':
        appointment.status = 'cancelled'
        appointment.save()
        send_appointment_email(appointment, 'cancelled')
        messages.warning(request, "Your appointment request has been cancelled.")
    return redirect('request_status', tracking_uuid=tracking_uuid)


@login_required
@ensure_csrf_cookie
def simple_ceo_dashboard(request):
    """
    Sleek, simple CEO Dashboard displaying all incoming visitor requests and their descriptions.
    """
    if request.user.role != 'ceo' and not request.user.is_superuser:
        raise PermissionDenied("Access Denied: CEO only dashboard.")
        
    ceo = get_default_ceo()
    appointments = AppointmentRequest.objects.filter(ceo=ceo).order_by('-created_at')
    
    # Counts
    pending_count = appointments.filter(status='pending').count()
    approved_count = appointments.filter(status='approved').count()
    rejected_count = appointments.filter(status='rejected').count()
    
    return render(request, 'appointments/simple_dashboard.html', {
        'appointments': appointments,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
        'ceo': ceo
    })


@login_required
@require_POST
def simple_ceo_action(request, request_id):
    """
    Action handler for the CEO to Accept (Approve) or Reject a request.
    """
    if request.user.role != 'ceo' and not request.user.is_superuser:
        raise PermissionDenied()
        
    appointment = get_object_or_404(AppointmentRequest, id=request_id)
    action = request.POST.get('action')
    remarks = request.POST.get('remarks', '')
    
    if action == 'approve':
        appointment.status = 'approved'
        appointment.remarks = remarks
        appointment.scheduled_date = timezone.now().date()
        appointment.scheduled_time = timezone.now().time()
        appointment.generate_token()
        appointment.save()
        send_appointment_email(appointment, 'approved')
        messages.success(request, f"Appointment accepted! Token #{appointment.token_number} generated.")
    elif action == 'reject':
        appointment.status = 'rejected'
        appointment.remarks = remarks
        appointment.save()
        send_appointment_email(appointment, 'rejected')
        messages.warning(request, "Appointment request has been declined.")
        
    return redirect('ceo_dashboard')
