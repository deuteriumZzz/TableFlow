from django.contrib import admin
from .models import Reservation


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['guest_name', 'guest_phone', 'table', 'reserved_at', 'status', 'restaurant']
    list_filter = ['status', 'restaurant', 'reserved_at']
    search_fields = ['guest_name', 'guest_phone']
