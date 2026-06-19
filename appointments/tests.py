from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from .models import CEOProfile, AppointmentRequest
from .utils import analyze_appointment_request

User = get_user_model()

class SaaSAppointmentTestCase(TestCase):
    def setUp(self):
        # 1. Create two Tenants (Organizations)
        self.tenant_anits = Tenant.objects.create(
            name="ANITS Engineering",
            slug="anits",
            email="admin@anits.edu",
            contact_number="1234567890",
            subscription_plan="free",
            is_active=True
        )
        self.tenant_hospital = Tenant.objects.create(
            name="City General Hospital",
            slug="hospital",
            email="admin@hospital.org",
            contact_number="0987654321",
            subscription_plan="professional",
            is_active=True
        )

        # 2. Create CEO Users
        self.ceo_user_anits = User.objects.create_user(
            username="ceo_anits",
            email="principal@anits.edu",
            password="password123",
            role="ceo",
            tenant=self.tenant_anits
        )
        self.ceo_profile_anits = CEOProfile.objects.create(
            user=self.ceo_user_anits,
            tenant=self.tenant_anits,
            title="Principal",
            department="College Admin"
        )

        self.ceo_user_hospital = User.objects.create_user(
            username="ceo_hospital",
            email="director@hospital.org",
            password="password123",
            role="ceo",
            tenant=self.tenant_hospital
        )
        self.ceo_profile_hospital = CEOProfile.objects.create(
            user=self.ceo_user_hospital,
            tenant=self.tenant_hospital,
            title="Medical Director",
            department="Hospital Board"
        )

    def test_tenant_and_user_creation(self):
        """Verify models are created and linked correctly."""
        self.assertEqual(self.tenant_anits.slug, "anits")
        self.assertEqual(self.ceo_user_anits.role, "ceo")
        self.assertEqual(self.ceo_profile_anits.user, self.ceo_user_anits)
        self.assertEqual(self.ceo_profile_anits.tenant, self.tenant_anits)

    def test_appointment_request_token_sequence(self):
        """Test token generation sequence (CEO-2026-001, CEO-2026-002)."""
        # Create request for ANITS CEO
        req1 = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="John Doe",
            designation="Assistant Professor",
            department="CSE",
            email="johndoe@anits.edu",
            mobile_number="5551112222",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Syllabus Review",
            description="Discuss the new artificial intelligence curriculum."
        )

        # Approve and check token
        req1.status = 'approved'
        req1.scheduled_date = timezone.now().date()
        req1.scheduled_time = timezone.now().time()
        req1.generate_token()
        req1.save()

        # Should match CEO-YYYY-001
        current_year = timezone.now().year
        self.assertEqual(req1.token_number, f"CEO-{current_year}-001")

        # Create second request
        req2 = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="Jane Smith",
            designation="Lecturer",
            department="IT",
            email="janesmith@anits.edu",
            mobile_number="5551113333",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Leave Extension",
            description="Requesting medical leave extension for 5 days."
        )
        req2.status = 'approved'
        req2.scheduled_date = timezone.now().date()
        req2.scheduled_time = timezone.now().time()
        req2.generate_token()
        req2.save()

        # Should increment to CEO-YYYY-002
        self.assertEqual(req2.token_number, f"CEO-{current_year}-002")

    def test_data_isolation(self):
        """Ensure requests for one tenant aren't queryable or visible under another."""
        # Add request under ANITS
        req_anits = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="John Doe",
            designation="Staff",
            department="CSE",
            email="johndoe@anits.edu",
            mobile_number="5551112222",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Review",
            description="Discuss syllabus"
        )
        
        # Verify database filter queries restrict records correctly
        anits_reqs = AppointmentRequest.objects.filter(tenant=self.tenant_anits)
        hospital_reqs = AppointmentRequest.objects.filter(tenant=self.tenant_hospital)
        
        self.assertIn(req_anits, anits_reqs)
        self.assertNotIn(req_anits, hospital_reqs)

    def test_ai_helper_heuristics(self):
        """Test rule-based AI categorization and priority suggestions."""
        req = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="Jane Smith",
            designation="Lecturer",
            department="IT",
            email="janesmith@anits.edu",
            mobile_number="5551113333",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Leave Approval",
            description="URGENT: I need immediate permission for sick leave extension due to a medical emergency."
        )

        ai_insights = analyze_appointment_request(req)
        self.assertEqual(ai_insights['suggested_priority'], "urgent")
        self.assertEqual(ai_insights['suggested_category'], "HR / Leave Request")
        self.assertFalse(ai_insights['is_duplicate'])

    def test_ceo_delete_approved_request(self):
        """CEO can delete approved appointment requests."""
        from django.urls import reverse
        req = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="Delete Approved",
            designation="Lecturer",
            department="IT",
            email="approved@anits.edu",
            mobile_number="5551113333",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Meeting",
            description="Discuss meeting details.",
            status="approved"
        )
        
        self.client.login(username="ceo_anits", password="password123")
        url = reverse('ceo_delete_request', kwargs={'request_id': req.id})
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('ceo_dashboard'))
        self.assertFalse(AppointmentRequest.objects.filter(id=req.id).exists())

    def test_ceo_delete_rejected_request(self):
        """CEO can delete rejected appointment requests."""
        from django.urls import reverse
        req = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="Delete Rejected",
            designation="Lecturer",
            department="IT",
            email="rejected@anits.edu",
            mobile_number="5551113333",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Meeting",
            description="Discuss meeting details.",
            status="rejected"
        )
        
        self.client.login(username="ceo_anits", password="password123")
        url = reverse('ceo_delete_request', kwargs={'request_id': req.id})
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('ceo_dashboard'))
        self.assertFalse(AppointmentRequest.objects.filter(id=req.id).exists())

    def test_ceo_cannot_delete_pending_request(self):
        """CEO cannot delete pending appointment requests."""
        from django.urls import reverse
        req = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="Delete Pending",
            designation="Lecturer",
            department="IT",
            email="pending@anits.edu",
            mobile_number="5551113333",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Meeting",
            description="Discuss meeting details.",
            status="pending"
        )
        
        self.client.login(username="ceo_anits", password="password123")
        url = reverse('ceo_delete_request', kwargs={'request_id': req.id})
        response = self.client.post(url)
        
        self.assertRedirects(response, reverse('ceo_dashboard'))
        self.assertTrue(AppointmentRequest.objects.filter(id=req.id).exists())

    def test_unauthorized_user_cannot_delete_request(self):
        """Non-CEO users cannot delete appointment requests."""
        from django.urls import reverse
        req = AppointmentRequest.objects.create(
            tenant=self.tenant_anits,
            ceo=self.ceo_profile_anits,
            full_name="Delete Unauthorized",
            designation="Lecturer",
            department="IT",
            email="unauth@anits.edu",
            mobile_number="5551113333",
            preferred_date=timezone.now().date(),
            preferred_time=timezone.now().time(),
            purpose="Meeting",
            description="Discuss meeting details.",
            status="approved"
        )
        
        # Test 1: Anonymous user redirect
        url = reverse('ceo_delete_request', kwargs={'request_id': req.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Test 2: Regular user raises 403
        regular_user = User.objects.create_user(
            username="regular_staff",
            email="staff@anits.edu",
            password="password123",
            role="staff",
            tenant=self.tenant_anits
        )
        self.client.login(username="regular_staff", password="password123")
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertTrue(AppointmentRequest.objects.filter(id=req.id).exists())

