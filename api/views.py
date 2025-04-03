from rest_framework import generics
from service.models import Service
from service.serializers import ServiceSerializer
from rest_framework.filters import OrderingFilter

class ServiceSortByRatingView(generics.ListAPIView):
    serializer_class = ServiceSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['average_rating']
    ordering = ['-average_rating']
    
    def get_queryset(self):
        return Service.objects.all()
