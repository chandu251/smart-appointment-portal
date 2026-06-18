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
