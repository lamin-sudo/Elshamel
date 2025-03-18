from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import PurchaseInvoice, Supplier, PurchaseInvoiceLine
from inventory.models import Product

@login_required
def purchase_invoice_list(request):
    invoices = PurchaseInvoice.objects.all().order_by('-date')
    context = {
        'title': 'فواتير المشتريات',
        'invoices': invoices
    }
    return render(request, 'purchases/invoice_list.html', context)

@login_required
def purchase_invoice_create(request):
    suppliers = Supplier.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    context = {
        'title': 'فاتورة مشتريات جديدة',
        'suppliers': suppliers,
        'products': products
    }
    return render(request, 'purchases/invoice_form.html', context)

@login_required
def purchase_invoice_detail(request, pk):
    invoice = get_object_or_404(PurchaseInvoice, pk=pk)
    context = {
        'title': f'فاتورة مشتريات رقم {invoice.number}',
        'invoice': invoice
    }
    return render(request, 'purchases/invoice_detail.html', context)
