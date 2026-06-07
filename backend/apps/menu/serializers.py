from rest_framework import serializers
from .models import Product, Category, Modifier

class ModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modifier
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    modifiers = ModifierSerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
