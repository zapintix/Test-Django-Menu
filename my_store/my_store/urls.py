from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from store.views import ProductsViewSet, CartViewSet, OrderViewSet,CategoryViewSet, SearchProducts  
from .yasg import urlpatterns as doc_urls

router = routers.DefaultRouter()
router.register(r'api/product', SearchProducts)
router.register(r'api/products', ProductsViewSet, basename='products')
router.register(r'api/cart', CartViewSet)
router.register(r'api/ord', OrderViewSet)
router.register(r'api/categories', CategoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
]

urlpatterns += doc_urls