from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, Venue
from django.utils import timezone
import requests
import random

@shared_task
def send_event_email(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

@shared_task
def published_sheduled_events():
    now = timezone.now()

    events_to_publish = Event.objects.filter(status="DRAFT", published_datetime__lte = now)
    for event in events_to_publish:
        event.status = "PUBLISHED"
        event.save()

@shared_task
def update_weather_for_venues():
    # api_key = 'e089dc936f0c460bbe02d8a402816b9e' 'Сначала пробовал реализовал поиск погоды по ширине и долготе 
    # через сайт с погодой, но потом перечитал задание и понял что мудрю, сделал просто рандомную погоду

    directions = ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW']
    events = Event.objects.all()
    for event in events:
        weather_data = {
            "temp": round(random.uniform(-5, 35), 1),
            "humidity": random.randint(20, 100),
            "pressure": random.randint(740, 780),
            "wind_speed": round(random.uniform(0, 15), 1),
            "wind_dir": random.choice(directions)
        }
        event.weather = weather_data
        event.save()

    

