from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ServiceViewSet,
    CartItemViewSet,
    OrderViewSet,
    ReviewViewSet,
    CartViewSet,
    OrderItemViewSet,
    initiate_payment,
    payment_success,
    payment_fail,
    payment_cancel,
    HasOrderedProduct,
    PurchaseCreateView,
    PurchaseCheckView
    
)
from users.views import UserServiceHistoryViewSet, UserViewSet

router = DefaultRouter()
router.register(r'services', ServiceViewSet, basename='service')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'cart-items', CartItemViewSet, basename='cartitem') 
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'order-items', OrderItemViewSet, basename='orderitem')
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'Client', UserServiceHistoryViewSet, basename='client')
router.register(r'users', UserViewSet, basename='user')
app_name = 'service'

urlpatterns = [
    path('', include(router.urls)),
    path('payment/initiate/', initiate_payment, name='initiate-payment'),
    path('payment/success/', payment_success, name='payment-success'),
    path("payment_cancel/", payment_cancel, name="payment-cancel"),  
    path("payment/fail/", payment_fail, name="payment-fail"),  
    path('orders/has-ordered/<int:service_id>/', HasOrderedProduct.as_view(), name='has-ordered-service'),
    path('api/purchase/', PurchaseCreateView.as_view(), name='purchase-create'),
    path('api/purchase/check/', PurchaseCheckView.as_view(), name='purchase-check'),
    
]
