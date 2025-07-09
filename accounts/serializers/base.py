from rest_framework import serializers

from django.contrib.auth import get_user_model

User = get_user_model()


class BaseMobileUserSerializer(serializers.Serializer):
    mobile = serializers.CharField(max_length=11)

    def get_user(self, attrs, require_active=True):
        mobile = attrs.get('mobile')
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            raise serializers.ValidationError({'mobile': 'User not found.'})

        if require_active and not user.is_active:
            raise serializers.ValidationError({'mobile': 'Phone not verified yet.'})
        elif not require_active and user.is_active:
            raise serializers.ValidationError({'mobile': 'Phone already verified.'})
        
        return user
    