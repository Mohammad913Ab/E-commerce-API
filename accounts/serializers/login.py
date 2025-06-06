from rest_framework import serializers

from django.contrib.auth import authenticate

from rest_framework_simplejwt.tokens import RefreshToken

from .base import BaseMobileUserSerializer

from .mixins import OTPValidationMixin

class LoginSerializer(BaseMobileUserSerializer, OTPValidationMixin):
    """
    Logs in with either:
      1) mobile + password
      2) mobile + OTP
    Issues JWT tokens on success.
    """

    password = serializers.CharField(required=False, write_only=True)
    otp = serializers.IntegerField(required=False, write_only=True)
 
    def validate(self, attrs):
        password = attrs.get('password')
        otp = attrs.get('otp')
        user = self.get_user(attrs=attrs, require_active=True)

        # Case 1: password login
        if password:
            user_auth = authenticate(mobile=user.mobile, password=password)
            if not user_auth:
                raise serializers.ValidationError('Invalid credentials.')
            user = user_auth

        # Case 2: OTP login
        elif otp is not None:
            self.validate_otp_code(user=user, otp=otp)
            user.otp = None
            user.save()

        else:
            raise serializers.ValidationError('Provide either password or OTP.')

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
