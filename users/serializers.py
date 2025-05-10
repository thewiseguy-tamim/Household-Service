from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from service.models import Order, OrderItem, Service
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from django.conf import settings
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

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

        self.send_activation_email(user)  

        return user

    def send_activation_email(self, user):  
        uid = str(user.pk)
        token = default_token_generator.make_token(user)

        activation_link = f"https://home-snapx-ekr9rekgz-tamims-projects-bb8a6785.vercel.app/activate/{uid}/{token}/"

        subject = "Activate your account"
        message = (
            f"Hello,\n\n"
            f"Welcome to HomeSnap! To activate your account, please click the link below to activate and:\n\n"
            f"{activation_link}\n\n"
            f"Thank you for joining us!\n\n"
            f"Best regards,\n"
            f"The HomeSnap Team and Tamim Islam"
        )

        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])



class UserProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False)
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                   'phone_number', 'bio', 'profile_picture', 'social_media', 'role', 'password', 'password2')
        read_only_fields = ('id', 'username', 'email', 'role')

    def validate(self, attrs):
        if 'password' in attrs and attrs['password'] != attrs.get('password2', None):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)
        
        if password:
            instance.set_password(password)
            instance.save()

        return instance
 
        
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
        fields = ['id', 'username', 'email', 'role', 'first_name', 'last_name', 'phone_number', 'bio', 'profile_picture', 'social_media']
        read_only_fields = ['username', 'email', 'role']

class UserPromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['role']
        
    def validate_role(self, value):
        if value not in [choice[0] for choice in User.ROLE_CHOICES]:
            raise serializers.ValidationError(f"Role must be one of {[choice[0] for choice in User.ROLE_CHOICES]}")
        return value
