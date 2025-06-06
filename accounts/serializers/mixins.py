from django.utils import timezone

from rest_framework import serializers

from datetime import timedelta


class OTPValidationMixin:
    @staticmethod
    def validate_otp_code(user, otp:int):
        if timezone.now() - user.otp_created_at > timedelta(minutes=5):
            raise serializers.ValidationError("OTP has expired.")
        
        if not user.otp == otp:
            raise serializers.ValidationError("Invalid OTP.")
