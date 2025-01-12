import datetime
import matplotlib.pyplot as plt
import io
from django.contrib.auth.hashers import make_password 
from django.urls import reverse
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from django.http import JsonResponse
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponse
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
from .models import SalesData, Transaction, Item, Supplier, Employee, Admin, Report
from .forms import ReportForm, EmployeeForm
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from datetime import timedelta

def home(request):
    return render(request, 'home.html')

def employee(request):
    return render(request, 'employee.html')

def log_in(request):
    error_message = None
    next_url = request.GET.get('next', '/')
    user_type = request.GET.get('user_type', 'employee')  # Default to employee login

    if request.method == 'POST':
        password = request.POST.get('password')
        
        if user_type == 'employee':
            # Employee login logic
            email = request.POST.get('email_address')
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')

            try:
                employee = Employee.objects.get(email_address=email, first_name=first_name, last_name=last_name)
                if check_password(password, employee.password):
                    request.session['employee_id'] = employee.id
                    return redirect('monthly_total_sales')
                else:
                    error_message = "Invalid credentials for employee."
            except Employee.DoesNotExist:
                error_message = "Employee with these details does not exist."

        elif user_type == 'admin':
            # Admin login using superadmin-created account
            username = request.POST.get('username')
            try:
                admin_user = Admin.objects.get(username=username)
                if admin_user.password == password:  # Assuming passwords are stored in plaintext (not recommended)
                    request.session['admin_id'] = admin_user.id
                    messages.success(request, f"Welcome {admin_user.firstname} in {admin_user.stall_name}")
                    return redirect(next_url if next_url != '/' else 'home')
                else:
                    error_message = "Invalid admin credentials."
            except Admin.DoesNotExist:
                error_message = "Admin with this username does not exist."

        elif user_type == 'superadmin':
            # SuperAdmin login using Django's admin account
            username = request.POST.get('username')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_superuser:
                login(request, user)
                return redirect(next_url if next_url != '/' else 'home')
            else:
                error_message = "Invalid superadmin credentials."

    return render(request, 'log_in.html', {'error_message': error_message, 'user_type': user_type})

def transactions_view(request):
    now = timezone.now()
    last_24_hours = now - timedelta(hours=24)
    
    # Filter transactions from the last 24 hours
    transactions = Transaction.objects.filter(order_date__gte=last_24_hours)
    
    # Calculate total sales for the last 24 hours
    total_sales = transactions.aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    return render(request, 'transaction.html', {
        'transactions': transactions,
        'total_sales': total_sales
    })
    
@csrf_exempt
def save_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")  # Log received data
            transaction = Transaction(
                ubtransact_id=data['ubtransact_id'],
                order_date=timezone.now(),
                description=data['description'],
                size=data['size'],
                quantity=data['quantity'],
                total_price=data['total_price']
            )
            transaction.save()
            print(f"Transaction saved: {transaction}")  
            return JsonResponse({'success': True})
        except Exception as e:
            print(f"Error saving transaction: {e}")
            return JsonResponse({'success': False})
    return JsonResponse({'success': False})

@csrf_exempt
def process_order(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"Received order data: {data}")  # Log incoming data

            # Check if all required fields are present
            if not all(key in data for key in ('ubtransact_id', 'description', 'size', 'quantity', 'total_price')):
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)

            # Create transaction
            transaction = Transaction.objects.create(
                ubtransact_id=data['ubtransact_id'],
                order_date=timezone.now(),
                description=data['description'],
                size=data['size'],
                quantity=data['quantity'],
                total_price=data['total_price']
            )

            print(f"Transaction created: {transaction}")  

            return JsonResponse({'success': True, 'transaction_id': transaction.ubtransact_id})

        except Exception as e:
            print(f"Error processing order: {str(e)}")  
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


@login_required
def monthly_total_sales(request):
    # Query for monthly sales data
    monthly_sales = SalesData.objects.annotate(
        month=ExtractMonth('order_date')
    ).values('month').annotate(
        total_amount=Sum('total_amount')
    ).order_by('month')

    # Prepare data for the bar chart
    months = [item['month'] for item in monthly_sales]
    totals = [item['total_amount'] for item in monthly_sales]

    # Create a bar chart using matplotlib
    fig, ax = plt.subplots()
    ax.bar(months, totals, color='blue')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Sales Amount')
    ax.set_title('Monthly Total Sales')

    # Save the plot to a BytesIO object and encode it in base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    # Render the graph in the template
    return render(request, 'monthly_total_sales.html', {'graph': img_str})

