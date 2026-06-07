from django.db.models import Sum, Count
from orders.models import Order, OrderItem
from menu.models import Product
from datetime import datetime

def generate_sales_report(date):
    orders = Order.objects.filter(
        created_at__date=date,
        status='completed',
        payment__status='success'
    ).annotate(
        total_amount=Sum('total_amount')
    )
    total_orders = orders.count()
    total_revenue = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    return {
        'date': date,
        'total_orders': total_orders,
        'total_revenue': total_revenue
    }

def generate_product_report(product_id, date):
    order_items = OrderItem.objects.filter(
        product_id=product_id,
        order__created_at__date=date,
        order__status='completed'
    ).values('product').annotate(
        quantity_sold=Count('id'),
        total_revenue=Sum('total_price')
    )
    return order_items.first() or {}
