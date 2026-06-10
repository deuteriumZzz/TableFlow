from rest_framework import serializers
from .models import Order, OrderItem, OrderItemModifier
from apps.menu.serializers import ProductSerializer, ModifierSerializer

class OrderItemModifierSerializer(serializers.ModelSerializer):
    modifier = ModifierSerializer(read_only=True)

    class Meta:
        model = OrderItemModifier
        fields = ['id', 'modifier', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    applied_modifiers = OrderItemModifierSerializer(
        source='orderitemmodifier_set', many=True, read_only=True
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'total_price',
                  'comment', 'status', 'applied_modifiers']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'table', 'table_number', 'waitress', 'status', 'payment_status',
                  'total_amount', 'discount', 'tax', 'comment', 'is_online',
                  'created_at', 'updated_at', 'items']
        read_only_fields = ['total_amount', 'created_at', 'updated_at',
                            'waitress', 'restaurant']

    def get_table_number(self, obj):
        return obj.table.number if obj.table else None

class OrderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['table', 'comment', 'is_online']

    def create(self, validated_data):
        validated_data['restaurant'] = self.context['request'].user.restaurant
        validated_data['waitress'] = self.context['request'].user
        return super().create(validated_data)

class AddItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    modifier_ids = serializers.ListField(
        child=serializers.IntegerField(), required=False, default=list
    )
