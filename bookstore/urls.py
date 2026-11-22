from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('update_server/', views.update, name='update_server'),
    path('hello/', views.hello, name='hello'),
    path('api/', include('product.urls')),
    path('api/', include('order.urls')),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
