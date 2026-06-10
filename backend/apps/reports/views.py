from datetime import date as date_type

from django.utils import timezone
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import ProductReportSerializer, SalesReportSerializer
from .utils import generate_product_report, generate_sales_report


class SalesReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                report_date = date_type.fromisoformat(date_str)
            except ValueError:
                return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)
        else:
            report_date = timezone.now().date()

        data = generate_sales_report(report_date)
        serializer = SalesReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class ProductReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, product_id):
        date_str = request.query_params.get('date')
        if date_str:
            try:
                report_date = date_type.fromisoformat(date_str)
            except ValueError:
                return Response({'error': 'Неверный формат даты. Используйте YYYY-MM-DD'}, status=400)
        else:
            report_date = timezone.now().date()

        data = generate_product_report(product_id, report_date)
        serializer = ProductReportSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)
