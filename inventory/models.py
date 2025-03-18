from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

class Category(models.Model):
    """Model for product categories"""
    name = models.CharField(_('اسم التصنيف'), max_length=100)
    code = models.CharField(_('كود التصنيف'), max_length=10, unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_('التصنيف الرئيسي'))
    description = models.TextField(_('الوصف'), blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('تصنيف')
        verbose_name_plural = _('التصنيفات')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class Product(models.Model):
    """Model for products"""
    UNIT_CHOICES = [
        ('piece', _('قطعة')),
        ('kg', _('كيلوجرام')),
        ('m', _('متر')),
        ('l', _('لتر')),
    ]

    code = models.CharField(_('كود المنتج'), max_length=20, unique=True)
    barcode = models.CharField(_('باركود'), max_length=50, blank=True)
    name = models.CharField(_('اسم المنتج'), max_length=200)
    description = models.TextField(_('الوصف'), blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products', verbose_name=_('التصنيف'))
    unit = models.CharField(_('وحدة القياس'), max_length=10, choices=UNIT_CHOICES)
    purchase_price = models.DecimalField(_('سعر الشراء'), max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(_('سعر البيع'), max_digits=10, decimal_places=2)
    min_stock = models.DecimalField(_('الحد الأدنى للمخزون'), max_digits=10, decimal_places=2, default=0)
    current_stock = models.DecimalField(_('المخزون الحالي'), max_digits=10, decimal_places=2, default=0)
    image = models.ImageField(_('صورة المنتج'), upload_to='products/', blank=True)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('منتج')
        verbose_name_plural = _('المنتجات')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

    def update_stock(self):
        """Update current stock based on stock movements"""
        from django.db.models import Sum
        inward = self.stock_movements.filter(movement_type='in').aggregate(Sum('quantity'))['quantity__sum'] or 0
        outward = self.stock_movements.filter(movement_type='out').aggregate(Sum('quantity'))['quantity__sum'] or 0
        self.current_stock = inward - outward
        self.save()

class Warehouse(models.Model):
    """Model for warehouses"""
    name = models.CharField(_('اسم المخزن'), max_length=100)
    code = models.CharField(_('كود المخزن'), max_length=10, unique=True)
    location = models.TextField(_('الموقع'))
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='managed_warehouses', verbose_name=_('المسؤول'))
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('مخزن')
        verbose_name_plural = _('المخازن')
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.name}"

class StockMovement(models.Model):
    """Model for tracking stock movements"""
    MOVEMENT_TYPES = [
        ('in', _('وارد')),
        ('out', _('منصرف')),
    ]

    MOVEMENT_REASONS = [
        ('purchase', _('شراء')),
        ('sale', _('بيع')),
        ('return_in', _('مرتجع وارد')),
        ('return_out', _('مرتجع منصرف')),
        ('adjustment', _('تسوية مخزن')),
        ('transfer', _('تحويل مخزني')),
    ]

    date = models.DateField(_('تاريخ الحركة'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stock_movements', verbose_name=_('المنتج'))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='stock_movements', verbose_name=_('المخزن'))
    movement_type = models.CharField(_('نوع الحركة'), max_length=3, choices=MOVEMENT_TYPES)
    reason = models.CharField(_('سبب الحركة'), max_length=20, choices=MOVEMENT_REASONS)
    quantity = models.DecimalField(_('الكمية'), max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    unit_price = models.DecimalField(_('سعر الوحدة'), max_digits=10, decimal_places=2)
    reference = models.CharField(_('المرجع'), max_length=50)
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stock_movements', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)

    class Meta:
        verbose_name = _('حركة مخزنية')
        verbose_name_plural = _('حركات المخزن')
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.date} - {self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.product.update_stock()

class Stocktaking(models.Model):
    """Model for stock counting and adjustments"""
    STATUS_CHOICES = [
        ('draft', _('مسودة')),
        ('in_progress', _('جاري الجرد')),
        ('completed', _('مكتمل')),
        ('cancelled', _('ملغي')),
    ]

    date = models.DateField(_('تاريخ الجرد'))
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, related_name='stocktakings', verbose_name=_('المخزن'))
    status = models.CharField(_('الحالة'), max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(_('ملاحظات'), blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='stocktakings', verbose_name=_('تم الإنشاء بواسطة'))
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('جرد مخزني')
        verbose_name_plural = _('عمليات الجرد')
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.warehouse.name}"

class StocktakingLine(models.Model):
    """Model for individual stocktaking lines"""
    stocktaking = models.ForeignKey(Stocktaking, on_delete=models.CASCADE, related_name='lines', verbose_name=_('الجرد'))
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='stocktaking_lines', verbose_name=_('المنتج'))
    expected_quantity = models.DecimalField(_('الكمية المتوقعة'), max_digits=10, decimal_places=2)
    actual_quantity = models.DecimalField(_('الكمية الفعلية'), max_digits=10, decimal_places=2)
    difference = models.DecimalField(_('الفرق'), max_digits=10, decimal_places=2)
    notes = models.TextField(_('ملاحظات'), blank=True)

    class Meta:
        verbose_name = _('بند جرد')
        verbose_name_plural = _('بنود الجرد')

    def __str__(self):
        return f"{self.stocktaking.date} - {self.product.name}"

    def save(self, *args, **kwargs):
        self.difference = self.actual_quantity - self.expected_quantity
        super().save(*args, **kwargs)
