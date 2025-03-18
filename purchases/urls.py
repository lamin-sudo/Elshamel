from django.urls import path
from . import views

app_name = 'purchases'

urlpatterns = [
    path('invoices/', views.purchase_invoice_list, name='invoice_list'),
    path('invoices/new/', views.purchase_invoice_create, name='invoice_create'),
    path('invoices/<int:pk>/', views.purchase_invoice_detail, name='invoice_detail'),
]