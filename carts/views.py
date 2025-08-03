from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from django.core.exceptions import ValidationError

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, DiscountUseSerializer

from core.permissions import IsOwner

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def add_item(self, request, pk=None):
        cart = self.get_object()
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity', 1)
        if not product:
            return Response({'error': 'product is none'}, status=status.HTTP_400_BAD_REQUEST)
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += quantity
            item.save()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def update_item_quantity(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', -1))

        if not product_id or quantity < 0:
            return Response({'error': 'product_id and quantity required'}, status=400)

        try:
            item = CartItem.objects.get(cart=cart, product_id=product_id)
            if quantity <= 0:
                item.delete()
            else:
                item.quantity = quantity
                item.save()
        except CartItem.DoesNotExist:
            return Response({'error': 'Item does not exist'}, status=404)

        return Response(CartSerializer(cart).data)


class DiscountApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def post(self, request):
        serializer = DiscountUseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.create(validated_data=serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)