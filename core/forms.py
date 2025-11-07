from django import forms
from django.contrib.auth import get_user_model
from .models import Employee

User = get_user_model()

# ----------------------------------
# User Form (for HR/Admin to create employee user)
# ----------------------------------
class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data['password']
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

# ----------------------------------
# Employee Form
# ----------------------------------
class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = ['department', 'designation', 'contact_number', 'basic_salary', 'photo']

    # Optional: automatically generate employee_id (already in model save)



from django import forms
from .models import Lead

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['status', 'priority', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
