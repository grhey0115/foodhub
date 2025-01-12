import matplotlib.pyplot as plt
from django.db.models.functions import TruncWeek, TruncMonth, TruncYear
from django.db.models import Sum
from django.db.models.functions import ExtractMonth, ExtractYear
import io
import os
import time
from django.db.models import Sum, functions as models_functions
import logging
from django.core.serializers.json import DjangoJSONEncoder
import calendar
from reportlab.lib.pagesizes import letter
from django.core.files.storage import FileSystemStorage
from reportlab.pdfgen import canvas
from django.template.loader import render_to_string
from io import StringIO
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from django.http import Http404
from .forms import StallForm, SupplierForm, FoodItemForm, SupplierItemForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login as django_login
from django.core.mail import send_mail
from django.contrib.auth.hashers import make_password 
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import JsonResponse, FileResponse
from django.conf import settings
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse
from django.db.models import Sum
from .models import SalesData, Transaction, Suplier, Employee, Admin, Report, Stall, SalesData, Profile, Inventory, Transaction, SalesReport, FoodItem, SupplierItem, EmailOTP, Product
from .forms import ReportForm, EmployeeForm, ProfileForm, ContactForm, StallForm, ProductForm
from django.views.decorators.csrf import csrf_exempt
import json
import csv
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import random
from datetime import datetime


def index(request):
    return render(request, 'index.html')

def home(request):
    return render(request, 'home.html')

def contact(request):
    return render(request, 'contact.html')

def employee(request):
    stalls = Stall.objects.all()  # Or show all stalls if no admin is logged in
    return render(request, 'employee.html', {'stalls': stalls})

def log_in(request):
    error_message = None
    next_url = request.GET.get('next', None)  # Get the next URL after successful login
    user_type = request.GET.get('user_type', 'employee')  # Default to employee login
    
    # Create default superadmin if it doesn't exist
    if user_type == 'super' and not User.objects.filter(username='superadmin').exists():
        User.objects.create_superuser(
            username='superadmin',
            email='superadmin@gmail.com',
            password='superadmin123'
        )
    
    if request.method == 'POST':
        password = request.POST.get('password')

        if user_type == 'employee':
            email = request.POST.get('email_address', '').strip()

            # Check for required fields
            if not email or not password:
                messages.error(request, "All fields are required.")
                return redirect('log_in')

            try:
                # Debug log to see the values being queried
                print(f"Attempting login for: {email}")

                # Query Employee with the provided email
                employee = Employee.objects.get(email_address=email)
                
                # Check if password matches the stored hash
                if check_password(password, employee.password):  # Validate password
                    request.session['employee_id'] = employee.id  # Store employee ID in session
                    logger.debug(f"Session after login: {request.session.items()}")
                    messages.success(request, f"Welcome {employee.firstname} {employee.lastname}!")
                    print(f"Redirecting to monthly_total_sales...")  # Debug log
                    return redirect('monthly_total_sales')  # Redirect to employee dashboard
                else:
                    error_message = "Invalid credentials for this employee."
                    print(f"Incorrect password for employee: {email}")  # Debug log
                    messages.error(request, error_message)
                    return redirect('log_in')

            except Employee.DoesNotExist:
                error_message = f"Employee with email {email} does not exist."
                print(f"Employee does not exist: {email}")  
                messages.error(request, error_message)
                return redirect('log_in')

                
        elif user_type == 'admin':
                    username = request.POST.get('username')
                    print(f"Attempting login for admin: {username}")  
                    try:
                        admin_user = Admin.objects.get(username=username)
                        print(f"Admin user found: {admin_user}")  
                        if check_password(password, admin_user.password):  
                            print("Password is correct.")  
                            if not admin_user.stall_name:
                                print("No stall assigned to admin.")  
                                messages.error(request, "You are not assigned to a stall.")
                                return redirect('log_in')
                            
                            request.session['admin_id'] = admin_user.id
                            print(f"Session admin_id set to: {admin_user.id}")  
                            messages.success(request, f"Welcome to {admin_user.stall_name.name} Admin {admin_user.firstname}!")
                            return redirect('admin_graph')  
                        else:
                            print("Incorrect password.")  
                            messages.error(request, "Incorrect password.")
                    except Admin.DoesNotExist:
                        print("Admin account does not exist.")  
                        messages.error(request, "Admin account does not exist.")
                    except Exception as e:
                        print(f"Unexpected error: {str(e)}")  
                        messages.error(request, f"An unexpected error occurred: {str(e)}")


        elif user_type == 'super' or user_type == 'superadmin':
            username = request.POST.get('username')
            user = authenticate(request, username=username, password=password)

            if user is not None and user.is_superuser:
                django_login(request, user)
                messages.success(request, f"Welcome, Superadmin {{ user.profile.first_name }} {{ user.profile.last_name }}!")
                return redirect(next_url if next_url != '/' else 'home')
            else:
                error_message = "Invalid superadmin credentials."

    return render(request, 'log_in.html', {
        'error_message': error_message,
        'user_type': user_type,
        'next_url': next_url,
    })

def stall(request):
    # Display list of stalls and handle adding, deleting, and updating
    stalls = Stall.objects.all()
    form = StallForm()

    if request.method == 'POST':
        # Add Stall
        if 'add_stall' in request.POST:
            form = StallForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    form.save()
                    #request.session['alert_message'] = 'Stall added successfully!'
                    #request.session['alert_type'] = 'success'
                    #return redirect('stall')
                    return JsonResponse({'success': True, 'message': 'Stall added successfully!'})
                except IntegrityError:
                    #request.session['alert_message'] = 'A stall with this name already exists.'
                    #request.session['alert_type'] = 'error'
                    return JsonResponse({'success': False, 'message': 'A stall with this name already exists.'})

        # Delete Stall
        elif 'delete_stall' in request.POST:
            stall_id = request.POST.get('stall_id')
            try:
                stall = get_object_or_404(Stall, id=int(stall_id))
                stall.delete()
                request.session['alert_message'] = 'Stall deleted successfully!'
                request.session['alert_type'] = 'success'
            except (ValueError, Stall.DoesNotExist):
                request.session['alert_message'] = 'Invalid stall ID or stall does not exist.'
                request.session['alert_type'] = 'error'

        elif 'update_stall' in request.POST:
            if 'update_stall' in request.POST:
                stall_id = request.POST.get('stall_id')
                try:
                    stall = get_object_or_404(Stall, id=int(stall_id))
                    form = StallForm(request.POST, request.FILES, instance=stall)
                    if form.is_valid():
                        form.save()
                        return JsonResponse({'success': True, 'message': 'Stall updated successfully!'})
                    else:
                        return JsonResponse({'success': False, 'message': 'Failed to update the stall. Please check the form.'})
                except (ValueError, Stall.DoesNotExist):
                    return JsonResponse({'success': False, 'message': 'Invalid stall ID or stall does not exist.'})
            
    # Clear session messages after use
    alert_message = request.session.pop('alert_message', None)
    alert_type = request.session.pop('alert_type', None)

    return render(request, 'stall.html', {
        'stalls': stalls,
        'form': form,
        'alert_message': alert_message,
        'alert_type': alert_type,
    })
    
def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(user):
    otp = generate_otp()
    EmailOTP.objects.update_or_create(user=user, defaults={"otp": otp})
    send_mail(
        subject="Your OTP Code",
        message=f"Your OTP code is {otp}",
        from_email="your-email@example.com",
        recipient_list=[user.email],
    )


