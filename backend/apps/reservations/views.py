from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Reservation
from .serializers import ReservationSerializer
from apps.api.permissions import IsManagerOrAdmin


class ReservationViewSet(viewsets.ModelViewSet):
    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Reservation.objects.filter(restaurant=self.request.user.restaurant)
        date = self.request.query_params.get('date')
        if date:
            qs = qs.filter(reserved_at__date=date)
        status_param = self.request.query_params.get('status')
        if status_param:
            qs = qs.filter(status=status_param)
        return qs.select_related('table', 'created_by')

    def perform_create(self, serializer):
        serializer.save(
            restaurant=self.request.user.restaurant,
            created_by=self.request.user,
        )

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status != 'pending':
            return Response(
                {'error': 'Можно подтвердить только бронь в статусе "pending"'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation.status = 'confirmed'
        if reservation.table:
            reservation.table.status = 'reserved'
            reservation.table.save()
        reservation.save()
        return Response(ReservationSerializer(reservation).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        reservation = self.get_object()
        if reservation.status in ('cancelled', 'completed'):
            return Response(
                {'error': 'Бронь уже завершена или отменена'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation.status = 'cancelled'
        if reservation.table and reservation.table.status == 'reserved':
            reservation.table.status = 'free'
            reservation.table.save()
        reservation.save()
        return Response(ReservationSerializer(reservation).data)
