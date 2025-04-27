from django.urls import path, include
from .views import (
    MyTokenObtainPairView, 
    RegisterView, 
    UserProfileView, 
    UpdateProfileView
)
from . import views


urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    path('activate/<uidb64>/<token>/', views.activate_user, name='activate_user'),
]