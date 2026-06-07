from rest_framework import viewsets, permissions
from .serializers import SalesReportSerializer, ProductReportSerializer
from .utils import generate_sales_report, generate_product_report

class SalesReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def list(self, request):
        date = request.query_params.get('date')
        if not date:
            date = timezone.now().date()
        report = generate_sales_report(date)
        serializer = SalesReportSerializer(data=report)
        if serializer.is_valid():
            return serializer.data
        return Response(serializer.errors, status=400)

class ProductReportViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAdminUser]

    def retrieve(self, request, pk=None):
        product_id = pk
        date = request.query_params.get('date') or timezone.now().date()
        report = generate_product_report(product_id, date)
        serializer = ProductReportSerializer(data=report)
        if serializer.is_valid():
            return serializer.data
        return Response(serializer.errors, status=400)
