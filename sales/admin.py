from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Customer, SalesInvoice, SalesInvoiceLine, 
    CustomerPayment, SalesReturn, SalesReturnLine
)

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'phone', 'get_balance_display', 'credit_limit', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'phone', 'email')
    ordering = ('code',)
    readonly_fields = ('current_balance', 'created_at', 'updated_at')

    fieldsets = (
        ('معلومات العميل', {
            'fields': (('code', 'name'), ('phone', 'mobile'), 'email')
        }),
        ('معلومات الحساب', {
            'fields': ('account', 'credit_limit', 'current_balance', 'discount_percentage')
        }),
        ('معلومات إضافية', {
            'fields': ('contact_person', 'address', 'tax_number', 'notes', 'is_active'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_balance_display(self, obj):
        color = 'red' if obj.current_balance > 0 else 'green'
        return format_html(
            '<span style="color: {};">{:.2f} ج.م</span>',
            color,
            abs(obj.current_balance)
        )
    get_balance_display.short_description = 'الرصيد'

class SalesInvoiceLineInline(admin.TabularInline):
    model = SalesInvoiceLine
    extra = 0
    fields = ('product', 'quantity', 'unit_price', 'tax_rate', 'discount_amount', 'total')
    readonly_fields = ('total',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('product')

@admin.register(SalesInvoice)
class SalesInvoiceAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'customer', 'total_amount', 'status', 'created_by')
    list_filter = ('status', 'date')
    search_fields = ('number', 'customer__name', 'notes')
    ordering = ('-date', '-number')
    readonly_fields = ('subtotal', 'total_amount', 'created_by', 'created_at', 'updated_at')
    inlines = [SalesInvoiceLineInline]
    date_hierarchy = 'date'

    fieldsets = (
        ('معلومات الفاتورة', {
            'fields': (('number', 'date'), 'customer', 'due_date')
        }),
        ('القيم المالية', {
            'fields': (('subtotal', 'tax_amount'), ('discount_amount', 'total_amount'))
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'status')
        }),
        ('معلومات النظام', {
            'fields': (('created_by', 'created_at'), 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

class SalesReturnLineInline(admin.TabularInline):
    model = SalesReturnLine
    extra = 0
    fields = ('invoice_line', 'quantity', 'unit_price', 'total')
    readonly_fields = ('unit_price', 'total')

@admin.register(SalesReturn)
class SalesReturnAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'customer', 'invoice', 'total_amount', 'status')
    list_filter = ('status', 'date')
    search_fields = ('number', 'customer__name', 'invoice__number')
    ordering = ('-date', '-number')
    readonly_fields = ('total_amount', 'created_by', 'created_at', 'updated_at')
    inlines = [SalesReturnLineInline]
    date_hierarchy = 'date'

    fieldsets = (
        ('معلومات المرتجع', {
            'fields': (('number', 'date'), ('customer', 'invoice'))
        }),
        ('تفاصيل المرتجع', {
            'fields': ('reason', 'total_amount')
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'status')
        }),
        ('معلومات النظام', {
            'fields': (('created_by', 'created_at'), 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(CustomerPayment)
class CustomerPaymentAdmin(admin.ModelAdmin):
    list_display = ('number', 'date', 'customer', 'amount', 'payment_method', 'status')
    list_filter = ('status', 'payment_method', 'date')
    search_fields = ('number', 'customer__name', 'reference')
    ordering = ('-date', '-number')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    date_hierarchy = 'date'

    fieldsets = (
        ('معلومات السند', {
            'fields': (('number', 'date'), 'customer')
        }),
        ('تفاصيل الدفع', {
            'fields': ('amount', 'payment_method', 'reference')
        }),
        ('معلومات إضافية', {
            'fields': ('notes', 'status')
        }),
        ('معلومات النظام', {
            'fields': (('created_by', 'created_at'), 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
