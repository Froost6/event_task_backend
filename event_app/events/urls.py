from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import VenueViewSet, EventViewSet,ImportEventsAPIView, ExportEventsAPIView, UploadEventImagesAPIView

router = DefaultRouter()
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'events', EventViewSet, basename='event')

app_name = 'events'

urlpatterns = [
    path('api/', include(router.urls)),
    path("import/", ImportEventsAPIView.as_view(), name='events-import'),
    path("export/", ExportEventsAPIView.as_view(), name='events-export'),
    path('api/events/<int:event_id>/images/', UploadEventImagesAPIView.as_view(), name='upload-event-images'),
]
