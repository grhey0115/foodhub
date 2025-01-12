from django.urls import path
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('employee/', views.employee, name='employee'),
    path('log_in/', views.log_in, name='log_in'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('verify_otp/<int:user_id>/', views.verify_otp, name='verify_otp'),
    path('reset_password/<int:user_id>/', views.reset_password, name='reset_password'),
    path('monthly_total_sales/', views.monthly_total_sales, name='monthly_total_sales'),
    path('yummy_mango/', views.yummy_mango, name='yummy_mango'),
    path('pos/', views.pos, name='pos'),
    path('process-transaction/', views.process_transaction, name='process_transaction'),
    path('process_order/', views.process_order, name='process_order'),
    path('save-transaction/', views.save_transaction, name='save_transaction'),
    path('transaction_list/', views.transactions_view, name='transaction_list'),
    path('download_transactions/', views.download_transactions, name='download_transactions'),
    path('clear_transaction/', views.clear_transaction, name='clear_transaction'),
    path('admin_graph/', views.admin_graph, name='admin_graph'),
    path('add-food-item/', views.add_food_item, name='add_food_item'),
    path('add-supplier-item/', views.add_supplier_item, name='add_supplier_item'),
    path('edit_supplier/<int:supplier_id>/', views.edit_supplier, name='edit_supplier'),
    path('edit-supplier-item/<int:supplier_item_id>/', views.edit_supplier_item, name='edit_supplier_item'), 
    path('food-and-supplier-items/delete/<int:item_id>/', views.delete_food_item, name='delete_food_item'),
    path('delete_supplier_item/<int:supplier_item_id>/', views.delete_supplier_item, name='delete_supplier_item'),
    path('edit_food_item/<int:item_id>/', views.edit_food_item, name='edit_food_item'),
    path('delete_supplier/<int:supplier_id>/', views.delete_supplier, name='delete_supplier'),  
    path('food-and-supplier-items/', views.food_and_supplier_items, name='food_and_supplier_items'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('suppliers/', views.supplier_list, name='suppliers'),
    path('update-stall/<stall_id>/', views.update_stall_ajax, name='update_stall_ajax'),  
    path('delete-stall/<int:stall_id>/', views.delete_stall, name='delete-stall'), 
    path('add_product/', views.add_product, name='add_product'),
    path('employee/create/', views.employee_create, name='employee_create'),
    path('emp_records/', views.employees, name='emp_records'),
    path('employee/update/<int:emp_id>/', views.update_employee, name='update_employee'),
    path('employee/delete/<int:id>/', views.delete_employee, name='delete_employee'),
    path('emp_success/', views.emp_success, name='emp_success'),
    path('sales_data/', views.get_sales_data, name='sales_data'),
    path('export_sales_data/<str:stall_name>/<str:period>/', views.export_sales_data, name='export_sales_data'),
    path('super/', views.superadmin_dashboard, name='super'),
    path('supreg/', views.supreg, name='supreg'),
    path('adminrec/', views.adminrec, name='adminrec'),  # List all admins
    path('adminrec/<int:id>/', views.adminrec, name='adminrec_with_id'),  # View specific admin
    path('adminrec/edit/<int:admin_id>/', views.edit_admin, name='edit_admin'),
    path('adminrec/delete/<int:admin_id>/', views.delete_admin, name='delete_admin'),
    path('report/', views.report, name='report'),
    path('reports/', views.report_list, name='report_list'),
    path('delete_report/<int:report_id>/', views.delete_report, name='delete_report'),
    path('user/', views.user, name='user'),
    path('about/', views.about, name='about'),
    path('stall/', views.stall, name='stall'),
    path('manage_profile/', views.manage_profile, name='manage_profile'),
    path('inventory_list/', views.inventory_list, name='inventory_list'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('download_report/<str:period>/', views.download_report, name='download_report'),
    path('contact/', views.submit_contact_form, name='submit_contact_form'),
    
    path('get_products_for_stall/', views.get_products_for_stall, name='get_products_for_stall'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)