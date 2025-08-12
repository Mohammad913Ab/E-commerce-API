from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError
from rest_framework import status
import pytest

from carts.models import Cart, CartItem, CartDiscountUse

User = get_user_model()

import pytest
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from django.utils.timezone import timedelta

from rest_framework import status
from rest_framework.test import APIClient

from carts.models import Cart, CartItem, DiscountCode, CartDiscountUse
from carts.serializers import DiscountUseSerializer


pytestmark = pytest.mark.django_db


class TestCartApi:
    def test_cartitem_total_price(self, product, cart):
        item = CartItem.objects.create(cart=cart, product=product, quantity=3)
        assert item.total_price == product.price * 3

    def test_cart_total_price_without_discount(self, product_factory, user_factory):
        user = user_factory(mobile='09100000000')
        cart = Cart.objects.create(user=user)
        p1 = product_factory(title="a", price=40)
        p2 = product_factory(title="b", price=60)
        CartItem.objects.create(cart=cart, product=p1, quantity=2)  # 80
        CartItem.objects.create(cart=cart, product=p2, quantity=1)  # 60
        assert int(cart.total_price) == 140

    def test_cart_total_price_with_fixed_discount(self, product, cart, discount_code_factory):
        CartItem.objects.create(cart=cart, product=product, quantity=1)
        code = discount_code_factory(
            title='fixed',
            code='FIXED1',
            expired_at=timezone.now() + timedelta(hours=1),
            discount_value=20,
            discount_type='F',
            can_uses=5,
        )
        CartDiscountUse.objects.create(cart=cart, code=code)
        expected = int(product.price - code.discount_value)
        assert int(cart.total_price) == expected

    def test_cart_total_price_with_percentage_discount(self, product, cart, discount_code_factory):
        CartItem.objects.create(cart=cart, product=product, quantity=2)
        code = discount_code_factory(
            title='pct',
            code='PCT1',
            expired_at=timezone.now() + timedelta(hours=1),
            discount_value=25,
            discount_type='P',
            can_uses=5,
        )
        CartDiscountUse.objects.create(cart=cart, code=code)
        total = product.price * 2
        expected = int(total - (total * code.discount_value / 100.0))
        assert int(cart.total_price) == expected

    def test_discountcode_clean_invalid_percentage_raises(self):
        future = timezone.now() + timedelta(days=1)
        bad = DiscountCode(
            title='badpct',
            code='BAD1',
            expired_at=future,
            discount_value=150.0,
            discount_type='P',
        )
        with pytest.raises(ValidationError):
            bad.full_clean()

    def test_discountcode_clean_expired_at_in_past_raises(self):
        past = timezone.now() - timedelta(days=1)
        bad = DiscountCode(
            title='badt',
            code='BAD2',
            expired_at=past,
            discount_value=10,
            discount_type='F',
        )
        with pytest.raises(ValidationError):
            bad.full_clean()

    def test_discountcode_expires_in_sets_inactive(self, discount_code_factory):
        past = timezone.now() - timedelta(hours=1)
        code = discount_code_factory(
            title='past',
            code='PAST',
            expired_at=past,
            discount_value=5,
            discount_type='F',
            is_active=True,
        )
        delta = code.expires_in
        assert delta == timedelta(0)
        code.refresh_from_db()
        assert code.is_active is False

    def test_discountuse_serializer_create_and_idempotence(self, cart, discount_code_factory):
        code = discount_code_factory(
            title='use-test',
            code='USE1',
            expired_at=timezone.now() + timedelta(hours=1),
            discount_value=10,
            discount_type='F',
            can_uses=10,
            use_count=0,
        )

        data = {"cart_id": cart.id, "code": code.code}
        serializer = DiscountUseSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        created_instance = serializer.create(validated_data=serializer.validated_data)
        code.refresh_from_db()
        assert created_instance.code == code
        assert code.use_count == 1
        assert code.can_uses == 9

        # Running create again should not increment counts again because get_or_create returns existing
        created_instance2 = serializer.create(validated_data=serializer.validated_data)
        code.refresh_from_db()
        assert created_instance2.id == created_instance.id
        assert code.use_count == 1  # still 1
        assert code.can_uses == 9  # still 9

    def test_discount_api_view_success_and_error_flows(self, api_client, user, cart, product, discount_code_factory):
        api_client.force_authenticate(user=user)
        CartItem.objects.create(cart=cart, product=product, quantity=1)

        code = discount_code_factory(
            title='ok',
            code='OK1',
            expired_at=timezone.now() + timedelta(hours=1),
            discount_value=50,
            discount_type='F',
            can_uses=2,
        )

        resp = api_client.post(reverse('cart-discount'), {"cart": cart.id, "code": code.code}, format='json')
        assert resp.data == status.HTTP_200_OK
        cart.refresh_from_db()
        assert hasattr(cart, 'discount')
        assert cart.discount.code == code

        # exhausted usage
        exhausted = discount_code_factory(
            title='exh',
            code='EXH',
            expired_at=timezone.now() + timedelta(hours=1),
            discount_value=5,
            discount_type='F',
            can_uses=0,
        )
        resp2 = api_client.post(reverse('cart-discount'), {"cart_id": cart.id, "code": exhausted.code}, format='json')
        assert resp2.status_code == status.HTTP_200_OK
        assert 'error' in resp2.data

        # expired
        expired = discount_code_factory(
            title='exp',
            code='EXP2',
            expired_at=timezone.now() - timedelta(hours=1),
            discount_value=5,
            discount_type='F',
            can_uses=10,
        )
        resp3 = api_client.post(reverse('cart-discount'), {"cart_id": cart.id, "code": expired.code}, format='json')
        assert resp3.status_code == status.HTTP_200_OK
        assert 'error' in resp3.data

    def test_cart_viewset_create_and_update(self, api_client, user, product_factory):
        api_client.force_authenticate(user=user)
        p1 = product_factory(title='one', price=10)
        p2 = product_factory(title='two', price=20)

        resp = api_client.post(reverse('cart-list'), {"items": [{"product_id": p1.id, "quantity": 2}]}, format='json')
        assert resp.status_code == status.HTTP_201_CREATED
        cart_id = resp.data['id']

        resp_update = api_client.put(reverse('cart-detail', kwargs={'pk': cart_id}),
                                     {"items": [{"product_id": p2.id, "quantity": 3}]},
                                     format='json')
        assert resp_update.status_code == status.HTTP_200_OK
        from carts.models import Cart as CartModel
        c = CartModel.objects.get(id=cart_id)
        assert c.items.count() == 1
        assert int(c.total_price) == int(p2.price * 3)

    def test_unique_cart_per_user_enforced(self, user_factory):
        user = user_factory(mobile='09111111111')
        Cart.objects.create(user=user)
        with pytest.raises(IntegrityError):
            Cart.objects.create(user=user)


@pytest.fixture
def api_client():
    return APIClient()
