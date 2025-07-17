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
    readonly_fields = ('created_at', 'image_preview')
    

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" />')
        return 'No image'
    

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'slug', 'price', 'category', 'view_count', 'like_count',
        'is_active', 'is_delete', 'created_at'
    )
    list_filter = ('is_active', 'is_delete', 'category', 'created_at')
    search_fields = ('title', 'slug', 'description')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('category',)
    filter_horizontal = ('tags',)
    readonly_fields = ('created_at', 'view_count', 'like_count')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    inlines = [ProductImageInline]

@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'short_text', 'reply', 'created_at', 'is_active', 'is_delete')
    list_filter = ('is_active', 'is_delete', 'created_at')
    search_fields = ('text', 'user__username', 'product__name')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    @admin.display(description='Comment')
    def short_text(self, obj):
        return str(obj)  # __str__ method of object
