from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer
from .models import Product

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(ModelViewSet):
    """
    ViewSet for managing Product objects.

    Provides CRUD operations:
    - Create new products
    - Retrieve list of products or single product detail
    - Update existing products
    - Delete products

    Supports filtering and search functionality:
    - Search by title and description using `?search=...`
    - Ordering by price and created_at using `?ordering=-price`

    Uses ProductSerializer for serialization.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']