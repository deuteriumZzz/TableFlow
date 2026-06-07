from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    image = models.ImageField(upload_to='menu_categories/', blank=True, verbose_name=_("Изображение"))
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, verbose_name=_("Ресторан"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    sort_order = models.PositiveIntegerField(default=0, verbose_name=_("Порядок"))

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ['sort_order', 'name']

class Product(models.Model):
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('out_of_stock', 'Нет в наличии'),
        ('limited', 'Ограниченное количество'),
    ]

    name = models.CharField(max_length=200, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Категория"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_("Себестоимость"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name=_("Статус"))
    image = models.ImageField(upload_to='menu_products/', blank=True, verbose_name=_("Изображение"))
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, verbose_name=_("Ресторан"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создано"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    min_stock = models.PositiveIntegerField(default=0, verbose_name=_("Минимальный остаток"))
    current_stock = models.PositiveIntegerField(default=0, verbose_name=_("Текущий остаток"))

    class Meta:
        verbose_name = _("Товар")
        verbose_name_plural = _("Товары")
        ordering = ['name']

class Modifier(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Название"))
    description = models.TextField(blank=True, verbose_name=_("Описание"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена"))
    is_required = models.BooleanField(default=False, verbose_name=_("Обязательный"))
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, verbose_name=_("Ресторан"))

    class Meta:
        verbose_name = _("Модификатор")
        verbose_name_plural = _("Модификаторы")
        ordering = ['name']

class ProductModifier(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name=_("Товар"))
    modifier = models.ForeignKey(Modifier, on_delete=models.CASCADE, verbose_name=_("Модификатор"))
    max_allowed = models.PositiveIntegerField(default=1, verbose_name=_("Максимальное количество"))

    class Meta:
        verbose_name = _("Связь товара и модификатора")
        verbose_name_plural = _("Связи товара и модификаторов")
        unique_together = ('product', 'modifier')
