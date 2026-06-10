from django.db import models
from django.utils.translation import gettext_lazy as _

class Table(models.Model):
    STATUS_CHOICES = [
        ('free', 'Свободен'),
        ('occupied', 'Занят'),
        ('reserved', 'Забронирован'),
    ]

    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE,
        related_name='tables', verbose_name=_('Ресторан')
    )
    number = models.PositiveIntegerField(verbose_name=_('Номер стола'))
    capacity = models.PositiveIntegerField(default=4, verbose_name=_('Вместимость'))
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='free',
        verbose_name=_('Статус')
    )

    class Meta:
        verbose_name = _('Стол')
        verbose_name_plural = _('Столы')
        unique_together = ('restaurant', 'number')
        ordering = ['number']

    def __str__(self):
        return f"Стол #{self.number} ({self.get_status_display()})"
