from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from order.models import Order
from product.models import Category, Product


class OrderViewSetTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='breno', password='senha-segura-123'
        )
        self.category = Category.objects.create(title='Livros', slug='livros')
        self.product_1 = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        self.product_1.category.add(self.category)
        self.product_2 = Product.objects.create(
            title='DRF', price=Decimal('70.50')
        )
        self.order = Order.objects.create(user=self.user)
        self.order.product.add(self.product_1)
        self.valid_data = {
            'user': self.user.id,
            'products_id': [self.product_1.id, self.product_2.id],
        }

    def test_list_returns_orders(self):
        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_returns_order_with_products_and_total(self):
        url = reverse('order-detail', args=[self.order.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['product'][0]['title'], 'Django')
        self.assertEqual(response.data['total'], Decimal('50.00'))

    def test_retrieve_returns_404_for_unknown_order(self):
        url = reverse('order-detail', args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order(self):
        response = self.client.post(
            reverse('order-list'), self.valid_data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 2)
        self.assertEqual(response.data['total'], Decimal('120.50'))

    def test_create_requires_products(self):
        data = dict(self.valid_data)
        data.pop('products_id')

        response = self.client.post(
            reverse('order-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('products_id', response.data)

    def test_create_rejects_unknown_user(self):
        data = dict(self.valid_data, user=999999)

        response = self.client.post(
            reverse('order-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('user', response.data)

    def test_update_order_products(self):
        url = reverse('order-detail', args=[self.order.id])
        data = {'user': self.user.id, 'products_id': [self.product_2.id]}

        response = self.client.put(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(list(self.order.product.all()), [self.product_2])

    def test_delete_order_keeps_products(self):
        url = reverse('order-detail', args=[self.order.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(Product.objects.count(), 2)
