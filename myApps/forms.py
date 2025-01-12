from django import forms
from .models import Report, Employee, Stall, Profile, Suplier, FoodItem, SupplierItem, Product
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.core.exceptions import ValidationError
import re
import os

class StallForm(forms.ModelForm):
    class Meta:
        model = Stall
        fields = ['name', 'logo', 'contact_number', 'is_active']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Stall name cannot be blank.")
        if len(name) > 255:
            raise ValidationError("Stall name is too long. Maximum 255 characters allowed.")
        if name.strip() != name:
            raise ValidationError("Stall name cannot start or end with spaces.")
        return name

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if logo:
            # Get the file extension by splitting the name and checking the extension
            file_extension = os.path.splitext(logo.name)[1].lower()
            valid_image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            if file_extension not in valid_image_extensions:
                raise ValidationError("Invalid image file. Allowed formats: .jpg, .jpeg, .png, .gif.")

            # Check if the image size is reasonable (e.g., less than 5MB)
            if logo.size > 5 * 1024 * 1024:  # 5MB size limit
                raise ValidationError("Image size must be less than 5MB.")
        return logo

    def clean_contact_number(self):
        contact_number = self.cleaned_data.get('contact_number')
        if contact_number:
            if not re.match(r'^\+?[0-9]*$', contact_number):
                raise ValidationError("Contact number should contain only digits and an optional '+' at the beginning.")
            if len(contact_number) < 10 or len(contact_number) > 15:
                raise ValidationError("Contact number must be between 10 and 15 digits.")
        return contact_number
       
class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['title', 'description', 'file', 'stall_name']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        
class SupplierItemForm(forms.ModelForm):
    class Meta:
        model = SupplierItem
        fields = [
            'supplier', 'food_item', 'lead_time', 
            'minimum_order_quantity', 'price_per_unit'
        ]
        widgets = {
            'lead_time': forms.NumberInput(attrs={'min': '1'}),  # Set minimum lead time as 1
            'minimum_order_quantity': forms.NumberInput(attrs={'min': '1'}),  # Set minimum quantity to 1
            'price_per_unit': forms.NumberInput(attrs={'step': '0.01'}),  # Allows decimal input for price
        }
        
class EmployeeForm(forms.ModelForm):
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    stallname = forms.ChoiceField(
        required=True, label="Stall Name"
    )

    class Meta:
        model = Employee
        fields = ['stallname', 'firstname', 'middle_initial', 'lastname', 'age', 'birthdate', 
                  'address', 'contact_number', 'email_address', 'religion', 'position', 
                  'username', 'password']
        widgets = {'password': forms.PasswordInput()}

    def __init__(self, *args, **kwargs):
        # Pass the logged-in admin as a parameter
        self.admin = kwargs.pop('admin')
        super().__init__(*args, **kwargs)

        # Filter stalls based on the admin's assigned stall
        self.fields['stallname'].choices = [(self.admin.stall_name.id, self.admin.stall_name.name)]  # Use id for the choi

    def save(self, commit=True):
        employee = super().save(commit=False)
        employee.password = make_password(self.cleaned_data['password'])

        # Link employee to the admin's stall
        employee.stall_name = self.admin.stall_name  # Ensure this is a Stall instance
        if commit:
            employee.save()
        return employee

class ProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)
    phone = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    birthdate = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    gender_choices = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = forms.ChoiceField(choices=gender_choices, required=True)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = Profile
        fields = ['phone', 'address', 'birthdate', 'gender', 'profile_photo', 'first_name', 'last_name', 'password']

    def clean_birthdate(self):
        birthdate = self.cleaned_data['birthdate']
        today = timezone.now().date()
        age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
        if age < 1:
            raise ValidationError("You must be at least one year old to register.")
        return birthdate

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 10:
            raise ValidationError("Please enter a valid phone number.")
        return phone
    
class SupplierForm(forms.ModelForm):
    class Meta:
        model = Suplier
        fields = ['supplier_name', 'contact_person', 'contact_info', 'address', 'payment_terms', 'tax_information', 'license_number', 'contract_start_date', 'contract_end_date']

    
class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = [
            'item_name', 'category', 'unit_of_measurement', 'description',
            'stock_quantity', 'reorder_level', 'batch_number', 'expiry_date',
            'arrival_date', 'cost_price', 'selling_price', 'stall_location'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'cost_price': forms.NumberInput(attrs={'step': '0.01'}),
            'selling_price': forms.NumberInput(attrs={'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        # Remove 'admin' from kwargs if it exists
        admin = kwargs.pop('admin', None)
        super(FoodItemForm, self).__init__(*args, **kwargs)

        # Dynamically set the queryset for stall_location field based on the admin's stall
        if admin:
            self.fields['stall_location'].queryset = Stall.objects.filter(name=admin.stall_name.name)
        else:
            self.fields['stall_location'].queryset = Stall.objects.all()

            
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'placeholder': 'Enter your name', 'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email', 'class': 'form-control'}))
    subject = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        'placeholder': 'Enter subject', 'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder': 'Write your message here', 'class': 'form-control'}))

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['item_name', 'category', 'price', 'quantity', 'stall_name']
        widgets = {
            'stall_id': forms.HiddenInput(),
        }