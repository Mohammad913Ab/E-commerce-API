from django.utils.text import slugify
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import Truncator
from django.core.exceptions import ValidationError
from core.utils import product_image_upload_to

User = get_user_model()

class BaseProduct(models.Model):
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    class Meta:
        abstract = True
    
    def save(self, *args, **kwargs) -> None:
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.title
    
        
class ProductCategory(BaseProduct):
    parnt = models.ForeignKey(
        'self',
        models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['title']
    
class ProductTag(BaseProduct):
    class Meta:
        ordering = ['title']
        
class Product(BaseProduct):
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)

    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.CASCADE,
        related_name='products',
        null=True,
        blank=True
    )
    tags = models.ManyToManyField(
        ProductTag,
        related_name='products',
        blank=True
    )
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to=product_image_upload_to,
        )
    created_at = models.DateTimeField(auto_now_add=True)
    

    def clean(self):
        if self.product.images.count() >= 6:
            from django.core.exceptions import ValidationError
            raise ValidationError("A product can have up to 5 images.")
    
    def __str__(self):
        # return <product-slug>: <img-name>
        return ': '.join(self.image.name.split('/')[1:])
    
    
class ProductComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='comments', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments', blank=True)
    reply = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='replies',
        null=True,
        blank=True
        )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    def __str__(self):
        return Truncator(self.text).words(4, truncate='...')


class ProductView(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_views')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name='user_views')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.product}-{self.user}-{self.ip_address}'

class ProductLike(models.Model):
    product = models.ForeignKey(Product, models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('product', 'user')
    
    def __str__(self):
        return f'{self.product}-{self.user}'

class ProductInventory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inventory_logs')
    change = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created_at', )
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventories'

    def __str__(self):
        return f'{self.product.title}: {self.change}'
    
    def clean(self):
        new_quantity = self.product.quantity + self.change
        if new_quantity < 0:
            raise ValidationError({'change': 'The product quantity cannot be less than 0.'})
    
    def save(self, *args, **kwargs):
        self.product.quantity += self.change
        self.product.save(update_fields=['quantity'])
        return super().save(*args, **kwargs)

# -- Attribiute --

class Attribute(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Attribute'
        verbose_name_plural = 'Attributes'

    def __str__(self):
        return self.title


class AttributeValue(models.Model):
    attribute = models.ForeignKey(Attribute, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('attribute', 'value')
        verbose_name = 'Attribute Value'
        verbose_name_plural = 'Attribute Values'

    def __str__(self):
        return f"{self.attribute.title}: {self.value}"


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='attributes')
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'attribute_value')
        verbose_name = 'Product Attribute Value'
        verbose_name_plural = 'Product Attribute Values'

    def __str__(self):
        return f"{self.product.title} - {self.attribute_value}"
