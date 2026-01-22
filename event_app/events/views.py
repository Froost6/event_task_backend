import django_filters
from rest_framework import viewsets, filters
from .models import Venue, Event
from .serializers import VenueSerializer, EventSerializer
from .filters import EventFilter
from rest_framework.filters import SearchFilter, OrderingFilter
from .permissions import IsAdminReadOnly
from .pagination import TestPagination

class VenueViewSet(viewsets.ModelViewSet):
    queryset = Venue.objects.all()
    serializer_class = VenueSerializer

class EventViewSet(viewsets.ModelViewSet):
    serializer_class = EventSerializer
    permission_classes = [IsAdminReadOnly]
    pagination_class = TestPagination

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        SearchFilter,
        OrderingFilter,
    )

    filterset_class = EventFilter
    search_fields = ['title', 'venue__name']
    ordering_fields = ['start_datetime', 'end_datetime', 'title']
    ordering = ['title']

    def get_queryset(self):
        queryset = Event.objects.all()

        if not self.request.user.is_superuser:
            queryset = queryset.filter(status='PUBLISHED')

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
