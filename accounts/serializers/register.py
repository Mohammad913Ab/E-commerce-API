from rest_framework import serializers

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password 
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone

from ..utils import send_otp, random_otp




User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    """
    Registers a new User with mobile + password + confirm_password.
    - Validates that password == confirm_password.
    - Generates an OTP and sets is_active=False.
    """

    confirm_password = serializers.CharField(max_length=128, write_only=True)

    class Meta:
        model = User
        fields = ['mobile', 'password', 'confirm_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def validate(self, attrs):
        pw = attrs.get('password')
        cpw = attrs.get('confirm_password')

        if pw != cpw:
            raise serializers.ValidationError({
                'confirm_password': 'Passwords do not match.'
            })

        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        
        mobile = validated_data['mobile']
        password = validated_data['password']

        user = User(mobile=mobile,is_active=False)
        
        try:
            validate_password(password=password, user=user)
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})
        
        user.set_password(password)

        user.otp = random_otp()
        user.otp_created_at = timezone.now()
        user.save()

        return user

    def to_representation(self, instance):
        """
        Return the OTP in the response only if 'debug' is set in context.
        """
        ret = {
            'mobile': instance.mobile,
            'message': 'User registered. Verify phone with OTP.'
        }
        
        if send_otp(user=instance, otp=instance.otp):
            ret['otp'] = instance.otp
        return ret
