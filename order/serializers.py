from decimal import Decimal

from rest_framework import serializers

from product.models import Product
from product.serializers import ProductSerializer

from .models import Order


class OrderSerializer(serializers.ModelSerializer):
    # Leitura: os produtos (com suas categorias) aparecem completos no pedido
    product = ProductSerializer(many=True, read_only=True)
    # Escrita: os produtos são enviados apenas pelos ids
    products_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        write_only=True,
        many=True,
        allow_empty=False,
    )
    total = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'product', 'products_id', 'total', 'user']

    def get_total(self, instance):
        return sum((p.price for p in instance.product.all()), Decimal('0'))

    def create(self, validated_data):
        products = validated_data.pop('products_id')
        order = Order.objects.create(**validated_data)
        order.product.set(products)

        return order
