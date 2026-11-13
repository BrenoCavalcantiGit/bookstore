from decimal import Decimal

from django.conf import settings
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Category, Product


class PaginationSettingsTest(SimpleTestCase):
    def test_pagination_is_configured_in_rest_framework(self):
        config = settings.REST_FRAMEWORK

        self.assertEqual(
            config['DEFAULT_PAGINATION_CLASS'],
            'rest_framework.pagination.PageNumberPagination',
        )
        self.assertEqual(config['PAGE_SIZE'], 5)

    def test_debug_toolbar_is_installed(self):
        self.assertIn('debug_toolbar', settings.INSTALLED_APPS)
        self.assertIn(
            'debug_toolbar.middleware.DebugToolbarMiddleware',
            settings.MIDDLEWARE,
        )


class CategoryPaginationTest(APITestCase):
    def setUp(self):
        for number in range(7):
            Category.objects.create(
                title=f'Categoria {number}', slug=f'categoria-{number}'
            )

    def test_list_returns_paginated_structure(self):
        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            set(response.data.keys()),
            {'count', 'next', 'previous', 'results'},
        )

    def test_first_page_has_page_size_items(self):
        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.data['count'], 7)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['previous'])
        self.assertIn('page=2', response.data['next'])

    def test_second_page_has_remaining_items(self):
        response = self.client.get(reverse('category-list'), {'page': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])

    def test_page_out_of_range_returns_404(self):
        response = self.client.get(reverse('category-list'), {'page': 3})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProductPaginationTest(APITestCase):
    def setUp(self):
        for number in range(6):
            Product.objects.create(
                title=f'Produto {number}', price=Decimal('10.00')
            )

    def test_first_page_has_page_size_items(self):
        response = self.client.get(reverse('product-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 6)
        self.assertEqual(len(response.data['results']), 5)
        self.assertIsNone(response.data['previous'])
        self.assertIn('page=2', response.data['next'])

    def test_second_page_has_remaining_items(self):
        response = self.client.get(reverse('product-list'), {'page': 2})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertIsNone(response.data['next'])

    def test_page_out_of_range_returns_404(self):
        response = self.client.get(reverse('product-list'), {'page': 3})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
