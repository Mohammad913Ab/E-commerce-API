from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer


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
    API view to retrieve a single product by ID.

    Returns a single product if it is active and not deleted.
    """
    queryset = Product.objects.filter(is_active=True, is_delete=False)
    serializer_class = ProductSerializer
