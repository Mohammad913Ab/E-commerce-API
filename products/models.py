from django.utils.text import slugify
from django.db import models
from core.utils import product_image_upload_to

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
    
    