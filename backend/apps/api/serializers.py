from rest_framework import serializers


class TimestampedSerializer(serializers.ModelSerializer):
    """Base serializer that marks created_at/updated_at as read-only."""
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
