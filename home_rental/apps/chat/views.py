"""
NestMate — Chat & Negotiation Views + WebSocket Consumer
Feature 10: Real-time Rental Negotiation Chat

Django Views handle:
  - Chat room list
  - Start a new chat room
  - Chat room page (WebSocket connects here)
  - Mark messages as read
  - Close / archive a chat

Django Channels WebSocket Consumer handles:
  - Real-time message send/receive
  - Offer / counter-offer / deal messages
  - Auto-save every message to MongoDB
"""

import json
import logging
from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.views import View

# Django Channels
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from mongoengine.errors import DoesNotExist

from apps.listings.models import ChatRoom, Listing, Message as ChatMessage
from apps.accounts.models import User

logger = logging.getLogger('apps.chat')


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def get_mongo_user(django_user):
    """Resolve Django session user → MongoEngine User by email."""
    return User.objects(email=django_user.email).first()


def _iso_timestamp(value: datetime) -> str:
    if not value:
        return ''
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')


def _safe_reference(doc, field_name):
    try:
        return getattr(doc, field_name)
    except (DoesNotExist, AttributeError, ValueError) as exc:
        logger.warning(
            'Failed to dereference %s on room %s: %s',
            field_name, getattr(doc, 'id', '<unknown>'), exc,
            exc_info=True,
        )
        return None


def _user_display_name(user):
    if not user:
        return 'User'
    display = getattr(user, 'get_full_name', None)
    if callable(display):
        return display() or getattr(user, 'full_name', None) or getattr(user, 'username', 'User')
    return getattr(user, 'full_name', None) or getattr(user, 'username', 'User') or 'User'


def _serialize_message(msg: ChatMessage) -> dict:
    """Convert an embedded chat message document to a JSON-safe dict."""
    message_id = getattr(msg, 'id', None)
    if not message_id:
        timestamp_epoch = int(msg.timestamp.timestamp()) if msg.timestamp else 0
        message_id = f'{msg.sender_id or "unknown"}-{timestamp_epoch}-{hash(msg.content or "") & 0xfffff}'

    return {
        'id':        str(message_id),
        'sender_id': str(msg.sender_id or ''),
        'content':   msg.content or '',
        'msg_type':  msg.msg_type or 'text',
        'offer_amt': msg.offer_amt,
        'timestamp': _iso_timestamp(msg.timestamp),
        'is_read':   bool(msg.is_read),
    }


def _serialize_room(room: ChatRoom, current_user_id: str) -> dict:
    """Convert a ChatRoom document to a JSON-safe dict for the room list."""
    listing     = _safe_reference(room, 'listing')
    tenant      = _safe_reference(room, 'tenant')
    owner       = _safe_reference(room, 'owner')
    last_msg    = room.get_last_message()
    unread      = room.get_unread_count(current_user_id)

    if tenant and str(getattr(tenant, 'id', '')) == current_user_id:
        other_party = owner
    else:
        other_party = tenant

    return {
        'id':            str(room.id),
        'listing_id':    str(getattr(listing, 'id', '')) if listing else '',
        'listing_title': getattr(listing, 'title', 'Deleted listing') if listing else 'Deleted listing',
        'listing_rent':  getattr(listing, 'rent', 0) if listing else 0,
        'other_name':    _user_display_name(other_party),
        'other_avatar':  getattr(other_party, 'avatar_url', ''),
        'status':        room.status or 'active',
        'agreed_rent':   room.agreed_rent,
        'unread':        unread,
        'last_message':       last_msg.content if last_msg else 'No messages yet',
        'last_msg_type':      last_msg.msg_type if last_msg else 'text',
        'last_msg_time':      last_msg.timestamp.strftime('%d %b, %I:%M %p') if last_msg and last_msg.timestamp else '',
        'last_msg_timestamp': _iso_timestamp(last_msg.timestamp) if last_msg and last_msg.timestamp else '',
    }


