import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_app.settings')

os.environ['CELERY_TASK_ALWAYS_EAGER'] = 'True'
os.environ['CELERY_TASK_EAGER_PROPAGATES'] = 'True'

import django
django.setup()
from django.core import mail
from rest_framework.test import APITestCase
from django.conf import settings
from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import Venue, Event
from datetime import timedelta
from django.utils import timezone
from openpyxl import Workbook
from django.core.files.uploadedfile import SimpleUploadedFile
import io
from events.tasks import (
    update_weather_for_venues, 
    publish_scheduled_events,
    send_event_email
)

User = get_user_model()

class EventAPITestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(name='admin', email='Admin@mail.ru', password='adminpass')

        self.user = User.objects.create_user(name='user',email='User@mail.ru', password='userpass')

        self.venue = Venue.objects.create(name='Test Venue', latitude=40.7128, longitude=-74.0060, weather="sunny")

        self.event_data = {
            "title": "Test Event",
            "desk": "This is a test event.",
            "publish_datetime": timezone.now().isoformat(),
            "start_datetime": "2026-01-01T10:00:00Z",
            "end_datetime": "2026-01-01T12:00:00Z",
            "venue": self.venue.id,
            "rating": 10,
            "status": "PUBLISHED",
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

class EventXlxsAPITestCase(APITestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(name='Admin', email = "Admin@mail.ru", password='adminpass')

        self.user = User.objects.create_user(name='User', email='User@mail.ru', password='userpass')

        self.venue = Venue.objects.create(name="Test Venue", latitude=40.87352, longitude=-74.34635, weather='sunny')

        self.import_url = reverse('events:events-import')
        self.export_url = reverse('events:events-export')

    def create_test_xlxs(self, events_data):
        wb = Workbook()
        ws = wb.active
        ws.title = "Events"
        headers = [
            "title", "desk", "publish_datetime", "start_datetime", "end_datetime",
        "venue_name", "venue_coordinates", "rating", 'weather'
        ]
        ws.append(headers)
        for e in events_data:
            ws.append([
                e.get("title"),
                e.get("desk"),
                e.get("publish_datetime"),
                e.get("start_datetime"),
                e.get("end_datetime"),
                e.get("venue_name"),
                e.get('venue_coordinates'),
                e.get("rating"),
            ])
        file_stream = io.BytesIO()
        wb.save(file_stream)
        file_stream.seek(0)
        return file_stream
        
    def test_import_xlxs_creates_event(self):
        self.client.login(email="Admin@mail.ru", password="adminpass")

        events_data = [{
            "title": "Event 1",
            "desk": "Desk 1",
            "publish_datetime": "2026-01-01 08:00",
            "start_datetime": "2026-01-02 10:00",
            "end_datetime": "2026-01-02 12:00",
            "venue_name": self.venue.name,
            "venue_coordinates": "40.7128,-74.0060",
            "rating": 10
        }]
        upload_file = self.create_test_xlxs(events_data)

        xlxs_file = SimpleUploadedFile(
            'events.xlsx',
            upload_file.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        response = self.client.post(self.import_url, {'file': xlxs_file}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 1)
        self.assertEqual(Event.objects.get().title, "Event 1")
        self.assertEqual(response.data['created'], 1)
        self.assertEqual(response.data['errors'], [])

    def test_export_xlsx_returns_file(self):
        self.client.login(email="Admin@mail.ru", password="adminpass")

        Event.objects.create(
            title="Event",
            desk="Desk",
            publish_datetime=timezone.now(),
            start_datetime=timezone.now(),
            end_datetime=timezone.now(),
            venue=self.venue,
            rating=5,
            status="PUBLISHED",
            author=self.superuser
        )

        response = self.client.get(self.export_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )




class test_celery_test_task(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(
            name='Admin',
            email='admin@test.com',
            password='testpass'
        )
        
        self.venue = Venue.objects.create(
            name='Test Venue',
            latitude=55.7558,
            longitude=37.6173,
            weather={"temp": 20, "humidity": 50, 'wind_speed':14}
        )
    
    def test_weather_update(self):
        result = update_weather_for_venues.delay()
        result.get(timeout=10) 
        
        self.venue.refresh_from_db()
        self.assertIn('temp', self.venue.weather)
        self.assertIn('humidity', self.venue.weather)
        self.assertIn('wind_speed', self.venue.weather)
        
        self.assertGreaterEqual(self.venue.weather['temp'], -5)
        self.assertLessEqual(self.venue.weather['temp'], 35)

    def test_event_auto_publish(self):

        event = Event.objects.create(
            title="Test Event",
            desk="Test Description",
            publish_datetime=timezone.now() - timedelta(hours=1), 
            start_datetime=timezone.now() + timedelta(days=1),
            end_datetime=timezone.now() + timedelta(days=1, hours=2),
            author=self.user,
            venue=self.venue,
            rating=10,
            status="DRAFT"
        )

        print(f"Event status before task: {event.status}")
        print(f"Event publish_datetime: {event.publish_datetime}")
        
        result = publish_scheduled_events()
        
        print(f"Результат выполнения задачи: {result}")

        self.assertEqual(result["published"], 1)

        event.refresh_from_db()
        self.assertEqual(event.status, "PUBLISHED")

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Celery Task Report: Автопубликация событий')
        self.assertIn('Опубликовано 1 событий', mail.outbox[0].body)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        self.assertEqual(mail.outbox[0].to, [settings.ADMIN_EMAIL])
        
        print(f"Событие '{event.title}' успешно опубликовано!")
    
    def test_event_not_published_if_future(self):
        event = Event.objects.create(
            title="Future Event",
            desk="Should not publish yet",
            publish_datetime=timezone.now() + timedelta(days=1),
            start_datetime=timezone.now() + timedelta(days=2),
            end_datetime=timezone.now() + timedelta(days=2, hours=2),
            author=self.user,
            venue=self.venue,
            rating=10,
            status="DRAFT"
        )
        
        result = publish_scheduled_events.delay()
        task_result = result.get(timeout=10)
        
        event.refresh_from_db()
        
        self.assertEqual(event.status, "DRAFT")
        self.assertEqual(task_result['published'], 0)
        
        print(f"Событие '{event.title}' правильно осталось в DRAFT")
    
    def test_send_email_task(self):
        recipient_list = ['test@example.com']

        mail.outbox = []
        
        result = send_event_email.delay(
            subject="Test Email",
            message="This is a test message from Celery",
            recipient_list=recipient_list
        )
        
        task_result = result.get(timeout=10)

        self.assertIsNone(task_result)
        
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Test Email")
        self.assertEqual(mail.outbox[0].body, "This is a test message from Celery")
        self.assertEqual(mail.outbox[0].to, recipient_list)
        self.assertEqual(mail.outbox[0].from_email, settings.DEFAULT_FROM_EMAIL)
        
        print("Email задача выполнена успешно")

if __name__ == "__main__":
    import django
    django.setup()
    
    test = test_celery_test_task()
    test.setUp()
    
    try:
        test.test_weather_update()
        test.test_event_auto_publish()
        test.test_event_not_published_if_future()
        test.test_send_email_task()
        
        print("-" * 40)
        print("Все тесты пройдены успешно!")
        
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        

