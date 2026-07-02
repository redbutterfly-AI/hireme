from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_conversations(request):
    convs = Conversation.objects.filter(
        participants=request.user
    ).order_by('-updated_at')
    serializer = ConversationSerializer(convs, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    other_id = request.data.get('user_id')
    job_id   = request.data.get('job_id')
    try:
        other = User.objects.get(pk=other_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other)
    if existing.exists():
        conv = existing.first()
    else:
        conv = Conversation.objects.create()
        if job_id:
            try:
                from jobs.models import Job
                conv.job = Job.objects.get(pk=job_id)
                conv.save()
            except Exception:
                pass
        conv.participants.add(request.user, other)

    serializer = ConversationSerializer(conv, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_messages(request, conv_id):
    try:
        conv = Conversation.objects.get(pk=conv_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found.'}, status=404)

    Message.objects.filter(
        conversation=conv
    ).exclude(sender=request.user).update(is_read=True)

    messages = conv.messages.order_by('timestamp')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_with_user(request, user_id):
    """Get messages between current user and another user"""
    try:
        other = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found.'}, status=404)

    conv = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other).first()

    if not conv:
        return Response([])

    Message.objects.filter(
        conversation=conv
    ).exclude(sender=request.user).update(is_read=True)

    messages = conv.messages.order_by('timestamp')
    serializer = MessageSerializer(messages, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_message(request, conv_id):
    try:
        conv = Conversation.objects.get(pk=conv_id, participants=request.user)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found.'}, status=404)

    content = request.data.get('content', '').strip()
    if not content:
        return Response({'error': 'Message cannot be empty.'}, status=400)

    msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
    conv.save()
    serializer = MessageSerializer(msg, context={'request': request})
    return Response(serializer.data, status=201)