# ══════════════════════════════════════════════════════════════════════════════
# 1. CHAT ROOM LIST
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ChatListView(View):
    """
    Shows all chat rooms for the logged-in user.
    Displays both rooms where user is tenant AND owner.
    Sorted by latest message time.
    """

    def get(self, request):
        mongo_user    = get_mongo_user(request.user)
        if not mongo_user:
            return JsonResponse({'error': 'User not found'}, status=404)
        mongo_user_id = str(mongo_user.id)

        # ── Rooms where I am the tenant ────────────────────────────────────────
        tenant_rooms = list(
            ChatRoom.objects(tenant=mongo_user)
            .order_by('-last_message_at')
        )

        # ── Rooms where I am the owner ─────────────────────────────────────────
        owner_rooms = list(
            ChatRoom.objects(owner=mongo_user)
            .order_by('-last_message_at')
        )

        # ── Merge and sort by last_message_at ─────────────────────────────────
        all_rooms = sorted(
            tenant_rooms + owner_rooms,
            key=lambda r: r.last_message_at or datetime.min,
            reverse=True,
        )

        # ── Total unread count (for nav badge) ────────────────────────────────
        total_unread = sum(
            r.get_unread_count(mongo_user_id)
            for r in all_rooms
        )

        # ── Separate by status ─────────────────────────────────────────────────
        active_rooms = [r for r in all_rooms if r.status == 'active']
        deal_rooms   = [r for r in all_rooms if r.status == 'deal_done']
        closed_rooms = [r for r in all_rooms if r.status == 'closed']

        context = {
            'mongo_user':    mongo_user,
            'mongo_user_id': mongo_user_id,
            'active_rooms':  active_rooms,
            'deal_rooms':    deal_rooms,
            'closed_rooms':  closed_rooms,
            'total_unread':  total_unread,
            'total_rooms':   len(all_rooms),
        }

        rooms_data = []
        for room in all_rooms:
            try:
                rooms_data.append(_serialize_room(room, mongo_user_id))
            except Exception as exc:
                logger.warning(
                    'Skipping invalid chat room %s in list view: %s',
                    getattr(room, 'id', '<unknown>'),
                    exc,
                    exc_info=True,
                )

        total_unread = sum(r['unread'] for r in rooms_data)

        return JsonResponse({
            'rooms':        rooms_data,
            'total_unread': total_unread,
        })

# ══════════════════════════════════════════════════════════════════════════════
# 2. START A NEW CHAT ROOM
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class StartChatView(View):
    """
    POST: Tenant initiates a chat with the listing owner.
    If a chat room already exists for this (listing, tenant) pair,
    redirect to existing room instead of creating a duplicate.
    """

    def post(self, request, listing_id):
        mongo_user = get_mongo_user(request.user)

        # ── Fetch listing ──────────────────────────────────────────────────────
        try:
            listing = Listing.objects.get(id=listing_id)
        except (Listing.DoesNotExist, Exception):
            error_msg = 'Listing not found.'
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': error_msg}, status=404)
            messages.error(request, error_msg)
            return redirect('home')

        # ── Owner cannot chat with themselves ──────────────────────────────────
        if str(listing.owner.id) == str(mongo_user.id):
            error_msg = "You can't start a chat on your own listing."
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'error': error_msg}, status=400)
            messages.warning(request, error_msg)
            return redirect('listing_detail', listing_id=listing_id)

        # ── Check for existing room ────────────────────────────────────────────
        existing_room = ChatRoom.objects(
            listing=listing,
            tenant=mongo_user,
        ).first()

        if existing_room:
            # Room already exists — go straight there
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({
                    'room_id': str(existing_room.id),
                    'message': 'Chat room already exists',
                })
            return redirect('chat_room', room_id=str(existing_room.id))

        # ── Create new room ────────────────────────────────────────────────────
        room = ChatRoom(
            listing = listing,
            tenant  = mongo_user,
            owner   = listing.owner,
            status  = 'active',
        )
        room.save()

        if request.headers.get('Accept') == 'application/json':
            return JsonResponse({
                'room_id': str(room.id),
                'message': 'Chat started',
            })

        messages.success(
            request,
            f'💬 Chat started with {listing.owner.get_full_name()}!'
        )
        return redirect('chat_room', room_id=str(room.id))
    def get(self, request, listing_id):
        """GET → just redirect to the listing page."""
        return redirect('listing_detail', listing_id=listing_id)