def verify_otp(request):
    if request.method == "POST":
        otp = request.POST.get("otp")
        user_id = request.session.get("user_id")
        user = User.objects.get(id=user_id)
        otp_record = EmailOTP.objects.filter(user=user).first()
        if otp_record and otp_record.otp == otp and otp_record.is_valid():
            login(request, user)
            return HttpResponse("Login successful!")
        return HttpResponse("Invalid OTP or OTP expired")
    return render(request, "verify_otp.html")

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()
        if user:
            send_otp_email(user)
            return redirect("reset_password", user_id=user.id)
        return HttpResponse("Email not found")
    return render(request, "forgot_password.html")

def reset_password(request, user_id):
    if request.method == "POST":
        otp = request.POST.get("otp")
        new_password = request.POST.get("password")
        user = User.objects.get(id=user_id)
        otp_record = EmailOTP.objects.filter(user=user).first()
        if otp_record and otp_record.otp == otp and otp_record.is_valid():
            user.set_password(new_password)
            user.save()
            return HttpResponse("Password reset successful!")
        return HttpResponse("Invalid OTP or OTP expired")
    return render(request, "reset_password.html")

def transactions_view(request):
    # Get the employee ID from the session
    employee_id = request.session.get('employee_id')
    if not employee_id:
        messages.error(request, "You must be logged in to view transactions.")
        return redirect('log_in')

    try:
        # Fetch the employee instance using the session data
        employee = Employee.objects.get(id=employee_id)
        print(f"Employee fetched: {employee}")  # Debug log

        # Ensure the employee has a stall
        if not employee.stall_name:
            raise Http404("You are not assigned to a stall.")

        # Fetch the stall associated with the employee
        stall = employee.stall_name
        print(f"Stall fetched: {stall}")  # Debug log

        # Filter transactions for the specific stall using stall_name (not stall)
        transactions = Transaction.objects.filter(stall_name=stall)  # Corrected field name
        print(f"Transactions fetched for stall {stall.name}: {transactions}")  # Debug log

        # Check if no transactions were found
        if not transactions.exists():
            messages.info(request, f"No transactions found for {stall.name}.")
        
    except Employee.DoesNotExist:
        raise Http404("Employee record not found.")
    except Exception as e:
        print(f"Error occurred: {e}")
        transactions = Transaction.objects.none()  # Return an empty queryset, not a list
        messages.warning(request, "An error occurred while fetching transactions.")

    # Calculate total sales for the filtered transactions
    total_sales = transactions.aggregate(Sum('total_price'))['total_price__sum'] or 0
    print(f"Total sales: {total_sales}")  # Debug log

    # Render the transactions in the template
    return render(request, 'transaction_list.html', {
        'transactions': transactions,
        'total_sales': total_sales,
        'stall': stall if 'stall' in locals() else None,  # Pass stall if available
    })
    
@csrf_exempt
def save_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Log received data
            
            # Extract stall_name from the request data
            stall_name = data.get('stall_name')  # This should be the name of the stall
            if not stall_name:
                return JsonResponse({'success': False, 'error': 'stall_name is required'}, status=400)

            # Fetch the Stall object by its name
            try:
                stall = Stall.objects.get(name=stall_name)
                print(f"Stall fetched: {stall}")  # Debug log
            except Stall.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Stall not found'}, status=400)

            # Create transaction
            transaction = Transaction(
                ubtransact_id=data['ubtransact_id'],
                order_date=timezone.now(),
                description=data['description'],
                size=data['size'],
                quantity=data['quantity'],
                total_price=data['total_price'],
                stall_name=stall  # Assign the stall_name (ForeignKey)
            )
            transaction.save()
            print(f"Transaction saved: {transaction}")  # Debug log

            return JsonResponse({'success': True, 'transaction_id': transaction.ubtransact_id})

        except Exception as e:
            print(f"Error saving transaction: {e}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@csrf_exempt
def process_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received order data: {data}")  # Log incoming data

            # Check if all required fields are present
            required_fields = ['ubtransact_id', 'description', 'size', 'quantity', 'total_price', 'stall_name']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'success': False, 'error': f'Missing required field: {field}'}, status=400)

            # Fetch the Stall object by its name
            stall_name = data.get('stall_name')
            try:
                stall = Stall.objects.get(name=stall_name)
            except Stall.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Stall not found'}, status=400)
            
            print(f"Stall fetched: {stall}")  # Debug log

            # Create transaction
            transaction = Transaction.objects.create(
                ubtransact_id=data['ubtransact_id'],
                order_date=timezone.now(),
                description=data['description'],
                size=data['size'],
                quantity=data['quantity'],
                total_price=data['total_price'],
                stall_name=stall  # Assign the stall_name (ForeignKey)
            )

            print(f"Transaction created: {transaction}")  # Debug log
            return JsonResponse({'success': True, 'transaction_id': transaction.ubtransact_id})

        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            print(f"Error processing order: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

def monthly_total_sales(request):
    employee_id = request.session.get('employee_id')
    if not employee_id:
        messages.error(request, "You must be logged in to view this data.")
        return redirect('log_in')

    try:
        employee = Employee.objects.get(id=employee_id)
        stall = employee.stall_name

        if not stall:
            messages.error(request, "No stall is associated with your account.")
            return redirect('log_in')

        if not stall.is_active:
            messages.error(request, "Your stall is not active.")
            return redirect('log_in')

        # Get current week details
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6)  # Sunday

        # Query sales data for the current week
        weekly_sales = SalesData.objects.filter(
            stall_name=stall,
            order_date__range=[start_of_week, end_of_week]
        ).values('order_date').annotate(
            total_amount=Sum('total_amount')
        ).order_by('order_date')

        # Prepare data for the bar chart
        labels = []
        totals = []
        for day in range(7):  # Iterate through each day of the current week
            current_date = start_of_week + timedelta(days=day)
            labels.append(current_date.strftime('%m-%d-%y'))  # Format as month-day-year
            sales_data = next(
                (item for item in weekly_sales if item['order_date'] == current_date),
                {'total_amount': 0}  # Default to 0 if no sales data
            )
            totals.append(sales_data['total_amount'])

        # Create the bar chart
        fig, ax = plt.subplots(figsize=(10, 6))  # Adjust size for better visibility
        ax.bar(labels, totals, color='blue')
        ax.set_xlabel('Date (Month-Day-Year)')
        ax.set_ylabel('Total Sales Amount')
        ax.set_title(f'Sales for the Current Week ({stall.name})')
        ax.tick_params(axis='x', rotation=45)

        # Save the graph as a base64-encoded string
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        return render(request, 'monthly_total_sales.html', {'graph': img_str, 'stall': stall.name})

    except Employee.DoesNotExist:
        messages.error(request, "Employee account not found.")
        return redirect('log_in')
    except Stall.DoesNotExist:
        messages.error(request, "Stall associated with this employee does not exist.")
        return redirect('log_in')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('log_in')

def yummy_mango(request):
    return render(request, 'yummy_mango.html')
    
def report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the report to the database
            report_instance = form.save()

            # Handle file upload
            file = form.cleaned_data.get('file')
            if file:
                fs = FileSystemStorage()
                filename = fs.save(file.name, file)
                file_url = fs.url(filename)
            else:
                file_url = None

            # Return a JSON response for success
            return JsonResponse({
                'success': True,
                'message': 'Report submitted successfully!',
                'file_url': file_url,
                'file_type': os.path.splitext(file.name)[-1] if file else None,
            })
        else:
            # Return a JSON response for errors
            return JsonResponse({
                'success': False,
                'errors': form.errors,
            })

    else:
        # On GET, render the template with the form
        form = ReportForm()
        return render(request, 'report.html', {
            'form': form,
            'downloaded_file_url': None,
            'downloaded_file_type': None,
        })

