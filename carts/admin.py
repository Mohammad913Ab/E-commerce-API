from django.contrib import admin
from .models import Cart, CartItem, DiscountCode, CartDiscountUse

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at', 'total_price')
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'quantity', 'total_price')

@admin.register(DiscountCode)
class DiscountCodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'expires_in', 'created_at', 'expired_at', 'discount_value', 'discount_type', 'is_active', 'can_uses', 'use_count')
    search_fields = ('title', 'code')
    list_filter = ('discount_type', 'is_active')
    ordering  = ('discount_value', 'can_uses', 'expired_at', 'use_count')
    readonly_fields = ('use_count', )

admin.site.register(CartDiscountUse)
