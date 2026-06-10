from django.urls import path
from .views import SalesReportView, ProductReportView

urlpatterns = [
    path('reports/sales/', SalesReportView.as_view(), name='report-sales'),
    path('reports/products/<int:product_id>/', ProductReportView.as_view(), name='report-product'),
]
