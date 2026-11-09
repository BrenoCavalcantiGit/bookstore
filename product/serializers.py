from rest_framework import serializers

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title', 'slug', 'description', 'active']


class ProductSerializer(serializers.ModelSerializer):
    # Leitura: as categorias aparecem completas dentro do produto
    category = CategorySerializer(many=True, read_only=True)
    # Escrita: as categorias são enviadas apenas pelos ids
    categories_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        write_only=True,
        many=True,
        allow_empty=False,
    )

    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'active',
            'category',
            'categories_id',
        ]

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('O preço deve ser maior que zero.')

        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories_id')
        product = Product.objects.create(**validated_data)
        product.category.set(categories)

        return product

    def update(self, instance, validated_data):
        categories = validated_data.pop('categories_id', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        if categories is not None:
            instance.category.set(categories)

        return instance
