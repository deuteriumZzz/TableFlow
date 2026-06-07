from django.db import models
from django.utils import timezone
from django.db.models import Sum, Count

class SalesReport(models.Model):
    date = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отчет за {self.date}"

class ProductReport(models.Model):
    product = models.ForeignKey('menu.Product', on_delete=models.CASCADE)
    date = models.DateField()
    quantity_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.product.name} - {self.date}"
