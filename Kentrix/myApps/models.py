from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Transaction(models.Model):
    ubtransact_id = models.CharField(max_length=20, primary_key=True)
    order_date = models.DateTimeField(default=timezone.now)
    description = models.CharField(max_length=255, default='No description provided') 
    size = models.CharField(max_length=10)
    quantity = models.IntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Transaction {self.ubtransact_id} - {self.description}'

class SalesData(models.Model):
    stall_name = models.CharField(max_length=100)
    order_date = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.order_date} - {self.stall_name} - {self.total_amount}"
    
class Report(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    file = models.FileField(upload_to='reports/')
    submitted_by = models.ForeignKey(User, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_name = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)

    def __str__(self):
        return self.name

 
class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=255)
    expiration_date = models.DateField()
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Employee(models.Model):
    firstname = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=1, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    age = models.IntegerField()
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    email_address = models.EmailField()
    religion = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50)
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
    
class Admin(models.Model):
    firstname = models.CharField(max_length=50)
    middle_initial = models.CharField(max_length=1, blank=True, null=True)
    lastname = models.CharField(max_length=50)
    age = models.IntegerField()
    username = models.CharField(max_length=50, unique=True)
    password = models.CharField(max_length=100)
    birthdate = models.DateField()
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
    stall_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.firstname} {self.lastname}'
