from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from order.models import Order
from product.models import Product


class OrderPaginationTest(APITestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(
            username='breno', password='senha-segura-123'
        )
        product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        for _ in range(6):
            order = Order.objects.create(user=user)
            order.product.add(product)

    def test_first_page_has_page_size_items(self):
        response = self.client.get(reverse('order-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['previous'])
        self.assertIn('page=2', response.data['next'])

    def test_second_page_has_remaining_items(self):
        response = self.client.get(reverse('order-list'), {'page': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNone(response.data['next'])

    def test_page_out_of_range_returns_404(self):
        response = self.client.get(reverse('order-list'), {'page': 3})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
