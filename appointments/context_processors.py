from tenants.models import Tenant

def tenant_context(request):
    """
    Resolves the active tenant from the URL path (/t/<tenant_slug>/...)
    and adds it to the template context.
    """
    tenant = None
    
    # Check resolver_match first (most accurate)
    if hasattr(request, 'resolver_match') and request.resolver_match:
        kwargs = request.resolver_match.kwargs
        if 'tenant_slug' in kwargs:
            slug = kwargs['tenant_slug']
            try:
                tenant = Tenant.objects.get(slug=slug, is_active=True)
            except Tenant.DoesNotExist:
                pass

    # Fallback to splitting path if resolver_match isn't available yet
    if not tenant:
        path_parts = request.path.strip('/').split('/')
        if len(path_parts) >= 2 and path_parts[0] == 't':
            slug = path_parts[1]
            try:
                tenant = Tenant.objects.get(slug=slug, is_active=True)
            except Tenant.DoesNotExist:
                pass

    return {
        'active_tenant': tenant
    }
