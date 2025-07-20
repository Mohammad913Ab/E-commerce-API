from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView,
    VerifyPhoneView,
    SendLoginOTPView,
    LoginView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-phone/', VerifyPhoneView.as_view(), name='verify-phone'),
    path('send-login-otp/', SendLoginOTPView.as_view(), name='send-login-otp'),
    path('login/', LoginView.as_view(), name='login'),
    
    # JWT
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh')
]
