from django.shortcuts import render
from rest_framework import viewsets
from .models import Venue, Event
from .serializers import VenueSerializer, EventSerializer, EventImageSerializer
from rest_framework.permissions import IsAdminUser

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return Event.objects.filter(status="PUBLISHED")
        return Event.objects.all()

