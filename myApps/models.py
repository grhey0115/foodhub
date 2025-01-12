from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.timezone import now
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password, check_password
import secrets


class Transaction(models.Model):
    ubtransact_id = models.CharField(max_length=20, primary_key=True)
    order_date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, default='No description provided') 
    size = models.CharField(max_length=10)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    stall_name = models.ForeignKey('Stall', on_delete=models.CASCADE, null=True, blank=True) 

    def __str__(self):
        return f'Transaction {self.ubtransact_id} - {self.description}'

class Stall(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    contact_number = models.CharField(max_length=15, blank=True)
    logo = models.ImageField(upload_to='stall_logos/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    raw_password = models.CharField(max_length=128, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    address = models.TextField()
    birthdate = models.DateField(null=False)
    gender = models.CharField(max_length=10, choices=[('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')])
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.raw_password:
            self.user.set_password(self.raw_password)
            self.raw_password = None
            self.user.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.username} Profile'


    
class Report(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='reports/')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    stall_name = models.ForeignKey('Stall', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return self.title
    
class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Beverage', 'Beverage'),
        ('Food', 'Food'),
        ('Dessert', 'Dessert'),
    ]

    stall_name = models.ForeignKey(
        'Stall', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='products',
        db_column='stall_name_id'
    )
    item_name = models.ForeignKey(
        'FoodItem', 
        on_delete=models.CASCADE, 
        related_name='products',
        db_column='item_name_id',
        null=False 
    )
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Food')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    size_prices = models.JSONField(default=dict)  # Store prices for small, medium, large
    add_ons = models.JSONField(default=list)      # Store add-ons as a list of dicts
    quantity = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.item_name} ({self.stall_name.name if self.stall_name else 'No Stall'})"

    def reduce_stock(self, quantity):
        """Reduce the product's stock by the given quantity and trigger alert if stock is low."""
        if quantity > self.quantity:
            raise ValueError(f"Cannot reduce stock by {quantity}. Only {self.quantity} items available.")
        self.quantity -= quantity
        if self.quantity <= 10:
            self.send_low_stock_alert()
        self.save()

    def send_low_stock_alert(self):
        """Send an alert when stock is low."""
        # Customize this function to send real notifications, such as email or SMS.
        # For now, it simply prints the warning.
        print(f"Warning: Stock for {self.item_name} is low! Only {self.quantity} left.")

    
class Inventory(models.Model):
    product_name = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stall = models.CharField(max_length=100)

    def __str__(self):
        return self.product_name
    
class SalesReport(models.Model):
    stall = models.CharField(max_length=100)
    report_date = models.DateField()
    total_sales = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Report for {self.stall} on {self.report_date}"
    
class Employee(models.Model):
    stall_name = models.ForeignKey('Stall', on_delete=models.SET_NULL, null=True, blank=True)
    firstname = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=1, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    age = models.IntegerField()
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    email_address = models.EmailField(unique=True)
    religion = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    


class SalesData(models.Model):
    stall_name = models.ForeignKey(
        'Stall', on_delete=models.CASCADE, related_name='sales_data'
    )
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order_date} - {self.stall_name.name} - {self.total_amount}"



class Suplier(models.Model):
    supplier_id = models.AutoField(primary_key=True)  # Auto-increment primary key
    supplier_name = models.CharField(max_length=255, default="Unknown Supplier")  # Name of the supplier
    contact_person = models.CharField(max_length=255, default="Not Provided", verbose_name="Contact Person")  # Representative
    contact_info = models.CharField(max_length=255, default="Not Provided", verbose_name="Contact Information")  # Phone or email
    address = models.TextField(default="Not Provided")  # Full address
    payment_terms = models.TextField(default="Not Provided")  # Credit period, payment due dates, etc.
    tax_information = models.CharField(max_length=255, default="Not Provided", verbose_name="Tax Information")
    license_number = models.CharField(max_length=255, default="Not Provided", verbose_name="License Number")
    contract_start_date = models.DateField(default="2024-01-01", verbose_name="Contract Start Date")  # Default start date
    contract_end_date = models.DateField(default="2025-01-01", verbose_name="Contract End Date")  # Default end date
    stall_name = models.ForeignKey('Stall', on_delete=models.SET_NULL, null=True, blank=True, related_name="suppliers")

    def __str__(self):
        return self.supplier_name


