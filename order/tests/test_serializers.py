from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from order.models import Order
from order.serializers import OrderSerializer
from product.models import Category, Product


class OrderSerializerTest(TestCase):
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
        self.valid_data = {
            'user': self.user.id,
            'products_id': [self.product_1.id, self.product_2.id],
        }

    def test_serializer_accepts_valid_data(self):
        serializer = OrderSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_serializer_requires_user(self):
        data = dict(self.valid_data)
        data.pop('user')

        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)

    def test_serializer_requires_products(self):
        data = dict(self.valid_data)
        data.pop('products_id')

        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('products_id', serializer.errors)

    def test_serializer_rejects_empty_products(self):
        data = dict(self.valid_data, products_id=[])

        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('products_id', serializer.errors)

    def test_serializer_rejects_product_that_does_not_exist(self):
        data = dict(self.valid_data, products_id=[999999])

        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('products_id', serializer.errors)

    def test_serializer_rejects_user_that_does_not_exist(self):
        data = dict(self.valid_data, user=999999)

        serializer = OrderSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn('user', serializer.errors)

    def test_serializer_creates_order(self):
        serializer = OrderSerializer(data=self.valid_data)

        self.assertTrue(serializer.is_valid(), serializer.errors)
        order = serializer.save()

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(order.user, self.user)
        self.assertEqual(
            set(order.product.all()), {self.product_1, self.product_2}
        )

    def test_serializer_returns_expected_fields(self):
        order = Order.objects.create(user=self.user)
        order.product.add(self.product_1)

        serializer = OrderSerializer(order)

        self.assertEqual(
            set(serializer.data.keys()),
            {'id', 'product', 'total', 'user'},
        )

    def test_serializer_represents_products_with_categories(self):
        order = Order.objects.create(user=self.user)
        order.product.add(self.product_1, self.product_2)

        serializer = OrderSerializer(order)

        products = {item['title']: item for item in serializer.data['product']}
        self.assertEqual(set(products.keys()), {'Django', 'DRF'})
        self.assertEqual(products['Django']['category'][0]['slug'], 'livros')
        self.assertEqual(products['DRF']['category'], [])

    def test_serializer_calculates_total(self):
        order = Order.objects.create(user=self.user)
        order.product.add(self.product_1, self.product_2)

        serializer = OrderSerializer(order)

        self.assertEqual(serializer.data['total'], Decimal('120.50'))

    def test_products_id_is_write_only(self):
        order = Order.objects.create(user=self.user)
        order.product.add(self.product_1)

        serializer = OrderSerializer(order)

        self.assertNotIn('products_id', serializer.data)
