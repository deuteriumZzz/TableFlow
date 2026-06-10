from rest_framework import serializers
from .models import Payment, PaymentMethod

class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = ['id', 'name', 'description']

class PaymentSerializer(serializers.ModelSerializer):
    method_name = serializers.CharField(source='method.name', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'method', 'method_name',
                  'status', 'transaction_id', 'created_at']
        read_only_fields = ['created_at']
