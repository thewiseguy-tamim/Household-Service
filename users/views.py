from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, UserProfileSerializer, UserSerializer, UserPromotionSerializer
from django.contrib.auth import get_user_model
from .permissions import IsAdminUser, IsProfileOwner
from users.serializers import UserServiceHistorySerializer
from rest_framework.decorators import action

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import generics, permissions


from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.http import JsonResponse
from django.contrib.auth import login

User = get_user_model()

def activate_user(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return JsonResponse({"detail": "Invalid activation link."}, status=400)

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return JsonResponse({"detail": "Account activated successfully!"})
    else:
        return JsonResponse({"detail": "Activation link is invalid or expired."}, status=400)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]

    def get_object(self):
        return self.request.user

class UpdateProfileView(generics.UpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwner]

    def get_object(self):
        return self.request.user

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    
    @action(detail=True, methods=['patch'], url_path='promote')
    def promote_user(self, request, pk=None):
        user = self.get_object()
        serializer = UserPromotionSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'status': 'success',
                'message': f'User {user.username} updated with role {user.role}'
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserServiceHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = UserServiceHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']  

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)