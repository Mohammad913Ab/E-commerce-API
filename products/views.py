from rest_framework.viewsets import ModelViewSet
from .serializers import ProductSerializer
from .models import Product

class ProductViewSet(ModelViewSet):
    """
    ViewSet for managing Product objects.

    Provides CRUD operations:
    - Create new products
    - Retrieve list of products or single product detail
    - Update existing products
    - Delete products

    Uses ProductSerializer for serialization.
    """
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    
    