def report_list(request):
    # Check if admin is logged in
    if 'admin_id' not in request.session:
        return render(request, 'report_list.html', {"error_message": "You do not have the necessary permissions. Please log in."})

    try:
        # Get the logged-in admin
        admin_user = Admin.objects.get(id=request.session['admin_id'])

        # Ensure admin has an assigned stall
        if not admin_user.stall_name:
            return render(request, 'report_list.html', {"error_message": "You are not assigned to a valid stall, access denied."})

        # Get the stall name assigned to the admin
        stall = admin_user.stall_name

        # Fetch reports filtered by the admin's stall
        reports = Report.objects.filter(stall_name=stall).order_by('-submitted_at')

        # Pass the filtered reports to the template
        return render(request, 'report_list.html', {
            'reports': reports
        })

    except Admin.DoesNotExist:
        return render(request, 'report_list.html', {"error_message": "Admin profile not found."})

    except Exception as e:
        return render(request, 'report_list.html', {"error_message": "An unexpected error occurred."})

def delete_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)

    if request.method == 'POST':
        # Delete the report object
        report.delete()
        messages.success(request, 'Report deleted successfully!')
        return redirect('report_list')  # Redirect to the report list page

    return render(request, 'report_list.html', {'report': report})


def clear_transaction(request):
    Transaction.objects.filter(order_date__lt=datetime.date.today()).delete()
    return HttpResponse('Transactions cleared')

def admin_graph(request):
    try:
        # Debug session data
        print(f"Session data: {request.session.items()}")

        # Check if admin_id is in session
        admin_id = request.session.get('admin_id')
        if not admin_id:
            print("admin_id not found in session. Redirecting to login.")
            return redirect('log_in')

        # Get the logged-in admin
        try:
            admin_user = Admin.objects.get(id=admin_id)
        except Admin.DoesNotExist:
            print("Admin profile not found for the given admin_id. Redirecting to login.")
            return redirect('log_in')

        print(f"Logged-in Admin: {admin_user}")

        # Ensure admin has an assigned stall
        if not admin_user.stall_name:
            print(f"Admin {admin_user} does not have a valid stall assigned.")
            return render(request, 'admin_graph.html', {"error_message": "You are not assigned to a valid stall, access denied."})

        # Get stall and current year
        stall = admin_user.stall_name
        current_year = datetime.now().year

        # Fetch and process monthly sales data
        monthly_sales = (
            SalesData.objects.filter(stall_name=stall, order_date__year=current_year)
            .annotate(month=ExtractMonth("order_date"))
            .values("month")
            .annotate(total_monthly_sales=Sum("total_amount"))
            .order_by("month")
        )
        monthly_sales = [
            {"month": calendar.month_name[item["month"]], "total_monthly_sales": float(item["total_monthly_sales"])}
            for item in monthly_sales
        ]

        print(f"Monthly sales data: {monthly_sales}")

        # Fetch and process annual sales data
        annual_sales = (
            SalesData.objects.filter(stall_name=stall)
            .annotate(year=ExtractYear("order_date"))
            .values("year")
            .annotate(total_annual_sales=Sum("total_amount"))
            .order_by("year")
        )
        annual_sales = [
            {"year": item["year"], "total_annual_sales": float(item["total_annual_sales"])}
            for item in annual_sales
        ]

        print(f"Annual sales data: {annual_sales}")

        # Pass data to template
        return render(request, 'admin_graph.html', {
            "stall_name": stall,
            "monthly_sales": json.dumps(monthly_sales),
            "annual_sales": json.dumps(annual_sales),
        })

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return render(request, 'admin_graph.html', {"error_message": "An unexpected error occurred."})
    
def employees(request):
    try:
        # Fetch the logged-in admin using session data
        admin = Admin.objects.get(id=request.session.get('admin_id'))
    except Admin.DoesNotExist:
        messages.error(request, "Admin session is invalid. Please log in again.")
        return redirect('login')

    form = EmployeeForm(request.POST or None, admin=admin)  # Pass admin to the form
    if request.method == 'POST':
        if form.is_valid():
            employee = form.save(commit=False)
            # Assign the stall from the admin's `stall_name` to the employee
            if admin.stall_name:
                employee.stall_name = admin.stall_name  # Ensure this is a Stall instance
            employee.save()  # Save the Employee with the correct Stall assigned
            messages.success(request, "Employee created successfully!")
            return redirect('emp_success')
        else:
            messages.error(request, "Failed to create employee. Please check the form.")
            
    return render(request, 'emp_records.html', {'form': form})

def employee_create(request):
    try:
        # Fetch the logged-in admin using session data
        admin = Admin.objects.get(id=request.session.get('admin_id'))
    except Admin.DoesNotExist:
        messages.error(request, "Admin session is invalid. Please log in again.")
        return redirect('login')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, admin=admin)
        if form.is_valid():
            employee = form.save(commit=False)
            # Assign the stall from the admin's `stall_name` to the employee
            if admin.stall_name:
                employee.stall_name = admin.stall_name  # Ensure this is a Stall instance
            employee.save()  # Save the Employee with the correct Stall assigned
            messages.success(request, "Employee created successfully!")
            return redirect('emp_success')
        else:
            messages.error(request, "Failed to create employee. Please check the form.")
    else:
        form = EmployeeForm(admin=admin)

    return render(request, 'supreg.html', {'form': form})


def emp_success(request):
    try:
        # Get the logged-in admin
        admin = Admin.objects.get(id=request.session.get('admin_id'))
        
        # Fetch the stall associated with the admin
        stall = admin.stall_name  # Assuming `stall_name` is a ForeignKey to Stall
        
        # Fetch employees associated with the stall
        employees = Employee.objects.filter(stall_name=stall)
    except Admin.DoesNotExist:
        employees = []
        messages.error(request, "Admin session is invalid. Please log in again.")
    except Stall.DoesNotExist:
        employees = []
        messages.error(request, "The associated stall does not exist.")

    return render(request, 'emp_success.html', {'employees': employees})


