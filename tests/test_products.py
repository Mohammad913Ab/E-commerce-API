from rest_framework.test import APIClient
from rest_framework import status
from django.core.exceptions import ValidationError
from django.urls import reverse
import pytest

from products.models import (
    Attribute, AttributeValue, ProductAttributeValue, ProductComment,
    ProductInventory, Product
)
@pytest.mark.django_db
class TestProductApi:
    def test_product_detail(self, api_client, product):
        assert product.title == "ProductTest (1)"
        url = reverse('product-detail', kwargs={'pk': product.id})
        res = api_client.get(url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data.get('view_count') > 0
        
    def test_product_list(self, api_client):
        url = reverse('product-list')
        res = api_client.get(url)
        data = res.data
        assert res.status_code == status.HTTP_200_OK
        assert isinstance(data, dict)
        assert 'results' in data
        assert isinstance(data['results'], list)
        
    def test_unauthenticated_user_cannot_like(self, api_client, product):
        url = reverse('product-like', kwargs={'pk': product.id})
        res = api_client.post(url)
        assert (
            res.status_code == status.HTTP_401_UNAUTHORIZED or 
            res.status_code == status.HTTP_403_FORBIDDEN
        )
    def test_user_can_like_product_once(self, api_client, user, product):
        url = reverse('product-like', kwargs={'pk': product.id})
        
        api_client.force_authenticate(user=user)

        res = api_client.post(url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['liked'] == True
        assert res.data['like_count'] == 1
        
        res = api_client.post(url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data['liked'] == False
        assert res.data['like_count'] == 0
        
    def test_unauthenticated_user_cannot_comment(self, api_client, product):
        url = reverse('product-comment', kwargs={'pk': product.id})
        res = api_client.post(url)
        assert (
            res.status_code == status.HTTP_401_UNAUTHORIZED or 
            res.status_code == status.HTTP_403_FORBIDDEN
        )
        
    def test_user_can_like_product(self, api_client:APIClient, user, product):
        url = reverse('product-comment', kwargs={'pk': product.id})
        
        api_client.force_authenticate(user=user)
        
        res = api_client.post(url, data={'text':'Comment Test (1)'})
        assert res.status_code == status.HTTP_201_CREATED
        assert 'text' in res.data
        comment = ProductComment.objects.filter(product=product, user=user, text='Comment Test (1)').first()
        assert comment is not None
    
    def test_product_attributes(self, product):
        attribute = Attribute.objects.create(title='Color', slug='color')
        attribute_value = AttributeValue.objects.create(value='Red', attribute=attribute)
        product_attribute_value = ProductAttributeValue.objects.create(
            product=product,attribute_value=attribute_value
        )
        assert product_attribute_value in product.attributes.all()
        assert 'Red' == AttributeValue.objects.get(attribute__title='Color').value

    def test_inventory_prevents_negative_product_quantity(self, product):
        assert product.quantity == 0

        with pytest.raises(ValidationError) as exc_info:
            inventory = ProductInventory(product=product, change=-1)
            inventory.full_clean()
            inventory.save()
        
        assert 'The product quantity cannot be less than 0.' in str(exc_info)
        product.refresh_from_db()
        assert product.quantity == 0
    
    def test_inventory_plus_minus(self, product):
        inventory_plus_3 = ProductInventory.objects.create(product=product, change=3)
        product = Product.objects.get(id=product.id)
        assert product.quantity == 3
        inventory_minus_1 = ProductInventory.objects.create(product=product, change=-1)
        product = Product.objects.get(id=product.id)
        assert product.quantity == 2
        assert inventory_minus_1 in product.inventory_logs.all()
        assert inventory_plus_3 in product.inventory_logs.all()
        
        
        