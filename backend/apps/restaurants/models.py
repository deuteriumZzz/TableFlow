from django.db import models

class Restaurant(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    logo = models.ImageField(upload_to='restaurants/logos/')
    is_active = models.BooleanField(default=True)
    currency = models.CharField(max_length=3, default='RUB')

    def __str__(self):
        return self.name
