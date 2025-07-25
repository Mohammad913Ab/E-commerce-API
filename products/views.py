from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
)
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .serializers import ProductSerializer, ProductCommentSerializer
from core.utils import get_client_ip
from .models import (
    Product,
    ProductView,
    ProductLike
)

class ProductListAPIView(ListAPIView):
    """
    API view to retrieve a list of active products.

    Provides read-only access to products:
    - Supports searching by title and description (e.g., `?search=...`)
    - Supports ordering by price or creation date (e.g., `?ordering=-price`)

    Only products marked as is_active=True and is_delete=False will be returned.
    """
    queryset = Product.objects.filter(is_active=True, is_delete=False)
    serializer_class = ProductSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']


class ProductDetailAPIView(RetrieveAPIView):
    """
    API view to retrieve the details of a single product.

    Provides read-only access to a specific product by its ID:
    - Increments the product's view count only once per user or IP address.
    - Ensures each user/IP can only increment the view count once per product.

    View data is stored using the ProductView model.
    Only one view is recorded per unique combination of user (if authenticated) or IP.
    """
    queryset = Product.objects.filter(is_active=True, is_delete=False)
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        user = request.user if request.user.is_authenticated else None
        ip = get_client_ip(request)

        
        already_viewed = ProductView.objects.filter(
            Q(user=user) | Q(ip_address=ip),
            product=product
        ).exists()

        if not already_viewed:
            ProductView.objects.create(product=product, user=user, ip_address=ip)
            product.view_count += 1
            product.save(update_fields=['view_count'])

        serializer = self.get_serializer(product)
        return Response(serializer.data)
    
class ProductLikeCreateView(CreateAPIView):
    """
    API view to like a product.

    Allows authenticated users to like a product by its ID:
    - Ensures a user can only like a specific product once.
    - If the like already exists, returns an error response.
    - On successful like, increments the product's like count.

    Like data is stored using the ProductLike model.
    Only one like is recorded per unique combination of user and product.
    """

    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        
        like, created = ProductLike.objects.get_or_create(user=request.user, product=product)
        if not created:
            return Response(
                {'detail': 'You have already like this product.'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        product.like_count += 1
        product.save(update_fields=['like_count'])
        
        return Response(
            {
                'message': 'Product liked successfully.',
                'product_id': product.id,
                'likes': product.like_count
            },
            status=status.HTTP_201_CREATED
        )
        

class ProductCommentCreateView(CreateAPIView):
    """
    API view to create comments and replies for a product.

    Allows authenticated users to post:
    - A top-level comment on a product
    - A reply to an existing comment using the `reply` field

    Requirements:
    - The user must be authenticated
    - The `text` field is required
    - To reply to a comment, include the `reply` field with the parent comment's ID

    Example requests:
    - POST /products/1/comment/
      {
        "text": "Great product!"
      }

    - POST /products/1/comment/
      {
        "text": "I agree!",
        "reply": 5
      }

    Only comments marked as is_active=True and is_delete=False will be used in responses.
    """
    serializer_class = ProductCommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        product_id = self.kwargs.get('pk')
        serializer.save(user=self.request.user, product_id=product_id)
