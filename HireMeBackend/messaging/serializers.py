from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.username', read_only=True)
    sender_picture = serializers.SerializerMethodField()
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'sender_picture', 'content', 'status', 'is_read', 'timestamp']
        read_only_fields = ['sender', 'timestamp']

    def get_is_read(self, obj):
        return obj.status == 'read'

    def get_sender_picture(self, obj):
        request = self.context.get('request')
        if obj.sender.profile_picture and request:
            return request.build_absolute_uri(obj.sender.profile_picture.url)
        return None

class ConversationSerializer(serializers.ModelSerializer):
    last_message    = serializers.SerializerMethodField()
    other_user      = serializers.SerializerMethodField()
    unread_count    = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'job', 'last_message', 'other_user', 'unread_count', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-timestamp').first()
        if msg:
            return {'content': msg.content, 'timestamp': msg.timestamp}
        return None

    def get_other_user(self, obj):
        request = self.context.get('request')
        user    = request.user if request else None
        other   = obj.participants.exclude(id=user.id).first() if user else None
        if other:
            pic = request.build_absolute_uri(other.profile_picture.url) if other.profile_picture and request else None
            return {'id': other.id, 'username': other.username, 'profile_picture': pic, 'role': other.role}
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        user    = request.user if request else None
        if user:
            return obj.messages.exclude(status='read').exclude(sender=user).count()
        return 0
