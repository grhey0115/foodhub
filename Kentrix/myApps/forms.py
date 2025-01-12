from django import forms
from .models import Report, Employee
from django.contrib.auth.hashers import make_password


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
class EmployeeForm(forms.ModelForm):
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Employee
        fields = ['firstname', 'middle_initial', 'lastname', 'age', 'birthdate', 'address', 'contact_number', 'email_address', 'religion', 'position', 'username', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        employee = super(EmployeeForm, self).save(commit=False)
        # Hash the password
        employee.password = make_password(self.cleaned_data['password'])
        if commit:
            employee.save()
        return employee

        