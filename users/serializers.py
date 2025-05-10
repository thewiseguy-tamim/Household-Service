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
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

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
        login_url = "https://home-snapx-ekr9rekgz-tamims-projects-bb8a6785.vercel.app/login"

        subject = "Activate your account"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [user.email]

        
        text_content = (
            f"Hello {user.first_name},\n\n"
            f"Click the link below to activate your account:\n{login_url}"
        )

        
        html_content = f"""
        <html>
        <body>
            <p>Hello {user.first_name},</p>
            <p>Welcome to HomeSnap! To activate your account, please click the button below:</p>
            <p style="text-align: center;">
                <a href="{login_url}" style="
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                ">Activate</a>
            </p>
            <br>
            <p>Thank you for joining us!</p>
            <p>Best regards,<br>The HomeSnap Team and Tamim Islam</p>
        </body>
        </html>
        """

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()




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
