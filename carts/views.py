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


class DiscountApiView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def post(self, request):
        serializer = DiscountUseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        code = serializer.validated_data['code']
        if code.can_uses < 1:
            return Response({'error': 'This discount code has reached its maximum usage limit and can no longer be used.'})
        if not code.expires_in:
            return Response({'error': 'This discount code has expired and is no longer valid.'})
        
        serializer.create(validated_data=serializer.validated_data)
        return Response(data=serializer.data, status=status.HTTP_200_OK)