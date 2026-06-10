from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField(blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    logo = models.ImageField(upload_to='restaurants/logos/', blank=True)
    is_active = models.BooleanField(default=True)
    currency = models.CharField(max_length=3, default='RUB')

    def __str__(self):
        return self.name
