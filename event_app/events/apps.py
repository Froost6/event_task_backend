from django.apps import AppConfig

def ready(self):
    import events.signals

class EventsConfig(AppConfig):
    name = 'events'
