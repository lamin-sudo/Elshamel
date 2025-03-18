from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from inventory.models import Product
from accounts.models import Account

class Supplier(models.Model):
    """Model for suppliers"""
    code = models.CharField(_('كود المورد'), max_length=20, unique=True)
    name = models.CharField(_('اسم المورد'), max_length=200)
    contact_person = models.CharField(_('الشخص المسؤول'), max_length=100, blank=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    mobile = models.CharField(_('رقم الجوال'), max_length=20, blank=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    address = models.TextField(_('العنوان'))
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50, blank=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='suppliers', verbose_name=_('الحساب'))
    credit_limit = models.DecimalField(_('حد الائتمان'), max_digits=10, decimal_places=2, default=0)
    current_balance = models.DecimalField(_('الرصيد الحالي'), max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(_('نشط'), default=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مورد')
        verbose_name_plural = _('الموردين')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def update_balance(self):
        """Update supplier's current balance"""
        from django.db.models import Sum
        purchases = self.purchase_invoices.filter(status='posted').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        payments = self.supplier_payments.filter(status='posted').aggregate(Sum('amount'))['amount__sum'] or 0
        self.current_balance = purchases - payments
        self.save()

class PurchaseInvoice(models.Model):
    """Model for purchase invoices"""
    INVOICE_STATUS = [
        ('draft', _('مسودة')),
        ('posted', _('مرحلة')),
        ('cancelled', _('ملغاة')),
    ]

    number = models.CharField(_('رقم الفاتورة'), max_length=20, unique=True)
    date = models.DateField(_('تاريخ الفاتورة'))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='purchase_invoices', verbose_name=_('المورد'))
    status = models.CharField(_('الحالة'), max_length=10, choices=INVOICE_STATUS, default='draft')
    subtotal = models.DecimalField(_('المجموع'), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('مبلغ الضريبة'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('مبلغ الخصم'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('الإجمالي'), max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(_('تاريخ الاستحقاق'))
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='purchase_invoices', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('فاتورة مشتريات')
        verbose_name_plural = _('فواتير المشتريات')
        ordering = ['-date', '-number']

    def __str__(self):
        return f"{self.number} - {self.supplier.name}"

    def calculate_totals(self):
        """Calculate invoice totals"""
        self.subtotal = sum(line.total for line in self.lines.all())
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()

class PurchaseInvoiceLine(models.Model):
    """Model for purchase invoice lines"""
    invoice = models.ForeignKey(PurchaseInvoice, on_delete=models.CASCADE, related_name='lines', verbose_name=_('الفاتورة'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='purchase_lines', verbose_name=_('المنتج'))
    quantity = models.DecimalField(_('الكمية'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(_('سعر الوحدة'), max_digits=10, decimal_places=2)
    tax_rate = models.DecimalField(_('نسبة الضريبة'), max_digits=5, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('مبلغ الخصم'), max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(_('الإجمالي'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('بند الفاتورة')
        verbose_name_plural = _('بنود الفاتورة')

    def __str__(self):
        return f"{self.invoice.number} - {self.product.name}"

    def save(self, *args, **kwargs):
        self.total = (self.quantity * self.unit_price) * (1 + self.tax_rate/100) - self.discount_amount
        super().save(*args, **kwargs)
        self.invoice.calculate_totals()

class SupplierPayment(models.Model):
    """Model for supplier payments"""
    PAYMENT_STATUS = [
        ('draft', _('مسودة')),
        ('posted', _('مرحل')),
        ('cancelled', _('ملغي')),
    ]

    PAYMENT_METHODS = [
        ('cash', _('نقدي')),
        ('bank', _('تحويل بنكي')),
        ('cheque', _('شيك')),
    ]

    number = models.CharField(_('رقم السند'), max_length=20, unique=True)
    date = models.DateField(_('تاريخ السند'))
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, related_name='supplier_payments', verbose_name=_('المورد'))
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('طريقة الدفع'), max_length=10, choices=PAYMENT_METHODS)
    reference = models.CharField(_('المرجع'), max_length=50, blank=True)
    status = models.CharField(_('الحالة'), max_length=10, choices=PAYMENT_STATUS, default='draft')
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='supplier_payments', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('سند صرف')
        verbose_name_plural = _('سندات الصرف')
        ordering = ['-date', '-number']

    def __str__(self):
        return f"{self.number} - {self.supplier.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'posted':
            self.supplier.update_balance()
