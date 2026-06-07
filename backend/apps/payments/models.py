from django.db import models
from orders.models import Order

class PaymentMethod(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('success', 'Успешно'),
        ('failed', 'Не удалось'),
        ('refunded', 'Возврат'),
    )

    order = models.OneToOneField(Order, related_name='payment', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Платеж #{self.id} за заказ #{self.order.id}"
