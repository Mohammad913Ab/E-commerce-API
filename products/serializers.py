from rest_framework import serializers
from .models import Product, ProductComment, ProductLike

class ProductSerializer(serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        exclude = ('is_active', 'is_delete', 'quantity')
        
    def get_comments(self, obj):
        comments = obj.comments.filter(is_active=True, is_delete=False, reply__isnull=True)
        return ProductCommentSerializer(comments, many=True).data
    
class ProductCommentSerializer(serializers.ModelSerializer):
    replies = serializers.SerializerMethodField()
    class Meta:
        model = ProductComment
        exclude = ('is_active', 'is_delete')
    
    def get_replies(self, obj):
        if obj.replies.exists():
            return ProductCommentSerializer(obj.replies.filter(is_active=True, is_delete=False), many=True).data
        return []


class ProductLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLike
        fields = ['id', 'product', 'user', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        
    