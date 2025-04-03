import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from service.models import Service, Cart, CartItem, Order, OrderItem, Review
from faker import Faker

User = get_user_model()

class Command(BaseCommand):
    help = 'Seeds the database with dummy data'

    def handle(self, *args, **options):
        fake = Faker()
        
        # Check if admin exists, create if not
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                role='ADMIN',
                phone_number='+1234567890'
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        else:
            self.stdout.write(self.style.NOTICE('Admin user already exists'))
        
        # Create regular users if they don't exist
        users = []
        for i in range(5):
            username = f'user{i}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password=f'{username}123',
                    role='CLIENT',
                    phone_number=fake.phone_number(),
                    bio=fake.text()
                )
                users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user {username}'))
            else:
                user = User.objects.get(username=username)
                users.append(user)
                self.stdout.write(self.style.NOTICE(f'User {username} already exists'))
        
        # Clear existing services and create new ones
        Service.objects.all().delete()
        services = []
        service_names = [
            'House Cleaning', 'Plumbing', 'Electrical', 
            'Gardening', 'Painting', 'Carpentry'
        ]
        
        for name in service_names:
            service = Service.objects.create(
                name=name,
                description=fake.paragraph(),
                price=random.uniform(20, 200),
                duration=timedelta(minutes=random.choice([30, 60, 90, 120]))
            )
            services.append(service)
            self.stdout.write(self.style.SUCCESS(f'Created service {name}'))
        
        # Clear existing carts and create new ones
        Cart.objects.all().delete()
        for user in users:
            cart = Cart.objects.create(user=user)
            for _ in range(random.randint(1, 3)):
                service = random.choice(services)
                CartItem.objects.create(
                    cart=cart,
                    service=service,
                    quantity=random.randint(1, 3)
                )
        
        # Clear existing orders and create new ones
        Order.objects.all().delete()
        for user in users:
            order = Order.objects.create(
                user=user,
                total_price=0  # Will be updated
            )
            total = 0
            for _ in range(random.randint(1, 3)):
                service = random.choice(services)
                quantity = random.randint(1, 3)
                price = service.price * quantity
                OrderItem.objects.create(
                    order=order,
                    service=service,
                    quantity=quantity,
                    price=price
                )
                total += price
            order.total_price = total
            order.save()
        
        # Clear existing reviews and create new ones
        Review.objects.all().delete()
        for service in services:
            for user in random.sample(users, random.randint(1, 3)):
                Review.objects.create(
                    user=user,
                    service=service,
                    rating=random.randint(1, 5),
                    comment=fake.paragraph()
                )
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded database'))
