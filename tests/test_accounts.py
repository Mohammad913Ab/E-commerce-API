import pytest
from django.urls import reverse
from rest_framework import status
from accounts.models import User
from accounts.custom_backend import CustomBackend

@pytest.mark.django_db
class TestAccountApi:
    def test_create_user(self):
        # User with out mobile
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_user(
                mobile='',
                password='TestPass123'
                )
        assert 'The Mobile must be set' in str(exc_info)
        
        # User creation
        User.objects.create_user(
            mobile='09123456789',
            password='TestPass123'
            )
        
        # Superuser create test
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_superuser(
                password='TestPass123',
                mobile='09123456789',
                is_staff=False
                )
        assert 'Superuser must have is_staff=True.' in str(exc_info)
        
        with pytest.raises(ValueError) as exc_info:
            User.objects.create_superuser(
                password='TestPass123',
                mobile='09123456789',
                is_superuser=False
                )
        assert 'Superuser must have is_superuser=True.' in str(exc_info)
        
        User.objects.create_superuser(
                mobile='09123456700',
                password='TestPass123',
                )
        

        
    def test_authenticate_with_valid_mobile(self):
        user = User.objects.create_user(mobile='1234567890', password='test123')
        backend = CustomBackend()
        
        authenticated_user = backend.authenticate(request=None, mobile='1234567890')
        
        assert authenticated_user == user
    
    def test_authenticate_with_invalid_mobile(self):
        backend = CustomBackend()
        
        authenticated_user = backend.authenticate(request=None, mobile='0000000000')
        
        assert authenticated_user is None
    
    def test_register_user(self, api_client):
        url = reverse('register')
        user_mobile = '09123456789'
        data = {
            'mobile': user_mobile,
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }
        res = api_client.post(url, data)
        assert res.status_code == status.HTTP_201_CREATED
        assert 'mobile' in res.data
        assert User.objects.filter(mobile=user_mobile).exists()
    
    def test_verify_phone(self, api_client, user_factory):
        user = user_factory(mobile='09123456789', otp=1234, is_active=False)
        url = reverse('verify-phone')
        data = {
            'mobile': user.mobile,
            'otp': 1234
        }
        res = api_client.post(url, data)
        assert res.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.is_active is True

    def test_send_login_otp(self, api_client, user_factory):
        user = user_factory(mobile='09123456789')
        url = reverse('send-login-otp')
        data = {'mobile': user.mobile}
        res = api_client.post(url, data)
        assert res.status_code == status.HTTP_200_OK
        assert 'message' in res.data

    def test_login_with_password(self, api_client, user_factory):
        user = user_factory(mobile='09123456789')
        user.set_password('TestPass123')
        user.is_active = True
        user.save()

        url = reverse('login')
        data = {'mobile': user.mobile, 'password': 'TestPass123'}
        res = api_client.post(url, data)
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data
        assert 'refresh' in res.data

    def test_login_with_otp(self, api_client, user_factory):
        user = user_factory(mobile='09123456789', otp=1234, is_active=True)
        url = reverse('login')
        data = {'mobile': user.mobile, 'otp': 1234}
        res = api_client.post(url, data)
        assert res.status_code == status.HTTP_200_OK
        assert 'access' in res.data
        assert 'refresh' in res.data
