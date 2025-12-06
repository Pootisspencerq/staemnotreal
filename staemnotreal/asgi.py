import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application 
# 1️⃣ Set Django settings module before anything else
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'staemnotreal.settings')
django.setup()  # ✅ initialize apps registry

# 2️⃣ Import your routing AFTER Django is ready
from notifications.routing import websocket_urlpatterns as notif_ws
from chat.routing import websocket_urlpatterns as chat_ws

# 3️⃣ Define ASGI application
application = ProtocolTypeRouter({
    "http": get_asgi_application(),  # optional, if you want HTTP to pass through
    "websocket": AuthMiddlewareStack(
        URLRouter(
            notif_ws + chat_ws
        )
    ),
})
