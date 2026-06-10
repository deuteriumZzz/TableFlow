from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from .models import Payment, PaymentMethod
from .serializers import PaymentSerializer, PaymentMethodSerializer
from apps.orders.models import Order

class PaymentMethodViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PaymentMethod.objects.all()
    serializer_class = PaymentMethodSerializer
    permission_classes = [permissions.IsAuthenticated]

class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(
            order__restaurant=self.request.user.restaurant
        )

    def create(self, request, *args, **kwargs):
        order_id = request.data.get('order_id')
        method_id = request.data.get('method_id')
        try:
            order = Order.objects.get(
                id=order_id,
                restaurant=request.user.restaurant,
            )
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)

        if hasattr(order, 'payment'):
            return Response(
                {'error': 'Заказ уже оплачен'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment = Payment.objects.create(
            order=order,
            amount=order.total_amount,
            method_id=method_id,
            status='success',
        )
        order.payment_status = 'paid'
        order.status = 'delivered'
        order.save()
        if order.table:
            order.table.status = 'free'
            order.table.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)
