from django.urls import path
from . import views
from .views import daily_sales_report, print_daily_sales_report
app_name = 'pos_system'

urlpatterns = [
    path('', views.pos_dashboard, name='pos_dashboard'),
    path('transaction/new/', views.create_transaction, name='create_transaction'),
    path('transaction/<int:pk>/', views.transaction_detail, name='transaction_detail'),
    path('transaction/<int:pk>/add_item/', views.add_transaction_item, name='add_transaction_item'),
    path('reports/', views.transaction_report, name='transaction_report'),
    path('reports/daily-sales/', views.daily_sales_report, name='daily_sales_report'),  # Daily Sales Report
    path('reports/customer-debt/', views.customer_debt_report, name='customer_debt_report'),  # Customer Debt Report
    path('reports/sold-items/', views.sold_item_report, name='sold_item_report'),  # Sold Item-Wise Report
    path('customers/', views.customer_list, name='customer_list'),
    path('customers/new/', views.customer_create, name='customer_create'),
    path('customers/<int:pk>/edit/', views.customer_update, name='customer_update'),
    path('customers/<int:pk>/delete/', views.customer_delete, name='customer_delete'),
    path('customers/<int:pk>/', views.customer_detail, name='customer_detail'),  # Add this line
    path('transaction_item/<int:item_id>/remove/', views.remove_transaction_item, name='remove_transaction_item'),
    path('transaction/<int:pk>/add_transaction_log/', views.add_transaction_log, name='add_transaction_log'),
    path('login/', views.login_view, name='login'),
    path('add_item_discount/<int:item_id>/', views.add_item_discount, name='add_item_discount'),
    path('transaction/<int:pk>/receipt/', views.receipt_view, name='receipt_view'),
    path('daily_sales_report/', daily_sales_report, name='daily_sales_report'),
    path('print_daily_sales_report/<str:start_date>/<str:end_date>/', print_daily_sales_report, name='print_daily_sales_report'),



]
