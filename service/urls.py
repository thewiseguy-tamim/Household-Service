from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet,
    CartViewSet,
    CartItemViewSet,
    OrderViewSet,
    ReviewViewSet
)

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'carts', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cart-item')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'reviews', ReviewViewSet, basename='review')

urlpatterns = [
    path('', include(router.urls)),
    path('carts/<int:pk>/add_item/', CartViewSet.as_view({'post': 'add_item'}), name='cart-add-item'),
    path('carts/<int:pk>/remove_item/', CartViewSet.as_view({'post': 'remove_item'}), name='cart-remove-item'),
]
