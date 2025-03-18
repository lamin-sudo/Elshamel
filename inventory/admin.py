from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, Warehouse, StockMovement, Stocktaking, StocktakingLine

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'parent', 'is_active')
    list_filter = ('is_active', 'parent')
    search_fields = ('code', 'name')
    ordering = ('code',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('معلومات التصنيف', {
            'fields': ('code', 'name', 'parent')
        }),
        ('معلومات إضافية', {
            'fields': ('description', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'category', 'get_stock_status', 'sale_price', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'name', 'barcode')
    ordering = ('code',)
    readonly_fields = ('current_stock', 'created_at', 'updated_at')
    
    fieldsets = (
        ('معلومات المنتج', {
            'fields': (('code', 'barcode'), 'name', 'category', 'unit')
        }),
        ('معلومات الأسعار', {
            'fields': (('purchase_price', 'sale_price'),)
        }),
        ('معلومات المخزون', {
            'fields': (('current_stock', 'min_stock'),)
        }),
        ('معلومات إضافية', {
            'fields': ('description', 'image', 'is_active'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_stock_status(self, obj):
        if obj.current_stock <= 0:
            color = 'red'
            status = 'نفذ المخزون'
        elif obj.current_stock <= obj.min_stock:
            color = 'orange'
            status = 'منخفض'
        else:
            color = 'green'
            status = 'متوفر'
        
        return format_html(
            '<span style="color: {};">{} ({})</span>',
            color,
            obj.current_stock,
            status
        )
    get_stock_status.short_description = 'المخزون'

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'manager', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name', 'location')
    ordering = ('code',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('معلومات المخزن', {
            'fields': ('code', 'name', 'manager')
        }),
        ('معلومات إضافية', {
            'fields': ('location', 'is_active')
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class StocktakingLineInline(admin.TabularInline):
    model = StocktakingLine
    extra = 0
    fields = ('product', 'expected_quantity', 'actual_quantity', 'difference', 'notes')
    readonly_fields = ('difference',)

@admin.register(Stocktaking)
class StocktakingAdmin(admin.ModelAdmin):
    list_display = ('date', 'warehouse', 'status', 'created_by')
    list_filter = ('status', 'warehouse')
    search_fields = ('warehouse__name',)
    ordering = ('-date',)
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    inlines = [StocktakingLineInline]
    date_hierarchy = 'date'

    fieldsets = (
        ('معلومات الجرد', {
            'fields': ('date', 'warehouse', 'status')
        }),
        ('معلومات إضافية', {
            'fields': ('notes',)
        }),
        ('معلومات النظام', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ('date', 'product', 'warehouse', 'movement_type', 'quantity', 'unit_price', 'reference')
    list_filter = ('date', 'movement_type', 'reason', 'warehouse')
    search_fields = ('reference', 'product__name', 'notes')
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_by', 'created_at')
    date_hierarchy = 'date'

    fieldsets = (
        ('معلومات الحركة', {
            'fields': ('date', 'product', 'warehouse')
        }),
        ('تفاصيل الحركة', {
            'fields': ('movement_type', 'reason', 'quantity', 'unit_price')
        }),
        ('معلومات إضافية', {
            'fields': ('reference', 'notes')
        }),
        ('معلومات النظام', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
