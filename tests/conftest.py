from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.timezone import timedelta

import pytest

from products.models import Product
from carts.models import Cart, DiscountCode

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
def product_factory(db):
    def create(**kwargs):
        return Product.objects.create(**kwargs)        
    return create

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_factory(db):
    def create_user(**kwargs):
        return User.objects.create(**kwargs)
    return create_user

@pytest.fixture
def cart(db, user):
    return Cart.objects.create(user=user)

@pytest.fixture
def discount_code(db):
    return DiscountCode.objects.create(
            title='DiscountCode 1',
            code='#123',
            expired_at=timezone.now() + timedelta(hours=1),
            discount_value=100,
            discount_type='F'
            )

@pytest.fixture
def discount_code_factory(db):
    def create_discount_code(**kwargs):
        return DiscountCode.objects.create(**kwargs)
    return create_discount_code