def supreg(request):
    if request.method == 'POST':
        # Extract form data
        firstname = request.POST.get('firstname', '').strip()
        middle_initial = request.POST.get('middle_initial', '').strip()
        lastname = request.POST.get('lastname', '').strip()
        birthdate = request.POST.get('birthdate', '').strip()
        address = request.POST.get('address', '').strip()
        username = request.POST.get('username', '').strip()
        contact_number = request.POST.get('contact_number', '').strip()
        stallname = request.POST.get('stallname', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()

        try:
            # Validate birthdate and age
            birthdate_obj = datetime.strptime(birthdate, '%Y-%m-%d').date()
            today = datetime.now().date()
            age_from_birthdate = (
                today.year - birthdate_obj.year -
                ((today.month, today.day) < (birthdate_obj.month, birthdate_obj.day))
            )
            if age_from_birthdate < 18:
                context = {'error_message': "Admin must be at least 18 years old."}
                return render(request, 'supreg.html', context)

            # Validate stall existence
            stall = Stall.objects.get(name=stallname)  # Validate that the provided stall exists
        except Stall.DoesNotExist:
            context = {'error_message': f"Stall '{stallname}' does not exist."}
            return render(request, 'supreg.html', context)
        except ValueError:
            context = {'error_message': "Invalid birthdate format. Use YYYY-MM-DD."}
            return render(request, 'supreg.html', context)

        try:
            # Check if the stall already has an admin
            if Admin.objects.filter(stall_name=stall).exists():
                context = {'error_message': f"Stall '{stallname}' already has an admin assigned."}
                return render(request, 'supreg.html', context)

            # Check for duplicate admin names
            if Admin.objects.filter(firstname=firstname, middle_initial=middle_initial, lastname=lastname).exists():
                context = {'error_message': f"Admin '{firstname} {middle_initial} {lastname}' already exists."}
                return render(request, 'supreg.html', context)

            # Check for duplicate username/email
            if Admin.objects.filter(username=username).exists():
                context = {'error_message': f"Username '{username}' is already taken."}
                return render(request, 'supreg.html', context)

            if Admin.objects.filter(email=email).exists():
                context = {'error_message': f"Email '{email}' is already registered."}
                return render(request, 'supreg.html', context)

            # Create the Admin record directly
            admin = Admin(
                firstname=firstname,
                middle_initial=middle_initial,
                lastname=lastname,
                birthdate=birthdate_obj,
                age=age_from_birthdate,
                address=address,
                username=username,
                contact_number=contact_number,
                email=email,
                stall_name=stall,
            )
            admin.set_password(password)  # Hash the password
            admin.save()

            # Render success context to trigger SweetAlert
            context = {'success': True}
            return render(request, 'supreg.html', context)

        except Exception as e:
            context = {'error_message': f"An unexpected error occurred: {str(e)}"}
            return render(request, 'supreg.html', context)

    # Handle GET request
    stalls = Stall.objects.all()
    return render(request, 'supreg.html', {'stalls': stalls})

def adminrec(request):
    admins = Admin.objects.select_related('stall_name').all()
    return render(request, 'adminrec.html', {'admins': admins})

def edit_admin(request, admin_id):
    admin = get_object_or_404(Admin, id=admin_id)
    stalls = Stall.objects.all()

    if request.method == 'POST':
        # Update fields
        admin.firstname = request.POST['firstname']
        admin.age = request.POST['age']
        admin.middle_initial = request.POST['middle_initial']
        admin.birthdate = request.POST['birthdate']
        admin.lastname = request.POST['lastname']
        admin.address = request.POST['address']
        admin.username = request.POST['username']
        admin.contact_number = request.POST['contact_number']

        # Update stall_name
        admin.stall_name = get_object_or_404(Stall, id=request.POST['stallname'])

        # Handle password: Only hash and update if a new password is provided
        new_password = request.POST['password']
        if new_password and new_password != admin.password:
            admin.password = make_password(new_password)

        # Save the updated admin record
        admin.save()

        # Add success message
        messages.success(request, f"Admin '{admin.firstname} {admin.lastname}' successfully updated!")

        # Redirect to the admin records page
        return redirect('adminrec')

    return render(request, 'edit_admin.html', {
        'admin': admin,
        'stalls': stalls,
    })
    
def delete_admin(request, admin_id):
    # Fetch the admin record based on the provided ID (which should be an integer)
    admin = get_object_or_404(Admin, id=admin_id)
    admin.delete()
    return redirect('adminrec')
def get_products_for_stall(request):
    
    return render(request, 'yummy_mango.html')
def get_admin_stall(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return None, "Admin not logged in."
    try:
        admin_user = Admin.objects.get(id=admin_id)
        if not admin_user.stall_name:
            return None, "Admin is not assigned to a valid stall."
        return admin_user.stall_name, None
    except Admin.DoesNotExist:
        return None, "Invalid admin ID."

def food_and_supplier_items(request):
    # Get the stall name and handle any errors
    stall_name, error = get_admin_stall(request) 
    if error:
        messages.error(request, error)
        return redirect('log_in')

    # Fetch all stalls to populate the dropdown
    stalls = Stall.objects.all()

    if request.method == "POST":
        try:
            # Handling form submission for food items
            if 'item_name' in request.POST and 'category' in request.POST:
                stall = Stall.objects.get(name=stall_name)
                FoodItem.objects.create(
                    item_name=request.POST['item_name'],
                    category=request.POST['category'],
                    stock_quantity=request.POST['stock_quantity'],
                    reorder_level=request.POST['reorder_level'],
                    batch_number=request.POST['batch_number'],
                    expiry_date=request.POST.get('expiry_date'),
                    arrival_date=request.POST['arrival_date'],
                    cost_price=request.POST['cost_price'],
                    selling_price=request.POST['selling_price'],
                    stall_location=stall
                )
            
            # Handling form submission for supplier items
            elif 'supplier_id' in request.POST and 'food_item_id' in request.POST:
                # Ensure supplier_id is valid for the current stall
                supplier_id = request.POST['supplier_id']
                supplier = Suplier.objects.get(supplier_id=supplier_id, stall_name__name=stall_name)
                SupplierItem.objects.create(
                    supplier=supplier,
                    food_item_id=request.POST['food_item_id'],
                    lead_time=request.POST['lead_time'],
                    minimum_order_quantity=request.POST['minimum_order_quantity'],
                    price_per_unit=request.POST['price_per_unit']
                )

            # Handling form submission for adding products
            elif 'quantity' in request.POST and 'price' in request.POST:
                item_name_id = request.POST.get('item_name') 
                if not item_name_id:
                    return JsonResponse({'success': False, 'error': 'Item ID is missing or invalid.'})

                food_item = get_object_or_404(
                    FoodItem,
                    id=item_name_id,
                    stall_location__name=stall_name
                )

                Product.objects.create(
                    item_name=food_item,
                    quantity=request.POST['quantity'],
                    price=request.POST['price'],
                    stall_name=food_item.stall_location
                )

            # After successful creation, redirect to the same page
            return redirect('food_and_supplier_items')

        except Stall.DoesNotExist:
            return render(request, 'food_and_supplier_items.html', {
                'food_items': FoodItem.objects.filter(stall_location__name=stall_name),
                'supplier_items': SupplierItem.objects.filter(supplier__stall_name=stall_name),
                'products': Product.objects.filter(stall_name__name=stall_name),
                'error_message': "The specified stall does not exist.",
                'stalls': stalls,
                'stall': Stall.objects.get(name=stall_name)  # Pass the stalls to the template
            })
        except Exception as e:
            return render(request, 'food_and_supplier_items.html', {
                'food_items': FoodItem.objects.filter(stall_location__name=stall_name),
                'supplier_items': SupplierItem.objects.filter(supplier__stall_name=stall_name),
                'products': Product.objects.filter(stall_name__name=stall_name),
                'error_message': str(e),
                'stalls': stalls,
                'stall': Stall.objects.get(name=stall_name)  # Pass the stalls to the template
            })

    # Fetch suppliers filtered by the stall for the dropdown
    suppliers = Suplier.objects.filter(stall_name__name=stall_name)

    # Render the page with the filtered suppliers, food, supplier items, and products
    return render(request, 'food_and_supplier_items.html', {
        'food_items': FoodItem.objects.filter(stall_location__name=stall_name),
        'supplier_items': SupplierItem.objects.filter(supplier__stall_name=stall_name),
        'products': Product.objects.filter(stall_name__name=stall_name),
        'stalls': stalls,
        'suppliers': suppliers,  # Pass filtered suppliers to the template
        'stall': Stall.objects.get(name=stall_name)  # Pass the stall to the template
    })
def add_product(request):
    if request.method == "POST":
        try:
            # Get input values
            stall_id = request.POST.get('stall_id')
            food_item_id = request.POST.get('food_item_id')  # Ensure this is the valid FoodItem ID
            category = request.POST.get('category')
            quantity = int(request.POST.get('quantity'))

            print(f"Stall ID: {stall_id}, Food Item ID: {food_item_id}")

            # Ensure required fields are provided
            if not stall_id or not food_item_id:
                return JsonResponse({'success': False, 'error': 'Stall ID or Food Item ID is missing.'})

            # Fetch Stall
            try:
                stall = Stall.objects.get(id=stall_id)
            except Stall.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Stall does not exist.'})

            # Fetch FoodItem object
            try:
                food_item = FoodItem.objects.get(item_id=food_item_id)
                print(f"Food Item: {food_item.item_name}")  # Debugging line
            except FoodItem.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Food Item does not exist.'})

            # Sizes and Prices
            size_prices = {
                "small": request.POST.get('price_small'),
                "medium": request.POST.get('price_medium'),
                "large": request.POST.get('price_large'),
            }
            size_prices = {k: float(v) for k, v in size_prices.items() if v}

            # Create Product
            product = Product.objects.create(
                stall_name=stall,
                item_name=food_item,  # Pass the actual FoodItem instance
                category=category,
                quantity=quantity,
                price=size_prices.get('small', 0),  # Default to small price if available
                size_prices=size_prices,
            )

            # Optional Add-Ons
            add_on_name = request.POST.get('add_on_name')
            add_on_price = request.POST.get('add_on_price')
            if add_on_name and add_on_price:
                product.add_ons.append({'name': add_on_name, 'price': float(add_on_price)})
                product.save()

            return JsonResponse({'success': True, 'message': 'Product added successfully!'})
        except Exception as e:
            import traceback
            print(traceback.format_exc())  # For debugging
            return JsonResponse({'success': False, 'error': f"Unexpected error: {e}"})

    return redirect('food_and_supplier_items')

def add_supplier_item(request):
    if request.method == "POST":
        supplier_id = request.POST.get('supplier_id')
        food_item_id = request.POST.get('food_item_id')
        lead_time = request.POST.get('lead_time')
        minimum_order_quantity = request.POST.get('minimum_order_quantity')
        price_per_unit = request.POST.get('price_per_unit')
        print(f"Supplier ID: {supplier_id}, Food Item ID: {food_item_id}")  # Debugging line

        try:
            # Get the logged-in admin's stall
            stall_name, error = get_admin_stall(request)
            if error:
                return JsonResponse({'success': False, 'error': error})

            # Fetch the Stall object associated with the admin
            stall = Stall.objects.get(name=stall_name)

            # Validate that the supplier belongs to the admin's stall
            supplier = Suplier.objects.get(supplier_id=supplier_id, stall_name=stall)
            print(f"Supplier: {supplier.supplier_name}")  # Debugging line

            # Validate that the food item belongs to the admin's stall
            food_item = FoodItem.objects.get(item_id=food_item_id, stall_location=stall_name)

            # Create a new supplier item record
            supplier_item = SupplierItem.objects.create(
                supplier=supplier,
                food_item=food_item,
                lead_time=int(lead_time),  # Ensure lead_time is an integer
                minimum_order_quantity=int(minimum_order_quantity),
                price_per_unit=float(price_per_unit),  # Ensure price_per_unit is a float
            )

        except Suplier.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': "Invalid supplier ID or supplier does not belong to your stall."
            })
        except FoodItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': "Invalid food item ID or food item does not belong to your stall."
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return redirect('food_and_supplier_items')


