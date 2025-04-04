from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from service.models import Order, OrderItem, Service

User = get_user_model()

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['role'] = user.role
        return token

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            phone_number=validated_data.get('phone_number', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'phone_number', 'bio', 'profile_picture', 'social_media', 'role')
        read_only_fields = ('id', 'username', 'email', 'role')  
        
class ServiceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'name', 'price']

class OrderItemSerializer(serializers.ModelSerializer):
    service = ServiceHistorySerializer()
    
    class Meta:
        model = OrderItem
        fields = ['service', 'quantity', 'price']

class OrderSerializer1(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, source='order_items.all')
    
    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'created_at', 'order_items']

class UserServiceHistorySerializer(serializers.ModelSerializer):
    orders = OrderSerializer1(many=True, source='orders.all')
    profile_picture = serializers.ImageField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'phone_number', 
            'bio', 'profile_picture', 'social_media', 'orders'
        ]
        read_only_fields = fields

class UserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField()
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone_number', 'bio', 'profile_picture', 'social_media']
        read_only_fields = ['username', 'email']

class UserPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        
    def validate_role(self, value):
        if value not in [choice[0] for choice in User.ROLE_CHOICES]:
            raise serializers.ValidationError(f"Role must be one of {[choice[0] for choice in User.ROLE_CHOICES]}")
        return value