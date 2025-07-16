from django.utils.safestring import mark_safe
from django.contrib import admin
from .models import (
    Product,
    ProductComment,
    ProductCategory,
    ProductImage,
    ProductLike,
    ProductTag,
    ProductView
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    max_num = 5
    extra = 1
    readonly_fields = ['created_at', 'image_preview']
    

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" />')
        return 'No image'
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    readonly_fields = ('created_at', 'like_count', 'view_count')


    