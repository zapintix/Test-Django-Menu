from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Product

class SearchProductsTestCase(APITestCase):
    def setUp(self):
        self.product = Product.objects.create(name='Test Product', price=10.0)

    def test_search_product(self):
        url = reverse('search_product')
        response = self.client.get(url, {'pk': self.product.pk})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.product.name)
        self.assertEqual(response.data['price'], str(self.product.price))  # Convert DecimalField to string for comparison

    def test_search_product_not_found(self):
        url = reverse('search_product')
        response = self.client.get(url, {'pk': 999})  # Assuming 999 is a non-existent product ID

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'Продукт не найден')