def edit_supplier(request, supplier_id):
    # Ensure the admin is logged in and get the current admin's stall location
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "You need to log in to edit suppliers.")
        return redirect('login')

    # Get the logged-in admin's stall location
    admin_user = get_object_or_404(Admin, id=admin_id)
    current_stall = admin_user.stall_name  # Assuming the admin's stall name is stored in 'stall_name'

    # Get the supplier and ensure it's linked to the current admin's stall
    supplier = get_object_or_404(Suplier, pk=supplier_id, stall_name=current_stall)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            messages.success(request, 'Supplier details updated successfully!')
            return redirect('suppliers')  # Redirect to the supplier list page
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'edit_supplier.html', {'form': form, 'supplier': supplier})

def edit_supplier_item(request, supplier_item_id):
    admin_id = request.session.get('admin_id')
    
    # Check if the admin is logged in
    if not admin_id:
        messages.error(request, "You need to log in to access this page.")
        return redirect('login')

    try:
        admin_user = Admin.objects.get(id=admin_id)
        stall_location = admin_user.stall_name  # Assuming stall_name represents the admin's stall
    except Admin.DoesNotExist:
        messages.error(request, "Admin account not found.")
        return redirect('login')

    # Fetch the supplier item using the ID
    supplier_item = get_object_or_404(SupplierItem, pk=supplier_item_id)

    # Ensure the supplier item belongs to the admin's stall (if applicable)
    if supplier_item.supplier.stall_name != stall_location:
        messages.error(request, "You are not authorized to edit this supplier item.")
        return redirect('supplier_items')  # Redirect to the list of supplier items

    # Get the list of suppliers and food items to populate the form fields
    suppliers = Suplier.objects.all()
    food_items = FoodItem.objects.all()

    # Handle the form submission
    if request.method == 'POST':
        print("POST Data:", request.POST)  # Debugging POST data
        form = SupplierItemForm(request.POST, instance=supplier_item)
        if form.is_valid():
            form.save()  # Save the updated supplier item
            messages.success(request, 'Supplier item updated successfully!')
            return redirect('food_and_supplier_items')  # Redirect to the supplier items list page
        else:
            print("Form errors:", form.errors)  # Debugging form errors
            messages.error(request, 'There was an error updating the supplier item.')

    else:
        # For GET requests, populate the form with the current data
        form = SupplierItemForm(instance=supplier_item)

    # Render the form with the necessary context
    return render(request, 'edit_supplier_item.html', {
        'form': form,
        'supplier_item': supplier_item,
        'suppliers': suppliers,
        'food_items': food_items,
        'stall_name': stall_location,  # Passing stall_name to template (if needed)
    })

    
logger = logging.getLogger(__name__)

def edit_product(request, product_id):
    # Get the logged-in admin's stall
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "You need to log in to access this page.")
        return redirect('login')

    try:
        admin_user = Admin.objects.get(id=admin_id)
        stall_location = admin_user.stall_name
    except Admin.DoesNotExist:
        messages.error(request, "Admin account not found.")
        return redirect('login')

    # Fetch the product
    product = get_object_or_404(Product, pk=product_id)

    # Ensure the product belongs to the logged-in admin's stall
    if product.stall_location != stall_location:
        messages.error(request, "You are not authorized to edit this product.")
        return redirect('products')  # Redirect to products list

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product updated successfully!')
            return redirect('products')  # Redirect to products list
    else:
        form = ProductForm(instance=product)

    # Pass the form to the template along with the stall name
    return render(request, 'edit_product.html', {'form': form, 'product': product, 'stall_name': stall_location})

