from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SalesInvoice, Customer, SalesInvoiceLine
from inventory.models import Product

@login_required
def sales_invoice_list(request):
    invoices = SalesInvoice.objects.all().order_by('-date')
    context = {
        'title': 'فواتير المبيعات',
        'invoices': invoices
    }
    return render(request, 'sales/invoice_list.html', context)

@login_required
def sales_invoice_create(request):
    customers = Customer.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    context = {
        'title': 'فاتورة مبيعات جديدة',
        'customers': customers,
        'products': products
    }
    return render(request, 'sales/invoice_form.html', context)

@login_required
def sales_invoice_detail(request, pk):
    invoice = get_object_or_404(SalesInvoice, pk=pk)
    context = {
        'title': f'فاتورة مبيعات رقم {invoice.number}',
        'invoice': invoice
    }
    return render(request, 'sales/invoice_detail.html', context)
