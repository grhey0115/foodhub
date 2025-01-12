from django.contrib import admin
from .models import Transaction, Employee, Suplier, SalesData, Report, Stall, Product, Inventory, SalesReport, FoodItem , SupplierItem


class TransactionAdmin(admin.ModelAdmin):
    list_display = ('ubtransact_id', 'order_date', 'description', 'size', 'quantity', 'total_price')
    ordering = ('order_date',)
    list_filter = ('order_date',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'position', 'birthdate')
    search_fields = ('firstname', 'lastname')
    list_filter = ('position', 'birthdate')

@admin.register(Suplier)
class SupplierAdmin(admin.ModelAdmin):
    # Fields to display in the list view
    list_display = (
        'supplier_id', 
        'supplier_name', 
        'contact_person', 
        'contact_info', 
        'address', 
        'payment_terms', 
        'tax_information', 
        'license_number', 
        'contract_start_date', 
        'contract_end_date'
    )
    
    # Fields that are searchable
    search_fields = ('supplier_name', 'contact_person', 'contact_info', 'license_number')
    
    # Fields for filtering
    list_filter = ('contract_start_date', 'contract_end_date')
    
    # Read-only fields
    readonly_fields = ('supplier_id',)
    
    # Fields to organize in the form view
    fieldsets = (
        ('Basic Information', {
            'fields': ('supplier_id', 'supplier_name', 'contact_person', 'contact_info', 'address')
        }),
        ('Contract Details', {
            'fields': ('payment_terms', 'tax_information', 'license_number', 'contract_start_date', 'contract_end_date')
        }),
    )


@admin.register(SupplierItem)
class SupplierItemAdmin(admin.ModelAdmin):
    list_display = ('supplier', 'food_item', 'lead_time', 'minimum_order_quantity', 'price_per_unit')
    search_fields = ('supplier__supplier_name', 'food_item__item_name')

@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'category', 'stock_quantity', 'selling_price', 'stall_location', 'date_created')
    search_fields = ('item_name', 'category', 'batch_number')
    
class SalesDataAdmin(admin.ModelAdmin):
    list_display = ('order_date', 'total_amount')
    search_fields = ('order_date',)
    list_filter = ('order_date',)

class ReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'submitted_at', 'file')
    search_fields = ('title',)
    list_filter = ('submitted_at',)

@admin.register(Stall)
class StallAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name',)
    ordering = ['-created_at']

# Define the Custom Admin Site
class CustomAdminSite(admin.AdminSite):
    site_header = "Inventory Management System"
    site_title = "Admin Portal"

    def index(self, request, extra_context=None):
        user = request.user
        # Welcome message for admin users
        if user.is_authenticated and user.is_superuser:
            welcome_message = f"Welcome admin {user.first_name} to admin page"
        else:
            welcome_message = "Welcome to the Admin page"
        
        extra_context = extra_context or {}
        extra_context['welcome_message'] = welcome_message

        return super().index(request, extra_context)

# Create an instance of the custom admin site
admin_site = CustomAdminSite(name='custom_admin')

# Registering models with the custom admin site
admin_site.register(Inventory)
admin_site.register(SalesReport)
admin_site.register(Product)
admin_site.register(Transaction, TransactionAdmin)  # Register with custom admin site only

# Register other models with the default admin site (do not register Transaction here)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(SalesData, SalesDataAdmin)
admin.site.register(Report, ReportAdmin)
