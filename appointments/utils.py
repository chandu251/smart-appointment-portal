import os
import re
from django.core.mail import send_mail
from django.urls import reverse
from django.utils import timezone
from django.conf import settings

def send_appointment_email(appointment, event_type):
    """
    Sends email notifications based on appointment status changes.
    """
    subject_map = {
        'submitted': f"Appointment Request Submitted - {appointment.purpose}",
        'approved': f"Appointment Request APPROVED - Token: {appointment.token_number}",
        'rejected': f"Appointment Request Update: Rejected",
        'rescheduled': f"Appointment Request Rescheduled - {appointment.token_number}",
        'cancelled': f"Appointment Request Cancelled - {appointment.purpose}",
    }
    
    subject = subject_map.get(event_type, "Appointment Status Update")
    recipient = appointment.email
    
    # Simple tenant host resolving helper
    # In a real app we'd get the actual domain name. We'll use a placeholder or config.
    domain = "localhost:8000"
    tracking_url = f"http://{domain}/t/{appointment.tenant.slug}/request/status/{appointment.tracking_uuid}/"
    
    body = f"Hello {appointment.full_name},\n\n"
    
    if event_type == 'submitted':
        body += (
            f"Your request for an appointment with {appointment.ceo.user.get_full_name()} ({appointment.ceo.title}) "
            f"has been submitted successfully.\n\n"
            f"Preferred Date: {appointment.preferred_date}\n"
            f"Preferred Time: {appointment.preferred_time}\n"
            f"Tracking Code: {appointment.tracking_uuid}\n\n"
            f"You can track the status of your request at any time using this link:\n{tracking_url}\n"
        )
    elif event_type == 'approved':
        body += (
            f"Your appointment request has been APPROVED by {appointment.ceo.user.get_full_name()}.\n\n"
            f"Meeting Details:\n"
            f"---------------------------------\n"
            f"Token Number: {appointment.token_number}\n"
            f"Appointment Number: {appointment.appointment_number}\n"
            f"Scheduled Date: {appointment.scheduled_date}\n"
            f"Scheduled Time: {appointment.scheduled_time}\n"
            f"---------------------------------\n\n"
            f"Remarks from CEO: {appointment.remarks or 'None'}\n\n"
            f"Please show your token when arriving at the office.\n"
            f"You can view your digital slip here:\n{tracking_url}\n"
        )
    elif event_type == 'rejected':
        body += (
            f"We regret to inform you that your appointment request with {appointment.ceo.user.get_full_name()} "
            f"has been declined.\n\n"
            f"CEO Remarks / Reason: {appointment.remarks or 'No reason provided.'}\n\n"
            f"You can view details here:\n{tracking_url}\n"
        )
    elif event_type == 'rescheduled':
        body += (
            f"Your appointment with {appointment.ceo.user.get_full_name()} has been rescheduled.\n\n"
            f"New Meeting Details:\n"
            f"---------------------------------\n"
            f"Token Number: {appointment.token_number}\n"
            f"Scheduled Date: {appointment.scheduled_date}\n"
            f"Scheduled Time: {appointment.scheduled_time}\n"
            f"---------------------------------\n\n"
            f"Remarks from CEO: {appointment.remarks or 'None'}\n\n"
            f"Track details here:\n{tracking_url}\n"
        )
    elif event_type == 'cancelled':
        body += (
            f"Your appointment request with purpose '{appointment.purpose}' has been marked as CANCELLED.\n\n"
            f"No further action is required.\n"
        )
        
    body += f"\nBest Regards,\n{appointment.tenant.name} Appointment Management System\n"
    
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=True
        )
    except Exception as e:
        # Log email sending failure
        print(f"Failed to send email to {recipient}: {str(e)}")


def analyze_appointment_request(appointment_request):
    """
    AI Enhancement: Analyzes an appointment request using keyword-based AI logic (or an external LLM call if configured).
    Suggests category, priority level, detects duplicate requests, and generates a short summary.
    """
    purpose = appointment_request.purpose.lower()
    description = appointment_request.description.lower()
    
    # 1. Category Suggestion
    category = "General Inquiry"
    if any(k in purpose or k in description for k in ['leave', 'holiday', 'sick', 'vacation', 'resignation']):
        category = "HR / Leave Request"
    elif any(k in purpose or k in description for k in ['admission', 'fees', 'exam', 'marksheet', 'certificate', 'degree']):
        category = "Academic / Student Affairs"
    elif any(k in purpose or k in description for k in ['invoice', 'payment', 'budget', 'salary', 'reimbursement', 'funds']):
        category = "Finance & Accounts"
    elif any(k in purpose or k in description for k in ['project', 'partnership', 'mou', 'collaboration', 'proposal']):
        category = "Business / Partnership Proposal"
    elif any(k in purpose or k in description for k in ['complaint', 'grievance', 'issue', 'bug', 'broken']):
        category = "Grievance / Support"
        
    # 2. Priority suggestion
    suggested_priority = "medium"
    if any(k in purpose or k in description for k in ['urgent', 'emergency', 'immediate', 'asap', 'critical', 'accident']):
        suggested_priority = "urgent"
    elif any(k in purpose or k in description for k in ['important', 'deadline', 'review', 'audit', 'sign-off']):
        suggested_priority = "high"
    elif any(k in purpose or k in description for k in ['casual', 'chat', 'feedback', 'routine', 'whenever']):
        suggested_priority = "low"

    # 3. Duplicate request detection
    # Look for requests from the same email or employee ID that are pending for the same CEO
    duplicates_query = appointment_request.__class__.objects.filter(
        ceo=appointment_request.ceo,
        email=appointment_request.email,
        status='pending'
    ).exclude(id=appointment_request.id)
    
    if appointment_request.employee_id:
        duplicates_query = duplicates_query | appointment_request.__class__.objects.filter(
            ceo=appointment_request.ceo,
            employee_id=appointment_request.employee_id,
            status='pending'
        ).exclude(id=appointment_request.id)

    is_duplicate = duplicates_query.exists()
    duplicate_count = duplicates_query.count()

    # 4. Generate summary
    summary = (
        f"{appointment_request.full_name} ({appointment_request.designation} from {appointment_request.department}) "
        f"is requesting a meeting regarding '{appointment_request.purpose}'. "
        f"The user suggested preferred date {appointment_request.preferred_date} at {appointment_request.preferred_time}. "
        f"Description summary: {appointment_request.description[:120]}..."
    )

    return {
        'suggested_category': category,
        'suggested_priority': suggested_priority,
        'is_duplicate': is_duplicate,
        'duplicate_count': duplicate_count,
        'summary': summary
    }
