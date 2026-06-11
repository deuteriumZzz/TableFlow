from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/', include('apps.api.urls')),          # health check
    path('api/', include('apps.accounts.urls')),
    path('api/', include('apps.restaurants.urls')),
    path('api/', include('apps.tables.urls')),
    path('api/', include('apps.menu.urls')),
    path('api/', include('apps.orders.urls')),
    path('api/', include('apps.payments.urls')),
    path('api/', include('apps.staff.urls')),
    path('api/', include('apps.reports.urls')),
    path('api/', include('apps.reservations.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
