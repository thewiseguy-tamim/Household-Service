from django.contrib import admin
from service.models import Service, Cart, Order, OrderItem, CartItem, Review, ServiceImage
admin.site.register(Service)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(CartItem)
admin.site.register(Review)
admin.site.register(ServiceImage)

