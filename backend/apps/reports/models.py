from django.db import models


class SalesReport(models.Model):
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE, null=True, blank=True,
    )
    date = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('restaurant', 'date')

    def __str__(self):
        return f"Отчет за {self.date}"


class ProductReport(models.Model):
    restaurant = models.ForeignKey(
        'restaurants.Restaurant', on_delete=models.CASCADE, null=True, blank=True,
    )
    product = models.ForeignKey('menu.Product', on_delete=models.CASCADE)
    date = models.DateField()
    quantity_sold = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        unique_together = ('restaurant', 'product', 'date')

    def __str__(self):
        return f"{self.product.name} - {self.date}"