def delete_supplier(request, supplier_id):
    # Ensure the admin is logged in and get the current admin's stall location
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "You need to log in to delete suppliers.")
        return redirect('login')

    # Get the logged-in admin's stall location
    admin_user = get_object_or_404(Admin, id=admin_id)
    current_stall = admin_user.stall_name  # Assuming the admin's stall name is stored in 'stall_name'

    # Get the supplier and ensure it's linked to the current admin's stall
    supplier = get_object_or_404(Suplier, pk=supplier_id, stall_name=current_stall)

    if request.method == 'POST':
        supplier.delete()
        messages.success(request, 'Supplier deleted successfully!')
        return redirect('suppliers')

    return render(request, 'confirm_delete.html', {'supplier': supplier})

def delete_food_item(request, item_id):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "You need to log in to delete food items.")
        return redirect('login')

    admin_user = get_object_or_404(Admin, id=admin_id)
    admin_stall = admin_user.stall_name

    try:
        item = FoodItem.objects.get(item_id=item_id, stall_location=admin_stall)
        item.delete()
        messages.success(request, 'Food item deleted successfully.')
        return redirect('food_and_supplier_items')
    except FoodItem.DoesNotExist:
        messages.error(request, 'The food item was not found or does not belong to your stall.')
        return redirect('food_and_supplier_items')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('food_and_supplier_items')

def delete_supplier_item(request, supplier_item_id):
    if request.method == "POST":
        try:
            admin_id = request.session.get('admin_id')
            if not admin_id:
                return JsonResponse({'success': False, 'error': "You need to log in to delete supplier items."})

            admin_user = get_object_or_404(Admin, id=admin_id)
            admin_stall = admin_user.stall_name

            # Fetch and delete the supplier item using the supplier_item_id
            supplier_item = SupplierItem.objects.get(supplier_item_id=supplier_item_id, supplier__stall_name=admin_stall)
            supplier_item.delete()
            return JsonResponse({'success': True})
        except SupplierItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'The supplier item was not found or does not belong to your stall.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f"An error occurred: {str(e)}"})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    
def add_food_item(request):
    if request.method == "POST":
        # Extract form data from POST request
        item_name = request.POST.get('item_name')
        category = request.POST.get('category')
        unit_of_measurement = request.POST.get('unit_of_measurement')
        stock_quantity = request.POST.get('stock_quantity')
        reorder_level = request.POST.get('reorder_level')
        batch_number = request.POST.get('batch_number')
        expiry_date = request.POST.get('expiry_date')  # Optional
        arrival_date = request.POST.get('arrival_date')
        cost_price = request.POST.get('cost_price')
        selling_price = request.POST.get('selling_price')
        stall_location_id = request.POST.get('stall_location')  # Expecting an ID here, not a name

        try:
            # Get the logged-in admin
            admin_id = request.session.get('admin_id')
            admin_user = Admin.objects.get(id=admin_id)

            # Validate stall location by ID
            if stall_location_id:
                stall_location = Stall.objects.get(id=stall_location_id)  # Fetch Stall object by ID
            else:
                stall_location = admin_user.stall_name  # Assign admin's stall if not provided

            # Create a new food item record
            food_item = FoodItem.objects.create(
                item_name=item_name,
                category=category,
                unit_of_measurement=unit_of_measurement,  # Make sure this is passed correctly
                stock_quantity=int(stock_quantity),
                reorder_level=int(reorder_level),
                batch_number=batch_number,
                expiry_date=expiry_date if expiry_date else None,
                arrival_date=arrival_date,
                cost_price=float(cost_price),
                selling_price=float(selling_price),
                stall_location=stall_location  # Assign the Stall object (not name)
            )

        except Stall.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': "Invalid stall location ID."
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })

    return redirect('food_and_supplier_items')

def edit_food_item(request, item_id):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        messages.error(request, "You need to log in to access this page.")
        return redirect('login')
    
    try:
        admin_user = Admin.objects.get(id=admin_id)
        stall_location = admin_user.stall_name
    except Admin.DoesNotExist:
        messages.error(request, "Admin account not found.")
        return redirect('login')

    # Fetch the food item
    item = get_object_or_404(FoodItem, pk=item_id)

    # Ensure the food item belongs to the logged-in admin's stall
    if item.stall_location != stall_location:
        messages.error(request, "You are not authorized to edit this food item.")
        return redirect('food_items')

    if request.method == 'POST':
        form = FoodItemForm(request.POST, instance=item, admin=admin_user)  # Pass admin to form
        if form.is_valid():
            form.save()
            messages.success(request, 'Food item updated successfully!')
            return redirect('food_and_supplier_items')  # Redirect to food items list
        else:
            print("Form errors:", form.errors)  # Debug form errors
    else:
        form = FoodItemForm(instance=item, admin=admin_user)  # Pass admin to form

    # Pass the form to the template along with the stall name
    return render(request, 'edit_food_item.html', {
        'food_item': item,
        'stall_name': stall_location,
        'stalls': Stall.objects.all(),
        'form': form,
    })



# View for managing suppliers
def supplier_list(request):
    stall_name, error = get_admin_stall(request)
    if error:
        messages.error(request, error)
        return redirect('log_in')

    suppliers = Suplier.objects.filter(stall_name=stall_name)

    if request.method == "POST":
        try:
            Suplier.objects.create(
                supplier_name=request.POST['supplier_name'],
                contact_person=request.POST['contact_person'],
                contact_info=request.POST['contact_info'],
                address=request.POST['address'],
                payment_terms=request.POST.get('payment_terms', 'Not Provided'),
                tax_information=request.POST.get('tax_information', 'Not Provided'),
                license_number=request.POST.get('license_number', 'Not Provided'),
                contract_start_date=request.POST['contract_start_date'],
                contract_end_date=request.POST['contract_end_date'],
                stall_name=stall_name  # Ensure the supplier is associated with the correct stall
            )
            return redirect('supplier_list')
        except Exception as e:
            return render(request, 'suppliers.html', {
                'suppliers': suppliers,
                'error_message': str(e)
            })

    return render(request, 'suppliers.html', {'suppliers': suppliers})


def update_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)  # Get the employee by ID
    if request.method == 'POST':
        # Get form data from the POST request
        employee.firstname = request.POST['firstname']
        employee.middle_initial = request.POST['middle_initial']
        employee.lastname = request.POST['lastname']
        employee.age = request.POST['age']
        employee.birthdate = request.POST['birthdate']  # Ensure this field is captured
        employee.address = request.POST['address']
        employee.contact_number = request.POST['contact_number']
        employee.email_address = request.POST['email_address']
        
        # Check if a new password is provided
        new_password = request.POST['password']
        if new_password:  # If a new password is provided
            employee.password = make_password(new_password)  # Hash the new password
        
        # Save the updated employee information
        employee.save()

        # Redirect back to the employee records page
        return redirect(reverse('emp_success'))  # Make sure 'emp_records' is defined in your URLs

    # If GET request, render the update form with the current employee data
    context = {'employee': employee}
    return render(request, 'update_employee.html', context)

def delete_employee(request, id):
    employee = get_object_or_404(Employee, id=id)
    employee.delete()
    return redirect('emp_success')  


@login_required
def superadmin_dashboard(request):
    return render(request, 'super.html')


def user(request):
    return render(request, 'user.html')

def about(request):
    return render(request, 'about.html')

def update_stall_ajax(request, stall_id):
    if request.method == 'POST':
        stall = get_object_or_404(Stall, id=stall_id)
        name = request.POST.get('name')
        contact_number = request.POST.get('contact_number')
        is_active = request.POST.get('is_active') == 'True'
        logo = request.FILES.get('logo')

        # Update the stall
        stall.name = name
        stall.contact_number = contact_number
        stall.is_active = is_active
        if logo:
            stall.logo = logo
        stall.save()

        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

