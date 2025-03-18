from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import F
from inventory.models import Product
from sales.models import SalesInvoice
from purchases.models import PurchaseInvoice

@login_required
def index(request):
    """Home page view with dashboard statistics"""
    try:
        today = timezone.now().date()
        
        # Get recent invoices
        recent_sales = SalesInvoice.objects.all().order_by('-date', '-created_at')[:5]
        recent_purchases = PurchaseInvoice.objects.all().order_by('-date', '-created_at')[:5]
        
        # Calculate daily sales
        daily_sales = SalesInvoice.objects.filter(
            date=today,
            status='posted'
        ).values('total_amount')
        daily_sales_total = sum(invoice['total_amount'] for invoice in daily_sales)
        
        # Get product statistics
        total_products = Product.objects.filter(is_active=True).count()
        
        # Get low stock products (where current_stock <= min_stock)
        low_stock_products = Product.objects.filter(
            is_active=True,
            current_stock__lte=F('min_stock')
        ).count()
        
        context = {
            'title': 'لوحة التحكم',
            'recent_sales': recent_sales,
            'recent_purchases': recent_purchases,
            'daily_sales': daily_sales_total,
            'total_products': total_products,
            'low_stock_products': low_stock_products,
        }
    except Exception as e:
        # Log the error in production
        print(f"Error in dashboard view: {e}")
        context = {
            'title': 'لوحة التحكم',
            'recent_sales': [],
            'recent_purchases': [],
            'daily_sales': 0,
            'total_products': 0,
            'low_stock_products': 0,
            'error_message': 'حدث خطأ في تحميل البيانات. الرجاء المحاولة مرة أخرى.'
        }
    
    return render(request, 'index.html', context)