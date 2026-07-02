from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import PortfolioItem, PortfolioLike, PortfolioComment
from .serializers import PortfolioItemSerializer, PortfolioCommentSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_portfolio(request, user_id):
    items = PortfolioItem.objects.filter(user_id=user_id).order_by('-created_at')
    serializer = PortfolioItemSerializer(items, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_portfolio(request):
    if request.user.role != 'seeker':
        return Response({'error': 'Only job seekers can upload portfolio items.'}, status=403)
    image = request.FILES.get('image')
    if not image:
        return Response({'error': 'No image provided.'}, status=400)
    caption = request.data.get('caption', '')
    item = PortfolioItem.objects.create(user=request.user, image=image, caption=caption)
    serializer = PortfolioItemSerializer(item, context={'request': request})
    return Response(serializer.data, status=201)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_portfolio(request, item_id):
    try:
        item = PortfolioItem.objects.get(pk=item_id, user=request.user)
        item.image.delete(save=False)
        item.delete()
        return Response({'message': 'Deleted successfully.'})
    except PortfolioItem.DoesNotExist:
        return Response({'error': 'Item not found.'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, item_id):
    try:
        item = PortfolioItem.objects.get(pk=item_id)
    except PortfolioItem.DoesNotExist:
        return Response({'error': 'Item not found.'}, status=404)
    like, created = PortfolioLike.objects.get_or_create(item=item, user=request.user)
    if not created:
        like.delete()
        return Response({'liked': False, 'likes_count': item.likes.count()})
    return Response({'liked': True, 'likes_count': item.likes.count()})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, item_id):
    try:
        item = PortfolioItem.objects.get(pk=item_id)
    except PortfolioItem.DoesNotExist:
        return Response({'error': 'Item not found.'}, status=404)
    text = request.data.get('text', '').strip()
    if not text:
        return Response({'error': 'Comment cannot be empty.'}, status=400)
    comment = PortfolioComment.objects.create(item=item, user=request.user, text=text)
    serializer = PortfolioCommentSerializer(comment)
    return Response(serializer.data, status=201)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    try:
        comment = PortfolioComment.objects.get(pk=comment_id, user=request.user)
        comment.delete()
        return Response({'message': 'Comment deleted.'})
    except PortfolioComment.DoesNotExist:
        return Response({'error': 'Comment not found.'}, status=404)
