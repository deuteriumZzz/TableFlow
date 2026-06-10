import django_filters

from apps.api.filters import BaseRestaurantFilter
from .models import Order


class OrderFilter(BaseRestaurantFilter):
    status = django_filters.CharFilter()
    date_from = django_filters.DateFilter(field_name='created_at__date', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at__date', lookup_expr='lte')

    class Meta:
        model = Order
        fields = ['status', 'date_from', 'date_to']
