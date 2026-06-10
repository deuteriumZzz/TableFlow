from rest_framework import viewsets, permissions
from .models import Product, Category, Modifier
from .serializers import ProductSerializer, CategorySerializer, ModifierSerializer
from apps.api.permissions import IsStaffOrReadOnly

class CategoryViewSet(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        return Category.objects.filter(
            restaurant=self.request.user.restaurant,
            is_active=True,
        )

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Product.objects.filter(
            restaurant=self.request.user.restaurant,
            is_active=True,
        )
        category_id = self.request.query_params.get('category')
        if category_id:
            qs = qs.filter(category_id=category_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)

class ModifierViewSet(viewsets.ModelViewSet):
    serializer_class = ModifierSerializer
    permission_classes = [permissions.IsAuthenticated, IsStaffOrReadOnly]

    def get_queryset(self):
        return Modifier.objects.filter(restaurant=self.request.user.restaurant)

    def perform_create(self, serializer):
        serializer.save(restaurant=self.request.user.restaurant)
