import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'event_app.settings')

app = Celery('event_app')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'update-weather-every-30-min' : {
        'task':'events.tasks.update_weather_for_venues',
        'schedule': 1800.0,
    }
}