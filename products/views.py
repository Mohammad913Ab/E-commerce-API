from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
    CreateAPIView,
)
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status, permissions
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch, F

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
    

class ProductLikeToggleView(APIView):
    """
    API view to like or unlike a product.

    This endpoint allows authenticated users to toggle their like status on a product:
    - If the user has not liked the product yet, a like will be created.
    - If the user has already liked the product, the like will be removed (unlike).
    - Always returns the updated like status and the total like count for the product.

    Rules:
    - Only authenticated users can access this endpoint.
    - Each user can have at most one like per product.
    - Like data is stored in the `ProductLike` model, ensuring uniqueness via a constraint.

    Response JSON example:
    {
        "product_id": 42,
        "liked": true,
        "like_count": 15
    }
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk, *args, **kwargs):
        product = get_object_or_404(Product, pk=pk)
        like_qs = ProductLike.objects.filter(user=request.user, product=product)

        if like_qs.exists():
            like_qs.delete()
            liked = False
            like_count = product.like_count - 1
        else:
            ProductLike.objects.create(user=request.user, product=product)
            liked = True
            like_count = product.like_count + 1
            
        product.like_count = like_count
        product.save()

        return Response(
            {
                'product_id': product.id,
                'liked': liked,
                'like_count': like_count
            },
            status=status.HTTP_200_OK
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


class LikedProductsListView(ListAPIView):
    """
    API view to retrieve all products liked by the authenticated user.

    Features:
    - Only authenticated users can access.
    - Returns Product objects that the current user has liked.
    - Optimized to avoid N+1 queries by:
        * `select_related('category')` for category FK (if used in serializer).
        * `prefetch_related('likes')` to load likes efficiently (if serializer uses it).

    Queryset Notes:
    - Filtering is done via `likes__user=self.request.user`.
    - You can add ordering, filtering, and pagination via DRF settings.

    Example response:
    [
        {
            "id": 12,
            "name": "Phone X",
            "category": {"id": 3, "name": "Electronics"},
            "like_count": 25
        },
        ...
    ]
    """

    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Product.objects.filter(
            likes__user=self.request.user
        )

        queryset = queryset.select_related('category')

        queryset = queryset.prefetch_related(
            Prefetch('likes', queryset=ProductLike.objects.select_related('user'))
        )

        return queryset
