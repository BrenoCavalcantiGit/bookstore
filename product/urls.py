from django.urls import include, path
from rest_framework import routers

from .viewsets import CategoryViewSet, ProductViewSet

router = routers.SimpleRouter()
router.register(r'category', CategoryViewSet, basename='category')
router.register(r'product', ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)),
]
