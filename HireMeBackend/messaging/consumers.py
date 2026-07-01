from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json
from django.utils import timezone
from rest_framework_simplejwt.tokens import AccessToken
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # We use conversation_id from routing.py
        self.conversation_id = self.scope['url_route']['kwargs']['conversation_id']
        self.room_group_name = f'chat_{self.conversation_id}'

        token = self.get_token()
        self.user = await self.get_user_from_token(token)

        if not self.user:
            await self.close()
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    def get_token(self):
        query = self.scope['query_string'].decode()
        for part in query.split("&"):
            if part.startswith("token="):
                return part.split("=", 1)[1]
        return None

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_text = data.get("message")
            conv_id = data.get("conversation_id") or self.conversation_id

            msg = await self.save_message(
                self.user,
                conv_id,
                message_text
            )

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "id": msg["id"],
                    "message": message_text,
                    "sender_id": self.user.id,
                    "sender_username": self.user.username,
                    "timestamp": msg["timestamp"],
                    "status": msg["status"]
                }
            )
        except Exception as e:
            print(f"WS Receive Error: {e}")

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def get_user_from_token(self, token):
        if not token: return None
        try:
            access = AccessToken(token)
            return User.objects.get(id=access["user_id"])
        except Exception:
            return None

    @database_sync_to_async
    def save_message(self, user, conversation_id, text):
        try:
            conv = Conversation.objects.get(id=conversation_id)
            msg = Message.objects.create(
                conversation=conv,
                sender=user,
                content=text,
                status="sent"
            )
            conv.save() # Update updated_at
            return {
                "id": msg.id,
                "timestamp": msg.timestamp.isoformat(),
                "status": msg.status
            }
        except Exception as e:
            print(f"Save Message Error: {e}")
            return {"id": 0, "timestamp": "", "status": "error"}

    @database_sync_to_async
    def mark_read(self, conversation_id):
        Message.objects.filter(
            conversation_id=conversation_id
        ).exclude(sender=self.user).update(status="read")
