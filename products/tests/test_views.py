from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from ..models import Product

class ProductAPIViewTest(APITestCase):
    def setUp(self):
        # Create some products to test with
        self.product1 = Product.objects.create(title="Product A", price=100)
        self.product2 = Product.objects.create(title="Product B", price=200)
        self.url = reverse('product-list')
        
        
    def test_get_product_list(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['results'][0]['title'], self.product2.title)