@login_required
def yummy_mango(request):
    return render(request, 'yummy_mango.html')

@login_required
def cravers_haven(request):
    return render(request, 'cravers_haven.html')

@login_required
def uncle_brew(request):
    return render(request, 'uncle_brew.html')

@login_required
def sealog_bbq(request):
    return render(request, 'sealog_bbq.html')

@login_required
def bja_lechon(request):
    return render(request, 'bja_lechon.html')

@login_required
def tusok_tusok(request):
    return render(request, 'tusok_tusok.html')


@login_required
def cravers(request):
    try:
        transactions = Transaction.objects.filter(stall_name='Cravers Haven', order_date__gte=datetime.date.today())
        transaction_data = [{
            'ubtransact_id': transaction.ubtransact_id,
            'order_date': transaction.order_date,
            'desc': transaction.desc,
            'size': transaction.size,
            'quantity': transaction.quantity,
            'total_price': transaction.total_price,
        } for transaction in transactions]
        return render(request, 'cravers.html', {'transactions_cravers': transaction_data})
    except Exception as e:
        # Log the exception here
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def uncle(request):
    try:
        transactions = Transaction.objects.filter(stall_name='Uncle Brew', order_date__gte=datetime.date.today())
        transaction_data = [{
            'ubtransact_id': transaction.ubtransact_id,
            'order_date': transaction.order_date,
            'desc': transaction.desc,
            'size': transaction.size,
            'quantity': transaction.quantity,
            'total_price': transaction.total_price,
        } for transaction in transactions]
        return render(request, 'uncle.html', {'transactions_uncle': transaction_data})
    except Exception as e:
        # Log the exception here
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def sealog(request):
    try:
        transactions = Transaction.objects.filter(stall_name='Sealog BBQ', order_date__gte=datetime.date.today())
        transaction_data = [{
            'ubtransact_id': transaction.ubtransact_id,
            'order_date': transaction.order_date,
            'desc': transaction.desc,
            'size': transaction.size,
            'quantity': transaction.quantity,
            'total_price': transaction.total_price,
        } for transaction in transactions]
        return render(request, 'sealog.html', {'transactions_sealog': transaction_data})
    except Exception as e:
        # Log the exception here
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def lechon(request):
    try:
        transactions = Transaction.objects.filter(stall_name='BJA Lechon', order_date__gte=datetime.date.today())
        transaction_data = [{
            'ubtransact_id': transaction.ubtransact_id,
            'order_date': transaction.order_date,
            'desc': transaction.desc,
            'size': transaction.size,
            'quantity': transaction.quantity,
            'total_price': transaction.total_price,
        } for transaction in transactions]
        return render(request, 'lechon.html', {'transactions_lechon': transaction_data})
    except Exception as e:
        # Log the exception here
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def tusok(request):
    try:
        transactions = Transaction.objects.filter(stall_name='Tusok Tusok', order_date__gte=datetime.date.today())
        transaction_data = [{
            'ubtransact_id': transaction.ubtransact_id,
            'order_date': transaction.order_date,
            'desc': transaction.desc,
            'size': transaction.size,
            'quantity': transaction.quantity,
            'total_price': transaction.total_price,
        } for transaction in transactions]
        return render(request, 'tusok.html', {'transactions_tusok': transaction_data})
    except Exception as e:
        # Log the exception here
        return HttpResponse(f'Error: {e}', status=500)
    
@login_required
def report(request):
    if request.method == 'POST':
        form = ReportForm(request.POST, request.FILES)
        if form.is_valid():
            report_instance = form.save(commit=False)  # Create report instance but don't save it yet
            report_instance.submitted_by = request.user  # Assign the current user
            report_instance.save()  # Now save the report instance
            
            # Return a success message
            return JsonResponse({'success': True, 'message': "Your report has been submitted successfully!"})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

    else:
        form = ReportForm()
    
    return render(request, 'report.html', {'form': form})

def report_list(request):
    reports = Report.objects.all().order_by('-submitted_at')  
    return render(request, 'report_list.html', {'reports': reports})


def clear_transaction(request):
    Transaction.objects.filter(order_date__lt=datetime.date.today()).delete()
    return HttpResponse('Transactions cleared')

