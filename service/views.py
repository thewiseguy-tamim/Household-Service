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

class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['rating', 'price', 'name']
    filterset_fields = ['name', 'price']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsAdminUser()]
        return [permissions.AllowAny()]
    
    def get_renderer_context(self):
        context = super().get_renderer_context()
        if context is not None:
            context['request'].accepted_renderer.format = 'json'
        return context
    
    def get_queryset(self):
        one_rating = Review.objects.filter(
            service=OuterRef('pk')
        ).values('rating')[:1]  # grab any single rating, e.g., the first

        return Service.objects.annotate(
            rating=Subquery(one_rating)
        )
    
class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    # @action(detail=True, methods=['post'])
    # def add_item(self, request, pk=None):
    #     cart = self.get_object()
    #     serializer = CartItemSerializer(
    #         data=request.data,
    #         context={'request': request}
    #     )
    #     serializer.is_valid(raise_exception=True)
    #     serializer.save(cart=cart)
    #     return Response(serializer.data, status=status.HTTP_201_CREATED)

    # @action(detail=True, methods=['post'])
    # def remove_item(self, request, pk=None):
    #     cart = self.get_object()
    #     service_id = request.data.get('service_id')
    #     quantity = request.data.get('quantity', 1)

    #     try:
    #         cart_item = CartItem.objects.get(cart=cart, service_id=service_id)
    #     except CartItem.DoesNotExist:
    #         return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)

    #     if cart_item.quantity > quantity:
    #         cart_item.quantity -= int(quantity)
    #         cart_item.save()
    #     else:
    #         cart_item.delete()

    #     return Response(status=status.HTTP_204_NO_CONTENT)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

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
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
