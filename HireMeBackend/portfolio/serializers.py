from rest_framework import serializers
from .models import PortfolioItem, PortfolioLike, PortfolioComment

class PortfolioCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    class Meta:
        model = PortfolioComment
        fields = ['id', 'username', 'text', 'created_at']

class PortfolioItemSerializer(serializers.ModelSerializer):
    likes_count = serializers.SerializerMethodField()
    comments = PortfolioCommentSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = PortfolioItem
        fields = ['id', 'caption', 'image_url', 'likes_count', 'is_liked', 'comments', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and request:
            return request.build_absolute_uri(obj.image.url)
        return None

    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
