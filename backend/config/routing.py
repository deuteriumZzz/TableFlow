import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import re_path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from apps.orders.consumers import OrderConsumer

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter([
            re_path(r'^ws/orders/(?P<restaurant_id>\d+)/$', OrderConsumer.as_asgi()),
        ])
    ),
})
