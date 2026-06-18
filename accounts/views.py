from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserLoginForm, UserRegistrationForm
from tenants.models import Tenant

def login_view(request):
    if request.user.is_authenticated:
        return redirect_role_based(request.user)

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                    return redirect_role_based(user)
                else:
                    messages.error(request, "This account is inactive.")
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect_role_based(request.user)

    tenants = Tenant.objects.filter(is_active=True)
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        tenant_id = request.POST.get('tenant')
        selected_tenant = None
        if tenant_id:
            try:
                selected_tenant = Tenant.objects.get(id=tenant_id, is_active=True)
            except Tenant.DoesNotExist:
                pass
                
        if form.is_valid():
            user = form.save(commit=False)
            if selected_tenant:
                user.tenant = selected_tenant
                user.save()
                
                # If they register as a CEO, auto-create a CEOProfile
                if user.role == 'ceo':
                    from appointments.models import CEOProfile
                    CEOProfile.objects.create(
                        user=user,
                        tenant=selected_tenant,
                        title="CEO",
                        department=user.department or "Administration"
                    )
                
                messages.success(request, "Registration successful! You can now log in.")
                return redirect('login')
            else:
                form.add_error(None, "Please select a valid Organization.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {
        'form': form,
        'tenants': tenants
    })


def redirect_role_based(user):
    """
    Utility function to redirect user to appropriate portal based on role.
    """
    if user.is_superuser or user.role == 'super_admin':
        return redirect('/admin/')
    elif user.role == 'ceo':
        return redirect('ceo_dashboard')
    return redirect('home')
