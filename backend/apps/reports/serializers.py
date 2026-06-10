from rest_framework import serializers

class SalesReportSerializer(serializers.Serializer):
    date = serializers.CharField()
    total_orders = serializers.IntegerField()
    total_revenue = serializers.FloatField()

class ProductReportSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    date = serializers.CharField()
    quantity_sold = serializers.IntegerField()
    total_revenue = serializers.FloatField()
