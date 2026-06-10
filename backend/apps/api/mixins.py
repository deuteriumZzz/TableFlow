class RestaurantMixin:
    """
    Scopes ViewSet queryset and creates to the authenticated user's restaurant.
    Use as the first base class: class MyViewSet(RestaurantMixin, viewsets.ModelViewSet)
    """

    def get_queryset(self):
        return super().get_queryset().filter(
            restaurant=self.request.user.restaurant
        )

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)
