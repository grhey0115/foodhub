from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('employee/', views.employee, name='employee'),
    path('log_in/', views.log_in, name='log_in'),
    path('yummy_mango/', views.yummy_mango, name='yummy_mango'),
    path('cravers_haven/', views.cravers_haven, name='cravers_haven'),
    path('uncle_brew/', views.uncle_brew, name='uncle_brew'),
    path('sealog_bbq/', views.sealog_bbq, name='sealog_bbq'),
    path('bja_lechon/', views.bja_lechon, name='bja_lechon'),
    path('tusok_tusok/', views.tusok_tusok, name='tusok_tusok'),
    path('transaction/', views.transaction, name='transaction'),
    path('cravers/', views.cravers, name='cravers'),
    path('uncle/', views.uncle, name='uncle'),
    path('sealog/', views.sealog, name='sealog'),
    path('lechon/', views.lechon, name='lechon'),
    path('tusok/', views.tusok, name='tusok'),
    path('clear_transaction/', views.clear_transaction, name='clear_transaction'),
    path('admin_dashboard/', views.admin_dashboard, name='admin-dashboard'),
    path('superadmin_dashboard/', views.superadmin_dashboard, name='superadmin-dashboard'),
    path('process_order/', views.process_order, name='process_order'),
]