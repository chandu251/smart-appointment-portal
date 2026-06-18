import uuid
from django.db import models
from django.conf import settings
from tenants.models import Tenant

class CEOProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ceo_profile')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='ceos')
    title = models.CharField(max_length=100, default="CEO", help_text="e.g. Principal, Director, Dean, Managing Director")
    department = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Administration, Computer Science, Cardiology")
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.title} ({self.tenant.name})"

    def generate_qr(self, request_host="localhost:8000"):
        """
        Generates and saves a QR code linking to this CEO's request page.
        """
        import qrcode
        from io import BytesIO
        from django.core.files import File
        
        # Construct url
        url = f"http://{request_host}/t/{self.tenant.slug}/ceo/{self.id}/request/"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        blob = BytesIO()
        img.save(blob, 'PNG')
        
        # Save to Model ImageField
        filename = f"qr_ceo_{self.id}.png"
        self.qr_code.save(filename, File(blob), save=False)


class AppointmentRequest(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    ]

    tracking_uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='appointments')
    ceo = models.ForeignKey(CEOProfile, on_delete=models.CASCADE, related_name='appointments')
    
    # Requester Information
    full_name = models.CharField(max_length=150)
    employee_id = models.CharField(max_length=50, blank=True, null=True, help_text="Employee or Faculty ID (optional)")
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)

    # Appointment Information
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    purpose = models.CharField(max_length=200)
    description = models.TextField(help_text="Provide details of the meeting topic.")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    attachment = models.FileField(upload_to='appointment_attachments/', blank=True, null=True, help_text="Upload PDF, DOC, DOCX or Images")

    # CEO Action & Queue Management
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    remarks = models.TextField(blank=True, null=True, help_text="Remarks/notes added by the CEO.")
    token_number = models.CharField(max_length=50, blank=True, null=True, help_text="e.g. CEO-2026-001")
    appointment_number = models.CharField(max_length=50, blank=True, null=True, unique=True)
    scheduled_date = models.DateField(blank=True, null=True)
    scheduled_time = models.TimeField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def generate_token(self):
        """
        Generates a token number like CEO-YYYY-NNN and an appointment number.
        """
        if not self.scheduled_date:
            return
        
        year = self.scheduled_date.year
        # Count existing approved appointments for this CEO in the same year
        approved_count = AppointmentRequest.objects.filter(
            ceo=self.ceo,
            status='approved',
            scheduled_date__year=year
        ).count()
        
        # Sequential number incremented
        seq = approved_count + 1
        self.token_number = f"CEO-{year}-{seq:03d}"
        
        # Secure unique appointment number
        random_hex = uuid.uuid4().hex[:6].upper()
        self.appointment_number = f"APT-{self.tenant.slug.upper()}-{random_hex}"

    def __str__(self):
        return f"{self.full_name} - {self.purpose} ({self.get_status_display()})"
