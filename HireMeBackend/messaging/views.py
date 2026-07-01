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

    if not other_id:
        return Response({'error': 'user_id is required.'}, status=400)

    try:
        other = User.objects.get(pk=other_id)
    except (User.DoesNotExist, ValueError, TypeError):
        return Response({'error': 'User not found.'}, status=404)

    if other == request.user:
        return Response({'error': 'You cannot chat with yourself.'}, status=400)

    # Find conversation with EXACTLY these participants?
    # For simplicity, we find any conversation containing both.
    existing = Conversation.objects.filter(
        participants=request.user
    ).filter(participants=other).first()

    if existing:
        conv = existing
    else:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other)

    if job_id:
        try:
            from jobs.models import Job
            job = Job.objects.get(pk=job_id)
            conv.job = job
            conv.save()
        except (Job.DoesNotExist, ValueError, TypeError):
            pass

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
    ).exclude(sender=request.user).update(status='read')

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
    ).exclude(sender=request.user).update(status='read')

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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def unread_messages_count(request):
    count = Message.objects.filter(
        conversation__participants=request.user
    ).exclude(status='read').exclude(sender=request.user).count()
    return Response({'unread_count': count})
