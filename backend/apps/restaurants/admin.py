from django.contrib import admin
from .models import Restaurant

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'is_active', 'currency']
    list_filter = ['is_active']
