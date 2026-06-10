from rest_framework import viewsets, permissions
from .models import Restaurant
from .serializers import RestaurantSerializer

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.filter(is_active=True)
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.IsAuthenticated]
