from django.contrib import admin
from .models import Event, EventImage, Venue

class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude', 'weather')
    search_fields = ('name',)

admin.site.register(Venue, VenueAdmin)

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1  

class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'publish_datetime', 'start_datetime', 'end_datetime',
        'author', 'venue', 'rating', 'status', 'venue_weather'
    )
    list_filter = ('status', 'publish_datetime', 'start_datetime', 'venue')
    search_fields = ('title', 'description', 'venue__name')
    inlines = [EventImageInline] 

    def venue(self, obj):
        return obj.venue.name 
    
    def venue_weather(self, obj):
        return obj.venue.weather if obj.venue else None
    venue_weather.short_description = 'Venue Weather'

admin.site.register(Event, EventAdmin)
