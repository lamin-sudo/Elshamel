from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class AccountType(models.Model):
    """Model for different types of accounts (Asset, Liability, Equity, Revenue, Expense)"""
    ACCOUNT_TYPES = [
        ('asset', 'أصول'),
        ('liability', 'خصوم'),
        ('equity', 'حقوق ملكية'),
        ('revenue', 'إيرادات'),
        ('expense', 'مصروفات'),
    ]

    name = models.CharField(_('اسم النوع'), max_length=50)
    code = models.CharField(_('كود النوع'), max_length=2)
    description = models.TextField(_('الوصف'), blank=True)

    class Meta:
        verbose_name = _('نوع الحساب')
        verbose_name_plural = _('أنواع الحسابات')

    def __str__(self):
        return f"{self.code} - {self.name}"

class Account(models.Model):
    """Model for individual accounts in the chart of accounts"""
    DEBIT_CREDIT_CHOICES = [
        ('debit', _('مدين')),
        ('credit', _('دائن')),
    ]

    code = models.CharField(_('كود الحساب'), max_length=10, unique=True)
    name = models.CharField(_('اسم الحساب'), max_length=100)
    type = models.ForeignKey(AccountType, on_delete=models.PROTECT, related_name='accounts', verbose_name=_('نوع الحساب'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('الحساب الرئيسي'))
    description = models.TextField(_('الوصف'), blank=True)
    balance = models.DecimalField(_('الرصيد الحالي'), max_digits=15, decimal_places=2, default=0)
    normal_balance = models.CharField(_('الرصيد الطبيعي'), max_length=6, choices=DEBIT_CREDIT_CHOICES)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('حساب')
        verbose_name_plural = _('الحسابات')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def update_balance(self):
        """Update account balance based on journal entries"""
        from django.db.models import Sum
        debit_sum = self.journal_entries.filter(entry_type='debit').aggregate(Sum('amount'))['amount__sum'] or 0
        credit_sum = self.journal_entries.filter(entry_type='credit').aggregate(Sum('amount'))['amount__sum'] or 0
        
        if self.normal_balance == 'debit':
            self.balance = debit_sum - credit_sum
        else:
            self.balance = credit_sum - debit_sum
        self.save()

class JournalEntry(models.Model):
    """Model for recording financial transactions"""
    ENTRY_TYPES = [
        ('debit', _('مدين')),
        ('credit', _('دائن')),
    ]

    date = models.DateField(_('تاريخ القيد'))
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='journal_entries', verbose_name=_('الحساب'))
    entry_type = models.CharField(_('نوع القيد'), max_length=6, choices=ENTRY_TYPES)
    amount = models.DecimalField(_('المبلغ'), max_digits=15, decimal_places=2)
    description = models.TextField(_('البيان'))
    reference = models.CharField(_('المرجع'), max_length=50)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='journal_entries', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('قيد يومية')
        verbose_name_plural = _('قيود اليومية')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.account.name} - {self.amount}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.account.update_balance()

class FiscalYear(models.Model):
    """Model for managing fiscal years"""
    name = models.CharField(_('السنة المالية'), max_length=50)
    start_date = models.DateField(_('تاريخ البداية'))
    end_date = models.DateField(_('تاريخ النهاية'))
    is_closed = models.BooleanField(_('مغلقة'), default=False)
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        verbose_name = _('سنة مالية')
        verbose_name_plural = _('السنوات المالية')
        ordering = ['-start_date']

    def __str__(self):
        return self.name

class FinancialStatement(models.Model):
    """Model for storing generated financial statements"""
    STATEMENT_TYPES = [
        ('balance_sheet', _('الميزانية العمومية')),
        ('income_statement', _('قائمة الدخل')),
        ('cash_flow', _('قائمة التدفقات النقدية')),
    ]

    fiscal_year = models.ForeignKey(FiscalYear, on_delete=models.CASCADE, related_name='statements', verbose_name=_('السنة المالية'))
    type = models.CharField(_('نوع القائمة'), max_length=20, choices=STATEMENT_TYPES)
    date = models.DateField(_('تاريخ القائمة'))
    data = models.JSONField(_('البيانات'))
    generated_by = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('تم الإنشاء بواسطة'))
    generated_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        verbose_name = _('قائمة مالية')
        verbose_name_plural = _('القوائم المالية')
        ordering = ['-date']

    def __str__(self):
        return f"{self.get_type_display()} - {self.date}"
