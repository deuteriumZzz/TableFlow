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
    category_id = serializers.PrimaryKeyRelatedField(
        source='category', queryset=__import__('apps.menu.models', fromlist=['Category']).Category.objects.all(),
        write_only=True, required=False,
    )

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['restaurant']