class Admin(models.Model):
    id = models.AutoField(primary_key=True)
    stall_name = models.ForeignKey('Stall', on_delete=models.SET_NULL, null=True, blank=True)
    firstname = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=1, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    age = models.IntegerField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    email = models.EmailField()

    class Meta:
        unique_together = ('firstname', 'lastname')

    def __str__(self):
        return f"{self.firstname} {self.lastname}"


    def clean(self):
    # Ensure birthdate is a valid date object
        if isinstance(self.birthdate, str):
            try:
                self.birthdate = datetime.strptime(self.birthdate, '%Y-%m-%d').date()  # Convert string to date
            except ValueError:
                raise ValidationError("Invalid birthdate format. Please provide a valid date.")
        
        today = datetime.today().date()
        calculated_age = today.year - self.birthdate.year - (
            (today.month, today.day) < (self.birthdate.month, self.birthdate.day)
        )
        
        if calculated_age < 18:
            raise ValidationError("Admin must be at least 18 years old.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)

    def set_otp(self):
        self.otp = str(secrets.randbelow(1000000)).zfill(6)
        self.otp_expiration = now() + timedelta(minutes=10)
        self.save()
        self.send_otp_email()

    def is_otp_valid(self, otp):
        return self.otp == otp and now() < self.otp_expiration

    def reset_otp(self):
        self.otp = None
        self.otp_expiration = None
        self.save()

    def send_otp_email(self):
        subject = "Your OTP Code"
        message = f"Hello {self.firstname},\n\nYour OTP code is: {self.otp}\nThis code will expire in 10 minutes.\n\nThank you!"
        send_mail(
            subject,
            message,
            'admin@example.com',  # Replace with a valid sender email
            [self.email],
            fail_silently=False,
        )
    

class FoodItem(models.Model):
    item_id = models.AutoField(primary_key=True)  # Primary Key
    item_name = models.CharField(max_length=255, verbose_name="Item Name")  # Name of the item
    category = models.CharField(max_length=255)  # Item category
    unit_of_measurement = models.CharField(max_length=50, verbose_name="Unit of Measurement")  # e.g., kg, liters, pieces
    description = models.TextField(blank=True, null=True)  # Optional description of the item
    stock_quantity = models.IntegerField(verbose_name="Stock Quantity")  # Current stock
    reorder_level = models.IntegerField(verbose_name="Reorder Level")  # Minimum stock before restock
    batch_number = models.CharField(max_length=100, verbose_name="Batch Number")  # Identifier for batches
    expiry_date = models.DateField(verbose_name="Expiry Date", blank=True, null=True)  # Expiration date
    arrival_date = models.DateField(verbose_name="Arrival/Delivery Date")  # Delivery date
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cost Price")  # Cost per item
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Selling Price")  # Selling price
    stall_location = models.ForeignKey('Stall', on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created")  # Auto date for creation

    def __str__(self):
        return self.item_name
    
class SupplierItem(models.Model):
    supplier_item_id = models.AutoField(primary_key=True)  # Primary Key
    supplier = models.ForeignKey(Suplier, on_delete=models.CASCADE, verbose_name="Supplier")  # FK to Supplier
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, verbose_name="Food Item")  # FK to FoodItem
    lead_time = models.IntegerField(verbose_name="Lead Time (days)")  # Time required to deliver
    minimum_order_quantity = models.IntegerField(verbose_name="Minimum Order Quantity")  # Min order quantity
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price Per Unit")  # Price/unit
    date_created = models.DateTimeField(auto_now_add=True, verbose_name="Date Created") 

    def __str__(self):
        return f"{self.supplier.supplier_name} - {self.food_item.item_name}"

class EmailOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        return self.created_at >= now() - timedelta(minutes=5)

