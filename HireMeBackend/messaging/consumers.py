from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']

        # FIXED: consistent group naming
        self.room_group_name = f'conversation_{self.room_name}'

        # AUTH
        self.user = await self.authenticate_user()

        if self.user is None:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)

        message_text = data.get('message', '')
        conversation_id = self.room_name

        # SAVE MESSAGE
        saved_msg = await self.save_message(
            self.user,
            conversation_id,
            message_text
        )

        # BROADCAST MESSAGE
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'id': saved_msg['id'],
                'message': message_text,
                'sender_id': self.user.id,
                'sender_username': self.user.username,
                'status': 'sent',
                'timestamp': saved_msg['timestamp'],
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'id': event['id'],
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_username': event['sender_username'],
            'status': event['status'],
            'timestamp': event['timestamp'],
        }))

    # =========================
    # AUTH FIXED
    # =========================
    async def authenticate_user(self):
        query_string = self.scope['query_string'].decode()
        token = None

        for part in query_string.split('&'):
            if part.startswith('token='):
                token = part.split('=', 1)[1]

        if not token:
            return None

        try:
            access = AccessToken(token)
            return await self.get_user(access['user_id'])
        except Exception:
            return None

    @database_sync_to_async
    def get_user(self, user_id):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    # =========================
    # SAVE MESSAGE FIXED
    # =========================
    @database_sync_to_async
    def save_message(self, sender, conversation_id, message):
        from .models import Conversation, Message

        try:
            conv = Conversation.objects.get(pk=conversation_id)
        except Conversation.DoesNotExist:
            return None

        msg = Message.objects.create(
            conversation=conv,
            sender=sender,
            content=message,
            status='sent'
        )

        return {
            'id': msg.id,
            'timestamp': msg.timestamp.isoformat()
        }