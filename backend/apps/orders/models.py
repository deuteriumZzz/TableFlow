from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Создан'),
        ('in_progress', 'В обработке'),
        ('ready', 'Готов'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменен'),
        ('refunded', 'Возврат'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Ожидание оплаты'),
        ('paid', 'Оплачен'),
        ('failed', 'Оплата не удалась'),
        ('refunded', 'Возврат средств'),
    ]

    table = models.ForeignKey(
        'tables.Table', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Стол"),
    )
    user = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Пользователь"),
    )
    waitress = models.ForeignKey(
        'accounts.User', related_name='orders_as_waitress',
        on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_("Официант"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Обновлено"))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='created',
        verbose_name=_("Статус"),
    )
    payment_status = models.CharField(
        max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending',
        verbose_name=_("Статус оплаты"),
    )
    total_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Итоговая сумма"),
    )
    discount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Скидка"),
    )
    tax = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name=_("Налог"),
    )
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    is_online = models.BooleanField(default=False, verbose_name=_("Онлайн-заказ"))
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE,
        verbose_name=_("Ресторан"),
    )

    class Meta:
        verbose_name = _("Заказ")
        verbose_name_plural = _("Заказы")
        ordering = ['-created_at']

    def __str__(self):
        return f"#{self.id} - {self.status} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def recalculate_total(self):
        """Recompute total_amount from item subtotals. Does not apply discount or tax."""
        from django.db.models import Sum
        result = OrderItem.objects.filter(order=self).aggregate(total=Sum('total_price'))
        self.total_amount = result['total'] or 0
        self.save(update_fields=['total_amount'])


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items',
        verbose_name=_("Заказ"),
    )
    product = models.ForeignKey(
        'menu.Product', on_delete=models.SET_NULL, null=True,
        verbose_name=_("Товар"),
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name=_("Количество"))
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Цена за единицу"))
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Итоговая цена"))
    comment = models.TextField(blank=True, verbose_name=_("Комментарий"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Создан"))
    status = models.CharField(max_length=20, default='pending', verbose_name=_("Статус"))
    modifiers = models.ManyToManyField(
        'menu.Modifier', through='OrderItemModifier', blank=True,
        verbose_name=_("Модификаторы"),
    )

    class Meta:
        verbose_name = _("Позиция заказа")
        verbose_name_plural = _("Позиции заказов")


class OrderItemModifier(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    modifier = models.ForeignKey('menu.Modifier', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = _("Модификатор позиции заказа")
        verbose_name_plural = _("Модификаторы позиций заказов")
