from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomBackend(ModelBackend):
    def authenticate(self, request, **kwargs):
        mobile = kwargs.get('mobile')
        try:
            user = User.objects.get(mobile=mobile)
            return user
        except User.DoesNotExist:
            pass