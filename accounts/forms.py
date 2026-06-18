from django import forms
from django.contrib.auth import get_user_model
from tenants.models import Tenant

User = get_user_model()

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter Username',
        'id': 'id_username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control form-control-lg',
        'placeholder': 'Enter Password',
        'id': 'id_password'
    }))


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Create password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm password'
    }))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'designation', 'department', 'mobile_number', 'role']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'employee_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee/Faculty ID (Optional)'}),
            'designation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Professor, Analyst'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. CSE, Finance'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        tenant = kwargs.pop('tenant', None)
        super().__init__(*args, **kwargs)
        self.tenant = tenant
        # Restrict role registration for normal signups - CEOs and staff are normal. Super admins are created via CLI.
        self.fields['role'].choices = [
            ('staff', 'Staff / Faculty / Employee'),
            ('ceo', 'CEO / Executive / Director'),
        ]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if self.tenant:
            user.tenant = self.tenant
        if commit:
            user.save()
        return user
