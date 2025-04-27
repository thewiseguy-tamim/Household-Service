from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from .models import Service, Cart, CartItem, Order, Review, OrderItem
from .serializers import (
    ServiceSerializer, 
    CartSerializer, 
    CartItemSerializer,
    OrderSerializer, 
    ReviewSerializer
)
from users.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, OuterRef, Subquery
from rest_framework.permissions import AllowAny


class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['average_rating', 'price', 'name']
    filterset_fields = ['name', 'price']
    permission_classes = [AllowAny]

    def get_queryset(self):
        first_rating_subquery = Review.objects.filter(
            service=OuterRef('pk')
        ).values('rating')[:1]

        return Service.objects.annotate(
            rating=Subquery(first_rating_subquery),
            average_rating=Avg('reviews__rating')
        ).order_by('-id') 

    
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_authenticators(self):
        if getattr(self, 'swagger_fake_view', False):
            return []  # No authentication for Swagger
        return super().get_authenticators()

    def filter_queryset(self, queryset):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()  # Bypass user filtering for Swagger
        return super().filter_queryset(queryset)

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_authenticators(self):
        if getattr(self, 'swagger_fake_view', False):
            return []  # No authentication for Swagger
        return super().get_authenticators()

    def filter_queryset(self, queryset):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()  # Bypass user filtering for Swagger
        return super().filter_queryset(queryset)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(
            user=request.user,
            total_price=sum(item.service.price * item.quantity for item in cart_items)
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                service=item.service,
                quantity=item.quantity,
                price=item.service.price
            )

        cart.items.all().delete()
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-id')
    serializer_class = ReviewSerializer
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    permission_classes = [AllowAny]
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
