from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django_filters.rest_framework import DjangoFilterBackend
from .models import Service, Cart, CartItem, Order, Review, OrderItem
from .serializers import (
    ServiceSerializer, 
    CartSerializer, 
    CartItemSerializer,
    OrderSerializer, 
    ReviewSerializer,
    OrderItemSerializer
)
from users.permissions import IsAdminUser
from django.db.models import Avg, OuterRef, Subquery
from rest_framework.permissions import AllowAny
import logging
from sslcommerz_lib import SSLCOMMERZ 
from rest_framework.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from rest_framework.views import APIView
from django.db.models import Q
from django.core.mail import send_mail
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from .models import Purchase
from .serializers import PurchaseSerializer


from django.core.mail import send_mail
from rest_framework import generics, views
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .models import Purchase
from .serializers import PurchaseSerializer

class PurchaseCreateView(generics.CreateAPIView):
    serializer_class = PurchaseSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        service_id = self.request.data.get('service_id')
        user = self.request.user if self.request.user.is_authenticated else None
        
        is_first_purchase = not Purchase.objects.filter(
            user=user, service_id=service_id
        ).exists()

        purchase = serializer.save(
            user=user,
            service_id=service_id,
            is_first_purchase=is_first_purchase
        )

        if is_first_purchase:
            try:
                send_mail(
                    subject='Thank You for Your Purchase!',
                    message=f'Dear {purchase.full_name},\n\nThank you for purchasing our service!\n\nDetails:\nService ID: {service_id}\nAddress: {purchase.address}\nPhone: [+country code]{purchase.phone_number}\n\nBest Regards,\nYour Company',
                    from_email='nottamimislam@gmail.com',
                    recipient_list=['your-test-email@example.com'],
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Email sending failed: {str(e)}")

        return purchase

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

class PurchaseCheckView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user = request.user if request.user.is_authenticated else None
        exists = Purchase.objects.filter(user=user).exists()
        return Response({'has_purchased': exists}, status=status.HTTP_200_OK)

logger = logging.getLogger(__name__)

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

    def create(self, request, *args, **kwargs):
        existing_cart = Cart.objects.filter(user=request.user).first()
        if existing_cart:
            serializer = self.get_serializer(existing_cart)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return super().create(request, *args, **kwargs)

class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_authenticators(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_authenticators()

    def filter_queryset(self, queryset):
        if getattr(self, 'swagger_fake_view', False):
            return CartItem.objects.none()
        return super().filter_queryset(queryset)

    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)

class OrderItemViewSet(viewsets.ModelViewSet):
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_authenticators(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_authenticators()

    def get_queryset(self):
        return OrderItem.objects.filter(order__user=self.request.user)

    def filter_queryset(self, queryset):
        if getattr(self, 'swagger_fake_view', False):
            return OrderItem.objects.none()
        return super().filter_queryset(queryset)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_authenticators(self):
        if getattr(self, 'swagger_fake_view', False):
            return []
        return super().get_authenticators()

    def filter_queryset(self, queryset):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        return super().filter_queryset(queryset)

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.items.all()

        if not cart_items.exists():
            logger.error("Cart is empty for user %s", request.user.id)
            return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate cart items
        for item in cart_items:
            if item.quantity < 1:
                logger.error("Invalid quantity %s for cart item %s", item.quantity, item.id)
                return Response(
                    {'error': f'Invalid quantity for service {item.service.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if item.service.price <= 0:
                logger.error("Invalid price %s for service %s", item.service.price, item.service.id)
                return Response(
                    {'error': f'Invalid price for service {item.service.name}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        total_price = sum(item.service.price * item.quantity for item in cart_items)
        if total_price <= 0:
            logger.error("Total price is %s for user %s", total_price, request.user.id)
            return Response(
                {'error': 'Total price must be positive'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order = Order.objects.create(
            user=request.user,
            total_price=total_price
        )
        logger.info("Created order %s for user %s", order.id, request.user.id)

        for item in cart_items:
            order_item = OrderItem.objects.create(
                order=order,
                service=item.service,
                quantity=item.quantity,
                price=item.service.price
            )
            logger.info("Created OrderItem %s for order %s", order_item.id, order.id)

        cart.items.all().delete()
        logger.info("Cleared cart items for user %s", request.user.id)

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'COMPLETED':
            logger.warning("Attempt to cancel completed order %s by user %s", order.id, request.user.id)
            return Response(
                {'error': 'Cannot cancel a completed order'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if order.status == 'CANCELLED':
            logger.warning("Attempt to cancel already cancelled order %s by user %s", order.id, request.user.id)
            return Response(
                {'error': 'Order is already cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        order.status = 'CANCELLED'
        order.save()
        logger.info("Cancelled order %s for user %s", order.id, request.user.id)
        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all().order_by('-id')
    serializer_class = ReviewSerializer
    permission_classes = [AllowAny]  
    
    def perform_create(self, serializer):
        user = self.request.user
        service = serializer.validated_data['service']
        
        if Review.objects.filter(user=user, service=service).exists():
            raise ValidationError("You have already reviewed this service.")
        
        serializer.save(user=user)
    
    def get_queryset(self):
        service_id = self.request.query_params.get('service')
        queryset = Review.objects.all().order_by('-id')
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset

@api_view(['POST'])
@permission_classes([AllowAny])
def initiate_payment(request):
    # Extract and validate request data
    amount = request.data.get('amount')
    order_id = request.data.get('orderId')
    num_items = request.data.get('numItems')
    cus_name = request.data.get('cus_name')
    cus_email = request.data.get('cus_email')
    cus_phone = request.data.get('cus_phone')
    ship_postcode = request.data.get('ship_postcode', '1000')  

    # Validation
    errors = {}
    try:
        amount = float(amount)
        if amount <= 0:
            errors['amount'] = 'Amount must be a positive number'
    except (TypeError, ValueError):
        errors['amount'] = 'Invalid amount format'

    if not order_id:
        errors['orderId'] = 'Order ID is required'
    try:
        order_id = int(order_id)
        if order_id <= 0:
            errors['orderId'] = 'Order ID must be a positive integer'
    except (TypeError, ValueError):
        errors['orderId'] = 'Invalid order ID format'

    try:
        num_items = int(num_items)
        if num_items <= 0:
            errors['numItems'] = 'Number of items must be a positive integer'
    except (TypeError, ValueError):
        errors['numItems'] = 'Invalid number of items format'

    if not cus_name or len(cus_name.strip()) < 2:
        errors['cus_name'] = 'Customer name must be at least 2 characters long'
    if not cus_email or '@' not in cus_email:
        errors['cus_email'] = 'Valid customer email is required'
    if not cus_phone or len(cus_phone.strip()) < 5:
        errors['cus_phone'] = 'Customer phone number must be at least 5 digits'
    if not ship_postcode or len(ship_postcode.strip()) < 4:
        errors['ship_postcode'] = 'Shipping postcode must be at least 4 characters'

    if errors:
        logger.error("Payment initiation failed due to validation errors: %s", errors)
        return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)

    # Fetch and update the order with the transaction ID
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        logger.error("Order with ID %s not found for user %s", order_id, request.user.id)
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    tran_id = f"txn_{order_id}"
    order.transaction_id = tran_id
    order.save()
    logger.info("Saved transaction ID %s for order %s", tran_id, order_id)

    settings = {
        'store_id': 'futur6810e83285aec',
        'store_pass': 'futur6810e83285aec@ssl',
        'issandbox': True
    }
    sslcz = SSLCOMMERZ(settings)

    post_body = {
        'total_amount': amount,
        'currency': "BDT",
        'tran_id': tran_id,
        'success_url': "https://household-service.vercel.app/payment/success/",
        'fail_url': "https://household-service.vercel.app/payment/fail/",
        'cancel_url': "https://household-service.vercel.app/payment/cancel/",
        'emi_option': 0,
        'cus_name': cus_name,
        'cus_email': cus_email,
        'cus_phone': cus_phone,
        'cus_add1': "Contact Us",
        'cus_city': "Dhaka",
        'cus_country': "Bangladesh",
        'shipping_method': "Courier",
        'ship_name': cus_name,
        'ship_add1': "Contact Us",
        'ship_city': "Dhaka",
        'ship_postcode': ship_postcode,
        'ship_country': "Bangladesh",
        'multi_card_name': "",
        'num_of_item': num_items,
        'product_name': "Service",
        'product_category': "General",
        'product_profile': "general"
    }

    try:
        response = sslcz.createSession(post_body)
        logger.info("SSLCOMMERZ response for order %s: %s", order_id, response)
    except Exception as e:
        logger.error("SSLCOMMERZ createSession failed for order %s: %s", order_id, str(e))
        return Response({"error": f"Payment gateway error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if response.get('status') == 'SUCCESS':
        return Response({"payment_url": response['GatewayPageURL']}, status=status.HTTP_201_CREATED)
    else:
        logger.error("SSLCOMMERZ session creation failed for order %s: %s", order_id, response)
        return Response({"error": response.get('failedreason', "Payment initiation failed")}, status=status.HTTP_400_BAD_REQUEST)

from datetime import datetime
@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def payment_success(request):
    logger.info("Received payment_success POST data: %s", request.POST)
    
    try:
        tran_id = request.POST.get('tran_id')
        if not tran_id or not tran_id.startswith('txn_'):
            return HttpResponseRedirect("http://localhost:5173/error-page/")

        try:
            order_id = int(tran_id.split('_')[1])
        except (IndexError, ValueError):
            return HttpResponseRedirect("http://localhost:5173/error-page/")

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return HttpResponseRedirect("http://localhost:5173/error-page/")

        # Set transaction_id if not already set
        if not order.transaction_id:
            order.transaction_id = tran_id

        settings = {
            'store_id': 'futur6810e83285aec',
            'store_pass': 'futur6810e83285aec@ssl',
            'issandbox': True
        }
        sslcz = SSLCOMMERZ(settings)

        try:
            verification_response = sslcz.transaction_query_tranid(tran_id)

            if verification_response.get('APIConnect') != 'DONE' or 'element' not in verification_response:
                return HttpResponseRedirect("http://localhost:5173/error-page/")

            transactions = verification_response['element']
            if not isinstance(transactions, list):
                transactions = [transactions]

            latest_transaction = None
            latest_date = None
            valid_statuses = ['VALID', 'VALIDATED']
            
            for transaction in transactions:
                if transaction.get('tran_id') == tran_id and transaction.get('status') in valid_statuses:
                    tran_date = transaction.get('tran_date')
                    if tran_date:
                        try:
                            parsed_date = datetime.strptime(tran_date, '%Y-%m-%d %H:%M:%S')
                            if latest_date is None or parsed_date > latest_date:
                                latest_date = parsed_date
                                latest_transaction = transaction
                        except ValueError:
                            continue

            if latest_transaction:
                # Save transaction_id and update order status
                if order.status != 'COMPLETED':
                    order.status = 'COMPLETED'
                order.save()  # Save both status and transaction_id
            else:
                return HttpResponseRedirect("http://localhost:5173/error-page/")

        except Exception as e:
            logger.error("SSLCOMMERZ verification failed: %s", str(e))
            return HttpResponseRedirect("http://localhost:5173/error-page/")

        return HttpResponseRedirect("http://localhost:5173/dashboard/orders/")

    except Exception as e:
        logger.error("Error processing payment success: %s", str(e))
        return HttpResponseRedirect("http://localhost:5173/error-page/")
    
@api_view(['POST'])
@permission_classes([AllowAny])
def payment_fail(request):
    order_id = request.POST.get('tran_id').split('_')[1]  
    try:
        order = Order.objects.get(id=order_id)  
        order.status = 'FAILED'
        order.save()
    except Order.DoesNotExist:
        logger.error("Order with ID %s not found", order_id)
        return HttpResponseRedirect("http://localhost:5173/error-page/")  
    
    return HttpResponseRedirect("http://localhost:5173/dashboard/orders/")

@api_view(['POST'])
@permission_classes([AllowAny])
def payment_cancel(request):
    order_id = request.POST.get('tran_id').split('_')[1]  
    order = Order.objects.get(id=order_id)  
    order.status = 'CANCELLED'
    order.save()
    return HttpResponseRedirect("http://localhost:5173/dashboard/orders/")

class HasOrderedProduct(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, service_id):
        user = request.user
        try:
            
            has_ordered = OrderItem.objects.filter(
                order__user=user,
                order__status='COMPLETED',  
                service_id=service_id
            ).exists()
            logger.info(f"User {user.id} checked for service {service_id}: {has_ordered}")
            return Response({'has_ordered': has_ordered})
        except Exception as e:
            logger.error(f"Error checking order for user {user.id}, service {service_id}: {str(e)}")
            return Response({'has_ordered': False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)