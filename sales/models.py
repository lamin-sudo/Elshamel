from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from inventory.models import Product
from accounts.models import Account

class Customer(models.Model):
    """Model for customers"""
    code = models.CharField(_('كود العميل'), max_length=20, unique=True)
    name = models.CharField(_('اسم العميل'), max_length=200)
    contact_person = models.CharField(_('الشخص المسؤول'), max_length=100, blank=True)
    phone = models.CharField(_('رقم الهاتف'), max_length=20)
    mobile = models.CharField(_('رقم الجوال'), max_length=20, blank=True)
    email = models.EmailField(_('البريد الإلكتروني'), blank=True)
    address = models.TextField(_('العنوان'))
    tax_number = models.CharField(_('الرقم الضريبي'), max_length=50, blank=True)
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='customers', verbose_name=_('الحساب'))
    credit_limit = models.DecimalField(_('حد الائتمان'), max_digits=10, decimal_places=2, default=0)
    current_balance = models.DecimalField(_('الرصيد الحالي'), max_digits=10, decimal_places=2, default=0)
    discount_percentage = models.DecimalField(_('نسبة الخصم'), max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(_('نشط'), default=True)
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('عميل')
        verbose_name_plural = _('العملاء')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def update_balance(self):
        """Update customer's current balance"""
        from django.db.models import Sum
        sales = self.sales_invoices.filter(status='posted').aggregate(Sum('total_amount'))['total_amount__sum'] or 0
        payments = self.customer_payments.filter(status='posted').aggregate(Sum('amount'))['amount__sum'] or 0
        self.current_balance = sales - payments
        self.save()

class SalesInvoice(models.Model):
    """Model for sales invoices"""
    INVOICE_STATUS = [
        ('draft', _('مسودة')),
        ('posted', _('مرحلة')),
        ('cancelled', _('ملغاة')),
    ]

    number = models.CharField(_('رقم الفاتورة'), max_length=20, unique=True)
    date = models.DateField(_('تاريخ الفاتورة'))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_invoices', verbose_name=_('العميل'))
    status = models.CharField(_('الحالة'), max_length=10, choices=INVOICE_STATUS, default='draft')
    subtotal = models.DecimalField(_('المجموع'), max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(_('مبلغ الضريبة'), max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(_('مبلغ الخصم'), max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(_('الإجمالي'), max_digits=10, decimal_places=2, default=0)
    due_date = models.DateField(_('تاريخ الاستحقاق'))
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales_invoices', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('فاتورة مبيعات')
        verbose_name_plural = _('فواتير المبيعات')
        ordering = ['-date', '-number']

    def __str__(self):
        return f"{self.number} - {self.customer.name}"

    def calculate_totals(self):
        """Calculate invoice totals"""
        self.subtotal = sum(line.total for line in self.lines.all())
        self.total_amount = self.subtotal + self.tax_amount - self.discount_amount
        self.save()

class SalesInvoiceLine(models.Model):
    """Model for sales invoice lines"""
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.CASCADE, related_name='lines', verbose_name=_('الفاتورة'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='sale_lines', verbose_name=_('المنتج'))
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

class SalesReturn(models.Model):
    """Model for sales returns"""
    RETURN_STATUS = [
        ('draft', _('مسودة')),
        ('posted', _('مرحل')),
        ('cancelled', _('ملغي')),
    ]

    number = models.CharField(_('رقم المرتجع'), max_length=20, unique=True)
    date = models.DateField(_('تاريخ المرتجع'))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='sales_returns', verbose_name=_('العميل'))
    invoice = models.ForeignKey(SalesInvoice, on_delete=models.PROTECT, related_name='returns', verbose_name=_('فاتورة المبيعات'))
    status = models.CharField(_('الحالة'), max_length=10, choices=RETURN_STATUS, default='draft')
    total_amount = models.DecimalField(_('إجمالي المرتجع'), max_digits=10, decimal_places=2, default=0)
    reason = models.TextField(_('سبب المرتجع'))
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='sales_returns', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مرتجع مبيعات')
        verbose_name_plural = _('مرتجعات المبيعات')
        ordering = ['-date', '-number']

    def __str__(self):
        return f"{self.number} - {self.customer.name}"

class SalesReturnLine(models.Model):
    """Model for sales return lines"""
    sales_return = models.ForeignKey(SalesReturn, on_delete=models.CASCADE, related_name='lines', verbose_name=_('مرتجع المبيعات'))
    invoice_line = models.ForeignKey(SalesInvoiceLine, on_delete=models.PROTECT, related_name='return_lines', verbose_name=_('بند الفاتورة'))
    quantity = models.DecimalField(_('الكمية'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(_('سعر الوحدة'), max_digits=10, decimal_places=2)
    total = models.DecimalField(_('الإجمالي'), max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = _('بند المرتجع')
        verbose_name_plural = _('بنود المرتجع')

    def __str__(self):
        return f"{self.sales_return.number} - {self.invoice_line.product.name}"

    def save(self, *args, **kwargs):
        self.unit_price = self.invoice_line.unit_price
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

class CustomerPayment(models.Model):
    """Model for customer payments"""
    PAYMENT_STATUS = [
        ('draft', _('مسودة')),
        ('posted', _('مرحل')),
        ('cancelled', _('ملغي')),
    ]

    PAYMENT_METHODS = [
        ('cash', _('نقدي')),
        ('bank', _('تحويل بنكي')),
        ('cheque', _('شيك')),
        ('card', _('بطاقة ائتمان')),
    ]

    number = models.CharField(_('رقم السند'), max_length=20, unique=True)
    date = models.DateField(_('تاريخ السند'))
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='customer_payments', verbose_name=_('العميل'))
    amount = models.DecimalField(_('المبلغ'), max_digits=10, decimal_places=2)
    payment_method = models.CharField(_('طريقة الدفع'), max_length=10, choices=PAYMENT_METHODS)
    reference = models.CharField(_('المرجع'), max_length=50, blank=True)
    status = models.CharField(_('الحالة'), max_length=10, choices=PAYMENT_STATUS, default='draft')
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='customer_payments', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('سند قبض')
        verbose_name_plural = _('سندات القبض')
        ordering = ['-date', '-number']

    def __str__(self):
        return f"{self.number} - {self.customer.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.status == 'posted':
            self.customer.update_balance()
