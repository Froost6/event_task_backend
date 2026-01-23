from django.contrib import admin
from .models import Event, EventImage, Venue
from django.utils.html import format_html

class VenueAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'latitude', 'longitude', 'weather')
    search_fields = ('name',)

admin.site.register(Venue, VenueAdmin)

class EventImageInline(admin.TabularInline):
    model = EventImage
    extra = 1  
    fields = ['image','preview_image']

    def preview_image(self, obj):
        if obj.preview:
            return format_html('<img src="{}" width="100" height="100"/>', obj.preview.url)
        return "No Preview"
    preview_image.short_description = 'Preview'

class EventAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'publish_datetime', 'start_datetime', 'end_datetime',
        'author', 'venue', 'rating', 'status', 'venue_weather', 'image_display'
    )
    list_filter = ('status', 'publish_datetime', 'start_datetime', 'venue')
    search_fields = ('title', 'description', 'venue__name')
    inlines = [EventImageInline] 

    def venue(self, obj):
        return obj.venue.name 
    
    def venue_weather(self, obj):
        return obj.venue.weather if obj.venue else None
    venue_weather.short_description = 'Venue Weather'

    def image_display(self,obj):
        if obj.image.exists():
            first_image = obj.image.first()
            return format_html('<img src="{}" width="100" height="100"/>', first_image.image.url)
        return "No images"
    image_display.short_deskription = "Preview Image"

admin.site.register(Event, EventAdmin)
