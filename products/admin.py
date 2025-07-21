from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import (
    Product,
    ProductComment,
    ProductCategory,
    ProductImage,
    ProductLike,
    ProductTag,
    ProductView,
    Attribute,
    AttributeValue,
    ProductAttributeValue
)

# -----------------------------------
# Shared Base Classes
# -----------------------------------

class BaseAdmin(admin.ModelAdmin):
    """Common options: readonly created_at, date hierarchy, ordering"""
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)


class ActiveDeleteAdmin(BaseAdmin):
    """Adds is_active and is_delete filters"""
    list_filter = ('is_active', 'is_delete', 'created_at')

class SlugPrepoulatedFieldMixin:
    prepopulated_fields = {'slug': ('title',)}


# -----------------------------------
# Inline Admin
# -----------------------------------

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    max_num = 5
    extra = 1
    readonly_fields = ('created_at', 'image_preview')

    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" height="80" />')
        return 'No image'
    image_preview.short_description = 'Preview'

class ProductAttributeValueInline(admin.TabularInline):
    model = ProductAttributeValue
    extra = 1
    raw_id_fields = ('attribute_value', )
    verbose_name = 'Attribute'
    verbose_name_plural = 'Attributes'

# -----------------------------------
# Model Admins
# -----------------------------------

@admin.register(Product)
class ProductAdmin(SlugPrepoulatedFieldMixin, ActiveDeleteAdmin):
    list_display = (
        'title', 'slug', 'price', 'category',
        'view_count', 'like_count', 'is_active', 'is_delete', 'created_at'
    )
    search_fields = ('title', 'slug', 'description')
    raw_id_fields = ('category',)
    filter_horizontal = ('tags',)
    readonly_fields = ActiveDeleteAdmin.readonly_fields + ('view_count', 'like_count')
    inlines = [ProductImageInline, ProductAttributeValueInline]


@admin.register(ProductComment)
class ProductCommentAdmin(BaseAdmin):
    list_display = ('user', 'product', 'short_text', 'reply', 'created_at', 'is_active', 'is_delete')
    list_filter = ('is_active', 'is_delete', 'created_at')
    search_fields = ('text', 'user__username', 'product__title')

    @admin.display(description='Comment')
    def short_text(self, obj):
        return str(obj)


@admin.register(ProductCategory)
class ProductCategoryAdmin(ActiveDeleteAdmin):
    list_display = ('title', 'slug', 'parnt', 'is_active', 'is_delete', 'created_at')
    search_fields = ('title', 'slug')
    ordering = ('title',)


@admin.register(ProductTag)
class ProductTagAdmin(SlugPrepoulatedFieldMixin, ActiveDeleteAdmin):
    list_display = ('title', 'slug', 'is_active', 'is_delete', 'created_at')
    search_fields = ('title', 'slug')
    ordering = ('title',)


@admin.register(ProductView)
class ProductViewAdmin(BaseAdmin):
    list_display = ('product', 'user', 'ip_address', 'created_at')
    search_fields = ('product__title', 'user__username', 'ip_address')
    list_filter = ('created_at',)


@admin.register(ProductLike)
class ProductLikeAdmin(BaseAdmin):
    list_display = ('product', 'user', 'created_at')
    search_fields = ('product__title', 'user__username')
    list_filter = ('created_at',)

@admin.register(AttributeValue)
class AttributeValueAdmin(BaseAdmin):
    search_fields = ('value', 'attribute__title')
    list_filter = ('attribute__title', )
    raw_id_fields = ('attribute', )

@admin.register(Attribute)
class AttributeAdmin(SlugPrepoulatedFieldMixin, BaseAdmin):
    search_fields = ('title', 'slug')
    