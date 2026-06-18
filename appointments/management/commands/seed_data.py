from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, timedelta
from tenants.models import Tenant
from appointments.models import CEOProfile, AppointmentRequest

User = get_user_model()

class Command(BaseCommand):
    help = "Seeds the database with sample Tenants, CEOs, Staff, and Appointment Requests"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")
        
        # 1. Clear existing data
        AppointmentRequest.objects.all().delete()
        CEOProfile.objects.all().delete()
        User.objects.all().delete()
        Tenant.objects.all().delete()
        
        self.stdout.write("Existing data cleared.")

        # 2. Create Tenants
        tenant_anits = Tenant.objects.create(
            name="ANITS Engineering College",
            slug="anits",
            email="info@anits.edu",
            contact_number="+91-8933-225577",
            address="Sangivalasa, Bheemunipatnam, Visakhapatnam, Andhra Pradesh 531162",
            subscription_plan="free",
            is_active=True
        )
        
        tenant_hospital = Tenant.objects.create(
            name="City General Hospital",
            slug="hospital",
            email="info@cityhospital.org",
            contact_number="+1-555-987-6543",
            address="450 Health Sciences Parkway, Boston, MA 02115",
            subscription_plan="professional",
            is_active=True
        )

        tenant_corp = Tenant.objects.create(
            name="Apex Corporate Headquarters",
            slug="apex",
            email="admin@apexcorp.com",
            contact_number="+1-800-555-0199",
            address="100 Innovation Way, Suite 500, San Francisco, CA 94107",
            subscription_plan="enterprise",
            is_active=True
        )
        
        self.stdout.write("Tenants created.")

        # 3. Create Super Admin
        super_admin = User.objects.create_superuser(
            username="admin",
            email="admin@system.com",
            password="password123",
            first_name="System",
            last_name="SuperAdmin",
            role="super_admin"
        )
        self.stdout.write("Superadmin created: admin / password123")

        # 4. Create CEOs
        # CEO 1: ANITS Principal
        ceo_anits_user = User.objects.create_user(
            username="principal_anits",
            email="principal@anits.edu",
            password="password123",
            first_name="Prof. R. V.",
            last_name="Krishna",
            role="ceo",
            tenant=tenant_anits,
            designation="Principal",
            department="College Board",
            mobile_number="9876543210"
        )
        ceo_anits_profile = CEOProfile.objects.create(
            user=ceo_anits_user,
            tenant=tenant_anits,
            title="Principal / Director",
            department="Academic Administration"
        )
        
        # CEO 2: Hospital Director
        ceo_hosp_user = User.objects.create_user(
            username="director_hosp",
            email="director@cityhospital.org",
            password="password123",
            first_name="Dr. Elizabeth",
            last_name="Vance",
            role="ceo",
            tenant=tenant_hospital,
            designation="Medical Director",
            department="Executive Board",
            mobile_number="555-321-7654"
        )
        ceo_hosp_profile = CEOProfile.objects.create(
            user=ceo_hosp_user,
            tenant=tenant_hospital,
            title="Medical Director & CEO",
            department="Hospital Operations"
        )

        self.stdout.write("CEO Users & Profiles created:")
        self.stdout.write(" - ANITS CEO: principal_anits / password123")
        self.stdout.write(" - Hospital CEO: director_hosp / password123")

        # 5. Create Staff / Faculty Users
        staff_anits = User.objects.create_user(
            username="staff_anits",
            email="prof.sharma@anits.edu",
            password="password123",
            first_name="Dr. Anil",
            last_name="Sharma",
            role="staff",
            tenant=tenant_anits,
            employee_id="ANT-CSE-102",
            designation="Associate Professor",
            department="Computer Science & Engineering",
            mobile_number="9876543001"
        )
        
        staff_hosp = User.objects.create_user(
            username="staff_hosp",
            email="nurse.johnson@cityhospital.org",
            password="password123",
            first_name="Sarah",
            last_name="Johnson",
            role="staff",
            tenant=tenant_hospital,
            employee_id="HSP-RN-405",
            designation="Head Nurse",
            department="Emergency Care",
            mobile_number="555-888-0002"
        )
        
        self.stdout.write("Staff Users created:")
        self.stdout.write(" - ANITS Staff: staff_anits / password123")
        self.stdout.write(" - Hospital Staff: staff_hosp / password123")

        # 6. Create Appointment Requests
        today = date.today()

        # Requests for ANITS
        # Pending Request
        AppointmentRequest.objects.create(
            tenant=tenant_anits,
            ceo=ceo_anits_profile,
            full_name="Dr. Anil Sharma",
            employee_id="ANT-CSE-102",
            designation="Associate Professor",
            department="CSE",
            email="prof.sharma@anits.edu",
            mobile_number="9876543001",
            preferred_date=today + timedelta(days=2),
            preferred_time=timezone.datetime.strptime("10:30", "%H:%M").time(),
            purpose="Syllabus Revision approval",
            description="URGENT request to review and approve the updated syllabus for the upcoming AI curriculum. The deadline is tomorrow.",
            priority="urgent",
            status="pending"
        )
        
        # Approved Request
        req_approved_anits = AppointmentRequest.objects.create(
            tenant=tenant_anits,
            ceo=ceo_anits_profile,
            full_name="Prof. Sunita Rao",
            employee_id="ANT-ECE-045",
            designation="Professor & HOD",
            department="Electronics & Communication",
            email="hod.ece@anits.edu",
            mobile_number="9876543022",
            preferred_date=today + timedelta(days=1),
            preferred_time=timezone.datetime.strptime("14:00", "%H:%M").time(),
            purpose="Lab Funding Review",
            description="Discussion regarding new signal processing laboratory equipment procurement budget.",
            priority="high",
            status="approved",
            scheduled_date=today,
            scheduled_time=timezone.datetime.strptime("14:30", "%H:%M").time(),
            remarks="Approved. Please bring the quotation spreadsheets."
        )
        req_approved_anits.generate_token()
        req_approved_anits.save()

        # Rejected Request
        AppointmentRequest.objects.create(
            tenant=tenant_anits,
            ceo=ceo_anits_profile,
            full_name="Ramesh Kumar",
            employee_id="ANT-MA-900",
            designation="Student Coordinator",
            department="Mathematics",
            email="ramesh.ma@anits.edu",
            mobile_number="9876543099",
            preferred_date=today + timedelta(days=5),
            preferred_time=timezone.datetime.strptime("16:00", "%H:%M").time(),
            purpose="Sponsorship request for Tech Fest",
            description="A meeting is requested to solicit college funds/sponsorships for the annual national student tech fest.",
            priority="medium",
            status="rejected",
            remarks="Please contact the Dean of Student Affairs first. Standard sponsorships are handled via the dean office."
        )

        # Requests for Hospital
        # Pending Request 1
        AppointmentRequest.objects.create(
            tenant=tenant_hospital,
            ceo=ceo_hosp_profile,
            full_name="Dr. Gregory House",
            employee_id="HSP-MD-007",
            designation="Chief of Diagnostic Medicine",
            department="Diagnostics",
            email="house@cityhospital.org",
            mobile_number="555-999-1007",
            preferred_date=today + timedelta(days=3),
            preferred_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            purpose="Clinic Resource Allocation",
            description="We require more MRI machine slots allocated to clinical research diagnostic tests immediately.",
            priority="high",
            status="pending"
        )
        
        # Pending Request 2 (Duplicate request example)
        AppointmentRequest.objects.create(
            tenant=tenant_hospital,
            ceo=ceo_hosp_profile,
            full_name="Dr. Gregory House",
            employee_id="HSP-MD-007",
            designation="Chief of Diagnostic Medicine",
            department="Diagnostics",
            email="house@cityhospital.org",
            mobile_number="555-999-1007",
            preferred_date=today + timedelta(days=4),
            preferred_time=timezone.datetime.strptime("09:00", "%H:%M").time(),
            purpose="Clinic Resource Allocation",
            description="URGENT: duplicate request to review diagnostic resource allocation slots.",
            priority="urgent",
            status="pending"
        )

        # Approved Request 1
        req_app1 = AppointmentRequest.objects.create(
            tenant=tenant_hospital,
            ceo=ceo_hosp_profile,
            full_name="Sarah Johnson",
            employee_id="HSP-RN-405",
            designation="Head Nurse",
            department="Emergency Care",
            email="nurse.johnson@cityhospital.org",
            mobile_number="555-888-0002",
            preferred_date=today,
            preferred_time=timezone.datetime.strptime("11:00", "%H:%M").time(),
            purpose="Emergency ward staffing shortages",
            description="Discussion on urgent hiring and double shift structures for ER nurses.",
            priority="urgent",
            status="approved",
            scheduled_date=today,
            scheduled_time=timezone.datetime.strptime("11:00", "%H:%M").time(),
            remarks="Agreed. ER shifts scheduling will be reviewed in person."
        )
        req_app1.generate_token()
        req_app1.save()

        self.stdout.write("Appointment requests seeded.")
        self.stdout.write(self.style.SUCCESS("Database seeding completed successfully!"))
