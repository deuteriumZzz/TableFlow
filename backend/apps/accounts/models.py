from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('manager', 'Менеджер'),
        ('cashier', 'Кассир'),
        ('waiter', 'Официант'),
        ('chef', 'Повар'),
        ('auditor', 'Аудитор'),
        ('client', 'Клиент'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    last_login_pos = models.DateTimeField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='accounts/avatars/', blank=True)
