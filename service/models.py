from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User
from cloudinary.models import CloudinaryField

from django.db import models
from django.conf import settings

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    service_id = models.IntegerField()
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    phone_number = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True)
    is_first_purchase = models.BooleanField(default=True)

    class Meta:
        unique_together = ('user', 'service_id')



class ServiceImage(models.Model):
    Service = models.ForeignKey('Service', on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image', default='default.jpg')

class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01, message="Price must be positive")]
    )
    duration = models.DurationField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        default=1, 
        validators=[MinValueValidator(1, message="Quantity must be at least 1")]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.quantity} x {self.service.name} in {self.cart.user.username}'s cart"

class Order(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(Service, through='OrderItem')
    total_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01, message="Total price must be positive")]
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # Added field

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1, message="Quantity must be at least 1")]
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01, message="Price must be positive")]
    )

    def __str__(self):
        return f"{self.quantity} x {self.service.name} in Order #{self.order.id}"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    service = models.ForeignKey(
        Service, 
        on_delete=models.CASCADE, 
        related_name='reviews' 
    )
    rating = models.FloatField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'service')

    def __str__(self):
        return f"Review by {self.user.username} for {self.service.name}"