import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.http import HttpResponse
from .models import Transaction
from django.urls import reverse

def home(request):
    return render(request, 'home.html')

def employee(request):
    return render(request, 'employee.html')

def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the desired stall's page
            stall_name = request.GET.get('next')  # Get the stall name from the GET request
            if stall_name == '/yummy_mango/':
                return redirect(reverse('yummy_mango'))
            elif stall_name == '/cravers_haven/':
                return redirect(reverse('cravers_haven'))
            elif stall_name == '/uncle_brew/':
                return redirect(reverse('uncle_brew'))
            elif stall_name == '/sealog_bbq/':
                return redirect(reverse('sealog_bbq'))
            elif stall_name == '/bja_lechon/':
                return redirect(reverse('bja_lechon'))
            elif stall_name == '/tusok_tusok/':
                return redirect(reverse('tusok_tusok'))
            else:
                return redirect('home')  # Default redirect to home page
        else:
            # Handle invalid login (e.g., display an error message)
            return render(request, 'log_in.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'log_in.html')

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
def transaction(request):
    print("Transaction view called")
    try:
        transactions = Transaction.objects.filter(order_date__gte=datetime.date.today())
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'ubtransact_id': transaction.ubtransact_id,
                'order_date': transaction.order_date,
                'desc': transaction.desc,
                'size': transaction.size,
                'quantity': transaction.quantity,
                'total_price': transaction.total_price,
            })
        return render(request, 'transaction.html', {'transactions': transaction_data})
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)
    
@login_required
def cravers(request):
    print("Transaction view called for Cravers Haven")
    try:
        transactions = Transaction.objects.filter(stall_name='Cravers Haven', order_date__gte=datetime.date.today())
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'ubtransact_id': transaction.ubtransact_id,
                'order_date': transaction.order_date,
                'desc': transaction.desc,
                'size': transaction.size,
                'quantity': transaction.quantity,
                'total_price': transaction.total_price,
            })
        return render(request, 'cravers.html', {'transactions_cravers': transaction_data})
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def uncle(request):
    print("Transaction view called for Uncle Brew")
    try:
        transactions = Transaction.objects.filter(stall_name='Uncle Brew', order_date__gte=datetime.date.today())
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'ubtransact_id': transaction.ubtransact_id,
                'order_date': transaction.order_date,
                'desc': transaction.desc,
                'size': transaction.size,
                'quantity': transaction.quantity,
                'total_price': transaction.total_price,
            })
        return render(request, 'uncle.html', {'transactions_uncle': transaction_data})
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def sealog(request):
    print("Transaction view called for Sealog BBQ")
    try:
        transactions = Transaction.objects.filter(stall_name='Sealog BBQ', order_date__gte=datetime.date.today())
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'ubtransact_id': transaction.ubtransact_id,
                'order_date': transaction.order_date,
                'desc': transaction.desc,
                'size': transaction.size,
                'quantity': transaction.quantity,
                'total_price': transaction.total_price,
            })
        return render(request, 'sealog.html', {'transactions_sealog': transaction_data})
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def lechon(request):
    print("Transaction view called for BJA Lechon")
    try:
        transactions = Transaction.objects.filter(stall_name='BJA Lechon', order_date__gte=datetime.date.today())
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'ubtransact_id': transaction.ubtransact_id,
                'order_date': transaction.order_date,
                'desc': transaction.desc,
                'size': transaction.size,
                'quantity': transaction.quantity,
                'total_price': transaction.total_price,
            })
        return render(request, 'lechon.html', {'transactions_lechon': transaction_data})
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)

@login_required
def tusok(request):
    print("Transaction view called for Tusok Tusok")
    try:
        transactions = Transaction.objects.filter(stall_name='Tusok Tusok', order_date__gte=datetime.date.today())
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'ubtransact_id': transaction.ubtransact_id,
                'order_date': transaction.order_date,
                'desc': transaction.desc,
                'size': transaction.size,
                'quantity': transaction.quantity,
                'total_price': transaction.total_price,
            })
        return render(request, 'tusok.html', {'transactions_tusok': transaction_data})
    except Exception as e:
        return HttpResponse(f'Error: {e}', status=500)
    
def clear_transaction(request):
    Transaction.objects.filter(order_date__lt=datetime.date.today()).delete()
    return HttpResponse('Transactions cleared')

@login_required
def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

@login_required
def superadmin_dashboard(request):
    return render(request, 'superadmin_dashboard.html')

def process_order(request):
    if request.method == 'POST':
        return HttpResponse("Order processed successfully.")
    return HttpResponse("Invalid request method.", status=405)