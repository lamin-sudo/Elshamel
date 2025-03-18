from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('invoices/', views.sales_invoice_list, name='invoice_list'),
    path('invoices/new/', views.sales_invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.sales_invoice_detail, name='invoice_detail'),
]