import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from django.urls import path
from notifications.consumers import NotificationsConsumer

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')

django_app = get_asgi_application()

websocket_urlpatterns = [
    path("ws/notifications/", NotificationsConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    "http": django_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
