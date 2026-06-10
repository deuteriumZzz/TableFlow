from rest_framework import viewsets, permissions
from .models import StaffSchedule, StaffSalary
from .serializers import StaffScheduleSerializer, StaffSalarySerializer
from apps.api.permissions import IsManagerOrAdmin

class StaffScheduleViewSet(viewsets.ModelViewSet):
    queryset = StaffSchedule.objects.all()
    serializer_class = StaffScheduleSerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]

    def get_queryset(self):
        return self.queryset.filter(restaurant=self.request.user.restaurant)

class StaffSalaryViewSet(viewsets.ModelViewSet):
    queryset = StaffSalary.objects.all()
    serializer_class = StaffSalarySerializer
    permission_classes = [permissions.IsAuthenticated, IsManagerOrAdmin]
