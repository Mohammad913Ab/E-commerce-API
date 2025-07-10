from rest_framework.viewsets import ModelViewSet

from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product
from .serializers import ProductSerializer
from core.permissions import IsAdminOrReadOnly

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

    Permission behavior:
    - Read operations (GET) are allowed for all users, including anonymous.
    - Write operations (POST, PUT, PATCH, DELETE) are restricted to authenticated users with proper permissions (e.g., admin).

    Uses ProductSerializer for serialization.
    """
    permission_classes = [IsAdminOrReadOnly]
    
    serializer_class = ProductSerializer
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at']
    
    def get_queryset(self):
        return Product.objects.filter(is_delete=False, is_active=True)

    def perform_destroy(self, instance):
        instance.is_delete = True
        instance.save()