@login_required
def graph(request):
    monthly_sales = SalesData.objects.annotate(
        month=ExtractMonth('order_date')
    ).values('month').annotate(
        total_amount=Sum('total_amount')
    ).order_by('month')

    # Check if data exists
    if not monthly_sales.exists():
        return render(request, 'admin_graph.html', {'error': 'No sales data available'})

    months = [item['month'] for item in monthly_sales]
    totals = [item['total_amount'] for item in monthly_sales]

    # Create bar chart using matplotlib
    fig, ax = plt.subplots()
    ax.bar(months, totals, color='brown')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Sales Amount')
    ax.set_title('Monthly Total Sales')

    # Convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')
    buffer.close()

    return render(request, 'admin_graph.html', {'graph': img_str})


def employees(request):
    form = EmployeeForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            return redirect('emp_success') 
    return render(request, 'emp_records.html', {'form': form})

def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('emp_success')  
    else:
        form = EmployeeForm()
    return render(request, 'employee_create.html', {'form': form})

def emp_success(request):
    employees = Employee.objects.all()  
    return render(request, 'emp_success.html', {'employees': employees})

def sales_data(request):
    # Monthly sales data
    monthly_sales = (
        SalesData.objects.values('stall_name', 'order_date__year', 'order_date__month')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('order_date__year', 'order_date__month')
    )

    # Annual sales data
    annual_sales = (
        SalesData.objects.values('stall_name', 'order_date__year')
        .annotate(total_sales=Sum('total_amount'))
        .order_by('order_date__year')
    )

    monthly_data = {}
    for sale in monthly_sales:
        stall = sale['stall_name']
        month = f"{sale['order_date__year']}-{sale['order_date__month']:02d}"
        if stall not in monthly_data:
            monthly_data[stall] = {'labels': [], 'sales': []}
        monthly_data[stall]['labels'].append(month)
        monthly_data[stall]['sales'].append(float(sale['total_sales']))

    annual_data = {}
    for sale in annual_sales:
        stall = sale['stall_name']
        year = sale['order_date__year']
        if stall not in annual_data:
            annual_data[stall] = {'labels': [], 'sales': []}
        annual_data[stall]['labels'].append(str(year))
        annual_data[stall]['sales'].append(float(sale['total_sales']))

    return JsonResponse({'monthly': monthly_data, 'annual': annual_data})

