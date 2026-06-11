from django.db.models import Sum, Count
from apps.orders.models import Order, OrderItem


def generate_sales_report(date, restaurant):
    orders = Order.objects.filter(
        created_at__date=date,
        status='delivered',
        payment_status='paid',
        restaurant=restaurant,
    )
    total_orders = orders.count()
    total_revenue = float(orders.aggregate(total=Sum('total_amount'))['total'] or 0)

    # Persist/update the cached report row
    from .models import SalesReport
    SalesReport.objects.update_or_create(
        restaurant=restaurant,
        date=date,
        defaults={'total_orders': total_orders, 'total_revenue': total_revenue},
    )

    return {
        'date': str(date),
        'total_orders': total_orders,
        'total_revenue': total_revenue,
    }


def generate_product_report(product_id, date, restaurant):
    row = OrderItem.objects.filter(
        product_id=product_id,
        order__created_at__date=date,
        order__status='delivered',
        order__restaurant=restaurant,
    ).aggregate(
        quantity_sold=Count('id'),
        total_revenue=Sum('total_price'),
    )
    quantity_sold = row['quantity_sold'] or 0
    total_revenue = float(row['total_revenue'] or 0)

    # Persist/update the cached report row
    from .models import ProductReport
    ProductReport.objects.update_or_create(
        restaurant=restaurant,
        product_id=product_id,
        date=date,
        defaults={'quantity_sold': quantity_sold, 'total_revenue': total_revenue},
    )

    return {
        'product_id': product_id,
        'date': str(date),
        'quantity_sold': quantity_sold,
        'total_revenue': total_revenue,
    }
