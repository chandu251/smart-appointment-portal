from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from appointments import views as app_views
from accounts import views as accounts_views

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # Direct Simple Routes
    path('', app_views.public_request_submit, name='home'),
    path('dashboard/', app_views.simple_ceo_dashboard, name='ceo_dashboard'),
    path('dashboard/action/<int:request_id>/', app_views.simple_ceo_action, name='ceo_action'),
    path('status/<uuid:tracking_uuid>/', app_views.simple_request_status, name='request_status'),
    path('status/<uuid:tracking_uuid>/cancel/', app_views.simple_request_cancel, name='request_cancel'),
    
    # Authentication Portal
    path('accounts/login/', accounts_views.login_view, name='login'),
    path('accounts/logout/', accounts_views.logout_view, name='logout'),
    path('accounts/register/', accounts_views.register_view, name='register'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
