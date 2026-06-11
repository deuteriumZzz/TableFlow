from django.db import models
from django.utils.translation import gettext_lazy as _


class Reservation(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('confirmed', 'Подтверждено'),
        ('cancelled', 'Отменено'),
        ('completed', 'Завершено'),
        ('no_show', 'Не пришли'),
    ]

    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE,
        verbose_name=_('Ресторан'),
    )
    table = models.ForeignKey(
        'tables.Table', on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name=_('Стол'),
    )
    guest_name = models.CharField(max_length=200, verbose_name=_('Имя гостя'))
    guest_phone = models.CharField(max_length=20, verbose_name=_('Телефон гостя'))
    guest_count = models.PositiveIntegerField(default=1, verbose_name=_('Количество гостей'))
    reserved_at = models.DateTimeField(verbose_name=_('Время брони'))
    duration_minutes = models.PositiveIntegerField(default=120, verbose_name=_('Длительность (мин)'))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='pending',
        verbose_name=_('Статус'),
    )
    comment = models.TextField(blank=True, verbose_name=_('Комментарий'))
    created_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True,
        verbose_name=_('Создал'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Обновлено'))

    class Meta:
        verbose_name = _('Бронирование')
        verbose_name_plural = _('Бронирования')
        ordering = ['reserved_at']

    def __str__(self):
        return f"{self.guest_name} — {self.reserved_at:%d.%m.%Y %H:%M}"
