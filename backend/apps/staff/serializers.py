from rest_framework import serializers
from .models import StaffSchedule, StaffSalary

class StaffScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSchedule
        fields = '__all__'

class StaffSalarySerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffSalary
        fields = '__all__'
