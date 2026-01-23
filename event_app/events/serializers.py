from rest_framework import serializers
from .models import Venue, Event, EventImage

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = ['id','name','latitude','longitude','weather']

class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['id','image','preview']


class EventSerializer(serializers.ModelSerializer):
    image = EventImageSerializer(many=True, required = False)
    venue_detail = VenueSerializer(source='venue', read_only=True)
    venue = serializers.PrimaryKeyRelatedField(queryset=Venue.objects.all())
    author = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'desk', 'publish_datetime',
            'start_datetime', 'end_datetime', 'author', 'venue_detail',
            'venue', 'rating', 'status', 'image'
        ]
    
    def create(self,validated_data):
        images_data = validated_data.pop('image',[])
        event = Event.objects.create(**validated_data)

        event_images = []
        for idx,image in enumerate(images_data):
            image_instance = EventImage.objects.create(event=event, **image)
            event_images.append(image_instance)
        
            if idx == 0:
                image_instance.save()
        
        if event_images:
            event.image.set(event_images)

        return event

