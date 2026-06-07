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
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='cashier')
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    last_login_pos = models.DateTimeField(null=True, blank=True)

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    last_activity = models.DateTimeField(auto_now=True)