def supreg(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        age = request.POST.get('age')
        middle_initial = request.POST.get('middle_initial')
        birthdate = request.POST.get('birthdate')
        lastname = request.POST.get('lastname')
        address = request.POST.get('address')
        username = request.POST.get('username')
        contact_number = request.POST.get('contact_number')
        password = request.POST.get('password')
        stallname = request.POST.get('stallname')

        # Check if an admin already exists for the selected stall
        if Admin.objects.filter(stall_name=stallname).exists():
            messages.error(request, f"An admin for '{stallname}' already exists.")
            return redirect('supreg')

        # Hash the password for secure storage
        hashed_password = make_password(password)

        # Create and save the admin instance
        admin = Admin(
            firstname=firstname,
            age=age,
            middle_initial=middle_initial,
            birthdate=birthdate,
            lastname=lastname,
            address=address,
            username=username,
            contact_number=contact_number,
            password=hashed_password,  # Store hashed password
            stall_name=stallname
        )
        admin.save()
        
        # Add a success message
        messages.success(request, f"Admin for '{stallname}' registered successfully.")
        return redirect('adminrec')  # Redirect to the admin records page

    return render(request, 'supreg.html')

def adminrec(request):
    admins = Admin.objects.all()  
    return render(request, 'adminrec.html', {'admins': admins})

def edit_admin(request, admin_id):
    # Fetch the admin record based on the provided ID
    admin = get_object_or_404(Admin, id=admin_id)

    if request.method == 'POST':
        # Update admin details with form data
        admin.firstname = request.POST.get('firstname')
        admin.age = request.POST.get('age')
        admin.middle_initial = request.POST.get('middle_initial')
        admin.birthdate = request.POST.get('birthdate')
        admin.lastname = request.POST.get('lastname')
        admin.address = request.POST.get('address')
        admin.username = request.POST.get('username')
        admin.contact_number = request.POST.get('contact_number')
        admin.password = request.POST.get('password')
        admin.stall_name = request.POST.get('stallname')
        admin.save()  # Save changes to the database

        messages.success(request, 'Admin details updated successfully!')
        return redirect('adminrec')  # Redirect to admin records page after update

    # Render the edit admin page with existing admin data
    return render(request, 'edit_admin.html', {'admin': admin})

def delete_admin(request, id):
    admin = get_object_or_404(Admin, id=id)
    admin.delete()
    messages.success(request, 'Admin deleted successfully!')  
    return redirect('adminrec')

def view_item(request):
    items = Item.objects.all()  
    return render(request, 'view_item.html', {'items': items})

@csrf_exempt  
def save_item(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) 

           
            supplier_name = data.get('supplier_name')
            contact_name = data.get('contact_name')
            contact_number = data.get('contact_number')
            address = data.get('address')
            email = data.get('email')

            
            supplier, created = Supplier.objects.get_or_create(
                name=supplier_name,
                defaults={
                    'contact_name': contact_name,
                    'contact_number': contact_number,
                    'address': address,
                    'email': email,
                }
            )

           
            item_name = data.get('item_name')
            category = data.get('category')
            price = data.get('price')
            expiration_date = data.get('expiration_date')

           
            item = Item.objects.create(
                name=item_name,
                category=category,
                price=price,
                expiration_date=expiration_date,
                supplier=supplier
            )

            return JsonResponse({'message': 'Item saved successfully!'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Only POST requests are allowed.'}, status=405)


def update_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    
    if request.method == 'POST':
        supplier_name = request.POST.get('name', supplier.name)  # Use current value if not provided
        contact_name = request.POST.get('contact_name', supplier.contact_name)
        contact_number = request.POST.get('contact_number', supplier.contact_number)
        address = request.POST.get('address', supplier.address)
        email = request.POST.get('email', supplier.email)
        
        # Only update if supplier_name and email are provided
        if supplier_name and email: 
            supplier.name = supplier_name
            supplier.contact_name = contact_name
            supplier.contact_number = contact_number
            supplier.address = address
            supplier.email = email
            supplier.save()
            return redirect('inventory')  # Redirect to the inventory page after updating
    
    # Pre-fill form with existing supplier data
    return render(request, 'inventory.html', {
        'supplier': supplier,
        'item': None,  
    })

def delete_supplier(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    supplier.delete()
    return redirect('view_supplier')  

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

def update_item(request, id):
    item = get_object_or_404(Item, id=id)
    
    if request.method == 'POST':
        item_name = request.POST.get('name')
        price = request.POST.get('price')
        category = request.POST.get('category')
        expiration_date = request.POST.get('expiration_date')
        
        if item_name and price and expiration_date:  # Basic validation
            item.name = item_name
            item.price = price
            item.category = category
            item.expiration_date = expiration_date
            item.save()
            return redirect('inventory')  # Redirect to the inventory page after updating
    
    # Render the inventory template with the existing item data to pre-fill the form
    return render(request, 'inventory.html', {
        'item': item,
        'supplier': None,  # Passing None for supplier in this case since it's only item being updated
    })


# Delete Item
def delete_item(request, id):
    item = get_object_or_404(Item, id=id)
    item.delete()
    return redirect('view_item')  # Replace with your item list URL


@login_required
def inventory(request):
    if request.method == 'POST':
        item_name = request.POST.get('item_name')
        price = request.POST.get('price')
        category = request.POST.get('category')
        expiration_date = request.POST.get('expiration_date')
        supplier_name = request.POST.get('supplier_name')
        contact_name = request.POST.get('contact_name')
        contact_number = request.POST.get('contact_number')
        address = request.POST.get('address')
        email = request.POST.get('email')

        supplier, created = Supplier.objects.get_or_create(
            name=supplier_name,
            defaults={'contact_name': contact_name, 'contact_number': contact_number, 'address': address, 'email': email}
        )

        item = Item.objects.create(
            name=item_name,
            price=price,
            category=category,
            expiration_date=expiration_date,
            supplier=supplier
        )
        return redirect('inventory')

    items = Item.objects.all()
    context = {
        'items': items,
    }
    return render(request, 'inventory.html', context)



@login_required
def view_supplier(request):
    suppliers = Supplier.objects.all()  
    return render(request, 'view_supplier.html', {'suppliers': suppliers})

@login_required
def superadmin_dashboard(request):
    return render(request, 'super.html')


def user(request):
    return render(request, 'user.html')

def about(request):
    return render(request, 'about.html')

def search_item(request):
    search_term = request.POST.get('search_term')
    item = Item.objects.filter(name__icontains=search_term).first()
    if item:
        return JsonResponse({'item_found': True, 'item_name': item.name, 'supplier_name': item.supplier.name})
    else:
        return JsonResponse({'item_found': False})

