from rest_framework import serializers
from .models import Service, Cart, CartItem, Order, Review, OrderItem

class ServiceSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True, allow_null=True)
    average_rating = serializers.FloatField(
        source='annotated_avg', 
        read_only=True
    )

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 
            'price', 'rating', 'average_rating','duration',
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

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
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
