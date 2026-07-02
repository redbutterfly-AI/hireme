from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name       = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user            = self.scope['user']

        if not self.user.is_authenticated:
            await self.close()
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data    = json.loads(text_data)
            message = data.get('message', '').strip()
            if not message:
                return

            sender = self.user
            await self.save_message(sender, message)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type':      'chat_message',
                    'message':   message,
                    'sender_id': sender.id,
                    'sender':    sender.username,
                }
            )
        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message':   event['message'],
            'sender_id': event['sender_id'],
            'sender':    event['sender'],
        }))

    @database_sync_to_async
    def save_message(self, sender, content):
        from .models import Message, Conversation
        # Find or create conversation from room name
        parts = self.room_name.split('_')
        if len(parts) == 2:
            try:
                id1, id2 = int(parts[0]), int(parts[1])
                conv = Conversation.objects.filter(
                    participants__id=id1
                ).filter(
                    participants__id=id2
                ).first()
                if conv:
                    Message.objects.create(
                        conversation=conv,
                        sender=sender,
                        content=content
                    )
                    conv.save()
            except Exception:
                pass
