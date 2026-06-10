from django.db import models
from apps.accounts.models import User
from apps.restaurants.models import Restaurant

class StaffSchedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.day} {self.start_time} - {self.end_time}"

class StaffSalary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"Зарплата {self.user.username} за {self.month}"
