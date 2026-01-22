from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Venue, Event
from datetime import datetime
from django.utils import timezone

User = get_user_model()

class EventAPITestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(name='admin', email='Admin@mail.ru', password='adminpass')

        self.user = User.objects.create_user(name='user',email='User@mail.ru', password='userpass')

        self.venue = Venue.objects.create(name='Test Venue', latitude=40.7128, longitude=-74.0060)

        self.event_data = {
            "title": "Test Event",
            "desk": "This is a test event.",
            "publish_datetime": timezone.now().isoformat(),
            "start_datetime": "2026-01-01T10:00:00Z",
            "end_datetime": "2026-01-01T12:00:00Z",
            "venue": self.venue.id,
            "rating": 10,
            "status": "PUBLISHED",
            "weather": None
        }

        self.event_url = reverse('events:event-list')

    def test_create_event_as_superuser(self):
        self.client.login(email='Admin@mail.ru', password='adminpass')
        response = self.client.post(self.event_url, self.event_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().title, 'Test Event')

    def test_create_event_as_user(self):
        self.client.login(email='User@mail.ru', password='userpass')
        response = self.client.post(self.event_url, self.event_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 0)

    def test_list_events_as_superuser(self):
        self.client.login(email='Admin@mail.ru', password='adminpass')
        self.client.post(self.event_url, self.event_data, format='json')
        response = self.client.get(self.event_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_events_as_user(self):
        self.client.login(email='Admin@mail.ru', password='adminpass')
        self.client.post(self.event_url, self.event_data, format='json')
        
        self.client.login(email='User@mail.ru', password='userpass')
        response = self.client.get(self.event_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_event_filter_by_date_range(self):
        self.client.login(email='Admin@mail.ru', password='adminpass')
        self.client.post(self.event_url, self.event_data, format='json')

        response = self.client.get(self.event_url, {'start_datetime_from': "2026-01-01T09:00:00Z", 'start_datetime_to': "2026-01-01T12:00:00Z"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_event_filtere_by_venue(self):
        self.client.login(email='Admin@mail.ru', password='adminpass')
        self.client.post(self.event_url, self.event_data, format='json')

        response = self.client.get(self.event_url, {'venue': self.venue.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_sorted_by_start_datetime(self):

        event_data2 = self.event_data.copy()
        event_data2['title'] = 'Another Event'
        event_data2['start_datetime'] = '2026-01-01T09:00:00Z'

        self.client.login(email='Admin@mail.ru', password='adminpass')
        self.client.post(self.event_url, self.event_data, format='json')
        self.client.post(self.event_url, event_data2, format='json')

        response = self.client.get(self.event_url, {'ordering':'start_datetime'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)        
        self.assertEqual(response.data[0]['title'], 'Another Event')
        self.assertEqual(response.data[1]['title'], 'Test Event')

    def test_event_search_by_title(self):
        self.client.login(email='Admin@mail.ru', password='adminpass')
        self.client.post(self.event_url, self.event_data, format='json')

        response = self.client.get(self.event_url, {'search': 'Test event'})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)