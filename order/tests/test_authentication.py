from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from order.models import Order
from product.models import Category, Product


class OrderAuthenticationTest(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username='breno', password='senha-segura-123'
        )
        self.other_user = user_model.objects.create_user(
            username='maria', password='senha-segura-123'
        )
        self.token = Token.objects.create(user=self.user)
        self.product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        self.order = Order.objects.create(user=self.user)
        self.order.product.add(self.product)
        self.other_order = Order.objects.create(user=self.other_user)
        self.other_order.product.add(self.product)

    def authenticate(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

    def test_authtoken_app_is_installed(self):
        self.assertIn('rest_framework.authtoken', settings.INSTALLED_APPS)

    def test_list_requires_authentication(self):
        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_requires_authentication(self):
        data = {'user': self.user.id, 'products_id': [self.product.id]}

        response = self.client.post(
            reverse('order-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 2)

    def test_invalid_token_is_rejected(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token token-invalido')

        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_valid_token_allows_access(self):
        self.authenticate()

        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_only_sees_own_orders(self):
        self.authenticate()

        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.order.id)

    def test_user_cannot_retrieve_order_from_another_user(self):
        self.authenticate()
        url = reverse('order-detail', args=[self.other_order.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_cannot_delete_order_from_another_user(self):
        self.authenticate()
        url = reverse('order-detail', args=[self.other_order.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Order.objects.filter(pk=self.other_order.id).exists())


class OpenEndpointsTest(APITestCase):
    def setUp(self):
        Category.objects.create(title='Livros', slug='livros')
        Product.objects.create(title='Django', price=Decimal('50.00'))

    def test_product_list_stays_open_without_authentication(self):
        response = self.client.get(reverse('product-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_category_list_stays_open_without_authentication(self):
        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
