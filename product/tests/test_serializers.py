from decimal import Decimal

from django.test import TestCase

from product.models import Category, Product
from product.serializers import CategorySerializer, ProductSerializer


class CategorySerializerTest(TestCase):
    def setUp(self):
        self.valid_data = {
            'title': 'Livros',
            'slug': 'livros',
            'description': 'Categoria de livros',
            'active': True,
        }

    def test_serializer_accepts_valid_data(self):
        serializer = CategorySerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_title(self):
        data = dict(self.valid_data)
        data.pop('title')

        serializer = CategorySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_requires_slug(self):
        data = dict(self.valid_data)
        data.pop('slug')

        serializer = CategorySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('slug', serializer.errors)

    def test_serializer_rejects_blank_title(self):
        data = dict(self.valid_data, title='')

        serializer = CategorySerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_rejects_duplicated_slug(self):
        Category.objects.create(title='Livros', slug='livros')

        serializer = CategorySerializer(data=self.valid_data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('slug', serializer.errors)

    def test_serializer_creates_category(self):
        serializer = CategorySerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        category = serializer.save()

        self.assertEqual(Category.objects.count(), 1)
        self.assertEqual(category.title, 'Livros')
        self.assertEqual(category.slug, 'livros')
        self.assertTrue(category.active)

    def test_serializer_returns_expected_fields(self):
        category = Category.objects.create(**self.valid_data)

        serializer = CategorySerializer(category)

        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'title', 'slug', 'description', 'active'},
        )


class ProductSerializerTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(title='Livros', slug='livros')
        self.other_category = Category.objects.create(
            title='Revistas', slug='revistas'
        )
        self.valid_data = {
            'title': 'Django para iniciantes',
            'description': 'Livro sobre Django',
            'price': '89.90',
            'active': True,
            'categories_id': [self.category.id],
        }

    def test_serializer_accepts_valid_data(self):
        serializer = ProductSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_title(self):
        data = dict(self.valid_data)
        data.pop('title')

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('title', serializer.errors)

    def test_serializer_requires_price(self):
        data = dict(self.valid_data)
        data.pop('price')

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_serializer_requires_categories(self):
        data = dict(self.valid_data)
        data.pop('categories_id')

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('categories_id', serializer.errors)

    def test_serializer_rejects_empty_categories(self):
        data = dict(self.valid_data, categories_id=[])

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('categories_id', serializer.errors)

    def test_serializer_rejects_zero_price(self):
        data = dict(self.valid_data, price='0.00')

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_serializer_rejects_negative_price(self):
        data = dict(self.valid_data, price='-10.00')

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_serializer_rejects_invalid_price(self):
        data = dict(self.valid_data, price='abc')

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('price', serializer.errors)

    def test_serializer_rejects_category_that_does_not_exist(self):
        data = dict(self.valid_data, categories_id=[999999])

        serializer = ProductSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('categories_id', serializer.errors)

    def test_serializer_creates_product_with_categories(self):
        data = dict(
            self.valid_data,
            categories_id=[self.category.id, self.other_category.id],
        )
        serializer = ProductSerializer(data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()

        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(product.title, 'Django para iniciantes')
        self.assertEqual(product.price, Decimal('89.90'))
        self.assertEqual(product.category.count(), 2)

    def test_serializer_updates_product_categories(self):
        product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        product.category.add(self.category)
        data = dict(self.valid_data, categories_id=[self.other_category.id])

        serializer = ProductSerializer(product, data=data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        product = serializer.save()

        self.assertEqual(list(product.category.all()), [self.other_category])

    def test_serializer_returns_expected_fields(self):
        product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        product.category.add(self.category)

        serializer = ProductSerializer(product)

        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'title', 'description', 'price', 'active', 'category'},
        )

    def test_serializer_represents_category_inside_product(self):
        product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        product.category.add(self.category)

        serializer = ProductSerializer(product)

        categories = serializer.data['category']
        self.assertEqual(len(categories), 1)
        self.assertEqual(categories[0]['title'], 'Livros')
        self.assertEqual(categories[0]['slug'], 'livros')

    def test_categories_id_is_write_only(self):
        product = Product.objects.create(
            title='Django', price=Decimal('50.00')
        )
        product.category.add(self.category)

        serializer = ProductSerializer(product)

        self.assertNotIn('categories_id', serializer.data)
