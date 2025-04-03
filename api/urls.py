from django.urls import path
from .views import ServiceSortByRatingView

urlpatterns = [
    path('services/sort_by_rating/', ServiceSortByRatingView.as_view(), name='sort_by_rating'),
]
