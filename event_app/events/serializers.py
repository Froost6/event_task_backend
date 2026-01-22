from rest_framework import serializers
from .models import Venue, Event, EventImage

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id','name','latitude','longitude']

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id','image','preview']


class EventSerializer(serializers.ModelSerializer):
    image = EventImageSerializer(many=True, read_only=True)
    venue_detail = VenueSerializer(source='venue', read_only=True)
    venue = serializers.PrimaryKeyRelatedField(queryset=Venue.objects.all())
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'desk', 'publish_datetime',
            'start_datetime', 'end_datetime', 'author', 'venue_detail',
            'venue', 'rating', 'status', 'weather', 'image'
        ]

