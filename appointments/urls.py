from django.urls import path
from . import views
from . import api_views

app_name = 'appointments'

urlpatterns = [
    # Tenant Landing & Request Submission
    path('', views.tenant_landing, name='landing'),
    path('ceo/<int:ceo_id>/request/', views.request_submission, name='request_form'),
    
    # Request Tracking & Status
    path('request/status/<uuid:tracking_uuid>/', views.request_status, name='request_status'),
    path('request/status/<uuid:tracking_uuid>/cancel/', views.request_cancel, name='request_cancel'),
    
    # CEO Dashboard & Operations
    path('dashboard/', views.ceo_dashboard, name='ceo_dashboard'),
    path('dashboard/request/<int:request_id>/', views.request_detail, name='request_detail'),
    path('dashboard/request/<int:request_id>/action/', views.ceo_action, name='ceo_action'),
    path('dashboard/analytics/', views.ceo_analytics, name='ceo_analytics'),
    
    # Export Reports
    path('dashboard/export/excel/', views.export_excel, name='export_excel'),
    path('dashboard/export/pdf/', views.export_pdf, name='export_pdf'),
    
    # Staff / Employee History Dashboard
    path('staff/dashboard/', views.staff_dashboard, name='staff_dashboard'),
    
    # REST API Routes
    path('api/tenants/', api_views.TenantListAPI.as_view(), name='api_tenant_list'),
    path('api/ceos/', api_views.CEOListAPI.as_view(), name='api_ceo_list'),
    path('api/appointment/submit/<int:ceo_id>/', api_views.AppointmentAPI.as_view(), name='api_appointment_submit'),
    path('api/appointment/status/<uuid:tracking_uuid>/', api_views.AppointmentAPI.as_view(), name='api_appointment_status'),
]

