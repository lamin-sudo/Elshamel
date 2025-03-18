from django.contrib import admin
from django.utils.html import format_html
from .models import AccountType, Account, JournalEntry, FiscalYear, FinancialStatement

@admin.register(AccountType)
class AccountTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'description')
    search_fields = ('code', 'name')
    ordering = ('code',)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'type', 'get_balance_display', 'parent', 'is_active')
    list_filter = ('type', 'is_active')
    search_fields = ('code', 'name')
    ordering = ('code',)
    readonly_fields = ('balance', 'created_at', 'updated_at')
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('code', 'name', 'type', 'parent')
        }),
        ('معلومات الرصيد', {
            'fields': ('balance', 'normal_balance')
        }),
        ('معلومات إضافية', {
            'fields': ('description', 'is_active'),
            'classes': ('collapse',)
        }),
        ('معلومات النظام', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def get_balance_display(self, obj):
        color = 'red' if obj.balance < 0 else 'green'
        return format_html(
            '<span style="color: {};">{:.2f} ج.م</span>',
            color,
            abs(obj.balance)
        )
    get_balance_display.short_description = 'الرصيد'

@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = ('date', 'account', 'entry_type', 'amount', 'reference', 'created_by')
    list_filter = ('date', 'entry_type', 'created_by')
    search_fields = ('reference', 'description', 'account__name')
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_by', 'created_at', 'updated_at')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('معلومات القيد', {
            'fields': ('date', 'account', 'entry_type', 'amount')
        }),
        ('تفاصيل القيد', {
            'fields': ('description', 'reference')
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

@admin.register(FiscalYear)
class FiscalYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_closed')
    list_filter = ('is_closed',)
    search_fields = ('name',)
    ordering = ('-start_date',)
    readonly_fields = ('is_closed',)

    fieldsets = (
        ('معلومات السنة المالية', {
            'fields': ('name', 'start_date', 'end_date')
        }),
        ('الحالة', {
            'fields': ('is_closed', 'notes')
        }),
    )

@admin.register(FinancialStatement)
class FinancialStatementAdmin(admin.ModelAdmin):
    list_display = ('get_type_display', 'fiscal_year', 'date', 'generated_by')
    list_filter = ('type', 'fiscal_year')
    search_fields = ('type', 'fiscal_year__name')
    ordering = ('-date',)
    readonly_fields = ('generated_by', 'generated_at')
    date_hierarchy = 'date'

    fieldsets = (
        ('معلومات القائمة', {
            'fields': ('type', 'fiscal_year', 'date')
        }),
        ('البيانات', {
            'fields': ('data', 'notes')
        }),
        ('معلومات النظام', {
            'fields': ('generated_by', 'generated_at'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        if not obj.generated_by:
            obj.generated_by = request.user
        super().save_model(request, obj, form, change)
