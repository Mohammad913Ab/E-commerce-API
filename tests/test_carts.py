from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from django.utils.timezone import timedelta
from django.core.exceptions import ValidationError
from rest_framework import status
import pytest

from carts.models import Cart, CartItem

User = get_user_model()

@pytest.mark.django_db
class TestCartApi:
    def test_create_cart_and_cart_item(self, cart, product):
        assert str(cart) == "Cart #1 for 09986543342"
        item = CartItem.objects.create(cart=cart, product=product)
        assert str(item) == "1 × ProductTest (1)"

    def test_unauthenticated_user_create_cart(self, api_client):
        url = reverse('cart-list')
        res = api_client.post(url)
        assert (
            res.status_code == status.HTTP_401_UNAUTHORIZED or 
            res.status_code == status.HTTP_403_FORBIDDEN
        )
        
    def test_authenticated_user_create_cart(self, api_client, user):
        url = reverse('cart-list')
        api_client.force_authenticate(user=user)
        res = api_client.post(url)
        assert res.status_code == status.HTTP_201_CREATED
        assert 'user' in res.data
        assert res.data['user'] == user.id
        assert not res.data['items']

    def test_add_and_remove_item(self, api_client, cart, user, product):
        api_client.force_authenticate(user=user)
        # Add item
        url = reverse('cart-add-item', kwargs={'pk': cart.id})
        res = api_client.post(url, data={'product_id': product.id, 'quantity': 2})
        
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data['items']) == 1

        # Remove item
        url = reverse('cart-remove-item', kwargs={'pk': cart.id})
        res = api_client.post(url, data={'product_id': product.id})

        assert res.status_code == status.HTTP_200_OK
        assert len(res.data['items']) == 0
        
    def test_plus_and_minus_item_quantity(self, api_client, cart, user, product):
        api_client.force_authenticate(user=user)

        # Add item with quantity 2
        url = reverse('cart-add-item', kwargs={'pk': cart.id})
        res = api_client.post(url, data={'product_id': product.id, 'quantity': 2})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['items'][0]['quantity'] == 2

        # Add same item with quantity 2 more (should now be 4)
        res = api_client.post(url, data={'product_id': product.id, 'quantity': 2})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['items'][0]['quantity'] == 4

        # Decrease quantity to 2
        url = reverse('cart-update-item-quantity', kwargs={'pk': cart.id})
        res = api_client.post(url, data={'product_id': product.id, 'quantity': 2})
        assert res.status_code == status.HTTP_200_OK
        assert res.data['items'][0]['quantity'] == 2

        # Decrease quantity to 0 (should remove item)
        res = api_client.post(url, data={'product_id': product.id, 'quantity': 0})
        assert res.status_code == status.HTTP_200_OK
        assert not len(res.data['items'])

        # Quantity or product id not send in request
        res = api_client.post(url, data={'product_id': product.id})
        assert res.status_code == status.HTTP_400_BAD_REQUEST
        assert res.data['error'] == 'product_id and quantity required'

        # Item does not exists
        res = api_client.post(url, data={'product_id': product.id, 'quantity': 2})
        assert res.status_code == status.HTTP_404_NOT_FOUND
        assert res.data['error'] == 'Item does not exist'

    # Discount test
    def test_discount_create(self, discount_code, discount_code_factory):
        assert str(discount_code.title) == 'DiscountCode 1'

        discount_code.delete()

        with pytest.raises(ValidationError) as exc_info:
            new_discount_code = discount_code_factory(
                title='DiscountCode',
                code='#123',
                expired_at=timezone.now() + timedelta(hours=1),
                discount_value=101,
                discount_type='P'
            )
            new_discount_code.full_clean()
            new_discount_code.save()
            
        assert "Discount value cant upper than 100 while discount type is 'precentage'" in str(exc_info)
        new_discount_code.delete()
        
        with pytest.raises(ValidationError) as exc_info:
            new_discount_code = discount_code_factory(
                title='DiscountCode',
                code='#123',
                expired_at=timezone.now() - timedelta(hours=1),
                discount_value=90,
                discount_type='P'
            )
            new_discount_code.full_clean()
            new_discount_code.save()

        assert "The expiration date of the discount cannot be before the present time." in str(exc_info)

    def test_discount_expired(self, discount_code):
        assert discount_code.expires_in
        discount_code.expired_at = timezone.now() - timedelta(minutes=5)
        assert not discount_code.expires_in