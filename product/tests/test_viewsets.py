from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from product.models import Category, Product


class CategoryViewSetTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Livros', slug='livros')
        self.valid_data = {
            'title': 'Revistas',
            'slug': 'revistas',
            'description': 'Categoria de revistas',
            'active': True,
        }

    def test_list_returns_categories(self):
        Category.objects.create(title='Games', slug='games')

        response = self.client.get(reverse('category-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_retrieve_returns_one_category(self):
        url = reverse('category-detail', args=[self.category.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Livros')
        self.assertEqual(response.data['slug'], 'livros')

    def test_retrieve_returns_404_for_unknown_category(self):
        url = reverse('category-detail', args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_category(self):
        response = self.client.post(
            reverse('category-list'), self.valid_data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Category.objects.count(), 2)
        self.assertTrue(Category.objects.filter(slug='revistas').exists())

    def test_create_rejects_missing_title(self):
        data = dict(self.valid_data)
        data.pop('title')

        response = self.client.post(
            reverse('category-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('title', response.data)

    def test_create_rejects_duplicated_slug(self):
        data = dict(self.valid_data, slug='livros')

        response = self.client.post(
            reverse('category-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('slug', response.data)

    def test_update_category(self):
        url = reverse('category-detail', args=[self.category.id])

        response = self.client.put(url, self.valid_data, format='json')

        self.category.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.category.title, 'Revistas')
        self.assertEqual(self.category.slug, 'revistas')

    def test_partial_update_category(self):
        url = reverse('category-detail', args=[self.category.id])

        response = self.client.patch(
            url, {'title': 'Livros novos'}, format='json'
        )

        self.category.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.category.title, 'Livros novos')
        self.assertEqual(self.category.slug, 'livros')

    def test_delete_category(self):
        url = reverse('category-detail', args=[self.category.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Category.objects.count(), 0)


class ProductViewSetTest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Livros', slug='livros')
        self.other_category = Category.objects.create(
            title='Revistas', slug='revistas'
        )
        self.product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        self.product.category.add(self.category)
        self.valid_data = {
            'title': 'DRF na pratica',
            'description': 'Livro sobre DRF',
            'price': '70.50',
            'active': True,
            'categories_id': [self.category.id],
        }

    def test_list_returns_products(self):
        response = self.client.get(reverse('product-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Django')

    def test_retrieve_returns_product_with_category(self):
        url = reverse('product-detail', args=[self.product.id])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Django')
        self.assertEqual(response.data['category'][0]['slug'], 'livros')

    def test_retrieve_returns_404_for_unknown_product(self):
        url = reverse('product-detail', args=[999999])

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_product(self):
        response = self.client.post(
            reverse('product-list'), self.valid_data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 2)
        self.assertEqual(response.data['category'][0]['title'], 'Livros')

    def test_create_rejects_zero_price(self):
        data = dict(self.valid_data, price='0.00')

        response = self.client.post(
            reverse('product-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('price', response.data)

    def test_create_requires_categories(self):
        data = dict(self.valid_data)
        data.pop('categories_id')

        response = self.client.post(
            reverse('product-list'), data, format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('categories_id', response.data)

    def test_update_product_and_categories(self):
        url = reverse('product-detail', args=[self.product.id])
        data = dict(self.valid_data, categories_id=[self.other_category.id])

        response = self.client.put(url, data, format='json')

        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.title, 'DRF na pratica')
        self.assertEqual(
            list(self.product.category.all()), [self.other_category]
        )

    def test_partial_update_product_price(self):
        url = reverse('product-detail', args=[self.product.id])

        response = self.client.patch(url, {'price': '99.90'}, format='json')

        self.product.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.product.price, Decimal('99.90'))

    def test_delete_product(self):
        url = reverse('product-detail', args=[self.product.id])

        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
