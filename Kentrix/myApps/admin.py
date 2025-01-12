from django.contrib import admin
from .models import Transaction, Employee, Supplier, SalesData, Report

# Register your models here.

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ubtransact_id', 'order_date', 'description', 'size', 'quantity', 'total_price')
    search_fields = ('ubtransact_id', 'description')
    list_filter = ('order_date',)
    ordering = ('-order_date',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'position', 'birthdate')
    search_fields = ('firstname', 'lastname')
    list_filter = ('position', 'birthdate')

class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_name', 'contact_number', 'email')
    search_fields = ('name', 'contact_name')
    list_filter = ('name',)

class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('order_date', 'total_amount')
    search_fields = ('order_date',)
    list_filter = ('order_date',)

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted_at', 'file')
    search_fields = ('title',)
    list_filter = ('submitted_at',)

admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(SalesData, SalesDataAdmin)
admin.site.register(Report, ReportAdmin)
