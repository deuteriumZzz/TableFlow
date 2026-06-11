from rest_framework import serializers
from .models import Reservation


class ReservationSerializer(serializers.ModelSerializer):
    table_number = serializers.SerializerMethodField()

    class Meta:
        model = Reservation
        fields = [
            'id', 'table', 'table_number', 'guest_name', 'guest_phone',
            'guest_count', 'reserved_at', 'duration_minutes', 'status',
            'comment', 'created_by', 'created_at', 'updated_at',
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']

    def get_table_number(self, obj):
        return obj.table.number if obj.table else None

    def validate_table(self, table):
        request = self.context.get('request')
        if table and request and table.restaurant != request.user.restaurant:
            raise serializers.ValidationError('Стол не принадлежит вашему ресторану.')
        return table
