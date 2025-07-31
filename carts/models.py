from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError

from products.models import Product

User = get_user_model()

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', )

    def __str__(self):
        return f"Cart #{self.id} for {self.user}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')

    def __str__(self):
        return f"{self.quantity} × {self.product.title}"

    @property
    def total_price(self):
        return self.product.price * self.quantity

class DiscountCode(models.Model):
    class DiscountTypes(models.TextChoices):
        PERCENTAGE = ('P', 'Percentage')
        FIXED = ('F', 'Fixed amount')

    title = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()
    discount_value = models.FloatField(
        help_text="Enter the discount amount. If the type is 'Percentage', provide a number "
        "between 0 and 100. If it's 'Fixed amount', enter the exact value to subtract from the price."
        )
    discount_type = models.CharField(
        choices=DiscountTypes.choices,
        default=DiscountTypes.PERCENTAGE,
        max_length=1,
        help_text="Select the type of discount. 'Percentage' deducts a "
        "percentage of the original price. 'Fixed amount' deducts a constant value."
        )
    is_active = models.BooleanField(default=True)
    can_uses = models.PositiveIntegerField(default=100)
    use_count = models.PositiveIntegerField(default=0, editable=False)

    class Meta:
        ordering = ('expired_at', )

    @property
    def expires_in(self):
        zero_delta = timedelta(0)
        if not self.is_active:
            return zero_delta
        
        dif = self.expired_at - timezone.now()
        if dif <= zero_delta:
            self.is_active = False
            self.save(update_fields=['is_active'])
            return zero_delta
        return dif

    def clean(self):
        if self.discount_type == self.DiscountTypes.PERCENTAGE and self.discount_value > 100:
            raise ValidationError({
                'discount_value': "Discount value cant upper than 100 while discount type is 'precentage'"
                })
        if not self.expired_at - timezone.now():
            raise ValidationError({
                'expired_at': "The expiration date of the discount cannot be before the present time."
                })
    
    def __str__(self):
        return self.title

class CartDiscountUse(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='discount')
    code = models.ForeignKey(DiscountCode, related_name='used_on', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.cart.user}: {self.code.title}"