# Handle deleting a stall
def delete_stall(request, stall_id):
    stall = get_object_or_404(Stall, id=stall_id)
    stall.delete()
    return JsonResponse({'success': True})


def manage_stalls(request):
    stalls = Stall.objects.all()  # Fetch all stalls
    form = StallForm(request.POST or None, request.FILES or None)

    if request.method == "POST":
        if "add_stall" in request.POST:
            if form.is_valid():
                form.save()
                messages.success(request, "Stall added successfully!")
                return redirect('stall')  # Reload page to show updated data
        elif "update_stall" in request.POST:
            stall_id = request.POST.get("stall_id")
            stall = Stall.objects.get(id=stall_id)
            form = StallForm(request.POST, request.FILES, instance=stall)
            if form.is_valid():
                form.save()
                messages.success(request, "Stall updated successfully!")
                return redirect('stall')  # Reload page to show updated data
        elif "delete_stall" in request.POST:
            stall_id = request.POST.get("stall_id")
            Stall.objects.filter(id=stall_id).delete()
            messages.success(request, "Stall deleted successfully!")
            return redirect('stall')  # Reload page to show updated data

    return render(request, 'stall_template.html', {'stalls': stalls, 'form': form})
    
def get_sales_data(request):
    # Aggregate weekly sales
    weekly_sales = (
        SalesData.objects.annotate(week=TruncWeek("order_date"))
        .values("week", "stall_name__name")  # Group by week and stall name
        .annotate(total_sales=Sum("total_amount"))  # Calculate total sales
        .order_by("week")
    )

    # Aggregate monthly sales
    monthly_sales = (
        SalesData.objects.annotate(month=TruncMonth("order_date"))
        .values("month", "stall_name__name")  # Group by month and stall name
        .annotate(total_sales=Sum("total_amount"))  # Calculate total sales
        .order_by("month")
    )

    # Aggregate annual sales
    annual_sales = (
        SalesData.objects.annotate(year=TruncYear("order_date"))
        .values("year", "stall_name__name")  # Group by year and stall name
        .annotate(total_sales=Sum("total_amount"))  # Calculate total sales
        .order_by("year")
    )

    # Structure the response data
    response_data = {
        "weekly": {},
        "monthly": {},
        "annual": {},
    }

    # Organize weekly sales data
    for sale in weekly_sales:
        stall = sale["stall_name__name"]
        week = sale["week"]
        total_sales = sale["total_sales"]

        if stall not in response_data["weekly"]:
            response_data["weekly"][stall] = {"labels": [], "sales": []}
        
        response_data["weekly"][stall]["labels"].append(str(week))
        response_data["weekly"][stall]["sales"].append(total_sales)

    # Organize monthly sales data
    for sale in monthly_sales:
        stall = sale["stall_name__name"]
        month = sale["month"]
        total_sales = sale["total_sales"]

        if stall not in response_data["monthly"]:
            response_data["monthly"][stall] = {"labels": [], "sales": []}
        
        response_data["monthly"][stall]["labels"].append(str(month))
        response_data["monthly"][stall]["sales"].append(total_sales)

    # Organize annual sales data
    for sale in annual_sales:
        stall = sale["stall_name__name"]
        year = sale["year"]
        total_sales = sale["total_sales"]

        if stall not in response_data["annual"]:
            response_data["annual"][stall] = {"labels": [], "sales": []}
        
        response_data["annual"][stall]["labels"].append(str(year))
        response_data["annual"][stall]["sales"].append(total_sales)

    return JsonResponse(response_data)

def export_sales_data(request, stall_name, period):
    # Validate period
    if period not in ['weekly', 'monthly', 'annual']:
        return JsonResponse({'error': 'Invalid period parameter'}, status=400)

    # Ensure stall exists and is active
    try:
        stall = Stall.objects.get(name=stall_name, is_active=True)
    except Stall.DoesNotExist:
        return JsonResponse({'error': 'Stall does not exist or is inactive'}, status=404)

    # Get the current date/time
    end_date = timezone.now().date()

    # Fetch sales data based on period (weekly, monthly, or annual)
    if period == 'weekly':
        start_date_weekly = end_date - timedelta(days=7)
        sales = SalesData.objects.filter(
            stall_name=stall, order_date__range=[start_date_weekly, end_date]  # Use 'stall_name' instead of 'stall'
        ).values('order_date').annotate(total_sales=Sum('total_amount')).order_by('order_date')
    elif period == 'monthly':
        current_month = timezone.now().month
        sales = SalesData.objects.filter(
            stall_name=stall, order_date__month=current_month  # Use 'stall_name' instead of 'stall'
        ).values('order_date__day').annotate(total_sales=Sum('total_amount')).order_by('order_date__day')
    elif period == 'annual':
        current_year = timezone.now().year
        sales = SalesData.objects.filter(
            stall_name=stall, order_date__year=current_year  # Use 'stall_name' instead of 'stall'
        ).values('order_date__month').annotate(total_sales=Sum('total_amount')).order_by('order_date__month')

    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename={stall_name}_{period}_sales.csv'
    writer = csv.writer(response)
    writer.writerow(['Date', 'Total Sales'])

    for sale in sales:
        formatted_date = sale['order_date'].strftime('%Y-%m-%d')  # Format the date
        writer.writerow([formatted_date, sale['total_sales']])

    return response

@login_required
def view_and_edit_profile(request):
    try:
        # Try to get the user's profile; if it doesn't exist, create a new one
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.save()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)  # Include request.FILES
        if form.is_valid():
            # Save the form data
            user = form.save(commit=False)
            if form.cleaned_data['password']:
                user.set_password(form.cleaned_data['password'])
                update_session_auth_hash(request, user)
            user.save()  # Save the user object

            profile = user.profile
            profile.save()  # Ensure the profile is saved

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile:view_and_edit_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'super.html', {'form': form, 'profile': profile})

logger = logging.getLogger(__name__)

@login_required
def manage_profile(request):
    try:
        # Retrieve the profile linked to the logged-in user
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        # Create a new profile if none exists
        profile = Profile(user=request.user)
        profile.save()

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            # Update the User model
            user = request.user
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.email = form.cleaned_data['email']

            # Handle password change
            password = form.cleaned_data.get('password')
            if password:
                user.set_password(password)
                update_session_auth_hash(request, user)  # Keep user logged in after password change

            user.save()

            # Update Profile model
            profile.phone = form.cleaned_data.get('phone')
            profile.address = form.cleaned_data.get('address')
            profile.birthdate = form.cleaned_data.get('birthdate')
            profile.gender = form.cleaned_data.get('gender')

            if 'profile_photo' in request.FILES:
                profile.profile_picture = request.FILES['profile_photo']

            profile.save()

            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('manage_profile')  # Reload page with updated data
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'manage_profile.html', {
        'form': form,
        'profile': profile,
        'user': request.user
    })

def inventory_list(request):
    inventory_items = Inventory.objects.all()
    return render(request, 'inventory_list.html', {'inventory_items': inventory_items})

def transaction_list(request):
    transactions = Transaction.objects.all()
    return render(request, 'transaction_list.html', {'transactions': transactions})

