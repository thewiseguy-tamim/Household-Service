from rest_framework import generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, UserProfileSerializer, UserSerializer, UserPromotionSerializer
from django.contrib.auth import get_user_model
from .permissions import IsAdminUser, IsProfileOwner
from users.serializers import UserServiceHistorySerializer
from rest_framework.decorators import action


User = get_user_model()

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

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