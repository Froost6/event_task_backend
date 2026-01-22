from rest_framework import serializers
from .models import Venue, Event, EventImage

class VenueSerializer(serializers.Serializer):
    class Meta:
        model = Venue
        field = ['id','name','latitude','longitude']

class EventImageSerializer(serializers.Serializer):
    class Meta:
        model = EventImage
        fields = ['id','image','preview']


class EventSerializer(serializers.Serializer):
    image = EventImageSerializer(many=True, read_only=True)
    venue = VenueSerializer(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'publish_datetime',
            'start_datetime', 'end_datetime', 'author',
            'venue', 'rating', 'status', 'weather', 'images'
        ]

