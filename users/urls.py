from django.urls import path, include
from .views import (
    MyTokenObtainPairView, 
    RegisterView, 
    UserProfileView, 
    UpdateProfileView
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
    path('api/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', UpdateProfileView.as_view(), name='update_profile'),
    # path('promote/<int:pk>/', PromoteToAdminView.as_view(), name='promote_to_admin'),
]