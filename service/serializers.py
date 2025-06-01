from rest_framework import serializers
from .models import Service, Cart, CartItem, Order, Review, OrderItem
from users.serializers import UserSerializer  

from rest_framework import serializers
from .models import Service, ServiceImage
from rest_framework import serializers
from .models import Purchase

class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ['full_name', 'address', 'phone_number', 'service_id']

class ServiceSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True, allow_null=True)
    average_rating = serializers.FloatField(
        source='annotated_avg', 
        read_only=True
    )
    image = serializers.ImageField(required=False, allow_null=True)  

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 
            'price', 'rating', 'average_rating', 'duration',
            'image',  
            'created_at', 'updated_at'
        ]

class CartItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'service', 'service_id', 'quantity']
        extra_kwargs = {
            'cart': {'read_only': True}
        }

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def create(self, validated_data):
        service_id = validated_data.pop('service_id')
        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise serializers.ValidationError("Service does not exist")
        
        cart = validated_data.get('cart', None)
        if not cart:
            if 'request' in self.context:
                cart, _ = Cart.objects.get_or_create(user=self.context['request'].user)
            else:
                raise serializers.ValidationError("Cart is required")

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            service=service,
            defaults={'quantity': validated_data.get('quantity', 1)}
        )

        if not created:
            cart_item.quantity += validated_data.get('quantity', 1)
            cart_item.save()

        return cart_item

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'created_at', 'updated_at']
        extra_kwargs = {
            'user': {'read_only': True}
        }

class OrderItemSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'service', 'quantity', 'price']
        extra_kwargs = {
            'order': {'read_only': True}
        }
        ref_name = 'ServiceOrderItem'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True, source='order_items')
    user = UserSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'total_price', 'status', 'created_at', 'updated_at', 'items', 'transaction_id']
        extra_kwargs = {
            'user': {'read_only': True}
        }

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }
