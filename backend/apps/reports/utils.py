from django.db.models import Sum, Count
from apps.orders.models import Order, OrderItem

def generate_sales_report(date):
    orders = Order.objects.filter(
        created_at__date=date,
        status='delivered',
        payment_status='paid',
    )
    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    return {
        'date': str(date),
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
    }

def generate_product_report(product_id, date):
    row = OrderItem.objects.filter(
        product_id=product_id,
        order__created_at__date=date,
        order__status='delivered',
    ).aggregate(
        quantity_sold=Count('id'),
        total_revenue=Sum('total_price'),
    )
    return {
        'product_id': product_id,
        'date': str(date),
        'quantity_sold': row['quantity_sold'] or 0,
        'total_revenue': float(row['total_revenue'] or 0),
    }
