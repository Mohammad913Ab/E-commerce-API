from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import User
from .serializers import (
    RegisterSerializer,
    VerifyPhoneSerializer,
    SendLoginOTPSerializer,
    LoginSerializer
)


class RegisterView(CreateAPIView):
    """
    POST /register/
    - body: { "mobile": "...", "password": "...", "confirm_password": "..." }
    - Creates user (is_active=False), generates OTP for phone verification.
    - Response includes OTP only if debug=True in serializer context.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer




class VerifyPhoneView(APIView):
    """
    POST /verify-phone/
    - body: { "mobile": "...", "otp": 1234 }
    - Verifies the OTP and sets user.is_active=True
    """
    def post(self, request):
        serializer = VerifyPhoneSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class SendLoginOTPView(APIView):
    """
    POST /send-login-otp/
    - body: { "mobile": "..." }
    - Generates a fresh OTP and stores it on the user object (for OTP login).
    - Response includes OTP only if debug=True in serializer context.
    """
    def post(self, request):
        serializer = SendLoginOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(SendLoginOTPSerializer(instance=user).data, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
    POST /login/
    - body: one of:
        { "mobile": "...", "password": "..." }
        { "mobile": "...", "otp": 1234 }
    - Returns: { "refresh": "...", "access": "..." }
    """
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data, status=status.HTTP_200_OK)
