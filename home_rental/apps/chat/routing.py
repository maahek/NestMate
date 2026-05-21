"""
NestMate — Django Channels WebSocket URL Routing

This file defines which URL patterns should be
handled as WebSocket connections instead of HTTP.

Imported by home_rental/asgi.py and passed to
the ProtocolTypeRouter's 'websocket' key.

WebSocket URL:
  ws://localhost:8000/ws/chat/<room_id>/

How it works:
  1. Browser opens WebSocket to ws://<host>/ws/chat/<room_id>/
  2. Channels routes it to ChatConsumer (in apps/chat/views.py)
  3. ChatConsumer.connect() verifies access + joins channel group
  4. Messages flow: Browser ↔ ChatConsumer ↔ Redis ↔ All group members
  5. ChatConsumer._save_message() writes to MongoDB on every message
"""

from django.urls import re_path
from apps.chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(
        r'^ws/chat/(?P<room_id>[a-fA-F0-9]+)/$',
        ChatConsumer.as_asgi(),
    ),
]