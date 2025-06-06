from django.utils import timezone

from ..utils import random_otp, send_otp

from .base import BaseMobileUserSerializer

class SendLoginOTPSerializer(BaseMobileUserSerializer):
    """
    Sends (generates) an OTP for login (mobile + OTP login).
    Only works if user exists and is_active=True.
    """


    def validate(self, attrs):
        user = self.get_user(attrs=attrs, require_active=True)
        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        user.otp = random_otp()
        user.otp_created_at = timezone.now()
        user.save()
        return user

    def to_representation(self, instance):
        ret = {'message': 'Login OTP sent.'}
        if send_otp(user=instance, otp=instance.otp):
            ret['otp'] = instance.otp
        return ret


