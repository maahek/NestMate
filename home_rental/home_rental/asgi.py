"""
NestMate — ASGI Configuration

Handles both:
  1. Normal HTTP requests  → Django views
  2. WebSocket connections → Django Channels (chat feature)

Run in production:
    daphne home_rental.asgi:application --port 8000 --bind 0.0.0.0

Or with uvicorn:
    uvicorn home_rental.asgi:application --host 0.0.0.0 --port 8000
"""
"""
NestMate ASGI config — handles both HTTP and WebSocket connections.
"""
import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home_rental.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.chat.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})