from rest_framework import serializers
from rest_framework.decorators import action

from products.serializers import ProductSerializer
from products.models import Product

from .models import CartItem, Cart

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True, is_delete=False),
        write_only=True,
        source='product'
    )
    
    class Meta:
        model = CartItem
        fields = ('id', 'product', 'product_id', 'quantity', 'total_price')
        read_only_fields = ('id', 'product_id', 'total_price')

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'itmes', 'total_price', 'created_at', 'updated_at')
        read_only_fields = ('id', 'user', 'total_price', 'created_at', 'updated_at')
        
        
    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        cart = Cart.objects.create(**validated_data)
        for item in items_data:
            CartItem.objects.create(cart=cart, **item)
        return cart
    
    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', [])
        instance.items.all().delete()
        for item in items_data:
            CartItem.objects.create(cart=instance, **item)
        return instance
        