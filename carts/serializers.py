from rest_framework import serializers

from products.models import Product
from .models import CartItem, Cart, CartDiscountUse, DiscountCode


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True, is_delete=False),
        write_only=True,
        source='product'
    )

    class Meta:
        model = CartItem
        fields = ('id', 'product_id', 'quantity', 'total_price')
        read_only_fields = ('id', 'total_price')


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True)

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
        cart_instance = validated_data['cart']
        code = validated_data['code']

        instance, created = CartDiscountUse.objects.get_or_create(
            cart=cart_instance,
            defaults={'code': code}
        )

        if not created:
            if instance.code != code:
                instance.code = code
                instance.save(update_fields=['code'])
            return instance

        # created == True, update counters on the DiscountCode
        code.use_count = (code.use_count or 0) + 1
        if code.can_uses:
            code.can_uses = max(0, code.can_uses - 1)
        code.save(update_fields=['use_count', 'can_uses'])

        return instance
