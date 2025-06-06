from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework import serializers

from .base import BaseMobileUserSerializer

from .mixins import OTPValidationMixin

class VerifyPhoneSerializer(BaseMobileUserSerializer, OTPValidationMixin):
    """
    Verifies the user's phone by checking mobile + OTP.
    Sets is_active=True on success.
    """
    
    otp = serializers.IntegerField()
    class Meta:
        fields = ['mobile', 'otp']
    def validate(self, attrs):
        otp = attrs.get('otp')
        user = self.get_user(attrs=attrs, require_active=False)
        
        self.validate_otp_code(user=user, otp=otp)
        user.is_active = True
        user.otp = None
        user.save()

        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

