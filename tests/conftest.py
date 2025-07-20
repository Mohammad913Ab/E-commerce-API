from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
import pytest

from products.models import Product

User = get_user_model()

@pytest.fixture
def user(db):
    return User.objects.create(mobile='09986543342', password='Zxcvbnm@123')
    
@pytest.fixture
def product(db):
    return Product.objects.create(
        title="ProductTest (1)",
        price=100
    )

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        return User.objects.create(**kwargs)
    return create_user
