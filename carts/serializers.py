from rest_framework import serializers
from rest_framework.decorators import action

from products.serializers import ProductSerializer
from products.models import Product

from .models import CartItem, Cart, CartDiscountUse

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
    items = CartItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Cart
        fields = ('id', 'user', 'items', 'total_price', 'created_at', 'updated_at', 'discount')
        read_only_fields = ('id', 'user', 'total_price', 'created_at', 'updated_at', 'discount')
        
        
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
    
class DiscountUseSerializer(serializers.ModelSerializer):
    cart = CartSerializer(read_only=True)
    cart_id = serializers.PrimaryKeyRelatedField(
        queryset=Cart.objects.all(), write_only=True, source='cart'
    )
    
    class Meta:
        model = CartDiscountUse
        fields = ('id', 'cart', 'cart_id', 'code', 'created_at')
        read_only_fields = ('id', 'cart', 'created_at')

    def create(self, validated_data):
        instance, created = CartDiscountUse.objects.get_or_create(
            cart_id=validated_data['cart'],
        )
        instance.code = validated_data['code']
        instance.save()
        return instance