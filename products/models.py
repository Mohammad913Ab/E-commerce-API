from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_delete = models.BooleanField(default=False)

    
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    