import os

consumer_py = '''from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import json


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

        await self.mark_delivered()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data     = json.loads(text_data)
            msg_type = data.get('type', 'message')

            if msg_type == 'message':
                message = data.get('message', '').strip()
                if not message:
                    return

                msg_id = await self.save_message(self.user, message)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type':       'chat_message',
                        'message_id': msg_id,
                        'message':    message,
                        'sender_id':  self.user.id,
                        'sender':     self.user.username,
                        'status':     'sent',
                    }
                )

            elif msg_type == 'mark_read':
                await self.mark_read()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type':      'read_receipt',
                        'reader_id': self.user.id,
                    }
                )

        except Exception as e:
            await self.send(text_data=json.dumps({'error': str(e)}))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type':       'message',
            'message_id': event.get('message_id'),
            'message':    event['message'],
            'sender_id':  event['sender_id'],
            'sender':     event['sender'],
            'status':     event.get('status', 'sent'),
        }))

    async def read_receipt(self, event):
        await self.send(text_data=json.dumps({
            'type':      'read_receipt',
            'reader_id': event['reader_id'],
        }))

    def _get_conversation(self):
        from .models import Conversation
        parts = self.room_name.split('_')
        if len(parts) == 2:
            try:
                id1, id2 = int(parts[0]), int(parts[1])
                return Conversation.objects.filter(
                    participants__id=id1
                ).filter(
                    participants__id=id2
                ).first()
            except Exception:
                return None
        return None

    @database_sync_to_async
    def save_message(self, sender, content):
        from .models import Message, Conversation
        conv = self._get_conversation()
        if not conv:
            parts = self.room_name.split('_')
            if len(parts) == 2:
                try:
                    id1, id2 = int(parts[0]), int(parts[1])
                    conv = Conversation.objects.create()
                    conv.participants.add(id1, id2)
                except Exception:
                    return None
        if conv:
            msg = Message.objects.create(
                conversation=conv,
                sender=sender,
                content=content,
                status='sent'
            )
            conv.save()
            return msg.id
        return None

    @database_sync_to_async
    def mark_delivered(self):
        from .models import Message
        conv = self._get_conversation()
        if conv:
            Message.objects.filter(
                conversation=conv,
                status='sent'
            ).exclude(sender=self.user).update(status='delivered')

    @database_sync_to_async
    def mark_read(self):
        from .models import Message
        conv = self._get_conversation()
        if conv:
            Message.objects.filter(
                conversation=conv
            ).exclude(sender=self.user).update(status='read', is_read=True)
'''

path = os.path.join("HireMeBackend", "messaging", "consumers.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(consumer_py)
print("✅ messaging/consumers.py - removed module-level get_user_model() call")
print("   (was causing AppRegistryNotReady error)")
print("")
print("Now restart backend: start_backend.ps1")
