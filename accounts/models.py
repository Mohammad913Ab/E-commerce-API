from django.db import models
from django.contrib.auth.models import AbstractUser
from .custom_user_manager import CustomUserManager


class User(AbstractUser):
    username = None
    mobile = models.CharField(max_length=11, unique=True)
    otp = models.PositiveIntegerField(null=True, blank=True)
    otp_created_at = models.DateTimeField(auto_now=True)
    objects = CustomUserManager()
    USERNAME_FIELD = 'mobile'
    REQUIRED_FIELDS = []
    backend = 'accounts.custom_backend.CustomBackend'
    
    def __str__(self):
        return self.mobile