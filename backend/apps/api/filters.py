import django_filters


class BaseRestaurantFilter(django_filters.FilterSet):
    """
    Base FilterSet for restaurant-scoped models.
    Extend this in each app's filters.py:

        class OrderFilter(BaseRestaurantFilter):
            class Meta:
                model = Order
                fields = ['status']
    """

    class Meta:
        pass