# ══════════════════════════════════════════════════════════════════════════════
# 3. CHAT ROOM PAGE
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class ChatRoomView(View):
    def get(self, request, room_id):
        mongo_user = User.objects(email=request.user.email).first()
        try:
            room = ChatRoom.objects.get(id=room_id)
        except Exception:
            return JsonResponse({'error': 'Room not found'}, status=404)

        listing = _safe_reference(room, 'listing')
        messages = sorted(
            (room.messages or []),
            key=lambda m: m.timestamp or datetime.min,
        )

        return JsonResponse({
            'room_id':      str(room.id),
            'room_status':  room.status or 'active',
            'agreed_rent':  room.agreed_rent,
            'listing_id':   str(getattr(listing, 'id', '')) if listing else '',
            'listing_title': getattr(listing, 'title', 'Deleted listing') if listing else 'Deleted listing',
            'listing_rent':  getattr(listing, 'rent', 0) if listing else 0,
            'messages':     [_serialize_message(m) for m in messages],
        })
# ══════════════════════════════════════════════════════════════════════════════
# 4. CLOSE / ARCHIVE CHAT
# ══════════════════════════════════════════════════════════════════════════════

@method_decorator(login_required, name='dispatch')
class CloseChatView(View):
    """
    POST: Mark a chat room as closed.
    Only the owner can close the chat.
    """

    def post(self, request, room_id):
        mongo_user = get_mongo_user(request.user)

        try:
            room = ChatRoom.objects.get(id=room_id)
        except (ChatRoom.DoesNotExist, Exception):
            messages.error(request, 'Chat room not found.')
            return redirect('chat_list')

        # ── Only owner can close ───────────────────────────────────────────────
        try:
            owner_id = str(room.owner.id)
        except Exception:
            owner_id = ''

        if owner_id != str(mongo_user.id):
            messages.error(request, '❌ Only the property owner can close a chat.')
            return redirect('chat_room', room_id=room_id)

        room.update(status='closed')
        messages.info(request, 'Chat has been closed.')
        return redirect('chat_list')