@login_required
def dashboard(request):
    # Dashboard for Admin - Filtered by Stall
    stall = request.user.stall  # assuming the user has a stall attribute
    inventory_items = Inventory.objects.filter(stall=stall)
    sales_reports = SalesReport.objects.filter(stall=stall)

    # Show monthly sales
    month_sales = SalesReport.objects.filter(stall=stall, report_date__month=datetime.now().month)
    
    return render(request, 'dashboard.html', {
        'inventory_items': inventory_items,
        'sales_reports': sales_reports,
        'month_sales': month_sales,
    })

def download_report(request, period):
    # Example: Download report based on the selected period (daily, monthly, yearly)
    if period == 'daily':
        date_filter = datetime.today().date()
    elif period == 'monthly':
        date_filter = datetime.today().replace(day=1)
    elif period == 'yearly':
        date_filter = datetime.today().replace(month=1, day=1)

    # Query for sales reports based on period
    sales_reports = SalesReport.objects.filter(report_date__gte=date_filter)
    
    # Create a CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sales_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Stall', 'Date', 'Total Sales'])

    for report in sales_reports:
        writer.writerow([report.stall, report.report_date, report.total_sales])

    return 

def submit_contact_form(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process form data
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            # Example: Save to database or send an email
            # send_mail(subject, message, email, ['admin@example.com'])

            return HttpResponse("Thank you for contacting us!")
    else:
        form = ContactForm()

    return render(request, "submit_contact_form.html", {"form": form})


# Transaction view
def stall_transactions(request, stall_id):
    stall = Stall.objects.get(id=stall_id)
    transactions = Transaction.objects.filter(stall=stall).order_by('-date')

    return render(request, 'transactions.html', {
        'stall': stall,
        'transactions': transactions,
    })
    
def download_transactions(request):
    stall_id = request.GET.get('stall_id')  # Get stall ID from query parameter
    download_format = request.GET.get('format')  # Get the file format (csv, txt, pdf, image)
    
    if not stall_id:
        return HttpResponse("Stall ID is required.", status=400)
    
    try:
        stall = Stall.objects.get(id=stall_id)  # Fetch the stall
    except Stall.DoesNotExist:
        return HttpResponse("Stall matching query does not exist.", status=404)
    
    # Get the current time and the time 24 hours ago
    now = timezone.now()
    last_24_hours = now - timedelta(hours=24)

    # Filter transactions for the specific stall and within the last 24 hours
    transactions = Transaction.objects.filter(stall_name_id=stall.id, order_date__gte=last_24_hours)

    # Handle CSV download
    if download_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
        writer = csv.writer(response)
        writer.writerow(['UBTransactID', 'Date', 'Description', 'Size', 'Quantity', 'Total Price'])  # Header row
        for transaction in transactions:
            writer.writerow([transaction.ubtransact_id, transaction.order_date, transaction.description,
                             transaction.size, transaction.quantity, f"₱{transaction.total_price:,.2f}"])
        return response

    # Handle TXT download
    elif download_format == 'txt':
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="transactions.txt"'
        response.write("Transactions Report\n" + "=" * 50 + "\n")
        response.write("UBTransactID    Date    Description    Size    Quantity    Total Price\n")
        response.write("-" * 50 + "\n")
        for transaction in transactions:
            response.write(f"UBTransactID: {transaction.ubtransact_id}\n")
            response.write(f"Date: {transaction.order_date}\n")
            response.write(f"Description: {transaction.description}\n")
            response.write(f"Size: {transaction.size}\n")
            response.write(f"Quantity: {transaction.quantity}\n")
            response.write(f"Total Price: ₱{transaction.total_price:,.2f}\n")
            response.write("-" * 50 + "\n")
        return response

    # Handle PDF download
    elif download_format == 'pdf':
        buffer = BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        y_position = height - 40  # Starting Y position for writing
        p.setFont("Helvetica-Bold", 14)
        p.drawString(100, y_position, "Transactions Report")
        y_position -= 20
        p.setFont("Helvetica", 10)
        p.drawString(100, y_position, "UBTransactID    Date    Description    Size    Quantity    Total Price")
        y_position -= 20

        for transaction in transactions:
            p.drawString(100, y_position, f"{transaction.ubtransact_id}    {transaction.order_date}    {transaction.description}    {transaction.size}    {transaction.quantity}    ₱{transaction.total_price:,.2f}")
            y_position -= 20
            if y_position < 40:
                p.showPage()
                p.setFont("Helvetica", 10)
                y_position = height - 40

        p.showPage()
        p.save()
        buffer.seek(0)

        # Save PDF file to media directory
        file_name = "transactions.pdf"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        with open(file_path, 'wb') as f:
            f.write(buffer.read())

        # Provide URL for the file
        file_url = os.path.join(settings.MEDIA_URL, file_name)

        # Pass file URL to the report page
        return redirect('report', file_url=file_url, file_type='pdf')

    # Handle Image download
    elif download_format == 'image':
        image_width = 800
        image_height = 50 + len(transactions) * 30  # Adjust height based on number of transactions
        image = Image.new('RGB', (image_width, image_height), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()

        header_text = "UBTransactID    Date    Description    Size    Quantity    Total Price"
        draw.text((10, 10), header_text, fill="black", font=font)

        y_position = 40
        for transaction in transactions:
            transaction_text = f"{transaction.ubtransact_id}    {transaction.order_date}    {transaction.description}    {transaction.size}    {transaction.quantity}    ₱{transaction.total_price:,.2f}"
            draw.text((10, y_position), transaction_text, fill="black", font=font)
            y_position += 30

        # Save Image to media directory
        file_name = "transactions.png"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)
        image.save(file_path)

        # Provide URL for the file
        file_url = os.path.join(settings.MEDIA_URL, file_name)

        # Pass file URL to the report page
        return redirect('report', file_url=file_url, file_type='image')

    return HttpResponse("Invalid format", status=400)

def get_stall_id(request):
    print("Retrieving stall ID from request...")  # Debug log
    # First, try to get the stall_id from the POST data
    stall_id = request.POST.get('stall_id')

    # If stall_id is not in the POST data, attempt to get it from the session (if the user is logged in)
    if not stall_id:
        stall_id = request.session.get('stall_id')

    # If we still can't find the stall_id, return None or an error message
    if not stall_id or not stall_id.isdigit():
        return None, "Invalid stall ID received."
    
    return int(stall_id), None  # Ensure stall_id is returned as an integer

def pos(request):
    # Fetch products grouped by category
    categories = Product.CATEGORY_CHOICES
    products_by_category = {
        category[0]: Product.objects.filter(category=category[0], quantity__gt=0)
        for category in categories
    }
    return render(request, 'pos.html', {'products_by_category': products_by_category})

@csrf_exempt
def process_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cart = data.get('cart', [])
            stall_id = data.get('stall_id')
            order_date = data.get('order_date')
            total_price = data.get('total_price')

            # Generate unique transaction ID
            ubtransact_id = f"UBT-{int(time.time())}"

            # Create the transaction
            transaction = Transaction.objects.create(
                ubtransact_id=ubtransact_id,
                order_date=order_date,
                description="Order from POS",
                total_price=total_price,
                stall_name_id=stall_id,
            )

            # Update product quantities based on the cart
            for item in cart:
                product = Product.objects.get(id=item['product_id'])
                quantity = item['quantity']

                # Reduce product stock
                if product.quantity >= quantity:
                    product.quantity -= quantity
                    product.save()
                else:
                    return JsonResponse({'success': False, 'error': f"Insufficient stock for {product.item_name}"})

            return JsonResponse({'success': True, 'transaction_id': transaction.ubtransact_id})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})
