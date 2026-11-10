from django.conf import settings
from django.db import models

from product.models import Product


class Order(models.Model):
    # Um pedido tem vários produtos e pertence a um usuário
    product = models.ManyToManyField(Product)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return f'Pedido {self.pk}'
