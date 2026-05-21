from django.urls import path
from apps.chat.views import (
    ChatListView,
    ChatRoomView,
    StartChatView,
    CloseChatView,
    mark_read,
    get_messages,
    chat_rooms_api,
)

urlpatterns = [
    # ── API endpoints ──────────────────────────────────────────────────────
    path('api/rooms/',                    chat_rooms_api,              name='chat_rooms_api'),
    path('start/<str:listing_id>/',       StartChatView.as_view(),     name='start_chat'),
    path('<str:room_id>/messages/',        get_messages,                name='get_messages'),
    path('<str:room_id>/mark-read/',       mark_read,                   name='mark_read'),
    path('<str:room_id>/close/',           CloseChatView.as_view(),     name='close_chat'),
]