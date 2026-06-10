from rest_framework.routers import DefaultRouter
from .views import StaffScheduleViewSet, StaffSalaryViewSet

router = DefaultRouter()
router.register(r'staff/schedules', StaffScheduleViewSet, basename='staff-schedule')
router.register(r'staff/salaries', StaffSalaryViewSet, basename='staff-salary')

urlpatterns = router.urls
