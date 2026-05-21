"""Django Channels Chat Consumer.

This implementation mirrors the working consumer in `apps/chat/views.py`.
It verifies authentication/access, saves messages as embedded documents
and broadcasts events to the channel group.
"""
import json
import logging
from datetime import datetime, timezone
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

logger = logging.getLogger('apps.chat.consumer')


def _iso_timestamp(value: datetime) -> str:
    if not value:
        return ''
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group = f'chat_{self.room_id}'
        self.user = self.scope.get('user')

        # Verify Django session user
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # Verify access to room
        has_access = await self._check_access()
        if not has_access:
            await self.close(code=4003)
            return

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

        # Announce join
        mongo_user = await self._get_mongo_user()
        if mongo_user:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type': 'user_joined',
                    'user_name': mongo_user.get_full_name(),
                    'user_id': str(mongo_user.id),
                }
            )

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Invalid JSON'}))
            return

        msg_type = data.get('msg_type', 'text')
        content = data.get('content', '').strip()
        offer_amt = data.get('offer_amt')

        mongo_user = await self._get_mongo_user()
        sender_id = str(mongo_user.id) if mongo_user else ''

        if msg_type == 'typing':
            await self.channel_layer.group_send(self.room_group, {
                'type': 'typing_indicator',
                'sender_id': sender_id,
            })
            return

        if not content and msg_type == 'text':
            return

        if not sender_id:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Authentication failed'}))
            return

        result = await self._save_message(
            sender_id=sender_id,
            content=content,
            msg_type=msg_type,
            offer_amt=int(offer_amt) if offer_amt else None,
        )
        if not result:
            await self.send(text_data=json.dumps({'type': 'error', 'message': 'Unable to save message'}))
            return

        timestamp, msg_id, duplicated = result
        if duplicated:
            return

        await self.channel_layer.group_send(self.room_group, {
            'type': 'chat_message',
            'sender_id': sender_id,
            'content': content,
            'msg_type': msg_type,
            'offer_amt': offer_amt,
            'timestamp': timestamp,
            'message_id': msg_id,
        })

        if msg_type == 'deal' and offer_amt:
            await self.channel_layer.group_send(self.room_group, {
                'type': 'deal_struck',
                'agreed_rent': int(offer_amt),
                'sender_id': sender_id,
            })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'sender_id': event['sender_id'],
            'content': event['content'],
            'msg_type': event['msg_type'],
            'offer_amt': event.get('offer_amt'),
            'timestamp': event['timestamp'],
            'message_id': event.get('message_id', ''),
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({'type': 'typing', 'sender_id': event['sender_id']}))

    async def user_joined(self, event):
        await self.send(text_data=json.dumps({'type': 'user_joined', 'user_name': event['user_name'], 'user_id': event['user_id']}))

    async def deal_struck(self, event):
        await self.send(text_data=json.dumps({'type': 'deal_struck', 'agreed_rent': event['agreed_rent']}))

    @database_sync_to_async
    def _get_mongo_user(self):
        from apps.accounts.models import User
        return User.objects(email=self.user.email).first()

    @database_sync_to_async
    def _check_access(self):
        try:
            from apps.listings.models import ChatRoom
            from apps.accounts.models import User
            room = ChatRoom.objects.get(id=self.room_id)
            mongo_user = User.objects(email=self.user.email).first()
            if not mongo_user:
                return False
            user_id = str(mongo_user.id)
            return str(room.tenant.id) == user_id or str(room.owner.id) == user_id
        except Exception:
            return False

    @database_sync_to_async
    def _save_message(self, sender_id, content, msg_type, offer_amt=None):
        try:
            from apps.listings.models import ChatRoom, Message as ChatMessage
            room = ChatRoom.objects.get(id=self.room_id)
        except Exception:
            logger.warning('Unable to load room %s for save', self.room_id, exc_info=True)
            return None

        now = datetime.utcnow()

        duplicated = False
        last = None
        try:
            last = room.messages[-1] if room.messages else None
            if last and last.sender_id == (sender_id or '') and last.content == (content or '') and last.msg_type == (msg_type or '') and (last.offer_amt or None) == (offer_amt or None):
                delta = (now - last.timestamp).total_seconds() if last.timestamp else 9999
                if abs(delta) < 5:
                    duplicated = True
        except Exception:
            duplicated = False

        if duplicated:
            prev_ts = _iso_timestamp(last.timestamp) if last and last.timestamp else ''
            msg_id = str(getattr(last, 'id', f'{sender_id}_{int(now.timestamp())}'))
            return (prev_ts, msg_id, True)

        msg = ChatMessage(
            sender_id=sender_id,
            content=content,
            msg_type=msg_type,
            offer_amt=offer_amt,
            timestamp=now,
            is_read=False,
        )
        room.messages.append(msg)

        if msg_type == 'deal' and offer_amt:
            room.agreed_rent = offer_amt
            room.status = 'deal_done'

        room.last_message_at = now
        room.save()

        msg_id = str(getattr(msg, 'id', f'{sender_id}_{int(now.timestamp())}'))
        return (_iso_timestamp(now), msg_id, False)