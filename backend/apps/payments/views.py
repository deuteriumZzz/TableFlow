from rest_framework import viewsets, status
from rest_framework.response import Response
from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order

class PaymentViewSet(viewsets.ViewSet):
    def create(self, request):
        order_id = request.data.get('order_id')
        payment_method_id = request.data.get('method')

        try:
            order = Order.objects.get(id=order_id, payment=None)
            payment = Payment.objects.create(
                order=order,
                amount=order.total_amount,
                method_id=payment_method_id,
                status='success'  # Или 'pending' для асинхронной обработки
            )
            # Зинтегрировать платежную систему (YooMoney) и обновить статус платежа)
            serializer = PaymentSerializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({'error': 'Заказ не найден'}, status=status.HTTP_404_NOT_FOUND)