# ══════════════════════════════════════════════════════════════════════════════
# 5. MARK ALL MESSAGES AS READ (AJAX)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def mark_read(request, room_id):
    """
    POST: Mark all messages in a room as read for the current user.
    Called via AJAX when user opens a chat room.
    Returns: JSON { success: true, marked: <count> }
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    mongo_user    = get_mongo_user(request.user)
    mongo_user_id = str(mongo_user.id)

    try:
        room = ChatRoom.objects.get(id=room_id)
    except (ChatRoom.DoesNotExist, Exception):
        return JsonResponse({'error': 'Room not found'}, status=404)

    # Access check
    tenant_id = ''
    owner_id = ''
    try:
        tenant_id = str(room.tenant.id)
    except Exception:
        tenant_id = ''
    try:
        owner_id = str(room.owner.id)
    except Exception:
        owner_id = ''

    if tenant_id != mongo_user_id and owner_id != mongo_user_id:
        return JsonResponse({'error': 'Access denied'}, status=403)

    # Mark received messages
    count   = 0
    updated = False
    for msg in room.messages:
        if msg.sender_id != mongo_user_id and not msg.is_read:
            msg.is_read = True
            count  += 1
            updated = True

    if updated:
        room.save()

    return JsonResponse({'success': True, 'marked': count})


# ══════════════════════════════════════════════════════════════════════════════
# 6. GET MESSAGES (AJAX — polling fallback if WebSocket fails)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def get_messages(request, room_id):
    """GET /chat/<room_id>/messages/"""
    try:
        from apps.listings.models import ChatRoom
        from apps.accounts.models import User

        room = ChatRoom.objects(id=room_id).first()
        if not room:
            return JsonResponse({'error': 'Room not found'}, status=404)

        since = request.GET.get('since', '').strip()
        since_dt = None
        if since:
            try:
                if since.endswith('Z'):
                    since = since[:-1]
                since_dt = datetime.fromisoformat(since)
            except ValueError:
                return JsonResponse({'error': 'Invalid since timestamp'}, status=400)

        messages = sorted(
            (room.messages or []),
            key=lambda m: m.timestamp or datetime.min,
        )
        if since_dt:
            messages = [m for m in messages if m.timestamp and m.timestamp > since_dt]

        listing = _safe_reference(room, 'listing')

        return JsonResponse({
            'room_id':      str(room.id),
            'room_status':  room.status or 'active',
            'agreed_rent':  room.agreed_rent,
            'listing_id':   str(getattr(listing, 'id', '')) if listing else '',
            'listing_title': getattr(listing, 'title', 'Deleted listing') if listing else 'Deleted listing',
            'listing_rent':  getattr(listing, 'rent', 0) if listing else 0,
            'messages':     [_serialize_message(m) for m in messages],
        })
    except Exception as e:
        logger.exception('Error loading chat messages for room %s', room_id)
        return JsonResponse({'error': 'Unable to load messages'}, status=500)


# ══════════════════════════════════════════════════════════════════════════════
# 7. CHAT ROOMS API (JSON list — for mobile / AJAX)
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def chat_rooms_api(request):
    """
    GET: Return all chat rooms for the logged-in user as JSON.
    Used by mobile app or nav badge to show unread count.
    Returns: JSON { rooms: [...], total_unread }
    """
    mongo_user    = get_mongo_user(request.user)
    if not mongo_user:
        return JsonResponse({'error': 'User not found'}, status=404)
    mongo_user_id = str(mongo_user.id)

    tenant_rooms = list(ChatRoom.objects(tenant=mongo_user).order_by('-last_message_at'))
    owner_rooms  = list(ChatRoom.objects(owner=mongo_user).order_by('-last_message_at'))
    all_rooms    = sorted(
        tenant_rooms + owner_rooms,
        key=lambda r: r.last_message_at or datetime.min,
        reverse=True,
    )

    rooms_data = []
    for room in all_rooms:
        try:
            rooms_data.append(_serialize_room(room, mongo_user_id))
        except Exception as exc:
            logger.warning(
                'Skipping invalid chat room %s in API response: %s',
                getattr(room, 'id', '<unknown>'),
                exc,
                exc_info=True,
            )

    total_unread = sum(r['unread'] for r in rooms_data)

    return JsonResponse({
        'rooms':        rooms_data,
        'total_unread': total_unread,
    })


# ══════════════════════════════════════════════════════════════════════════════
# 8. WEBSOCKET CONSUMER
# ══════════════════════════════════════════════════════════════════════════════

class ChatConsumer(AsyncWebsocketConsumer):
    """
    Django Channels WebSocket Consumer.

    Lifecycle:
      connect()    → join room channel group
      receive()    → parse message, save to MongoDB, broadcast to group
      disconnect() → leave room channel group

    Message types:
      text    → normal chat message
      offer   → tenant makes a rent offer (e.g. ₹9,000)
      counter → owner counters with a different amount
      deal    → either party accepts → sets agreed_rent + status='deal_done'
      typing  → typing indicator (not saved to DB)

    Channel group name: chat_<room_id>
    All users in the same room are in the same group.
    """

    # ── Connect ───────────────────────────────────────────────────────────────
    async def connect(self):
        self.room_id     = self.scope['url_route']['kwargs']['room_id']
        self.room_group  = f'chat_{self.room_id}'
        self.user        = self.scope.get('user')

        # ── Verify user is authenticated ───────────────────────────────────────
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4001)
            return

        # ── Verify user has access to this room ────────────────────────────────
        has_access = await self._check_access()
        if not has_access:
            await self.close(code=4003)
            return

        # ── Join channel group ─────────────────────────────────────────────────
        await self.channel_layer.group_add(
            self.room_group,
            self.channel_name,
        )
        await self.accept()

        # ── Send join notification to room ─────────────────────────────────────
        mongo_user = await self._get_mongo_user()
        if mongo_user:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':      'user_joined',
                    'user_name': mongo_user.get_full_name(),
                    'user_id':   str(mongo_user.id),
                }
            )

    # ── Disconnect ────────────────────────────────────────────────────────────
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group,
            self.channel_name,
        )

    # ── Receive from WebSocket ────────────────────────────────────────────────
    async def receive(self, text_data):
        """
        Called when a message arrives from the browser WebSocket.
        Expected JSON payload:
        {
            "type":      "chat_message",
            "msg_type":  "text" | "offer" | "counter" | "deal" | "typing",
            "content":   "Can you reduce rent?",
            "offer_amt": 9000,         ← only for offer/counter/deal
            "sender_id": "<mongo_user_id>"
        }
        """
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type':    'error',
                'message': 'Invalid JSON',
            }))
            return

        msg_type = data.get('msg_type', 'text')
        content = data.get('content', '').strip()
        offer_amt = data.get('offer_amt')

        mongo_user = await self._get_mongo_user()
        sender_id = str(mongo_user.id) if mongo_user else ''

        # ── Typing indicator — broadcast only, don't save ──────────────────────
        if msg_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':      'typing_indicator',
                    'sender_id': sender_id,
                }
            )
            return

        # ── Validate content ───────────────────────────────────────────────────
        if not content and msg_type == 'text':
            return

        if not sender_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Authentication failed',
            }))
            return

        # ── Save message to MongoDB ────────────────────────────────────────────
        result = await self._save_message(
            sender_id = sender_id,
            content   = content,
            msg_type  = msg_type,
            offer_amt = int(offer_amt) if offer_amt else None,
        )
        if not result:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Unable to save message',
            }))
            return

        timestamp, msg_id, duplicated = result
        if duplicated:
            return

        # ── Broadcast to everyone in the room ──────────────────────────────────
        await self.channel_layer.group_send(
            self.room_group,
            {
                'type':      'chat_message',
                'sender_id': sender_id,
                'content':   content,
                'msg_type':  msg_type,
                'offer_amt': offer_amt,
                'timestamp': timestamp,
                'message_id': msg_id,
            }
        )

        # ── If deal struck — send special deal event ───────────────────────────
        if msg_type == 'deal' and offer_amt:
            await self.channel_layer.group_send(
                self.room_group,
                {
                    'type':        'deal_struck',
                    'agreed_rent': int(offer_amt),
                    'sender_id':   sender_id,
                }
            )

    # ── Event Handlers (called by channel layer group_send) ───────────────────

    async def chat_message(self, event):
        """Forward a chat message to the WebSocket client."""
        await self.send(text_data=json.dumps({
            'type':       'chat_message',
            'sender_id':  event['sender_id'],
            'content':    event['content'],
            'msg_type':   event['msg_type'],
            'offer_amt':  event.get('offer_amt'),
            'timestamp':  event['timestamp'],
            'message_id': event.get('message_id', ''),
        }))

    async def typing_indicator(self, event):
        """Forward typing indicator to WebSocket client."""
        await self.send(text_data=json.dumps({
            'type':      'typing',
            'sender_id': event['sender_id'],
        }))

    async def user_joined(self, event):
        """Notify room that a user has joined."""
        await self.send(text_data=json.dumps({
            'type':      'user_joined',
            'user_name': event['user_name'],
            'user_id':   event['user_id'],
        }))

    async def deal_struck(self, event):
        """Notify room that a deal has been reached."""
        await self.send(text_data=json.dumps({
            'type':        'deal_struck',
            'agreed_rent': event['agreed_rent'],
        }))

    # ── Database Helpers (sync wrapped for async) ─────────────────────────────

    @database_sync_to_async
    def _get_mongo_user(self):
        """Get MongoEngine User from Django session user."""
        return User.objects(email=self.user.email).first()

    @database_sync_to_async
    def _check_access(self):
        """
        Return True if the current Django user is either
        the tenant or the owner of this chat room.
        """
        try:
            room       = ChatRoom.objects.get(id=self.room_id)
            mongo_user = User.objects(email=self.user.email).first()
            if not mongo_user:
                return False
            user_id = str(mongo_user.id)
            return (
                str(room.tenant.id) == user_id or
                str(room.owner.id)  == user_id
            )
        except Exception:
            return False

    @database_sync_to_async
    def _save_message(
        self,
        sender_id: str,
        content: str,
        msg_type: str,
        offer_amt: int = None,
    ) -> str:
        """
        Save a message to the ChatRoom's embedded messages list.
        Returns formatted timestamp string.
        """
        try:
            room = ChatRoom.objects.get(id=self.room_id)
        except Exception:
            logger.warning('Unable to load chat room %s for saving message', self.room_id, exc_info=True)
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
            sender_id = sender_id,
            content   = content,
            msg_type  = msg_type,
            offer_amt = offer_amt,
            timestamp = now,
            is_read   = False,
        )
        room.messages.append(msg)

        # ── Handle deal: set agreed_rent + close negotiation ───────────────────
        if msg_type == 'deal' and offer_amt:
            room.agreed_rent = offer_amt
            room.status = 'deal_done'

        room.last_message_at = now
        room.save()

        msg_id = str(getattr(msg, 'id', f'{sender_id}_{int(now.timestamp())}'))
        return (_iso_timestamp(now), msg_id, False)