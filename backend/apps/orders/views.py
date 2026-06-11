import logging
from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models as db_models
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Order, OrderItem, OrderItemModifier
from .serializers import OrderSerializer, OrderCreateSerializer, AddItemSerializer
from .filters import OrderFilter
from apps.menu.models import Product, Modifier
from apps.api.pagination import StandardPagination

logger = logging.getLogger(__name__)


def _broadcast_order_update(order):
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'orders_{order.restaurant_id}',
            {
                'type': 'order_update',
                'order_id': order.id,
                'status': order.status,
            },
        )
    except Exception:
        logger.warning('WebSocket broadcast failed for order %d', order.id)

ITEM_STATUS_CHOICES = ('pending', 'in_progress', 'ready', 'delivered', 'cancelled')


class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = OrderFilter

    def get_serializer_class(self):
        if self.action == 'create':
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(
            restaurant=self.request.user.restaurant
        ).prefetch_related('items__product', 'items__modifiers')

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        if order.table:
            order.table.status = 'occupied'
            order.table.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        order = self.get_object()
        if order.status not in ('created', 'in_progress'):
            return Response(
                {'error': 'Нельзя добавить позицию в заказ с текущим статусом'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ser = AddItemSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data

        product = get_object_or_404(
            Product, id=data['product_id'],
            restaurant=request.user.restaurant, is_active=True,
        )

        if product.status == 'out_of_stock':
            return Response(
                {'error': 'Товар отсутствует в наличии'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if product.current_stock > 0 and product.current_stock < data['quantity']:
            return Response(
                {'error': f'Недостаточно товара. Доступно: {product.current_stock}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        modifier_price = Decimal('0')
        modifiers = []
        for mid in data.get('modifier_ids', []):
            m = get_object_or_404(Modifier, id=mid, restaurant=request.user.restaurant)
            modifier_price += m.price
            modifiers.append(m)

        unit_price = product.price + modifier_price
        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=data['quantity'],
            price=unit_price,
            total_price=unit_price * data['quantity'],
            comment=data.get('comment', ''),
        )
        for m in modifiers:
            OrderItemModifier.objects.create(order_item=item, modifier=m, quantity=1)

        # Списываем остаток если продукт отслеживается (current_stock > 0)
        if product.current_stock > 0:
            Product.objects.filter(pk=product.pk).update(
                current_stock=db_models.F('current_stock') - data['quantity']
            )
            logger.debug('Stock decremented: product=%d qty=%d', product.pk, data['quantity'])

        order.recalculate_total()
        order = Order.objects.prefetch_related('items__product', 'items__modifiers').get(pk=order.pk)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['delete'], url_path=r'remove_item/(?P<item_id>[^/.]+)')
    def remove_item(self, request, pk=None, item_id=None):
        order = self.get_object()
        item = get_object_or_404(OrderItem, id=item_id, order=order)
        item.delete()
        order.recalculate_total()
        order = Order.objects.prefetch_related('items__product', 'items__modifiers').get(pk=order.pk)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        valid = [s[0] for s in Order.STATUS_CHOICES]
        if new_status not in valid:
            return Response(
                {'error': f'Допустимые статусы: {valid}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        order.status = new_status
        if new_status in ('delivered', 'cancelled') and order.table:
            if not Order.objects.filter(
                table=order.table, status__in=('created', 'in_progress', 'ready')
            ).exclude(id=order.id).exists():
                order.table.status = 'free'
                order.table.save()
        order.save()
        _broadcast_order_update(order)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'], url_path=r'item_status/(?P<item_id>[^/.]+)')
    def update_item_status(self, request, pk=None, item_id=None):
        order = self.get_object()
        item = get_object_or_404(OrderItem, id=item_id, order=order)
        new_status = request.data.get('status')
        if new_status not in ITEM_STATUS_CHOICES:
            return Response(
                {'error': f'Допустимые статусы позиции: {ITEM_STATUS_CHOICES}'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        item.status = new_status
        item.save(update_fields=['status'])
        order = Order.objects.prefetch_related('items__product', 'items__modifiers').get(pk=order.pk)
        return Response(OrderSerializer(order).data)
