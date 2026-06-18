from django import forms
from .models import AppointmentRequest

DEPARTMENT_CHOICES = [
    ('', '-- Select Department --'),
    ('Engineering College', 'Engineering College'),
    ('Medical College', 'Medical College'),
    ('Dental College', 'Dental College'),
    ('Hospital', 'Hospital'),
    ('Corporate', 'Corporate'),
    ('Others', 'Others'),
]

class AppointmentRequestForm(forms.ModelForm):
    # Department dropdown with "Others" option
    department = forms.ChoiceField(
        choices=DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_department', 'required': 'true'}),
        required=True
    )
    # Extra field shown only when "Others" is selected — clean empty input, no placeholder
    department_other = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'id': 'id_department_other',
            'style': 'display:none;'
        })
    )

    # Designation is optional
    designation = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g. Student, Professor, Manager, Doctor'
        })
    )

    class Meta:
        model = AppointmentRequest
        fields = [
            'full_name', 'email', 'mobile_number',
            'department', 'designation',
            'preferred_date', 'preferred_time',
            'purpose', 'description', 'priority', 'attachment'
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Your Full Name', 'required': 'true'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email Address', 'required': 'true'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Mobile Number', 'required': 'true'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date', 'required': 'true'}),
            'preferred_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time', 'required': 'true'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Scholarship query, Medical report, Billing issue', 'required': 'true'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your problem in detail...', 'required': 'true'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        department_other = cleaned_data.get('department_other', '').strip()

        if department == 'Others':
            if department_other:
                # Use the typed custom value as the department
                cleaned_data['department'] = department_other
            else:
                cleaned_data['department'] = 'Others'
        return cleaned_data


class CEOActionForm(forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ['status', 'remarks', 'scheduled_date', 'scheduled_time']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select', 'required': 'true'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter comments or reason for rejection...'}),
            'scheduled_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'scheduled_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        scheduled_date = cleaned_data.get('scheduled_date')
        scheduled_time = cleaned_data.get('scheduled_time')

        if status == 'approved':
            if not scheduled_date or not scheduled_time:
                raise forms.ValidationError("Approved appointments must have a scheduled date and time.")
        return cleaned_data
