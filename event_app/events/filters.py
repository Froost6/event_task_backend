import django_filters
from .models import Event, Venue

class EventFilter(django_filters.FilterSet):
    start_datetime_from = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='gte', label='Start DateTime From')
    start_datetime_to = django_filters.DateTimeFilter(field_name='start_datetime', lookup_expr='lte', label='Start DateTime To')
    end_datetime_from = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='gte', label='End DateTime from')
    end_datetime_to = django_filters.DateTimeFilter(field_name='end_datetime', lookup_expr='lte', label='End DateTime To')
    venue = django_filters.NumberFilter(field_name='venue__id')
    rating_from = django_filters.NumberFilter(field_name='rating', lookup_expr='gte', label='Rating From')
    rating_to = django_filters.NumberFilter(field_name='rating', lookup_expr='lte', label='Rating To')

    class Meta:
        model = Event
        fields = ['start_datetime_from', 'start_datetime_to', 
                  'end_datetime_from', 'end_datetime_to', 'venue', 
                  'rating_from', 'rating_to']


