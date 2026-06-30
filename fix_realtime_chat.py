import os

# ── 1. Update Message model with status field ─────────────────────────────
models_py = '''from django.db import models
from django.conf import settings

class Conversation(models.Model):
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')
    job          = models.ForeignKey('jobs.Job', on_delete=models.SET_NULL, null=True, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('read', 'Read'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True, blank=True)
    sender       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content      = models.TextField()
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='sent')
    is_read      = models.BooleanField(default=False)
    timestamp    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
'''

path = os.path.join("HireMeBackend", "messaging", "models.py")
with open(path, "w", encoding="utf-8") as f:
    f.write(models_py)
print("✅ messaging/models.py - added status field (sent/delivered/read)")


# ── 2. Rewrite ChatConsumer for proper real-time delivery + ticks ─────────
consumer_py = '''from channels.generic.websocket import AsyncWebsocketConsumer
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

        # Mark any undelivered messages in this room as delivered now that user connected
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
                        'type':      'chat_message',
                        'message_id': msg_id,
                        'message':   message,
                        'sender_id': self.user.id,
                        'sender':    self.user.username,
                        'status':    'sent',
                    }
                )

            elif msg_type == 'mark_read':
                # Other user is viewing the chat - mark messages as read
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
            # Auto-create conversation from room name if it doesn't exist
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
print("✅ messaging/consumers.py - full real-time + delivery/read receipt system")


# ── 3. Create migration helper ─────────────────────────────────────────────
print("")
print("=========================================")
print("BACKEND DONE - run these next:")
print("=========================================")
print("  cd HireMeBackend")
print("  python manage.py makemigrations")
print("  python manage.py migrate")
print("")
